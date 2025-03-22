import os
import argparse
from pybrams.brams import formats
from pybrams import processing


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate spectrograms for WAV files in given directory path."
    )
    parser.add_argument(
        "--path",
        type=os.path.abspath,
        default=os.path.abspath("."),
        help="directory path containing WAV files (default is current directory).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    path = args.path
    files = os.listdir(path)

    for file in files:
        if file.endswith(".wav"):
            wav_file_path = os.path.join(path, file)
            metadata, series, pps = formats.Wav.read(wav_file_path)
            s = processing.Signal()
            s.process()
            s.plot_spectrogram(export=True, title=file[:-4], filename=file[:-3] + "png")
