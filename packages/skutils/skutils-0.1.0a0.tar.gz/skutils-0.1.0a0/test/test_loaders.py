import os

from skutils import (
    EventCSVLoader,
    IGORPulseHeightLoader,
    WrappedGretinaLoader,
    IGORWaveLoader,
    BaseLoader,
    GretaLoader,
)
import numpy as np
import pytest
from typing import Type

igor_pulseheight_file = (
    os.path.dirname(__file__)
    + "/test_data/vireo-16-timestamps_04.36.09PM_Jan29_2025_seq000001.itx"
)
igor_pulseheight_multichannel_file = (
    os.path.dirname(__file__)
    + "/test_data/GUI_recording_09.03.00AM_Feb12_2025_seq000001.itx"
)
igor_file = (
    os.path.dirname(__file__)
    + "/test_data/GUI_recording_09.41.39AM_Feb11_2025_seq000001.itx"
)
ecsv_file = (
    os.path.dirname(__file__)
    + "/test_data/GUI_recording_09.58.51AM_Feb10_2025_seq000001.ecsv"
)
gretina_file = (
    os.path.dirname(__file__)
    + "/test_data/GUI_recording_10.27.00AM_Feb10_2025_seq000001.geb"
)
igor_pulseheight_unittest = (
    os.path.dirname(__file__) + "/test_data/unit_test_data/igorph_test_seq000001.itx"
)
greta_file = (
    os.path.dirname(__file__)
    + "/test_data/GUI_recording_08.42.25AM_Feb27_2025_seq000001.geb"
)


class TestLoaders:
    def test_igorloader(self):
        loader = IGORPulseHeightLoader(igor_pulseheight_file)
        num_pulseheights = 1000
        num_heights = 0
        for _ in loader.channelByChannel():
            num_heights += 1

        assert num_heights == num_pulseheights
        loader2 = IGORPulseHeightLoader(igor_pulseheight_file)
        num_pulseheights = 1000
        i = 0
        for event in loader2.lazyLoad():
            assert len(event.channels) == 1
            i += 1
        assert i == num_pulseheights

    def test_igorloader2(self):
        loader = IGORPulseHeightLoader(igor_pulseheight_multichannel_file)
        num_pulseheights = 512 * 2
        i = 0
        for _ in loader.channelByChannel():
            i += 1
        assert i == num_pulseheights
        loader2 = IGORPulseHeightLoader(igor_pulseheight_multichannel_file)
        events = 0
        for event in loader2.lazyLoad():
            assert len(event.channels) == 2
            events += 1
        assert events == 512

    def test_ecsvloader(self):
        loader = EventCSVLoader(ecsv_file)
        events = 0
        for wave in loader.lazyLoad():
            assert len(wave.channel_data) == 2
            assert len(wave.channels) == 2
            assert len(wave.wavedata()) == 512
            events += 1
        assert events == 512

    def test_gretinaloader(self):
        loader = WrappedGretinaLoader(gretina_file, 0)
        events = 0
        for wave in loader.lazyLoad():
            assert len(wave.channel_data) == 2
            assert len(wave.wavedata()) == 512
            events += 1
        assert events == 512

    def test_igorwaveloader(self):
        # This test takes slightly long, because we're parsing 512 * 518 ~~ 265216 lines, which is a *LOT OF DATA* for reference even for small files.
        # On my machine it takes ~.5s, which is fairly modern with a (surprisingly RAIDed) 512GB ssd on a i7-8700, so not the most powerful machine, but no slouch either
        # Newer versions of python likely load this faster than the debian 12 on WSL python 3.11.2
        loader = IGORWaveLoader(igor_file)
        items = 0
        for wave in loader.channelByChannel():
            assert wave.num_wave_samples == 512
            items += 1
        # 512 events in each channel
        assert items == 1024
        loader2 = IGORWaveLoader(igor_file)
        events = 0
        for _ in loader2.lazyLoad():
            events += 1
        assert events == 512

    def test_unit_test_igorph(self):
        loader = IGORPulseHeightLoader(igor_pulseheight_unittest)
        i = 0
        wave_data = -(2**14)
        for item in loader.lazyLoad():
            assert i == item.timestamps[0]
            assert len(item.channels) == 1
            assert item.pulse_heights[0] == wave_data
            i += 1
            wave_data += 1

    def test_unit_test_greta(self):
        loader = GretaLoader(greta_file, 0)
        events = 0
        for event in loader.lazyLoad():
            assert event.has_summary
            assert len(event.channels) == 2
            for channel in event.channel_data:
                assert not channel.has_wave
                assert channel.has_summary
                assert channel.pulse_height is not None
                assert channel.trigger_height is not None
            events += 1
        assert events == 1000

    # Three tests, one common code base
    @pytest.mark.parametrize(
        "sequence_start,extension,loader_class,special_load",
        [
            ("igor_test_seq", ".itx", IGORWaveLoader, False),
            ("eventcsv_test_seq", ".ecsv", EventCSVLoader, False),
            ("gretina_test_seq", ".geb", WrappedGretinaLoader, False),
            ("igorph_test_seq", ".itx", IGORPulseHeightLoader, False),
            ("greta_test_seq", ".geb", GretaLoader, True),
        ],
    )
    def test_unit_test_files(
        self,
        sequence_start: str,
        extension: str,
        loader_class: Type[BaseLoader],
        special_load: bool,
    ):
        # The Gretina test is one of the slowest versions of the test that we deal with, there is no easy fix for the time without a major re-write sadly.
        # The current test for that is ~4.36s on my machine.
        file_list = os.listdir(os.path.dirname(__file__) + "/test_data/unit_test_data")
        igor_sequences = list(filter(lambda x: x.startswith(sequence_start), file_list))
        igor_sequences.sort(
            key=lambda x: int(x.removeprefix(sequence_start).removesuffix(extension))
        )
        values_to_write = list(range(-(2**14), 2**14 - 1))
        event_num = 0
        build_event_timestamps = None
        if special_load:
            build_event_timestamps = 0
        for file in igor_sequences:
            with loader_class(
                os.path.dirname(__file__) + f"/test_data/unit_test_data/{file}",
                build_event_timestamps,
            ) as loader:
                assert isinstance(loader, BaseLoader)
                for item in loader.lazyLoad():
                    desired_val = values_to_write[event_num % len(values_to_write)]
                    assert all(event_num == ts for ts in item.timestamps)

                    if item.has_waves:
                        wavedata = item.wavedata()
                        assert np.all(desired_val == wavedata)
                    # These checks take *excruciatingly* long on Vireo, i.e. one check == ~20s on Vireo across 20 files.
                    # So not implemented there, but *can* be implemented here
                    if item.has_summary:
                        assert all(desired_val == ph for ph in item.pulse_heights)
                        if not any(
                            trig_height is None for trig_height in item.trigger_heights
                        ):
                            assert all(
                                desired_val == trig_height
                                for trig_height in item.trigger_heights
                            )
                            assert (
                                (event_num % 256) * item.num_channels
                            ) == item.total_triggers
                        if all(cd.quadqdc_fast is not None for cd in item.channel_data):
                            assert all(
                                event_num == cd.quadqdc_fast for cd in item.channel_data
                            )
                            assert all(
                                event_num == cd.quadqdc_base for cd in item.channel_data
                            )
                            assert all(
                                event_num == cd.quadqdc_slow for cd in item.channel_data
                            )
                            assert all(
                                event_num == cd.quadqdc_tail for cd in item.channel_data
                            )

                    event_num += 1
            if "file_handle" in vars(loader):
                assert loader.file_handle.closed
        assert event_num == len(values_to_write)


if __name__ == "__main__":
    loader_tester = TestLoaders()
    loader_tester.test_unit_test_files(
        "eventcsv_test_seq", ".ecsv", EventCSVLoader, False
    )
