from typing import Dict, Any, Union, Optional
import copy
import numpy as np

from .constants import (
    BEACON_MIN_FREQUENCY,
    BEACON_MAX_FREQUENCY,
)
from .pps import PPS
from .series import Series
from pybrams.brams.system import System
from pybrams.utils import Config, Plot


class Signal:
    def __init__(
        self,
        series: Series,
        pps: PPS,
        samplerate: float,
        system: System,
        type: Union[str, None] = None,
        properties: Optional[dict[str, Any]] = {},
    ):
        self.series: Series = series
        self.pps: PPS = pps
        self.samplerate: float = samplerate
        self.system: System = system
        self.type: str = type if type else "RSP2" if self.samplerate == 6048 else str()
        self.beacon_frequency = (
            properties.get("beacon_frequency") if properties else None
        )
        self._cleaned_series: Optional[Series] = None
        self._corrected_pps: Optional[PPS] = None

    @property
    def cleaned_series(self):
        if self._cleaned_series is None:
            raise ValueError(
                "The signal needs to be cleaned before accessing the cleaned_series property"
            )
        return self._cleaned_series

    @property
    def corrected_pps(self):
        if self._corrected_pps is None:
            raise ValueError(
                "The PPS needs to be corrected before accessing the corrected_pps property"
            )
        return self._corrected_pps

    def process(self):
        self._corrected_pps = copy.deepcopy(self.pps)
        self.corrected_pps.correct(self.type)
        self.compute_beacon_frequency()

    def json(self) -> Dict[str, Any]:
        return {
            "samplerate": self.samplerate,
            "beacon_frequency": self.beacon_frequency,
        }

    def __add__(self, other: object) -> "Signal":
        if not isinstance(other, Signal):
            raise TypeError(
                f"Unsupported operand type(s) for +: Signal and {type(other).__name__}"
            )
        if self.system != other.system:
            raise ValueError(
                "Adding Signal objects from different systems is not supported"
            )
        if self.type != other.type:
            raise ValueError(
                "Adding Signal objects with different types is not supported"
            )

        series = self.series + other.series
        pps = PPS(
            np.concatenate(
                (
                    self.pps.index,
                    np.array([i + self.series.data.size for i in other.pps.index]),
                )
            ),
            np.concatenate((self.pps.time, other.pps.time)),
        )
        samplerate = np.mean([self.samplerate, other.samplerate])
        signal = Signal(series, pps, float(samplerate), self.system, self.type)

        if self._corrected_pps:
            signal._corrected_pps = PPS(
                np.concatenate(
                    (
                        self.corrected_pps.index,
                        np.array(
                            [
                                i + self.series.data.size
                                for i in other.corrected_pps.index
                            ]
                        ),
                    )
                ),
                np.concatenate((self.corrected_pps.time, other.corrected_pps.time)),
            )

        if self.beacon_frequency and other.beacon_frequency:
            signal.beacon_frequency = np.mean(
                (self.beacon_frequency, other.beacon_frequency)
            )

        signal._cleaned_series = (
            self.cleaned_series + other.cleaned_series
            if self._cleaned_series and other._cleaned_series
            else None
        )
        return signal

    def __eq__(self, other):
        if isinstance(other, Signal):
            return all(
                (self.series == other.series, self.samplerate == other.samplerate)
            )

        return False

    def compute_beacon_frequency(self):
        self.series.compute_fft(self.samplerate)
        indices_beacon_range = np.argwhere(
            (self.series.real_fft_freq >= BEACON_MIN_FREQUENCY)
            & (self.series.real_fft_freq <= BEACON_MAX_FREQUENCY)
        )

        reduced_real_fft = self.series.real_fft[indices_beacon_range]
        reduced_real_fft_freq = self.series.real_fft_freq[indices_beacon_range]
        beacon_index = np.argmax(abs(reduced_real_fft))
        self.beacon_frequency = reduced_real_fft_freq[beacon_index][0]

    def clean(self):
        from .airplane_removal import AirplaneRemoval
        from .beacon_removal import BeaconRemoval

        self._cleaned_series = copy.deepcopy(self.series)

        beacon_removal = BeaconRemoval(self)
        beacon_removal.remove_interference()

        if Config.get(__name__, "airplane_subtraction"):
            airplane_removal = AirplaneRemoval(self)
            airplane_removal.remove_interference()

    def plot_raw_spectrogram(
        self,
        title="Raw spectrogram",
        half_range_spect=100,
        export=False,
        filename=None,
        subplot=False,
        frame=True,
    ):
        Plot.spectrogram(
            self.series,
            self.samplerate,
            self.beacon_frequency,
            title,
            half_range_spect,
            export,
            filename,
            subplot,
            frame,
        )

    def plot_cleaned_spectrogram(
        self,
        title="Clean spectrogram",
        half_range_spect=100,
        export=False,
        filename=None,
        subplot=False,
        frame=True,
    ):
        Plot.spectrogram(
            self.cleaned_series,
            self.samplerate,
            self.beacon_frequency,
            title,
            half_range_spect,
            export,
            filename,
            subplot,
            frame,
        )
