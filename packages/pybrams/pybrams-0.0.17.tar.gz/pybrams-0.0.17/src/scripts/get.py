import os
import pybrams
import argparse

from pybrams.utils.interval import Interval

def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Download BRAMS WAV files in current directory",
        epilog=f"Example usage : python {os.path.basename(__file__)} 2023-01-01T00:00/2023-01-02T12:00 BEBILZ_SYS001 NLMAAS_SYS001 BEHUMA_SYS004"
    )
    parser.add_argument("interval", type=str, help="datetime interval in ISO 8601 format")
    parser.add_argument("systems", type=str, nargs="*", default=[], help="one or multiple BRAMS systems")
    parser.add_argument("-o", "--output-dir", type=os.path.abspath, default=os.path.abspath("."), help="output directory path")
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    interval_str = args.interval
    systems = args.systems if args.systems else None
    output_dir = args.output_dir

    interval = Interval.from_string(interval_str)
    files = pybrams.files.get(interval, systems)

    if files:

        for system, filelist in files.items():

            if isinstance(filelist, pybrams.files.File):

                filelist = [filelist]

            for file in filelist:

                file.process()
                file.save(output_dir)
                print(file.wav_name)

    else:

        print("No file retrieved")
