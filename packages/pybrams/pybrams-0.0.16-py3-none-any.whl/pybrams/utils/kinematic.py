import autograd.numpy as np
from .geometry import compute_specular_points_coordinates
from scipy.optimize import fsolve


def compute_time_delays(
    solution, TX_COORD, rx_coordinates, ref_rx_coordinates, deceleration_model
):
    # Compute time delays between specular points for a given solution

    start_coordinates = np.array([solution[0], solution[1], solution[2]])
    end_coordinates = np.array(
        [
            solution[0] + solution[3],
            solution[1] + solution[4],
            solution[2] + solution[5],
        ]
    )

    specular_points_coordinates = compute_specular_points_coordinates(
        start_coordinates, end_coordinates, TX_COORD, rx_coordinates
    )
    ref_specular_point_coordinates = start_coordinates

    time_delays = np.array(
        [
            compute_specular_time_delay(
                solution,
                specular_point_coordinates,
                ref_specular_point_coordinates,
                deceleration_model,
            )
            for specular_point_coordinates in specular_points_coordinates
        ]
    )

    return time_delays


def compute_specular_time_delay(
    solution,
    specular_point_coordinates,
    ref_specular_point_coordinates,
    deceleration_model,
):

    velocity = np.array([solution[3], solution[4], solution[5]])
    velocity_norm = np.linalg.norm(velocity)

    specular_point_distance_vector = (
        specular_point_coordinates - ref_specular_point_coordinates
    )
    specular_point_distance = np.linalg.norm(specular_point_distance_vector)

    if specular_point_distance != 0:

        if np.dot(velocity, specular_point_distance_vector) < 0:

            specular_point_distance = -specular_point_distance

        if deceleration_model == "constant":

            time_delay = specular_point_distance / velocity_norm

        if deceleration_model == "linear":

            delta_t0 = solution[6]
            a = solution[7]
            time_delay = fsolve(
                linear_time_delay,
                0,
                args=(velocity_norm, delta_t0, a, specular_point_distance),
            )

    else:

        time_delay = 0

    return time_delay


def linear_time_delay(delta_t, velocity_norm, delta_t0, a, specular_point_distance):

    if delta_t <= delta_t0:

        return specular_point_distance - delta_t * velocity_norm

    if delta_t > delta_t0:

        return (
            specular_point_distance
            - delta_t * velocity_norm
            + 1 / 2 * a * (delta_t - delta_t0) ** 2
        )


def compute_linear_velocity_profile(velocity_norm, delta_t0, a, time_delays):

    speeds = np.zeros(time_delays.shape[0])

    for index, time_delay in enumerate(time_delays):

        if time_delay <= delta_t0:

            speeds[index] = velocity_norm

        if time_delay > delta_t0:

            speeds[index] = velocity_norm - a * (time_delay - delta_t0)

    return speeds


def exponential_time_delay(delta_t, velocity_norm, a1, a2, specular_point_distance):

    return (
        specular_point_distance
        - delta_t * velocity_norm
        + np.abs(a1) * np.exp(a2 * delta_t)
    )


def compute_exponential_velocity_profile(velocity_norm, a1, a2, time_delays):

    speeds = np.zeros(time_delays.shape[0])

    for index, time_delay in enumerate(time_delays):

        if time_delay > 0:

            speeds[index] = velocity_norm - np.abs(a1 * a2) * np.exp(a2 * time_delay)

        else:

            speeds[index] = velocity_norm

    return speeds
