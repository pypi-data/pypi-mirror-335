from skutils import FemtoDAQController
from skutils.helpers import HitPatternCoincidenceBuilder
import pytest

VIREO_IP = "Vireo-000012.tek"


@pytest.fixture
def vireo_fixture():
    return FemtoDAQController("Vireo-000012.tek")


def test_recording_format_gettable(vireo_fixture: FemtoDAQController):
    vireo_fixture.getRecordingFormatInfo()


def test_streaming_format_gettable(vireo_fixture: FemtoDAQController):
    vireo_fixture.getStreamFormatInfo()


def test_configure_coincidence(vireo_fixture: FemtoDAQController):
    my_vireo = vireo_fixture
    # Coincidence hit pattern on all channels
    hit_pattern_coincidence = HitPatternCoincidenceBuilder(my_vireo.num_channels)
    hit_pattern_anticoincidence = HitPatternCoincidenceBuilder(my_vireo.num_channels)
    for channel in my_vireo.channels:
        hit_pattern_coincidence[channel] = "c"
        hit_pattern_anticoincidence[channel] = "a"
    my_vireo.configureCoincidence(
        "hit_pattern", hit_pattern=hit_pattern_coincidence.buildForSend()
    )
    returned_packet = my_vireo.getCoincidenceSettings()
    assert returned_packet["coincidence_mode"] == "hit_pattern"
    for channel in my_vireo.channels:
        assert (
            returned_packet[f"channel_{channel}_trigger_hit_pattern"]
            == hit_pattern_coincidence[channel]
        )

    my_vireo.configureCoincidence(
        "hit_pattern", hit_pattern=hit_pattern_anticoincidence.buildForSend()
    )

    returned_packet = my_vireo.getCoincidenceSettings()
    assert returned_packet["coincidence_mode"] == "hit_pattern"
    for channel in my_vireo.channels:
        assert (
            returned_packet[f"channel_{channel}_trigger_hit_pattern"]
            == hit_pattern_anticoincidence[channel]
        )

    my_vireo.configureCoincidence("multiplicity", 2)
    returned_packet = my_vireo.getCoincidenceSettings()
    assert returned_packet["trigger_multiplicity"] == 2

    my_vireo.configureCoincidence("multiplicity", 1)
    returned_packet = my_vireo.getCoincidenceSettings()
    assert returned_packet["trigger_multiplicity"] == 1

    with pytest.raises(ValueError):
        my_vireo.configureCoincidence("blargh")
    with pytest.raises(ValueError):
        my_vireo.configureCoincidence("hit_pattern")
    with pytest.raises(ValueError):
        my_vireo.configureCoincidence("multiplicity")


def test_configure_software_streaming(vireo_fixture: FemtoDAQController):
    vireo_fixture.configureSoftwareStreaming(
        vireo_fixture.channels, "greta", "192.168.1.1", 9000, True
    )
    data = vireo_fixture.getSoftwareStreamSettings()

    assert data["soft_stream_format"] == "greta"
    assert data["only_stream_triggered"]
    for channel in vireo_fixture.channels:
        assert channel in data["soft_stream_channels"]
    assert data["soft_stream_dest_port"] == 9000
    assert data["soft_stream_dest_ip"] == "192.168.1.1"
    vireo_fixture.configureSoftwareStreaming([], "gretina", "192.168.1.2", 9001, False)
    data = vireo_fixture.getSoftwareStreamSettings()

    assert data["soft_stream_format"] == "gretina"
    assert not data["only_stream_triggered"]
    assert len(data["soft_stream_channels"]) == 0
    assert data["soft_stream_dest_port"] == 9001
    assert data["soft_stream_dest_ip"] == "192.168.1.2"


def test_configure_software_recording(vireo_fixture: FemtoDAQController):
    vireo_fixture.configureRecording(vireo_fixture.channels)
    ret = vireo_fixture.getRecordingSettings()
    for chan in vireo_fixture.channels:
        assert chan in ret["channels_to_record"]
    assert ret["directory"] is None
    assert ret["format_type"] == "gretina"
    assert not ret["only_record_triggered"]
    assert not ret["record_summaries"]
    assert ret["record_waves"]
    assert ret["run_name"] == "API_Recording"
    assert ret["seq_file_size_MB"] == 100

    vireo_fixture.configureRecording(
        [],
        run_name="blargh",
        format_type="igorph",
        record_waves=False,
        record_summaries=True,
        directory="/mnt/stuff",
        seq_file_size_MB=200,
        only_record_triggered_channels=True,
    )
    ret = vireo_fixture.getRecordingSettings()
    assert len(ret["channels_to_record"]) == 0
    assert ret["directory"] == "/mnt/stuff"
    assert ret["format_type"] == "igorph"
    assert ret["record_summaries"]
    assert not ret["record_waves"]
    assert ret["run_name"] == "blargh"
    assert ret["seq_file_size_MB"] == 200
    assert ret["only_record_triggered"]

    with pytest.raises(RuntimeError):
        vireo_fixture.configureRecording(
            [],
            directory="/blargh/mnt/stuff",
        )
    with pytest.raises(RuntimeError):
        vireo_fixture.configureRecording([], format_type="igorph", record_waves=True)
    with pytest.raises(RuntimeError):
        vireo_fixture.configureRecording(
            [], format_type="eventcsv", record_summaries=True
        )


def test_not_supported(
    capsys: pytest.CaptureFixture[str], vireo_fixture: FemtoDAQController
):
    vireo_fixture.getBaselineRestorationExclusion()
    my_str = capsys.readouterr().out
    assert len(my_str) != 0


def test_versions(vireo_fixture: FemtoDAQController):
    vireo_fixture.getSoftwareVersion()
    vireo_fixture.getFirmwareVersion()
    vireo_fixture.getImageVersion()


def test_reserved(vireo_fixture: FemtoDAQController):
    vireo_fixture.setReservedInfo(False, "", "", "")
    assert not vireo_fixture.isReserved()
    vireo_fixture.setReservedInfo(True, "", "", "")
    assert vireo_fixture.isReserved()


if __name__ == "__main__":
    test_configure_coincidence(FemtoDAQController("Vireo-000012.tek"))
