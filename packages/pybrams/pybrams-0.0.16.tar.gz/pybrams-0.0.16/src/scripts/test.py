import logging
import pybrams

if __name__ == "__main__":
    pybrams.enable_logging(logging.INFO)
    pybrams.enable_cache()
    interval_str = "2025-02-21T00:55:30/2025-02-21T01:00:30"
    try:
        files = pybrams.brams.file.get(
            pybrams.utils.interval.Interval.from_string(interval_str),
            "BETRUI_SYS001",
            clean=True,
        )
    except Exception as e:
        print(e)

    print(files)
    f1 = files["BETRUI_SYS001"][0]
    f2 = files["BETRUI_SYS001"][1]

    synth_file = f1 + f2

    print(f1)
    print(f2)
    print()
    print(synth_file)
    for file in [f1, f2, synth_file]:
        print(f"Series length : {file.signal.series.data.size}")
        print(f"Cleaned series length : {file.signal.cleaned_series.data.size}")
        file.signal.plot_raw_spectrogram()
        file.signal.plot_cleaned_spectrogram()
