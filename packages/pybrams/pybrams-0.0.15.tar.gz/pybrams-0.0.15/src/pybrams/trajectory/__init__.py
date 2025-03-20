import json

from pybrams.utils import Cache
from pybrams.brams.location import Location
from pybrams import brams
from pybrams.brams import system as system
from pybrams.event.meteor import Meteor
from pybrams.utils.interval import Interval


def extract_file_data(args, file):

    meteor = Meteor()
    meteor.extract_infos(args.interval.start, args.interval.end, file, args.plot)

    return {
        "location": file.location,
        "meteor": meteor,
    }


def extract_solver_data(args):

    args.interval = Interval.from_string(args.interval_str)

    start_json_string = args.interval.start.strftime("%Y%m%dT_%H%M%S")
    end_json_string = args.interval.end.strftime("%Y%m%dT_%H%M%S")

    key = f"Start_{start_json_string}_End_{end_json_string}"

    cached_data = Cache.get(key)
    files_data = {}

    print("args system = ", args.system)

    if not args.system:

        args.system = [
            system.system_code
            for system in system.all().values()
            if system.system_code.endswith("SYS001")
        ]

    if not cached_data or args.recompute_meteors:

        try:

            files = brams.file.get(args.interval, args.system, clean=True)

            for system_code, file_list in files.items():

                if len(file_list) == 1:

                    file_to_extract = file_list[0]

                elif len(file_list) == 2:

                    file_to_extract = file_list[0] + file_list[1]

                files_data[system_code] = extract_file_data(args, file_to_extract)

        except:

            pass

    else:

        cached_json = json.loads(cached_data)
        cached_system_code = cached_json.keys()

        for system_code in cached_system_code:

            if system_code in args.system:

                entry = cached_json[system_code]
                files_data[system_code] = {
                    "location": Location(*entry["location"].values()),
                    "meteor": Meteor(*entry["meteor"].values()),
                }

        other_system_code = list(set(args.system) - set(cached_system_code))

        if other_system_code:

            try:

                files = brams.file.get(args.interval, other_system_code, clean=True)

                for file_list in files.values():

                    if len(file_list) == 1:

                        file_to_extract = file_list[0]

                    elif len(file_list) == 2:

                        file_to_extract = file_list[0] + file_list[1]

                    files_data[other_system_code] = extract_file_data(
                        args, file_to_extract
                    )

            except:

                pass

    if args.save_json:

        json_data = {
            outer_key: {
                inner_key: inner_value.json()
                for inner_key, inner_value in inner_dict.items()
            }
            for outer_key, inner_dict in files_data.items()
        }

        Cache.cache(key, json.dumps(json_data, indent=4))

    sorted_data = {
        system_code: entry
        for system_code, entry in files_data.items()
        if system_code.endswith("SYS001")
    }

    return sorted_data
