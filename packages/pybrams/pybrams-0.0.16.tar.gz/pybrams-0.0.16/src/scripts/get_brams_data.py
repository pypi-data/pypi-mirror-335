import logging
import pybrams
import numpy as np

if __name__ == "__main__":
    pybrams.enable_logging(logging.INFO)
    systems = "NLMAAS_SYS001"
    interval_str = "2020-07-29T23:13:59.43/2020-07-29T23:14:04.43"
    interval = pybrams.utils.interval.Interval.from_string(interval_str)

    for system_code, files in pybrams.brams.file.get(
        interval, systems, load=True
    ).items():
        for file in files:
            file.clean()
            meteor = pybrams.event.Meteor()
            print(meteor.extract_infos(interval.start, interval.end, file, True))
