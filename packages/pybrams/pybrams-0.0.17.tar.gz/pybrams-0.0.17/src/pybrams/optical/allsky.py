# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 18:05:36 2023

@author: joachimb
"""

import datetime
from pathlib import Path
import autograd.numpy as np
from pykml import parser

from pybrams.trajectory import extract_solver_data
from pybrams.trajectory.solver import Solver
from pybrams.utils.constants import TX_COORD
from pybrams.utils.geometry import (
    compute_specular_points_coordinates,
    compute_fresnel_geometry,
    compute_geometry_parameters,
    compute_angle,
)
from pybrams.utils.kinematic import (
    compute_exponential_velocity_profile,
    exponential_time_delay,
)
from pybrams.utils.coordinates import Coordinates


class AllSky:

    def __init__(self, args):

        self.args = args

    def load(self):

        date = datetime.datetime.strptime(self.args.date, "%Y-%m-%d")
        self.filename = (
            Path(__file__).resolve().parents[3]
            / "data"
            / f"AllSky_{date.strftime('%Y_%m_%d')}.kml"
        )

        with open(self.filename, "r", encoding="utf-8") as f:

            root = parser.parse(f).getroot()

            for place in root.Document.Folder.Placemark:

                if place.LineString.altitudeMode == "relativeToGround":

                    kml_list_coordinates = (
                        place.LineString.coordinates.text.strip().split(" ")
                    )

                    kml_start_coordinates = np.array(
                        [
                            float(coordinate)
                            for coordinate in kml_list_coordinates[0].split(",")
                        ]
                    )
                    kml_end_coordinates = np.array(
                        [
                            float(coordinate)
                            for coordinate in kml_list_coordinates[1].split(",")
                        ]
                    )

                    break

            print("kml start coord = ", kml_start_coordinates)
            print("kml end coord = ", kml_end_coordinates)

            trajectory_start = Coordinates.fromGeodetic(
                kml_start_coordinates[1],
                kml_start_coordinates[0],
                kml_start_coordinates[2] / 1000,
            )
            trajectory_end = Coordinates.fromGeodetic(
                kml_end_coordinates[1],
                kml_end_coordinates[0],
                kml_end_coordinates[2] / 1000,
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

            print("start coord = ", start_coordinates)
            print("end coord = ", end_coordinates)

    def process(self):
        pass
