import autograd.numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, Bounds
from scipy.constants import speed_of_light
from itertools import product
from pybrams.utils import Config
from pybrams.utils.coordinates import Coordinates

NUMBER_INITIAL_GUESSES_PER_VARIABLE = Config.get(
    __name__, "number_initial_guesses_per_variable"
)

# Position parameters [km]
MINIMUM_HORIZONTAL_LOCATION = Config.get(__name__, "minimum_horizontal_location")
MAXIMUM_HORIZONTAL_LOCATION = Config.get(__name__, "maximum_horizontal_location")
DEFAULT_HORIZONTAL_LOCATION = Config.get(__name__, "default_horizontal_location")
MINIMUM_ALTITUDE = Config.get(__name__, "minimum_altitude")
MAXIMUM_ALTITUDE = Config.get(__name__, "maximum_altitude")
DEFAULT_ALTITUDE = Config.get(__name__, "default_altitude")

# Velocity parameters [km/s]
MINIMUM_HORIZONTAL_SPEED = Config.get(__name__, "minimum_horizontal_speed")
MAXIMUM_HORIZONTAL_SPEED = Config.get(__name__, "maximum_horizontal_speed")
DEFAULT_HORIZONTAL_SPEED = Config.get(__name__, "default_horizontal_speed")

# Airplane parameters [km]
MINIMUM_AIRPLANE_DIMENSION = Config.get(__name__, "minimum_airplane_dimension")
MAXIMUM_AIRPLANE_DIMENSION = Config.get(__name__, "maximum_airplane_dimension")
DEFAULT_AIRPLANE_DIMENSION = Config.get(__name__, "default_airplane_dimension")

DEFAULT_VERTICAL_SPEED = Config.get(__name__, "default_vertical_speed")

TX_FREQUENCY = 49.97 * 1e6
SPEED_OF_LIGHT_KM = speed_of_light / 1e3  # [km/s]


class AirplaneInterference:
    def __init__(
        self,
        airplane_average_time,
        airplane_doppler_effect,
        airplane_amplitude,
        airplane_fit_residual,
        location,
    ):
        self.airplane_average_time = airplane_average_time
        self.airplane_doppler_effect = airplane_doppler_effect
        self.adim_airplane_amplitude = airplane_amplitude / max(airplane_amplitude)
        self.airplane_fit_residual = airplane_fit_residual

        self.location = location
        self.set_initial_guess()
        self.set_bounds()
        self.set_geometry()

    def set_initial_guess(self):
        x = np.linspace(
            MINIMUM_HORIZONTAL_LOCATION,
            MAXIMUM_HORIZONTAL_LOCATION,
            NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
        )[1:-1]
        y = np.linspace(
            MINIMUM_HORIZONTAL_LOCATION,
            MAXIMUM_HORIZONTAL_LOCATION,
            NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
        )[1:-1]
        z = np.linspace(
            MINIMUM_ALTITUDE, MAXIMUM_ALTITUDE, NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2
        )[1:-1]

        heading = np.linspace(0, 2 * np.pi, NUMBER_INITIAL_GUESSES_PER_VARIABLE + 1)[
            :NUMBER_INITIAL_GUESSES_PER_VARIABLE
        ]
        speed = np.linspace(
            MINIMUM_HORIZONTAL_SPEED,
            MAXIMUM_HORIZONTAL_SPEED,
            NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
        )[1:-1]

        airplane_dimension = np.linspace(
            MINIMUM_AIRPLANE_DIMENSION,
            MAXIMUM_AIRPLANE_DIMENSION,
            NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
        )[1:-1]

        self.initial_doppler_guesses = np.array(list(product(x, y, z, heading, speed)))
        self.initial_amplitude_guesses = np.array(
            list(product(x, y, z, heading, speed, airplane_dimension))
        )

    def set_bounds(self):
        lower_doppler_bounds = np.array(
            [
                MINIMUM_HORIZONTAL_LOCATION,
                MINIMUM_HORIZONTAL_LOCATION,
                MINIMUM_ALTITUDE,
                0,
                MINIMUM_HORIZONTAL_SPEED,
            ]
        )

        upper_doppler_bounds = np.array(
            [
                MAXIMUM_HORIZONTAL_LOCATION,
                MAXIMUM_HORIZONTAL_LOCATION,
                MAXIMUM_ALTITUDE,
                2 * np.pi,
                MAXIMUM_HORIZONTAL_SPEED,
            ]
        )

        lower_amplitude_bounds = np.append(
            lower_doppler_bounds, MINIMUM_AIRPLANE_DIMENSION
        )

        upper_amplitude_bounds = np.append(
            upper_doppler_bounds, MAXIMUM_AIRPLANE_DIMENSION
        )

        self.doppler_bounds = Bounds(lower_doppler_bounds, upper_doppler_bounds)
        self.amplitude_bounds = Bounds(lower_amplitude_bounds, upper_amplitude_bounds)

    def set_geometry(self):
        receiver_coordinates = self.location.coordinates.dourbocentric
        self.receiver_location = np.array(
            [receiver_coordinates.x, receiver_coordinates.y, receiver_coordinates.z]
        )

        TX_COORD = Coordinates.dourbes_dourbocentric_coordinates()
        self.tx_location = np.array([TX_COORD.x, TX_COORD.y, TX_COORD.z])

    def fit_doppler_effect(self):
        fit_parameters = np.zeros(self.initial_doppler_guesses.shape)
        fit_convergence = np.zeros(self.initial_doppler_guesses.shape[0])

        for index, initial_guess in enumerate(self.initial_doppler_guesses):
            try:
                popt, _, infodict, _, _ = curve_fit(
                    self.double_doppler_effect,
                    self.airplane_average_time,
                    self.airplane_doppler_effect,
                    p0=initial_guess,
                    bounds=self.doppler_bounds,
                    method="trf",
                    full_output=True,
                )
            except RuntimeError:
                continue

            fit_parameters[index, :] = popt
            fit_convergence[index] = np.sum(infodict["fvec"] ** 2)

        index_solution = np.argmin(fit_convergence)
        optimal_parameters = fit_parameters[index_solution, :]

        # Plot the fitted curve for the optimal parameters
        plt.figure()
        plt.plot(
            self.airplane_average_time,
            self.double_doppler_effect(self.airplane_average_time, *optimal_parameters),
            label="Fit",
        )

        # Plot the original data
        plt.plot(
            self.airplane_average_time,
            self.airplane_doppler_effect,
            "x",
            label="Data points",
            color="black",
        )
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Freq [Hz]")
        plt.title("Airplane frequency fit")
        plt.grid("True")
        plt.show()

        return self.double_doppler_effect(
            self.airplane_average_time, *optimal_parameters
        )

    def double_doppler_effect(self, t, x0, y0, z0, heading, speed):
        airplane_starting_location = np.array([x0, y0, z0])
        airplane_velocity = np.array(
            [speed * np.cos(heading), speed * np.sin(heading), DEFAULT_VERTICAL_SPEED]
        )

        airplane_time_location = (
            airplane_starting_location + t.reshape(-1, 1) * airplane_velocity
        )

        vector_tx_airplane = airplane_time_location - self.tx_location
        vector_receiver_airplane = airplane_time_location - self.receiver_location

        dot_tx_velocity = np.dot(vector_tx_airplane, airplane_velocity)
        dot_receiver_velocity = np.dot(vector_receiver_airplane, airplane_velocity)

        distance_tx_airplane = np.linalg.norm(vector_tx_airplane, axis=1)
        distance_receiver_airplane = np.linalg.norm(vector_receiver_airplane, axis=1)

        doppler_tx = (
            -dot_tx_velocity / distance_tx_airplane * TX_FREQUENCY / SPEED_OF_LIGHT
        )
        doppler_receiver = (
            -dot_receiver_velocity
            / distance_receiver_airplane
            * TX_FREQUENCY
            / SPEED_OF_LIGHT
        )
        doppler_total = doppler_tx + doppler_receiver
        return doppler_total

    def fit_amplitude_sinc(self):
        fit_parameters = np.zeros(self.initial_amplitude_guesses.shape)
        fit_convergence = np.zeros(self.initial_amplitude_guesses.shape[0])

        print(
            "len initiam aplitude guesses = ", self.initial_amplitude_guesses.shape[0]
        )

        for index, initial_guess in enumerate(self.initial_amplitude_guesses):
            print(" guess amplitude ", index)

            try:
                popt, _, infodict, _, _ = curve_fit(
                    self.amplitude_sinc,
                    self.airplane_average_time,
                    self.adim_airplane_amplitude,
                    p0=initial_guess,
                    bounds=self.amplitude_bounds,
                    method="trf",
                    full_output=True,
                )
            except RuntimeError:
                fit_convergence[index] = 1e9
                continue

            print(" opti param = ", popt)

            plt.figure()
            plt.plot(
                self.airplane_average_time,
                self.amplitude_sinc(self.airplane_average_time, *popt),
                label=f"Solution: {np.round(popt, 2)}",
            )
            plt.plot(
                self.airplane_average_time,
                self.adim_airplane_amplitude,
                "x",
                label="Original Data",
                color="black",
            )
            plt.show()

            fit_parameters[index, :] = popt
            fit_convergence[index] = np.sum(infodict["fvec"] ** 2)

        index_solution = np.argmin(fit_convergence)
        optimal_parameters = fit_parameters[index_solution, :]

        # Plot the fitted curve for the optimal parameters
        plt.figure()
        plt.plot(
            self.airplane_average_time,
            self.amplitude_sinc(self.airplane_average_time, *optimal_parameters),
            label="Fit",
        )

        # Plot the original data
        plt.plot(
            self.airplane_average_time,
            self.adim_airplane_amplitude,
            "x",
            label="Data points",
            color="black",
        )
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [-]")
        plt.title("Airplane amplitude fit")
        plt.grid("True")
        plt.show()

        return self.amplitude_sinc(self.airplane_average_time, *optimal_parameters)

    def amplitude_sinc(self, t, x0, y0, z0, heading, speed, airplane_dimension):
        airplane_starting_location = np.array([x0, y0, z0])
        airplane_velocity = np.array(
            [speed * np.cos(heading), speed * np.sin(heading), DEFAULT_VERTICAL_SPEED]
        )

        airplane_time_location = (
            airplane_starting_location + t.reshape(-1, 1) * airplane_velocity
        )

        angular_reference_vector = np.array([0, 0, 1])

        vector_tx_airplane = airplane_time_location - self.tx_location
        vector_receiver_airplane = airplane_time_location - self.receiver_location

        distance_tx_airplane = np.linalg.norm(vector_tx_airplane, axis=1)
        distance_receiver_airplane = np.linalg.norm(vector_receiver_airplane, axis=1)

        total_norm_distance_airplane = distance_tx_airplane + distance_receiver_airplane

        angular_reference_vector = np.array([0, 0, 1])
        vector_reflected_airplane = np.zeros_like(vector_tx_airplane)
        for i in range(vector_reflected_airplane.shape[0]):
            dot_product = np.dot(vector_tx_airplane[i, :], angular_reference_vector)
            vector_reflected_airplane[i, :] = (
                vector_tx_airplane[i, :] - 2 * dot_product * angular_reference_vector
            )

        vector_reflected_airplane = -vector_reflected_airplane
        phi = np.zeros(vector_reflected_airplane.shape[0])
        for i in range(vector_reflected_airplane.shape[0]):
            vector_a = vector_reflected_airplane[i, :]
            vector_b = vector_receiver_airplane[i, :]
            dot_product = np.dot(vector_a, vector_b)
            norm_a = np.linalg.norm(vector_a)
            norm_b = np.linalg.norm(vector_b)
            cos_angle = dot_product / (norm_a * norm_b)
            phi[i] = np.arccos(cos_angle)

        attenuation_factor = (
            min(total_norm_distance_airplane) ** 2 / (total_norm_distance_airplane) ** 2
        )
        beta = 2 * np.pi * TX_FREQUENCY / SPEED_OF_LIGHT
        psi_half = 1 / 2 * beta * airplane_dimension * np.sin(phi)
        amplitude_field = abs(
            attenuation_factor * airplane_dimension * np.sinc(psi_half / np.pi)
        )
        return amplitude_field / max(amplitude_field)
