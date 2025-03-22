import autograd.numpy as np

from scipy.optimize import minimize, Bounds, NonlinearConstraint
from pybrams.utils.geometry import compute_fresnel_geometry
from pybrams.utils.kinematic import compute_time_delays, compute_linear_velocity_profile
from pybrams.utils import Config
from pybrams.utils.constants import TX_COORD, WAVELENGTH

from .config import (
    generate_initial_guesses,
    set_lower_solution_bounds,
    set_upper_solution_bounds,
    set_lower_ineq_constraint_bounds,
    set_upper_ineq_constraint_bounds,
    ineq_constraints,
)

import copy

from autograd import grad, jacobian


class Solver:

    def __init__(self, brams_outputs, args=None):

        if args:

            self.velocity_model = args.velocity_model
            self.weight_pre_t0_objective = args.weight_pre_t0_objective
            self.outlier_removal = args.outlier_removal

        self.ref_system_code = None
        self.sorted_brams_outputs = None
        self.sort_brams_outputs(brams_outputs)
        self.format_inputs()
        self.set_ref_system()
        self.check_inputs()
        self.setup_solver()
        self.outlier_system_codes = []
        self.outlier_pre_t0_system_codes = []

    def solve(self):
        # Reconstruct a trajectory using BRAMS data

        self.converge_solution()
        self.output_solution()

    def sort_brams_outputs(self, brams_outputs):
        # Remove the system_codes which did not give a meteor t0

        for system_code, entry in brams_outputs.copy().items():

            meteor = entry["meteor"]

            if not meteor.t0:

                brams_outputs.pop(system_code)

        self.brams_outputs = brams_outputs
        self.sorted_brams_outputs = dict(
            sorted(self.brams_outputs.items(), key=lambda x: x[1]["meteor"].t0)
        )

    def format_inputs(self):
        # Format solver inputs from BRAMS outputs

        self.inputs = {}

        for system_code, entry in self.sorted_brams_outputs.items():

            if self.weight_pre_t0_objective == 0:

                t0 = entry["meteor"].t0_TOF

            else:

                t0 = entry["meteor"].t0

            self.inputs[system_code] = {
                "coordinates": np.array(
                    [
                        entry["location"].coordinates.dourbocentric.x,
                        entry["location"].coordinates.dourbocentric.y,
                        entry["location"].coordinates.dourbocentric.z,
                    ]
                ),
                "t0": t0,
                "SNR": entry["meteor"].SNR,
                "sigma_t0": entry["meteor"].sigma_t0,
                "v_pseudo_pre_t0": entry["meteor"].v_pseudo_pre_t0,
                "r_value_pre_t0": entry["meteor"].r_value_pre_t0,
                "sigma_pre_t0": entry["meteor"].sigma_pre_t0,
            }

        self.initial_inputs = copy.deepcopy(self.inputs)

    def set_ref_system(self):
        # Determine the reference system which will be used for the computation of time delays

        if self.weight_pre_t0_objective == 0:

            self.ref_system_code = min(
                self.inputs.items(), key=lambda item: item[1]["sigma_t0"]
            )[0]

        else:

            for system_code, entry in self.inputs.items():

                if (
                    entry.get("v_pseudo_pre_t0") is not None
                ):  # Check if field exists and is not None

                    self.ref_system_code = system_code
                    break  # Stop at the first valid system

        self.ref_t0 = self.inputs[self.ref_system_code]["t0"]
        self.ref_rx_coordinates = self.inputs[self.ref_system_code]["coordinates"]

    def check_inputs(self):

        self.inputs = {
            system_code: entry
            for system_code, entry in self.inputs.items()
            if abs(entry["t0"] - self.ref_t0)
            < Config.get(__name__, "maximum_time_delay")
        }

        if len(self.inputs) < Config.get(__name__, "minimum_number_systems"):

            raise ValueError(
                "Error occurred. Not enough BRAMS systems are exploitable."
            )

        print("")
        for system_code, entry in self.inputs.items():

            print(
                system_code,
                " - Time delay = ",
                entry["t0"] - self.ref_t0,
                " - sigma t0 = ",
                entry["sigma_t0"],
                " - Fresnel speed = ",
                entry["v_pseudo_pre_t0"],
                " - sigma_pre_t0 = ",
                entry["sigma_pre_t0"],
            )

    def setup_solver(self):

        self.system_codes = list(self.inputs.keys())
        self.ref_system_index = self.system_codes.index(self.ref_system_code)

        self.rx_coordinates = np.array(
            [
                system_code_dict["coordinates"]
                for system_code_dict in self.inputs.values()
            ]
        )

        self.time_delays = np.array(
            [
                (system_code_dict["t0"] - self.ref_t0)
                for system_code_dict in self.inputs.values()
            ]
        )
        self.max_time_delays = np.max(np.abs(self.time_delays))

        self.SNR = np.array(
            [system_code_dict["SNR"] for system_code_dict in self.inputs.values()]
        )
        self.sigma_time_delays = np.array(
            [
                np.sqrt(
                    system_code_dict["sigma_t0"] ** 2
                    + self.inputs[self.ref_system_code]["sigma_t0"] ** 2
                )
                for system_code_dict in self.inputs.values()
            ]
        )

        self.v_pseudo_pre_t0s = np.array(
            [
                system_code_dict["v_pseudo_pre_t0"]
                for system_code_dict in self.inputs.values()
                if system_code_dict["v_pseudo_pre_t0"]
            ]
        )
        self.system_codes_pre_t0s = [
            system_code
            for system_code, system_code_dict in self.inputs.items()
            if system_code_dict["v_pseudo_pre_t0"]
        ]
        self.rx_coordinates_pre_t0s = np.array(
            [
                system_code_dict["coordinates"]
                for system_code_dict in self.inputs.values()
                if system_code_dict["v_pseudo_pre_t0"]
            ]
        )
        self.sigma_pre_t0s = np.array(
            [
                system_code_dict["sigma_pre_t0"]
                for system_code_dict in self.inputs.values()
                if system_code_dict["v_pseudo_pre_t0"]
            ]
        )

    def converge_solution(self):
        # Solve the trajectory problem, excluding the system_codes with too high residuals

        self.solve = True

        while self.solve:

            self.call_solver()
            self.compute_residuals()

            if self.outlier_removal:

                self.remove_outliers()

    def compute_residuals(self):

        self.recon_time_delays = compute_time_delays(
            self.solution,
            TX_COORD,
            self.rx_coordinates,
            self.ref_rx_coordinates,
            self.velocity_model,
        )
        self.time_delays_residuals = self.time_delays - self.recon_time_delays

        start_coordinates = np.array(
            [self.solution[0], self.solution[1], self.solution[2]]
        )
        end_coordinates = np.array(
            [
                self.solution[0] + self.solution[3],
                self.solution[1] + self.solution[4],
                self.solution[2] + self.solution[5],
            ]
        )

        self.recon_K = compute_fresnel_geometry(
            start_coordinates, end_coordinates, TX_COORD, self.rx_coordinates_pre_t0s
        )
        self.recon_pre_t0_speeds = (
            self.recon_K * np.sqrt(WAVELENGTH / 2) * self.v_pseudo_pre_t0s
        )
        self.recon_speed_solution = np.sqrt(
            self.solution[3] ** 2 + self.solution[4] ** 2 + self.solution[5] ** 2
        )
        self.speeds_residuals = self.recon_pre_t0_speeds - self.recon_speed_solution

        median_time_delays_residuals = np.median(np.abs(self.time_delays_residuals))
        rel_time_delays_residuals = (
            np.abs(self.time_delays_residuals - median_time_delays_residuals)
            / median_time_delays_residuals
        )
        self.max_rel_time_delays_residuals = np.max(rel_time_delays_residuals)

        self.rel_speeds_residuals = (
            self.recon_pre_t0_speeds - self.recon_speed_solution
        ) / self.recon_pre_t0_speeds
        median_speeds_residuals = np.median(np.abs(self.rel_speeds_residuals))
        rel_median_speeds_residuals = (
            np.abs(self.rel_speeds_residuals - median_speeds_residuals)
            / median_speeds_residuals
        )
        self.max_rel_speeds_residuals = np.max(rel_median_speeds_residuals)

        self.solve = False

    def remove_outliers(self):
        # Remove outlier stations (too high pre-t0 speed residual or time delay residual)
        print("time delays residuals = ", self.time_delays_residuals)
        print("speeds residuals = ", self.rel_speeds_residuals)

        speed_outlier = any(
            speed_residual > Config.get(__name__, "maximum_speed_residual")
            for speed_residual in abs(self.rel_speeds_residuals)
        )
        time_delay_outlier = any(
            time_delay_residual > Config.get(__name__, "maximum_time_delays_residual")
            for time_delay_residual in abs(self.time_delays_residuals)
        )
        speed_to_remove = (
            self.max_rel_speeds_residuals > self.max_rel_time_delays_residuals
        )

        if (
            (speed_outlier and time_delay_outlier and speed_to_remove)
            or (speed_outlier and not time_delay_outlier)
        ) and (self.weight_pre_t0_objective != 0):

            self.solve = True

            index_max_speed_residual = np.argmax(abs(self.rel_speeds_residuals))
            speed_outlier_system_code = self.system_codes_pre_t0s[
                index_max_speed_residual
            ]

            self.inputs[speed_outlier_system_code]["v_pseudo_pre_t0"] = None
            self.inputs[speed_outlier_system_code]["r_value_pre_t0"] = None

            self.outlier_pre_t0_system_codes.append(speed_outlier_system_code)

            self.inputs[speed_outlier_system_code]["t0"] = self.sorted_brams_outputs[
                speed_outlier_system_code
            ]["meteor"].t0_TOF

            print("Remove ", speed_outlier_system_code, " - too high speed residual")

        elif (speed_outlier and time_delay_outlier and not speed_to_remove) or (
            time_delay_outlier and not speed_outlier
        ):

            self.solve = True

            index_max_time_delay_residual = np.argmax(abs(self.time_delays_residuals))
            time_delay_outlier_system_code = self.system_codes[
                index_max_time_delay_residual
            ]
            self.inputs.pop(time_delay_outlier_system_code)

            self.outlier_system_codes.append(time_delay_outlier_system_code)

            print(
                "Remove ",
                time_delay_outlier_system_code,
                " - too high time delay residual",
            )

        if self.solve:

            self.set_ref_system()
            self.check_inputs()
            self.setup_solver()

    def remove_inputs(
        self, system_codes_to_remove=None, system_codes_to_remove_pre_t0s=None
    ):

        if system_codes_to_remove:
            for system_code in system_codes_to_remove:

                self.inputs.pop(system_code)
                self.outlier_system_codes.append(system_code)

        if system_codes_to_remove_pre_t0s:
            for system_code in system_codes_to_remove_pre_t0s:

                self.inputs[system_code]["v_pseudo_pre_t0"] = None
                self.inputs[system_code]["r_value_pre_t0"] = None
                self.outlier_pre_t0_system_codes.append(system_code)

        self.set_ref_system()
        self.check_inputs()
        self.setup_solver()

    def to_dict(self):
        return self.__dict__

    def call_solver(self):
        # Call the trajectory solver with different initial guesses

        initial_guesses = generate_initial_guesses(self.velocity_model)

        lower_solution_bounds = set_lower_solution_bounds(self.velocity_model)
        upper_solution_bounds = set_upper_solution_bounds(self.velocity_model)
        self.solution_bounds = Bounds(lower_solution_bounds, upper_solution_bounds)

        lower_ineq_constraint_bounds = set_lower_ineq_constraint_bounds(self.inputs)
        upper_ineq_constraint_bounds = set_upper_ineq_constraint_bounds(self.inputs)
        solver_ineq_constraints = NonlinearConstraint(
            lambda x: ineq_constraints(x, self.rx_coordinates),
            lower_ineq_constraint_bounds,
            upper_ineq_constraint_bounds,
        )
        self.solver_constraints = solver_ineq_constraints

        solutions = np.zeros(initial_guesses.shape)
        objective_values = 1e9 * np.ones(initial_guesses.shape[0])
        condition_numbers = np.zeros(initial_guesses.shape[0])
        hessians = [None] * initial_guesses.shape[0]

        hessian_fun = jacobian(grad(self.objective_fun))

        for index, initial_guess in enumerate(initial_guesses):

            try:
                print("")
                print("Guess number = ", index)
                print("X [km] = ", round(initial_guess[0], 2))
                print("Y [km] = ", round(initial_guess[1], 2))
                print("Z [km] = ", round(initial_guess[2], 2))
                print("Vx [km/s] = ", round(initial_guess[3], 2))
                print("Vy [km/s] = ", round(initial_guess[4], 2))
                print("Vz [km/s] = ", round(initial_guess[5], 2))

                result = minimize(
                    self.objective_fun,
                    initial_guess,
                    method=Config.get(__name__, "optimization_method"),
                    bounds=self.solution_bounds,
                    constraints=self.solver_constraints,
                    tol=Config.get(__name__, "solver_tolerance"),
                )
                solutions[index, :] = result.x
                objective_values[index] = result.fun
                hessians[index] = hessian_fun(result.x)

                print("")
                print(
                    "Solution (FVal [1E-3] = ",
                    round(1000 * objective_values[index], 4),
                    ") : ",
                )
                print("X [km] = ", round(solutions[index, 0], 2))
                print("Y [km] = ", round(solutions[index, 1], 2))
                print("Z [km] = ", round(solutions[index, 2], 2))
                print("Vx [km/s] = ", round(solutions[index, 3], 2))
                print("Vy [km/s] = ", round(solutions[index, 4], 2))
                print("Vz [km/s] = ", round(solutions[index, 5], 2))

                if self.velocity_model == "linear":

                    print("delta_t0 [s] = ", solutions[index, 6])
                    print("a [km/s²] =", solutions[index, 7])

                print("")
                print("-----------")

            except:
                print("error")

        index_solution = np.argmin(objective_values)

        self.condition_number = condition_numbers[index_solution]
        self.solution = solutions[index_solution, :]
        self.objective_value = objective_values[index_solution]
        self.hessian = hessians[index_solution]

    def posterior_fun(self, x):

        return -self.objective_fun(x) / 2

    def objective_fun(self, x):
        # Function to minimize by the nonlinear optimizer

        if self.weight_pre_t0_objective == 0:

            objective_fun = self.time_fun(x)

        else:

            objective_fun = (1 - self.weight_pre_t0_objective) * self.time_fun(
                x
            ) + self.weight_pre_t0_objective * self.pre_t0_fun(x)

        return objective_fun

    def time_fun(self, x):

        time_residual = self.time_residual(x)

        return np.sum(time_residual**2)

    def pre_t0_fun(self, x):

        pre_t0_residual = self.pre_t0_residual(x)

        return np.sum(pre_t0_residual**2)

    def time_residual(self, x):
        # Time delays contribution to the objective

        iteration_time_delays = compute_time_delays(
            x,
            TX_COORD,
            self.rx_coordinates,
            self.ref_rx_coordinates,
            self.velocity_model,
        )

        time_residual = (self.time_delays - iteration_time_delays) / (
            self.sigma_time_delays
        )

        return time_residual

    def pre_t0_residual(self, x):
        # Pre-t0 speeds contribution to the objective

        start_coordinates = np.array([x[0], x[1], x[2]])
        end_coordinates = np.array([x[0] + x[3], x[1] + x[4], x[2] + x[5]])

        K = compute_fresnel_geometry(
            start_coordinates, end_coordinates, TX_COORD, self.rx_coordinates_pre_t0s
        )
        pre_t0_speeds = K * np.sqrt(WAVELENGTH / 2) * self.v_pseudo_pre_t0s

        if self.velocity_model == "constant":

            iteration_speed = np.sqrt(x[3] ** 2 + x[4] ** 2 + x[5] ** 2)
            iteration_speeds = iteration_speed * np.ones(len(self.v_pseudo_pre_t0s))

        elif self.velocity_model == "linear":

            fresnel_time_delays = compute_time_delays(
                x,
                TX_COORD,
                self.rx_coordinates_pre_t0s,
                self.ref_rx_coordinates,
                self.velocity_model,
            )
            iteration_speeds = compute_linear_velocity_profile(x, fresnel_time_delays)

        pre_t0_residual = (pre_t0_speeds - iteration_speeds) / (
            K * np.sqrt(WAVELENGTH / 2) * self.sigma_pre_t0s
        )

        return pre_t0_residual

    def is_within_bounds(self, x):

        return np.all(x >= self.solution_bounds.lb) and np.all(
            x <= self.solution_bounds.ub
        )

    def respects_constraints(self, x):

        constraint_value = self.solver_constraints.fun(x)

        # Check if the value is within the bounds
        return np.all(constraint_value >= self.solver_constraints.lb) and np.all(
            constraint_value <= self.solver_constraints.ub
        )

    def is_valid_fun(self, x):

        return self.is_within_bounds(x) and self.respects_constraints(x)

    def output_solution(self):

        self.number_inputs_tof = len(self.time_residual(self.solution))
        self.number_inputs_pre_t0 = len(self.pre_t0_residual(self.solution))
        self.number_inputs = self.number_inputs_tof

        if self.weight_pre_t0_objective != 0:
            self.number_inputs += self.number_inputs_pre_t0

        number_outputs = len(self.solution)
        self.number_dof = self.number_inputs - number_outputs
        residual_norm = self.objective_fun(self.solution)

        self.s_2 = residual_norm / (self.number_dof)

        print(" ")
        print("Final solution: ")
        print("X [km] = ", self.solution[0])
        print("Y [km] = ", self.solution[1])
        print("Z [km] = ", self.solution[2])
        print("Vx [km/s] = ", self.solution[3])
        print("Vy [km/s] = ", self.solution[4])
        print("Vz [km/s] = ", self.solution[5])
        print("Final time objective ", self.time_fun(self.solution))
        print("Final pre-t0 objective ", self.pre_t0_fun(self.solution))

        print("")
        print("Number of DOF = ", self.number_dof)

        self.compute_covariance_matrix(self.hessian)

    def compute_covariance_matrix(self, hessian):

        hessian_det = np.linalg.det(hessian)
        hessian_eig = np.linalg.eig(hessian)[0]
        self.hessian_cond = np.linalg.cond(hessian)

        print("Hessian determinant = ", hessian_det)
        print("Hessian eigenvalues = ", hessian_eig)
        print("Condition number = ", self.hessian_cond)

        self.cov = 2 * np.linalg.inv(hessian)
        v = np.sqrt(np.diag(self.cov))
        correlation_matrix = self.cov / np.outer(v, v)

        print("Standard deviation output = ", v)
        print("Correlation matrix = ")
        print(correlation_matrix)

        print("")
        print("Confidence interval")

        for i in range(len(self.solution)):
            print("Parameter", i, " = ", self.solution[i], " +-", 1.96 * v[i])

    def update_cov_hessian(self, x):

        hessian_fun = jacobian(grad(self.objective_fun))
        self.hessian = hessian_fun(x)
        self.cov = 2 * np.linalg.inv(self.hessian)
