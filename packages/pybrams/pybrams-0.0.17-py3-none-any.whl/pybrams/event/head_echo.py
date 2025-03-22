import numpy as np
import matplotlib.pyplot as plt
from pybrams.utils import Config


def compute_doppler_shift(
    times, start_rise, end_rise, meteor_signal, meteor_frequency, plot
):

    NUMBER_PERIODS_AVERAGE = Config.get(__name__, "number_period_average")
    TIME_SPAN_DOPPLER = Config.get(__name__, "time_span_doppler")
    MIN_DOPPLER_SHIFT = Config.get(__name__, "min_doppler_shift")

    time_crossings = find_zero_crossings(times, meteor_signal)

    number_crossings = len(time_crossings)
    number_crossings_average = 2 * NUMBER_PERIODS_AVERAGE + 1
    number_doppler_average = number_crossings - number_crossings_average + 1

    time_crossings_average = np.zeros(number_doppler_average)
    doppler_shift_average = np.zeros(number_doppler_average)

    for i in range(number_doppler_average):
        time_crossings_average[i] = np.mean(
            time_crossings[i : i + number_crossings_average]
        )
        doppler_shift_average[i] = (number_crossings_average - 1) / (
            2 * (time_crossings[i + number_crossings_average - 1] - time_crossings[i])
        )

    doppler_shift = 1 / (2 * np.gradient(time_crossings))

    if plot:
        plt.figure()
        plt.plot(time_crossings, doppler_shift)
        plt.plot(time_crossings_average, doppler_shift_average)
        plt.xlabel("Time [s]")
        plt.ylabel("Freq [Hz]")
        plt.tight_layout()
        plt.show()

    time_start_rise = times[start_rise]
    time_end_rise = times[end_rise]

    index_start_rise_average = np.argmin(abs(time_crossings_average - time_start_rise))
    index_end_rise_average = np.argmin(abs(time_crossings_average - time_end_rise))

    index_start_doppler = index_start_rise_average + np.argmax(
        doppler_shift_average[index_start_rise_average : index_end_rise_average + 1]
    )
    time_start_doppler = time_crossings_average[index_start_doppler]
    index_end_doppler = np.argmin(
        abs(time_crossings_average - (time_start_doppler + TIME_SPAN_DOPPLER))
    )

    time_crossings_average_crop = time_crossings_average[
        index_start_doppler : index_end_doppler + 1
    ]
    doppler_shift_average_crop = doppler_shift_average[
        index_start_doppler : index_end_doppler + 1
    ]

    if plot:
        plt.figure()
        plt.plot(time_crossings_average_crop, doppler_shift_average_crop)
        plt.xlabel("Time [s]")
        plt.ylabel("Freq [Hz]")
        plt.tight_layout()
        plt.show()

    index_end_fit = np.where(
        doppler_shift_average_crop < meteor_frequency + MIN_DOPPLER_SHIFT
    )[0][0]
    index_start_fit = 1

    time_crossings_average_fit = time_crossings_average_crop[
        index_start_fit:index_end_fit
    ]
    doppler_shift_average_fit = doppler_shift_average_crop[
        index_start_fit:index_end_fit
    ]

    if plot:
        plt.figure()
        plt.plot(time_crossings_average_fit, doppler_shift_average_fit)
        plt.xlabel("Time [s]")
        plt.ylabel("Freq [Hz]")
        plt.tight_layout()
        plt.show()


def find_zero_crossings(times, signal):
    idx = np.where(signal[1:] * signal[:-1] < 0)[0]
    time_crossings = np.zeros(len(idx))

    for i, j in enumerate(idx):
        time_crossings[i] = np.interp(0.0, signal[j : j + 2], times[j : j + 2])

    return time_crossings
