# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 18:05:36 2023

@author: joachimb
"""

import datetime
import autograd.numpy as np
from scipy.optimize import fsolve
from pathlib import Path

from pybrams.trajectory import extract_solver_data
from pybrams.trajectory.solver import Solver
from pybrams.utils.constants import TX_COORD, WAVELENGTH
from pybrams.utils.data import Data
from pybrams.utils.geometry import (
    compute_specular_points_coordinates,
    compute_fresnel_geometry,
    compute_angle,
)
from pybrams.utils.kinematic import (
    compute_exponential_velocity_profile,
    exponential_time_delay,
)
from pybrams.utils.coordinates import Coordinates
from pybrams.utils.interval import Interval
import pybrams.brams.location

from .constants import (
    MINIMUM_HORIZONTAL_POSITION_OPTICAL,
    MAXIMUM_HORIZONTAL_POSITION_OPTICAL,
    MINIMUM_ALTITUDE_OPTICAL,
    MAXIMUM_ALTITUDE_OPTICAL,
    MINIMUM_NUMBER_SYSTEMS_OPTICAL,
)


class CAMS:
    def __init__(self, args):
        self.args = args

    def load(self):
        date = datetime.datetime.strptime(self.args.date, "%Y-%m-%d").strftime(
            "%Y_%m_%d"
        )

        input = Data.load(__name__, f"SummaryMeteorLog_{date}.txt", False).splitlines()

        header = [
            "number",
            "observed_date",
            "reference_time",
            "TBeg",
            "TEnd",
            "RAinf",
            "RAinf+-",
            "DECinf",
            "DECinf+-",
            "Vinf",
            "Vinf+-",
            "Acc1",
            "Acc1+-",
            "Acc2",
            "Acc2+-",
            "LatBeg",
            "LatBeg+-",
            "LonBeg",
            "LonBeg+-",
            "HBeg",
            "HBeg+-",
            "LatEnd",
            "LatEnd+-",
            "LonEnd",
            "LonEnd+-",
            "HEnd",
            "HEnd+-",
            "Conv",
            "S-Azim",
            "ZenAng",
            "Hmax",
            "Max-mV",
            "Int-mV",
            "F-skew",
            "Cameras",
        ]

        self.data = []

        for line in input[3:-1]:
            trajectory_data = line.split()
            self.data.append(dict((x, y) for x, y in zip(header, trajectory_data)))

    def filter(self):
        brams_location = pybrams.brams.location.all()
        rx_coordinates = np.zeros((len(brams_location), 3))

        for index, location in enumerate(brams_location):
            rx_coordinates[index, :] = [
                brams_location[location].coordinates.dourbocentric.x,
                brams_location[location].coordinates.dourbocentric.y,
                brams_location[location].coordinates.dourbocentric.z,
            ]

        for trajectory in self.data:
            start_coordinates = Coordinates.fromGeodetic(
                float(trajectory["LatBeg"]),
                float(trajectory["LonBeg"]),
                float(trajectory["HBeg"]),
            )
            end_coordinates = Coordinates.fromGeodetic(
                float(trajectory["LatEnd"]),
                float(trajectory["LonEnd"]),
                float(trajectory["HEnd"]),
            )

            start_coordinates = np.array(
                [
                    start_coordinates.dourbocentric.x,
                    start_coordinates.dourbocentric.y,
                    start_coordinates.dourbocentric.z,
                ]
            )
            end_coordinates = np.array(
                [
                    end_coordinates.dourbocentric.x,
                    end_coordinates.dourbocentric.y,
                    end_coordinates.dourbocentric.z,
                ]
            )

            specular_points_coordinates = compute_specular_points_coordinates(
                start_coordinates, end_coordinates, TX_COORD, rx_coordinates
            )

            specular_points_in_range = np.array(
                list(
                    filter(self.is_specular_point_in_range, specular_points_coordinates)
                )
            )

            if len(specular_points_in_range) >= MINIMUM_NUMBER_SYSTEMS_OPTICAL:
                print(
                    f"Number of specular points in range: {len(specular_points_in_range)}"
                )
                print("Number = ", trajectory["number"])
                print("start coord = ", start_coordinates)
                print("end coord = ", end_coordinates)
                print("vinf = ", trajectory["Vinf"])
                print("vinf+- = ", trajectory["Vinf+-"])
                print("Acc1= ", trajectory["Acc1"])
                print("Acc1+- = ", trajectory["Acc1+-"])
                print("Acc2= ", trajectory["Acc2"])
                print("Acc2+- = ", trajectory["Acc2+-"])
                print("")

            else:
                self.data.remove(trajectory)

    def is_specular_point_in_range(self, array):
        return (
            array[0] > MINIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[0] < MAXIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[1] > MINIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[1] < MAXIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[2] > MINIMUM_ALTITUDE_OPTICAL
            and array[2] < MAXIMUM_ALTITUDE_OPTICAL
        )

    def get_interval(self, number):
        for trajectory in self.data:
            trajectory_number = trajectory["number"].lstrip("0")

            if trajectory_number == number:
                day = trajectory["observed_date"]
                time = trajectory["reference_time"]
                observed_date = datetime.datetime.strptime(
                    day + " " + time, "%Y-%m-%d %H:%M:%S.%f"
                ).replace(tzinfo=datetime.timezone.utc)

                start = observed_date - datetime.timedelta(seconds=1)
                end = observed_date + datetime.timedelta(seconds=4)

                interval = Interval(start, end)

                return interval

    def get_speed_range(self, number, rx_location):
        for trajectory in self.data:
            trajectory_number = trajectory["number"].lstrip("0")

            if trajectory_number == number:
                start_coord = (
                    Coordinates.fromGeodetic(
                        float(trajectory["LatBeg"]),
                        float(trajectory["LonBeg"]),
                        float(trajectory["HBeg"]),
                    )
                ).get_dourbocentric_array()
                end_coord = (
                    Coordinates.fromGeodetic(
                        float(trajectory["LatEnd"]),
                        float(trajectory["LonEnd"]),
                        float(trajectory["HEnd"]),
                    )
                ).get_dourbocentric_array()

                velocity_unit = (end_coord - start_coord) / np.linalg.norm(
                    end_coord - start_coord
                )
                velocity = float(trajectory["Vinf"]) * velocity_unit
                speed = np.linalg.norm(velocity)

                rx_coord = (
                    Coordinates.fromGeodetic(
                        rx_location.latitude,
                        rx_location.longitude,
                        rx_location.altitude,
                    )
                ).get_dourbocentric_array()

                cams_K = compute_fresnel_geometry(
                    start_coord, end_coord, TX_COORD, rx_coord
                )

                equiv_range = 2 * cams_K**2

                return speed, equiv_range

    def solve(self):
        # TO REFACTOR
        for trajectory in self.data:
            if trajectory["number"].lstrip("0") == self.args.number:
                print(trajectory)

                day = trajectory["observed_date"]
                time = trajectory["reference_time"]

                print(
                    "CAMS trajectory number =", trajectory["number"], "- Time =", time
                )

                observed_date = datetime.datetime.strptime(
                    day + " " + time, "%Y-%m-%d %H:%M:%S.%f"
                )

                start = observed_date - datetime.timedelta(seconds=1)
                end = observed_date + datetime.timedelta(seconds=4)

                print("start = ", start)
                print("end = ", end)

                interval = Interval(start, end)
                self.args.interval_str = interval.to_string()

                trajectory_start = Coordinates.fromGeodetic(
                    float(trajectory["LatBeg"]),
                    float(trajectory["LonBeg"]),
                    float(trajectory["HBeg"]),
                )
                trajectory_end = Coordinates.fromGeodetic(
                    float(trajectory["LatEnd"]),
                    float(trajectory["LonEnd"]),
                    float(trajectory["HEnd"]),
                )

                start_coordinates = np.array(
                    [
                        trajectory_start.dourbocentric.x,
                        trajectory_start.dourbocentric.y,
                        trajectory_start.dourbocentric.z,
                    ]
                )
                end_coordinates = np.array(
                    [
                        trajectory_end.dourbocentric.x,
                        trajectory_end.dourbocentric.y,
                        trajectory_end.dourbocentric.z,
                    ]
                )

                time_CAMS_record = float(trajectory["TEnd"]) - float(trajectory["TBeg"])
                velocity = (end_coordinates - start_coordinates) / time_CAMS_record
                unit_velocity = velocity / np.linalg.norm(velocity)

                speed_inf = float(trajectory["Vinf"])

                a1 = float(trajectory["Acc1"])
                a2 = float(trajectory["Acc2"])

                speed_0 = speed_inf - a1 * a2
                velocity_0 = speed_0 * unit_velocity

                brams_data = extract_solver_data(self.args)

                self.args.outlier_removal = True
                self.args.weight_pre_t0_objective = 0.5

                ref_solver = Solver(brams_data, args=self.args)

                specular_points_coordinates = compute_specular_points_coordinates(
                    start_coordinates,
                    end_coordinates,
                    TX_COORD,
                    ref_solver.rx_coordinates,
                )
                ref_specular_point_coordinates = compute_specular_points_coordinates(
                    start_coordinates,
                    end_coordinates,
                    TX_COORD,
                    ref_solver.ref_rx_coordinates,
                )

                solution_CAMS = np.array(
                    [
                        ref_specular_point_coordinates[0],
                        ref_specular_point_coordinates[1],
                        ref_specular_point_coordinates[2],
                        velocity_0[0],
                        velocity_0[1],
                        velocity_0[2],
                    ]
                )

                print("")
                print("CAMS solution")
                print("X [km] = ", round(solution_CAMS[0], 2))
                print("Y [km] = ", round(solution_CAMS[1], 2))
                print("Z [km] = ", round(solution_CAMS[2], 2))
                print("Vx [km/s] = ", round(solution_CAMS[3], 2))
                print("Vy [km/s] = ", round(solution_CAMS[4], 2))
                print("Vz [km/s] = ", round(solution_CAMS[5], 2))

                cams_constant_times = np.zeros(ref_solver.rx_coordinates.shape[0])
                cams_exponential_times = np.zeros(ref_solver.rx_coordinates.shape[0])

                for i in range(ref_solver.rx_coordinates.shape[0]):
                    specular_point_distance_vector = (
                        specular_points_coordinates[i, :] - start_coordinates
                    )
                    specular_point_distance = np.linalg.norm(
                        specular_point_distance_vector
                    )

                    if np.dot(specular_point_distance_vector, velocity) < 0:
                        specular_point_distance = -specular_point_distance

                    cams_constant_times[i] = specular_point_distance / speed_0
                    cams_exponential_times[i] = fsolve(
                        exponential_time_delay,
                        0,
                        args=((speed_inf, a1, a2, specular_point_distance)),
                    )

                cams_speeds = np.zeros_like(cams_exponential_times)
                cams_speeds = compute_exponential_velocity_profile(
                    speed_inf, a1, a2, cams_exponential_times
                )
                cams_K = compute_fresnel_geometry(
                    start_coordinates,
                    end_coordinates,
                    TX_COORD,
                    ref_solver.rx_coordinates,
                )
                cams_equiv_range = 2 * cams_K**2
                cams_v_pseudo_pre_t0s = cams_speeds / (cams_K * np.sqrt(WAVELENGTH / 2))

                print("")
                print("cams speeds = ", cams_speeds)
                print("cams_ratios = ", cams_speeds**2 / cams_equiv_range)

                radio_v_pseudo_pre_t0s = np.array(
                    [
                        inner_dict["v_pseudo_pre_t0"]
                        for inner_dict in ref_solver.inputs.values()
                    ]
                )
                radio_v_pseudo_pre_t0s[radio_v_pseudo_pre_t0s == None] = np.nan

                time_delays = (
                    cams_constant_times
                    - cams_constant_times[ref_solver.ref_system_index]
                )
                ref_solver.time_delays = (
                    ref_solver.time_delays
                    - ref_solver.time_delays[ref_solver.ref_system_index]
                )

                max_cams_time_delay = (
                    float(trajectory["TEnd"])
                    - float(trajectory["TBeg"])
                    - cams_constant_times[ref_solver.ref_system_index]
                )

                diff_time_delays = ref_solver.time_delays - time_delays
                diff_v_pseudo_pre_t0s = (
                    100
                    * (radio_v_pseudo_pre_t0s - cams_v_pseudo_pre_t0s)
                    / np.abs(cams_v_pseudo_pre_t0s)
                )

                print("")
                print("Max CAMS time delay = ", 1e3 * max_cams_time_delay, " ms")
                for index, system_code in enumerate(ref_solver.inputs):
                    print(
                        system_code,
                        " - Opt time delay = ",
                        np.round(1e3 * time_delays[index], 2),
                        " ms - Radio time delay = ",
                        np.round(1e3 * ref_solver.time_delays[index], 2),
                        " ms - Diff = ",
                        np.round(1e3 * diff_time_delays[index], 2),
                        " ms",
                    )

                print("")

                for index, system_code in enumerate(ref_solver.inputs):
                    if not np.isnan(radio_v_pseudo_pre_t0s[index]):
                        print(
                            system_code,
                            " - Opt pre-t0 speed = ",
                            np.round(
                                np.sqrt(WAVELENGTH / 2)
                                * cams_K[index]
                                * cams_v_pseudo_pre_t0s[index],
                                2,
                            ),
                            " - Radio pre-t0 speed = ",
                            np.round(
                                np.sqrt(WAVELENGTH / 2)
                                * cams_K[index]
                                * radio_v_pseudo_pre_t0s[index],
                                2,
                            ),
                            " - Diff = ",
                            np.round(diff_v_pseudo_pre_t0s[index], 2),
                            " %",
                        )

                print(
                    "Difference mean [%] = ", np.nanmean(np.abs(diff_v_pseudo_pre_t0s))
                )
                print(
                    "Difference median [%] = ",
                    np.nanmedian(np.abs(diff_v_pseudo_pre_t0s)),
                )
                print(
                    "Difference standard deviation [%] = ",
                    np.nanstd(np.abs(diff_v_pseudo_pre_t0s)),
                )

                if len(self.args.weights_pre_t0_objective) > 1:
                    try:
                        ref_solver.solve()
                    except:
                        continue

                solvers = []

                for i, weight_pre_t0_objective in enumerate(
                    self.args.weights_pre_t0_objective
                ):
                    self.args.outlier_removal = False
                    self.args.weight_pre_t0_objective = weight_pre_t0_objective

                    solver = Solver(brams_data, args=self.args)
                    solver.remove_inputs(
                        ref_solver.outlier_system_codes,
                        ref_solver.outlier_pre_t0_system_codes,
                    )

                    print(
                        "solver call number",
                        i + 1,
                        "out of",
                        len(self.args.weights_pre_t0_objective),
                    )

                    try:
                        solver.solve()
                    except:
                        continue

                    solution = solver.solution
                    radio_start_coordinates = np.array(
                        [solution[0], solution[1], solution[2]]
                    )
                    radio_end_coordinates = np.array(
                        [
                            solution[0] + solution[3],
                            solution[1] + solution[4],
                            solution[2] + solution[5],
                        ]
                    )

                    radio_ref_specular_points_coordinates = (
                        compute_specular_points_coordinates(
                            radio_start_coordinates,
                            radio_end_coordinates,
                            TX_COORD,
                            solver.ref_rx_coordinates,
                        )
                    )

                    radio_velocity = np.array(
                        [solver.solution[3], solver.solution[4], solver.solution[5]]
                    )

                    solver.speed_error = np.abs(
                        speed_0 - np.linalg.norm(radio_velocity)
                    )
                    solver.inclination_error = compute_angle(velocity_0, radio_velocity)
                    solver.ref_altitude_specular_point_error = np.abs(
                        ref_specular_point_coordinates[2]
                        - radio_ref_specular_points_coordinates[2]
                    )

                    solver.solution_CAMS = solution_CAMS

                    solver.target_tof = solver.time_fun(solver.solution)
                    solver.target_pre_t0 = solver.pre_t0_fun(solver.solution)

                    solvers.append(solver)

                    print("")
                    print("Speed error [km/s] = ", solver.speed_error)
                    print("Inclination error [°] = ", solver.inclination_error)
                    print(
                        "Reference altitude specular point error [km] = ",
                        solver.ref_altitude_specular_point_error,
                    )

                print("")
                print("CAMS solution")
                print("X [km] = ", round(ref_specular_point_coordinates[0], 2))
                print("Y [km] = ", round(ref_specular_point_coordinates[1], 2))
                print("Z [km] = ", round(ref_specular_point_coordinates[2], 2))
                print("Vx [km/s] = ", round(velocity[0], 2))
                print("Vy [km/s] = ", round(velocity[1], 2))
                print("Vz [km/s] = ", round(velocity[2], 2))

                return solvers


def find_elbow(x, y):
    # Compute first and second derivatives
    dx = np.gradient(x)
    dy = np.gradient(y)
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)

    # Compute curvature
    curvature = np.abs(ddx * dy - ddy * dx) / (dx**2 + dy**2) ** (3 / 2)

    # Find index of max curvature (elbow)
    elbow_index = np.argmax(curvature)
    return elbow_index


def is_dominated(index, tof, pre_t0):
    """Check if solution at 'index' is dominated by any other solution"""
    for j in range(len(tof)):
        if (
            j != index
            and all([tof[j] <= tof[index], pre_t0[j] <= pre_t0[index]])
            and any([tof[j] < tof[index], pre_t0[j] < pre_t0[index]])
        ):
            return True
    return False


def get_pareto_indices(target_tof, target_pre_t0):
    """Return indices of Pareto front solutions"""
    pareto_indices = [
        i
        for i in range(len(target_tof))
        if not is_dominated(i, target_tof, target_pre_t0)
    ]
    return np.array(pareto_indices)
