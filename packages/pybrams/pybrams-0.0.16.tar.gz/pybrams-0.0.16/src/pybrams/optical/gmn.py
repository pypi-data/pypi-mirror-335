import requests
import re
import datetime

import autograd.numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

import pybrams.brams.location
from pybrams.utils import http
from pybrams.trajectory import extract_solver_data
from pybrams.trajectory.solver import Solver
from pybrams.utils.constants import TX_COORD, WAVELENGTH
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

from .constants import (
    MINIMUM_HORIZONTAL_POSITION_OPTICAL,
    MAXIMUM_HORIZONTAL_POSITION_OPTICAL,
    MINIMUM_ALTITUDE_OPTICAL,
    MAXIMUM_ALTITUDE_OPTICAL,
    MINIMUM_NUMBER_SYSTEMS_OPTICAL,
)


class GMN:

    def __init__(self, args):

        self.args = args

    def load(self):

        url = "https://globalmeteornetwork.org/data/traj_summary_data/daily/"
        date = datetime.datetime.strptime(self.date, "%Y-%m-%d")

        response = requests.get(url)
        response_text = response.text

        match = re.search(
            rf"<a href=\"(traj_summary_{date.strftime('%Y%m%d')}_solrange_.*\.txt)\">.*</a>",
            response_text,
        )

        brams_location = pybrams.brams.location.all()
        rx_coordinates = np.zeros((len(brams_location), 3))

        for index, location in enumerate(brams_location):
            rx_coordinates[index, :] = [
                brams_location[location].coordinates.dourbocentric.x,
                brams_location[location].coordinates.dourbocentric.y,
                brams_location[location].coordinates.dourbocentric.z,
            ]

        if match:

            daily_url = url + match.group(1)

            response = http.get(daily_url)

            response_text = response.text.split("\n")
            headers = [header.strip("\r# ") for header in response_text[1].split(";")]
            units = [unit.strip("\r# ") for unit in response_text[2].split(";")]
            keys = [f"{key} ({unit})" for key, unit in zip(headers, units)]

            data = []

            for line in response_text[4:]:

                values = [value.strip("\r# ") for value in line.split(";")]

                if len(keys) == len(values):

                    entry = {key: value for key, value in zip(keys, values)}
                    data.append(entry)

            pattern = r"BE.{4},BE.{4}"

            belgian_trajectories = [
                item
                for item in data
                if re.match(pattern, item["Participating (stations)"])
            ]

            filtered_trajectories = []

            for trajectory in belgian_trajectories:

                start_coordinates = Coordinates.fromGeodetic(
                    float(trajectory["LatBeg (+N deg)"]),
                    float(trajectory["LonBeg (+E deg)"]),
                    float(trajectory["HtBeg (km)"]),
                )
                end_coordinates = Coordinates.fromGeodetic(
                    float(trajectory["LatEnd (+N deg)"]),
                    float(trajectory["LonEnd (+E deg)"]),
                    float(trajectory["HtEnd (km)"]),
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
                        filter(is_specular_point_in_range, specular_points_coordinates)
                    )
                )

                if specular_points_in_range.shape[0] > MINIMUM_NUMBER_SYSTEMS_OPTICAL:
                    filtered_trajectories.append(trajectory)

            print(len(filtered_trajectories), " exploitable trajectories")

            self.data = filtered_trajectories

    def process(self):

        for trajectory in self.data:
            pass

    def load_txt_report(self, args):

        trajectory_start = Coordinates.fromGeodetic(
            args.lat_beg, args.lon_beg, args.h_beg
        )
        trajectory_end = Coordinates.fromGeodetic(
            args.lat_end, args.lon_end, args.h_end
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

        velocity_unit = (end_coordinates - start_coordinates) / np.linalg.norm(
            end_coordinates - start_coordinates
        )
        velocity = float(args.v) * velocity_unit

        speed = np.linalg.norm(velocity)

        a1 = args.a1
        a2 = args.a2

        brams_data = extract_solver_data(args)

        solver = Solver(brams_data, self.args)

        specular_points_coordinates = compute_specular_points_coordinates(
            start_coordinates, end_coordinates, TX_COORD, solver.rx_coordinates
        )

        gmn_times = np.zeros(solver.rx_coordinates.shape[0])

        for i in range(solver.rx_coordinates.shape[0]):

            specular_point_distance_vector = (
                specular_points_coordinates[i, :] - start_coordinates
            )
            specular_point_distance = np.linalg.norm(specular_point_distance_vector)

            if np.dot(specular_point_distance_vector, velocity) < 0:
                specular_point_distance = -specular_point_distance

            gmn_times[i] = fsolve(
                exponential_time_delay,
                0,
                args=((speed, a1, a2, specular_point_distance)),
            )

        gmn_speeds = np.zeros_like(gmn_times)
        gmn_speeds = compute_exponential_velocity_profile(speed, a1, a2, gmn_times)
        gmn_K = compute_fresnel_geometry(
            start_coordinates, end_coordinates, TX_COORD, solver.rx_coordinates
        )
        gmn_equiv_range = 2 * gmn_K**2

        print("gmn speeds = ", gmn_speeds)
        print("gmn_ratios = ", gmn_speeds**2 / gmn_equiv_range)
        print("fresnel accel = ", solver.fresnel_accelerations)

        gmn_v_pseudo_pre_t0s = gmn_speeds / (gmn_K * np.sqrt(WAVELENGTH / 2))

        radio_v_pseudo_pre_t0s = np.array(
            [inner_dict["v_pseudo_pre_t0"] for inner_dict in solver.inputs.values()]
        )
        radio_v_pseudo_pre_t0s[radio_v_pseudo_pre_t0s == None] = np.nan

        corr_coeff = np.array(
            [inner_dict["corr_coeff"] for inner_dict in solver.inputs.values()]
        )
        corr_coeff[corr_coeff == None] = np.nan

        time_delays = gmn_times - gmn_times[solver.ref_system_index]

        diff_time_delays = solver.time_delays - time_delays
        diff_v_pseudo_pre_t0s = (
            100
            * (radio_v_pseudo_pre_t0s - gmn_v_pseudo_pre_t0s)
            / np.abs(gmn_v_pseudo_pre_t0s)
        )

        print("")
        for index, system_code in enumerate(solver.inputs):

            print(
                system_code,
                " - Opt time delay = ",
                np.round(1e3 * time_delays[index], 2),
                " ms - Radio time delay = ",
                np.round(1e3 * solver.time_delays[index], 2),
                " ms - Diff = ",
                np.round(1e3 * diff_time_delays[index], 2),
                " ms",
            )

        print("")

        system_code_fresnel = []

        for index, system_code in enumerate(solver.inputs):

            if not np.isnan(radio_v_pseudo_pre_t0s[index]):

                system_code_fresnel.append(system_code)

                print(
                    system_code,
                    " - Opt fresnel speed = ",
                    np.round(gmn_v_pseudo_pre_t0s[index], 2),
                    " - Radio fresnel speed = ",
                    np.round(radio_v_pseudo_pre_t0s[index], 2),
                    " - Diff = ",
                    np.round(diff_v_pseudo_pre_t0s[index], 2),
                    " % - Corr coeff = ",
                    np.round(corr_coeff[index], 3),
                )

        count = 0
        for x in radio_v_pseudo_pre_t0s:
            if x is not np.nan:
                count += 1

        print("")
        print("Number of pre-t0 stations = ", count)
        print("Difference pre-t0 speed [%] = ", diff_v_pseudo_pre_t0s)
        print("Difference mean [%] = ", np.nanmean(np.abs(diff_v_pseudo_pre_t0s)))
        print("Difference median [%] = ", np.nanmedian(np.abs(diff_v_pseudo_pre_t0s)))
        print(
            "Difference standard deviation [%] = ",
            np.nanstd(np.abs(diff_v_pseudo_pre_t0s)),
        )

        plt.figure(figsize=(10, 10))
        plt.title(f"Grazing event - {args.date}")
        plt.grid(True)
        plt.plot(1e3 * time_delays, gmn_speeds, label="GMN speed")
        plt.plot(
            1e3 * time_delays, radio_v_pseudo_pre_t0s * gmn_K, "*", label="Radio speeds"
        )
        plt.xlabel("Time delay [ms]")
        plt.ylabel("Speed [km/s]")

        for i in range(len(time_delays)):
            plt.text(
                1e3 * time_delays[i],
                radio_v_pseudo_pre_t0s[i] * gmn_K[i],
                f"{system_code_fresnel[i][:6]} - R² = {np.round(corr_coeff[i],3)}",
                fontsize=6,
                ha="right",
                va="bottom",
            )

        plt.legend()
        plt.show()

        solver.solve()
        solution = solver.solution
        radio_start_coordinates = np.array([solution[0], solution[1], solution[2]])
        radio_end_coordinates = np.array(
            [
                solution[0] + solution[3],
                solution[1] + solution[4],
                solution[2] + solution[5],
            ]
        )

        radio_ref_specular_points_coordinates = compute_specular_points_coordinates(
            radio_start_coordinates,
            radio_end_coordinates,
            TX_COORD,
            solver.ref_rx_coordinates,
        )

        radio_velocity = np.array(
            [solver.solution[3], solver.solution[4], solver.solution[5]]
        )

        speed_error = np.abs(speed - np.linalg.norm(radio_velocity))
        inclination_error = compute_angle(velocity, radio_velocity)
        ref_altitude_specular_point_error = np.abs(
            ref_specular_point_coordinates[2] - radio_ref_specular_points_coordinates[2]
        )

        print("")
        print("Speed error [km/s] = ", speed_error)
        print("Inclination error [°] = ", inclination_error)
        print(
            "Reference altitude specular point error [km] = ",
            ref_altitude_specular_point_error,
        )

        pass


def is_specular_point_in_range(array):

    return (
        array[0] > MINIMUM_HORIZONTAL_POSITION_OPTICAL
        and array[0] < MAXIMUM_HORIZONTAL_POSITION_OPTICAL
        and array[1] > MINIMUM_HORIZONTAL_POSITION_OPTICAL
        and array[1] < MAXIMUM_HORIZONTAL_POSITION_OPTICAL
        and array[2] > MINIMUM_ALTITUDE_OPTICAL
        and array[2] < MAXIMUM_ALTITUDE_OPTICAL
    )
