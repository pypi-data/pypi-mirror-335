import numpy as np
import os
import glob
import re
from scipy.integrate import trapezoid, simpson, romb, quad
from scipy.signal import convolve, fftconvolve, resample, find_peaks
import matplotlib.pyplot as plt
import pickle
import time
from pybrams.utils import Config

MIN_SPEED_FT = Config.get(__name__, "min_speed_ft")  # [km/s]
MAX_SPEED_FT = Config.get(__name__, "max_speed_ft")  # [km/s]
MIN_RANGE_FT = Config.get(__name__, "min_range_ft")  # [km]
MAX_RANGE_FT = Config.get(__name__, "max_range_ft")  # [km]
N_GUESSES_FT = Config.get(__name__, "n_guesses_ft")  # [-]
FICTITIOUS_RANGE = Config.get(__name__, "fictitious_range")  # [km]
MIN_SAMPLES_FOR_DIFF = Config.get(__name__, "min_samples_for_diff")  # [-]


def optimize_ft(signal, wavelength, delta, R0=None, infl=None, plot=False):

    print("wavelength = ", np.round(wavelength, 5))
    print("delta = ", np.round(delta, 5))

    if R0 is not None:

        speeds = np.linspace(MIN_SPEED_FT, MAX_SPEED_FT, N_GUESSES_FT)

    else:

        ratios = np.linspace(
            MIN_SPEED_FT**2 / MAX_RANGE_FT, MAX_SPEED_FT**2 / MIN_RANGE_FT, N_GUESSES_FT
        )
        speeds = np.sqrt(ratios * FICTITIOUS_RANGE)
        R0 = FICTITIOUS_RANGE

    M = np.zeros(len(speeds), dtype=int)
    grad_max = np.zeros(len(speeds))
    fts = []

    # weighting_spectrum = WeightingSpectrum(wavelength, len(signal), delta, R0)

    for i in range(len(speeds)):

        y_vector_ft, ft = compute_ft(
            signal, wavelength, delta, speeds[i], R0, spectral=True, plot=plot
        )

        grad_max[i] = np.min(np.gradient(np.abs(ft) / np.max(np.abs(ft))))
        M[i] = min_samples_for_diff(np.abs(ft), min_n_samples=MIN_SAMPLES_FOR_DIFF)

        plt.figure()
        plt.plot(y_vector_ft, np.abs(ft) / np.max(np.abs(ft)))
        plt.ylabel("Trail reflectivity [-]")
        plt.xlabel("Distance [km]")
        plt.title(f"Ratio = {np.round(ratios[i], 2)}")
        plt.show()

        fts.append(ft)

    plt.figure()
    plt.plot(ratios, M)
    plt.grid(True)
    plt.ylabel("N samples")
    plt.xlabel("Ratio [km/s²]")
    plt.title(f"Min N samples for difference of 0.6")
    plt.show()

    plt.figure()
    plt.plot(ratios, grad_max)
    plt.grid(True)
    plt.ylabel("Grad max")
    plt.xlabel("Ratio [km/s²]")
    plt.title(f"Max gradient for difference of 0.6")
    plt.show()

    M0 = np.min(M)

    if M0 == 0:
        return

    D = np.zeros(len(fts))

    for i in range(len(fts)):

        D[i] = max_amplitude_difference(np.abs(fts[i]), M0)

    plt.figure()
    plt.plot(ratios, D)
    plt.grid(True)
    plt.ylabel("Amplitude difference")
    plt.xlabel("Ratio [km/s²]")
    plt.title(f"Max amplitude difference in {M0} samples")
    plt.show()

    diff_speed = np.diff(speeds)[0]
    peaks, properties = find_peaks(D)

    return ratios[np.argmax(D)]


def compute_ft(
    signal,
    wavelength,
    delta,
    speed,
    R0=None,
    infl=None,
    spectral=False,
    weighting_spectrum=None,
    min_y=-20,
    max_y=20,
    step_factor=1,
    plot=False,
):

    sigma = np.sqrt((wavelength * R0) / (4 * np.pi))
    signal_duration = len(signal) * delta

    t_alias = (
        2 * (np.pi * (sigma**2)) / ((speed**2) * delta)
    )  # Factor 2 compared to (Holdsworth, 2007)

    f_max = (signal_duration * speed**2) / (4 * np.pi * sigma**2)

    delta_max = 2 * (np.pi * (sigma**2)) / ((speed**2) * signal_duration)
    oversampling_factor = int(np.round(delta / delta_max + 0.5))

    S = speed * signal_duration / sigma

    print("OF = ", oversampling_factor)

    if spectral:

        if weighting_spectrum is not None:

            t_vector = np.linspace(
                -len(signal) * delta / 2, len(signal) * delta / 2, len(signal)
            )

            if weighting_spectrum.N != len(signal):

                weighting_spectrum = WeightingSpectrum(
                    wavelength, len(signal), delta, R0
                )

            phase_multiplier = S / weighting_spectrum.S

            magnitude = np.abs(weighting_spectrum.spectrum)
            phase = np.unwrap(np.angle(weighting_spectrum.spectrum))
            modified_phase = phase * phase_multiplier
            new_weighting_spectrum = magnitude * np.exp(1j * modified_phase)
            new_weighting_freq = np.fft.fftshift(
                np.fft.fftfreq(len(new_weighting_spectrum), d=delta)
            )

            new_freq_condition = (new_weighting_freq > -f_max) & (
                new_weighting_freq < f_max
            )

            new_weighting_spectrum[new_freq_condition] = (
                1
                / speed
                * np.exp(1j * np.angle(new_weighting_spectrum[new_freq_condition]))
            )
            new_weighting_spectrum[~new_freq_condition] = 0 * np.exp(
                1j * np.angle(new_weighting_spectrum[~new_freq_condition])
            )

            fft_signal = np.fft.fftshift(np.fft.fft(signal))

            fresnel_transform = np.fft.ifft(fft_signal * new_weighting_spectrum)
            fresnel_transform = fresnel_transform[::-1]
            fresnel_transform = np.roll(fresnel_transform, len(fresnel_transform) // 2)

            return speed * t_vector, fresnel_transform

        else:

            t_vector = np.linspace(
                -len(signal) * delta / 2, len(signal) * delta / 2, len(signal)
            )
            upsampled_t_vector = np.linspace(
                -len(signal) * delta / 2,
                len(signal) * delta / 2,
                oversampling_factor * len(signal),
            )

            upsampled_weighting = weighting_func(upsampled_t_vector, speed, sigma)
            upsampled_weighting_spectrum = np.fft.fftshift(
                np.fft.fft(upsampled_weighting, len(upsampled_weighting))
            )
            upsampled_weighting_freq = np.fft.fftshift(
                np.fft.fftfreq(len(upsampled_weighting), d=delta / oversampling_factor)
            )

            freq_condition = (upsampled_weighting_freq > -f_max) & (
                upsampled_weighting_freq < f_max
            )

            upsampled_weighting_spectrum[freq_condition] = (
                1
                / speed
                * np.exp(1j * np.angle(upsampled_weighting_spectrum[freq_condition]))
            )
            upsampled_weighting_spectrum[~freq_condition] = 0 * np.exp(
                1j * np.angle(upsampled_weighting_spectrum[~freq_condition])
            )

            N = len(upsampled_weighting_spectrum)

            start_index = int(N * (oversampling_factor - 1) / (2 * oversampling_factor))
            end_index = int(N * (oversampling_factor + 1) / (2 * oversampling_factor))
            middle_upsampled_weighting_spectrum = upsampled_weighting_spectrum[
                start_index:end_index
            ]

            fft_signal = np.fft.fftshift(np.fft.fft(signal))

            fresnel_transform = np.fft.ifft(
                fft_signal * middle_upsampled_weighting_spectrum
            )
            fresnel_transform = fresnel_transform[::-1]
            fresnel_transform = np.roll(fresnel_transform, len(fresnel_transform) // 2)

            return speed * t_vector, fresnel_transform

    else:

        if infl is not None:

            t_vector = np.linspace(
                -infl * delta, (len(signal) - infl) * delta, len(signal)
            )

        else:

            t_vector = np.linspace(
                -len(signal) * delta / 2, len(signal) * delta / 2, len(signal)
            )

        step_y = delta * speed / step_factor

        y_vector = np.arange(min_y, max_y, step_y)

        fresnel_transform = np.zeros(len(y_vector), dtype=complex)

        for i, y in enumerate(y_vector):

            weighting = np.exp(1j * 1 / 2 * ((speed * t_vector + y) / sigma) ** 2)

            integrand = (speed / sigma) * signal * weighting

            integrand_real = np.real(integrand)
            integrand_imag = np.imag(integrand)

            fresnel_transform[i] = simpson(integrand_real, t_vector) + 1j * simpson(
                integrand_imag, t_vector
            )

        return y_vector, fresnel_transform


def weighting_func(t, speed, sigma):

    return np.exp(1j / 2 * ((speed * t) / sigma) ** 2)


def max_amplitude_difference(time_series, M):

    time_series = np.array(time_series)

    # Check if M is valid
    if M > len(time_series):
        raise ValueError("M cannot be greater than the length of the time series")

    max_diff = 0  # Initialize the maximum difference

    # Loop through all possible windows of size M

    for i in range(len(time_series) - M + 1):
        window = time_series[i : i + M]
        max_idx = np.argmax(window)
        min_idx = np.argmin(window)

        # Ensure max comes before min (i.e., decreasing trend)
        if max_idx < min_idx:
            amplitude_diff = window[max_idx] - window[min_idx]
            if amplitude_diff > max_diff:
                max_diff = amplitude_diff

    return max_diff


def min_samples_for_diff(time_series, target_diff=0.6, min_n_samples=1):

    n = len(time_series)
    if n < 2:
        return 0  # not enough data points to form any subset with a difference

    # Calculate the amplitude of the entire time series
    overall_min = np.min(time_series)
    overall_max = np.max(time_series)
    overall_range = overall_max - overall_min

    if overall_range == 0:
        return 0  # No difference in the time series

    target_diff_value = target_diff * overall_range

    # Find the minimum number of samples such that the normalized amplitude difference is at least target_diff
    for subset_size in range(min_n_samples, n + 1):
        for start in range(n - subset_size + 1):
            subset = time_series[start : start + subset_size]
            max_idx = np.argmax(subset)
            min_idx = np.argmin(subset)

            # Ensure max occurs before min (decreasing trend)
            if max_idx < min_idx:
                subset_range = subset[max_idx] - subset[min_idx]
                if subset_range >= target_diff_value:
                    return subset_size

    return n  # If no valid subset is found, return the length of the time series


def interp_time_series(time_series, M):

    real_series = np.real(time_series)
    imag_series = np.imag(time_series)

    N = len(time_series)

    xp = np.linspace(0, N, N)
    x = np.linspace(0, N, N * M)

    real_interp_series = np.interp(x, xp, real_series)
    imag_interp_series = np.interp(x, xp, imag_series)

    return real_interp_series + 1j * imag_interp_series


WEIGHTING_SPECTRUM_PKL_NAME = "ft_weighting_spectrum.pkl"


class WeightingSpectrum:

    def __init__(self, wavelength, N, delta=1 / 6048, R0=200):

        self.generate(wavelength, N, delta, R0)
        self.dump_pickle()

    def generate(self, wavelength, N, delta, R0):

        signal_duration = delta * N
        sigma = np.sqrt((wavelength * R0) / (4 * np.pi))
        speed = np.sqrt(
            2 * (np.pi * (sigma**2)) / (signal_duration * delta)
        )  # Speed to ensure that N*delta = t_alias
        f_max = (signal_duration * speed**2) / (4 * np.pi * sigma**2)

        S = speed * signal_duration / sigma  # S

        t_vector = np.linspace(-N * delta / 2, N * delta / 2, N)
        weighting = weighting_func(t_vector, speed, sigma)
        weighting_spectrum = np.fft.fftshift(np.fft.fft(weighting, len(weighting)))
        weighting_freq = np.fft.fftshift(np.fft.fftfreq(len(weighting), d=delta))

        freq_condition = (weighting_freq > -f_max) & (weighting_freq < f_max)
        weighting_spectrum[freq_condition] = (
            1 / speed * np.exp(1j * np.angle(weighting_spectrum[freq_condition]))
        )
        weighting_spectrum[~freq_condition] = 0 * np.exp(
            1j * np.angle(weighting_spectrum[~freq_condition])
        )

        self.S = S
        self.N = N
        self.spectrum = weighting_spectrum

    def dump_pickle(self):

        pkl_path = os.path.join(".", WEIGHTING_SPECTRUM_PKL_NAME)

        with open(pkl_path, "wb") as f:

            pickle.dump(self, f)


def load_weighting_spectrum():

    pkl_path = os.path.join(".", WEIGHTING_SPECTRUM_PKL_NAME)

    with open(pkl_path, "rb") as f:

        weighting_spectrum = pickle.load(f)

    return weighting_spectrum
