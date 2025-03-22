from scipy.signal import stft
import numpy as np
from .signal import Signal
from .constants import MAD_FACTOR, MAD_SCALE
from abc import ABC, abstractmethod
from pybrams.utils.config import Config


class InterferenceRemoval(ABC):
    def __init__(
        self, signal: Signal, duration_interval: float, overlaps_interval: float
    ):
        self.signal = signal
        self.duration_interval = duration_interval
        self.overlaps_interval = overlaps_interval
        self.initialize_removal_parameters()
        self.compute_noise_parameters()

    @abstractmethod
    def remove_interference(self):
        pass

    def initialize_removal_parameters(self):
        self.samples = len(self.signal.series.data)

        self.samples_per_interval = np.floor(
            self.duration_interval * self.signal.samplerate
        ).astype(int)

        if self.samples_per_interval % 2:  # Avoids problem with odd intervals
            self.samples_per_interval += 1

        self.overlaps_per_interval = np.floor(
            self.overlaps_interval * self.samples_per_interval
        ).astype(int)
        self.hop_size = self.samples_per_interval - self.overlaps_per_interval

        self.stft_frequency, self.stft_time, self.Zxx = stft(
            self.signal.cleaned_series.data,
            fs=self.signal.samplerate,
            nperseg=self.samples_per_interval,
            noverlap=self.overlaps_per_interval,
        )

        self.extended_data = np.pad(
            self.signal.series.data,
            pad_width=(self.samples_per_interval // 2, self.samples_per_interval // 2),
            mode="constant",
            constant_values=0,
        )
        self.extended_length = len(self.extended_data)

        nadd = (
            -(self.extended_data.shape[-1] - self.samples_per_interval) % self.hop_size
        ) % self.samples_per_interval
        zeros_shape = list(self.extended_data.shape[:-1]) + [nadd]
        self.padded_extended_data = np.concatenate(
            (self.extended_data, np.zeros(zeros_shape)), axis=-1
        )
        self.padded_extended_length = len(self.padded_extended_data)

        self.pad_width = self.padded_extended_length - self.extended_length

        self.time_vector = (
            1 / self.signal.samplerate * np.arange(self.padded_extended_length)
        )

        # Start and end indices of each STFT interval
        self.fit_intervals = self.Zxx.shape[1]
        self.start_fit_indices = self.hop_size * np.arange(self.fit_intervals)
        self.end_fit_indices = self.start_fit_indices + self.samples_per_interval - 1

        self.start_fit_time = self.time_vector[self.start_fit_indices]

        self.frequency_resolution = self.signal.samplerate / self.samples_per_interval
        self.apparent_time_resolution = self.duration_interval * (
            1 - self.overlaps_interval
        )

    def compute_noise_parameters(self):
        lower_noise_max_frequency = self.signal.beacon_frequency - Config.get(
            __name__, "noise_shift_frequency"
        )
        lower_noise_min_frequency = lower_noise_max_frequency - Config.get(
            __name__, "noise_range_frequency"
        )

        upper_noise_min_frequency = self.signal.beacon_frequency + Config.get(
            __name__, "noise_shift_frequency"
        )
        upper_noise_max_frequency = upper_noise_min_frequency + Config.get(
            __name__, "noise_range_frequency"
        )

        upper_noise_min_frequency_index = np.argmin(
            np.abs(self.stft_frequency - upper_noise_min_frequency)
        )
        upper_noise_max_frequency_index = np.argmin(
            np.abs(self.stft_frequency - upper_noise_max_frequency)
        )
        lower_noise_min_frequency_index = np.argmin(
            np.abs(self.stft_frequency - lower_noise_min_frequency)
        )
        lower_noise_max_frequency_index = np.argmin(
            np.abs(self.stft_frequency - lower_noise_max_frequency)
        )

        self.noise_powers = np.zeros(self.fit_intervals)
        self.noise_limits = np.zeros(self.fit_intervals)

        for j in range(self.fit_intervals):
            # Fft computation
            real_fft_interval = self.Zxx[:, j]
            magn_fft_interval = abs(real_fft_interval)
            magn_fft_interval[1:-1] = 2 * abs(magn_fft_interval[1:-1])

            # Noise computation
            lower_noise = magn_fft_interval[
                lower_noise_min_frequency_index : lower_noise_max_frequency_index + 1
            ]
            upper_noise = magn_fft_interval[
                upper_noise_min_frequency_index : upper_noise_max_frequency_index + 1
            ]
            noise = np.concatenate((lower_noise, upper_noise))

            self.noise_powers[j] = np.mean(noise**2)

            median_noise = np.median(noise)
            mad_noise = np.median(np.abs(noise - median_noise))
            noise_limit = median_noise + MAD_FACTOR * MAD_SCALE * mad_noise

            self.noise_limits[j] = noise_limit

    def hanning_window_function(self, freq_index, ampl, freq):
        return ampl * np.abs(
            np.sinc(freq - freq_index) / (1 - (freq - freq_index) ** 2)
        )
