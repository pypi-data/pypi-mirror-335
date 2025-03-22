from pybrams.brams import formats
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Displays information about BRAMS WAV file passed as an argument."
    )
    parser.add_argument("filepath", type=str, help="file path to the BRAMS WAVfile.")
    parser.add_argument(
        "--header",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="toggle header",
    )
    parser.add_argument(
        "--pps", action=argparse.BooleanOptionalAction, default=False, help="toggle PPS"
    )
    parser.add_argument(
        "--data",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="toggle data",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    filepath = args.filepath

    if filepath.endswith(".wav"):
        metadata, series, pps = formats.Wav.read(filepath)
        if args.header:
            print(metadata)
        if args.pps:
            print(pps)
        if args.data:
            print(series)
