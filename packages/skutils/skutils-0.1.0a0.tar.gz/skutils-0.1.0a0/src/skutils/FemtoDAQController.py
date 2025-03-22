import requests
import urllib.request
import os
from typing import Literal, Union, Optional, Sequence, Any, Dict, List


class FemtoDAQController:
    """
    A controller for FemtoDAQ devices, such as the FemtoDAQ Kingfisher or FemtoDAQ Vireo.
    For full functionality, use the FemtoDAQController with a v6 DDC_APPs version for your FemtoDAQ device.
    """

    def __init__(self, url: str, verbose: bool = False):
        """Initialize the FemtoDAQController to use a specified URL as its target FemtoDAQ device
        
        :param url: The local URL of the FemtoDAQ device.
        :param verbose: whether you want the FemtoDAQController to print things at you.
        """
        assert isinstance(url, str), "url must be a string"
        if url.startswith("https://"):
            raise ValueError(
                "Secure http not supported! (digitizer url must begin with 'http' not 'https')"
            )
        # add http:// manually if not provided
        elif not url.startswith("http://"):
            url = f"http://{url}"

        if url[-1] == "/":
            url = url[:-1]
        self.url = url
        self.verbose = verbose
        self.fpga_data = self.__get_fpga_data()

    # _________________________________________________________________________
    def __get_fpga_data(self):
        route = self.url + "/rest/fpga_data"
        resp = requests.get(route, json={})
        if not resp.ok:
            print(f"unable to connect with FemtoDAQ device at {self.url}!")
            exit()
        return resp.json()["data"]

    # _________________________________________________________________________
    def __config_url(self, channel: Union[str, int], setting: str):
        # ensure the channel is an acceptable range
        if channel == "global":
            pass
        elif channel not in self.channels:
            raise ValueError(
                f"Invalid Channel. Must be 'global' or integer between 0-{self.fpga_data['num_channels'] - 1}"
            )

        route = self.url + f"/rest/config/{channel}/{setting}"
        return route

    # _________________________________________________________________________
    def __runtime_url(self, command: str):
        route = self.url + f"/rest/runtime/{command}"
        return route

    # _________________________________________________________________________
    def __gui_url(self, command: str):
        route = self.url + f"/web_API/{command}"
        return route

    # _________________________________________________________________________
    def __download_url(self, filename: str):
        route = self.url + f"/DOWNLOAD_FILES_FROM_DIGITIZER/{filename}"
        return route

    # _________________________________________________________________________
    def __get(self, route: str, data: Dict[str, Any] = {}) -> Dict[str, Any]:
        if self.verbose:
            print(f"sending GET to {route} with payload {data}")
        resp = requests.get(route, json=data)
        if not resp.ok:
            print(f"Request to {route} failed due to {resp.status_code}:{resp.reason}")

        resp_json = resp.json()
        status = resp_json.get("status", "").upper()

        if status == "SUCCESS":
            pass
        elif status == "ERROR":
            raise RuntimeError(
                f"Vireo connection returned an error with message {resp_json['message']}"
            )
        elif status == "NOT SUPPORTED":
            print(
                f"Feature of {route} not supported on the specific unit and has been ignored."
            )
        elif status == "WARNING":
            print(f"Vireo connection has sent back a warning! {resp_json['message']}")
        elif status == "CRITICAL":
            raise RuntimeError(
                f"Vireo connection has returned a CRITICAL ERROR: {resp_json['message']}"
            )
        elif status == "FAILURE":
            print(
                "Vireo connection indicated FAILURE, this is an old error code for non-updated REST endpoints, so is treated as a warning"
                + f", this may be insufficient: {resp_json['message']}"
            )
        return resp_json

    # _________________________________________________________________________
    def __post(self, route: str, data: Dict[Any, Any] = {}, print_failure: bool = True):
        if self.verbose:
            print(f"sending POST to {route} with payload {data}")
        resp = requests.post(route, json=data)
        if not resp.ok:
            print(f"Request to {route} failed due to {resp.status_code}:{resp.reason}")
            raise requests.ConnectionError(
                f"Request to {route} failed due to {resp.status_code}:{resp.reason}"
            )

        resp_json = resp.json()
        status = resp_json.get("status", "").upper()

        if status == "SUCCESS":
            pass
        elif status == "ERROR":
            raise RuntimeError(
                f"Vireo connection returned an error with message {resp_json['message']}"
            )
        elif status == "NOT SUPPORTED":
            print(
                f"Feature of {route} not supported on the specific unit and has been ignored."
            )
        elif status == "WARNING":
            print(f"Vireo connection has sent back a warning! {resp_json['message']}")
        elif status == "CRITICAL":
            raise RuntimeError(
                f"Vireo connection has returned a CRITICAL ERROR: {resp_json['message']}"
            )
        elif status == "FAILURE":
            print(
                "Vireo connection indicated FAILURE, this is an old error code for non-updated REST endpoints, so is treated as a warning"
                + f", this may be insufficient: {resp_json['message']}"
            )
        return resp_json

    # #########################################################################
    #                       Global Settings
    # #########################################################################

    # _________________________________________________________________________
    # TriggerXPosition
    def getTriggerXPosition(self):
        """
        Get the position of where the triggered item will be located across the N-sample window
        """
        route = self.__config_url("global", "TriggerXPosition")
        resp = self.__get(route)
        return resp["data"]

    def setTriggerXPosition(self, x_position: int):
        """
        Set the position of the trigger in the N-sample window.

        :param x_position: The position of the trigger in the N-sample window.
        """
        route = self.__config_url("global", "TriggerXPosition")
        data = {"x_position": x_position}
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerActiveWindow
    def getTriggerActiveWindow(self):
        """
        Get the duration of the time window when the instrument is counting triggers occuring on all enabled ADC channels
        """
        route = self.__config_url("global", "TriggerActiveWindow")
        resp = self.__get(route)
        return resp["data"]

    def setTriggerActiveWindow(self, window_width: int):
        """
        Set the duration of the time window when the instrument is counting triggers occuring on all enabled ADC channels.
        For example, when dealing with HPGe detectors, the Trigger Active Window should cover the
        duration of the energy shaping filters. Additional trigger pulses in an ADC channel with signal a
        signal pileup. These events should be excluded from the pulse height histogram.

        In waveform capture mode, the waveform will be truncated to the size of "Trigger Active Window".

        If your events are short and do not need to use the entire 8192 sample window, you can reduce
        your file size and increase your event throughput.

        :param window_width: number of samples to keep the trigger active.
        """
        route = self.__config_url("global", "TriggerActiveWindow")
        data = {"window_width": window_width}
        self.__post(route, data)

    # _________________________________________________________________________
    # PulseHeightWindow
    def getPulseHeightWindow(self):
        """
        Get the window to check the maximum value of pulses in from the trigger
        """
        route = self.__config_url("global", "PulseHeightWindow")
        resp = self.__get(route)
        return resp["data"]

    def setPulseHeightWindow(self, window_width: int):
        """
        Set the active window for measuring pulse heights compared to the trigger

        :param window_width: Number of ADC samples after the trigger to look for maximum pulse height values
        """
        route = self.__config_url("global", "PulseHeightWindow")
        data = {"window_width": window_width}
        self.__post(route, data)

    # _________________________________________________________________________
    # EnableBaselineRestoration
    def getEnableBaselineRestoration(self):
        """
        Get the status of enablement of the Baseline Restoration feature, Baseline Restoration is not supported on all products
        """
        route = self.__config_url("global", "EnableBaselineRestoration")
        resp = self.__get(route)
        return resp["data"]

    def setEnableBaselineRestoration(self, enable: bool):
        """
        Enable (or disable) Baseline Restoration on some products, Baseline Restoration is not supported on all products
        """
        route = self.__config_url("global", "EnableBaselineRestoration")
        data = {"enable": enable}
        self.__post(route, data)

    # _________________________________________________________________________
    # BaselineRestorationExclusion
    def getBaselineRestorationExclusion(self):
        """
        Get the area used in baseline restoration exclusion to excluse your triggered pulse.
        """
        route = self.__config_url("global", "BaselineRestorationExclusion")
        resp = self.__get(route)
        return resp["data"]

    def setBaselineRestorationExclusion(self, window_width: int):
        """
        Set the area used to exclude an area from being affected from baseline restoration

        :param window_width: area to prevent affection from restoration exclusion.
        """
        route = self.__config_url("global", "BaselineRestorationExclusion")
        data = {"window_width": window_width}
        self.__post(route, data)

    # _________________________________________________________________________
    # PulseHeightAveragingWindow
    def getPulseHeightAveragingWindow(self):
        """
        Get how many pulseheights are averaged together for performing a trigger
        """
        route = self.__config_url("global", "PulseHeightAveragingWindow")
        resp = self.__get(route)
        return resp["data"]

    def setPulseHeightAveragingWindow(self, window_width: int):
        """
        Set how many pulseheights are averaged together for performing a trigger

        :param window_width: integer width in ADC samples
        """
        route = self.__config_url("global", "PulseHeightAveragingWindow")
        data = {"window_width": window_width}
        self.__post(route, data)

    # _________________________________________________________________________
    # QuadQDCWindows
    def getQuadQDCWindows(self):
        """
        Get the quad QDC integration windows.
        """
        route = self.__config_url("global", "QuadQDCWindows")
        resp = self.__get(route)
        return (
            resp["data"]["base_width"],
            resp["data"]["fast_width"],
            resp["data"]["slow_width"],
            resp["data"]["tail_width"],
        )

    def setQuadQDCWindows(
        self, base_width: int, fast_width: int, slow_width: int, tail_width: int
    ):
        """
        Set the windows for FGPA-based integration of an event

        :param base_width: pre-trigger area to integrate in ADC count, this is not configurable, but it is 128 samples wide and ends 8 samples before the FAST window
        :param fast_width: Width of the fast window, starts at hte maximum value of the sliding window integration and will always cover the peak of the pulse.
        :param slow_width: starts at the end of the fast window, integer in ADC counts.
        :param tail_width: Starts at the end of the slow window, integer in ADC counts.

        """
        route = self.__config_url("global", "QuadQDCWindows")
        data = {
            "base_width": base_width,
            "fast_width": fast_width,
            "slow_width": slow_width,
            "tail_width": tail_width,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # BiasVoltage
    def getBiasVoltage(self):
        """
        Read back the voltage offset for a detector
        """
        route = self.__config_url("global", "BiasVoltage")
        resp = self.__get(route)
        return resp["data"]

    def setBiasVoltage(self, voltage: float):
        """
        Set the intended voltage offset for biasing a detector.

        :param voltage: An integer indicating the voltage in volts to offset the HV output bias.
        """
        route = self.__config_url("global", "BiasVoltage")
        data = {"voltage": voltage}
        self.__post(route, data)

    # _________________________________________________________________________
    # BiasVoltageRaw
    def getBiasVoltageRaw(self):
        """
        Get the raw DAC value used to bias a detector
        """
        route = self.__config_url("global", "BiasVoltageRaw")
        resp = self.__get(route)
        return resp["data"]

    def setBiasVoltageRaw(self, voltage: int):
        """
        Set the raw DAC value used to bias output for a detector.

        :param voltage: an integer indicating the voltage in raw DAC bytes
        """
        route = self.__config_url("global", "BiasVoltageRaw")
        data = {"dac_value": voltage}
        self.__post(route, data)

    # _________________________________________________________________________
    # GlobalID (aka module_number)
    # _________________________________________________________________________
    def getGlobalId(self):
        """
        Get the assigned global ID for an experiment to the device.
        """
        route = self.__config_url("global", "GlobalID")
        resp = self.__get(route)
        return resp["data"]

    def setGlobalId(self, global_id: int):
        """
        Set the  globalID for an experiment to the device.

        :param global_id: a 0-255 integer representing an ID in an experiment
        """
        assert isinstance(global_id, int), "global id must be an integer between 0-255"
        assert (global_id >= 0) and (global_id <= 255), (
            "global id must be an integer between 0-255"
        )
        route = self.__config_url("global", "GlobalID")
        data = {"global_id": global_id}
        self.__post(route, data)

    def getStreamFormatInfo(self):
        """returns the output of `utils.get_formats` from the target unit"""
        return self.__get(self.url + "/rest/data/SoftwareStreamingFormats")["data"]

    def getRecordingFormatInfo(self):
        """returns the output of `utils.get_streaming_formats` from the target unit"""
        return self.__get(self.url + "/rest/data/RecordingFormats")["data"]

    def getSoftwareVersion(self):
        """Returns the Vireo Software version"""
        return self.__get(self.url + "/rest/data/SoftwareVersion")["data"]

    def getFirmwareVersion(self):
        """Returns the Vireo Firmware version"""
        return self.__get(self.url + "/rest/data/FirmwareVersion")["data"]

    def getImageVersion(self):
        """Returns the image version of the Vireo"""
        return self.__get(self.url + "/rest/data/ImageVersion")["data"]

    def zeroChannelHistogram(self, channel: int):
        self.__post(self.url + f"/rest/config/{channel}/ZeroHistogramCounts")

    def configureCoincidence(
        self,
        mode: Literal["hit_pattern", "multiplicity"],
        # Note, this will probably require some more complicated typing
        multiplicity: Optional[int] = None,
        hit_pattern: Optional[Dict[str, str]] = None,
    ):
        """
        Configures coincidence prior to an experimental run.

        :param mode: the coincidence mode for triggering. Must be one of two options.
            - "multiplicity" : global trigger requires at least the 
            specified number of individual channels to trigger
            - "hit_pattern"  : global trigger requires specific channels to trigger or not trigger. 
            AKA coincidence/anti-coincidence/ignore hit pattern

        :param multiplicity: Required if mode = "multiplicity". The minimum number
            individual channel triggers required to define an Event.
            This arugment is ignored if mode is "hit_pattern"

        :param hit_pattern: Required if mode = "hit_pattern". This argument must be a dictionary. Keys are the channel number,
            and value is one of:

                * 'COINCIDENCE'     : If a trigger is required on this channel
                * 'ANTICOINCIDENCE' : If a trigger is not allowed on this channel
                * 'IGNORE'          : If triggers on this channel have no impact on Event

            All channels must be present when presented to configureCoincidence. A simple builder
            for configureCoincidence is helpers.HitPatternCoincidenceBuilder which will fill in unspecified items with "IGNORE" exists.
            This arugment is ignored if mode is "multiplicity"

        Hit Pattern Example
        -------------------

        .. code-block:: python
            :linenos:

            hit_pattern = {"channel_0_trigger_hit_pattern" : "COINCIDENCE", "channel_1_trigger_hit_pattern" : "ANTICOINCIDENCE"}
            digitizer.configureCoincidence("hit_pattern", hit_pattern=hit_pattern)


        Multiplicity Example
        --------------------

        .. code-block:: python
            :linenos:

            multiplicity = 3
            digitizer.configureCoincidence("multiplicity", multiplicity=multiplicity)

        """
        t: Dict[str, Any] = {
            "coincidence_mode": mode,
        }
        if mode not in ["multiplicity", "hit_pattern"]:
            raise ValueError("Invalid mode pattern!")
        if mode == "multiplicity":
            if multiplicity is None:
                raise ValueError(
                    "If mode is multiplicity, the multiplicity must be defined!"
                )
            t["trigger_multiplicity"] = multiplicity

        if mode == "hit_pattern":
            if hit_pattern is None:
                raise ValueError(
                    "If mode is hit_pattern, the hit pattern must be defined!"
                )

            for channel in self.channels:
                if f"channel_{channel}_trigger_hit_pattern" not in hit_pattern:
                    raise ValueError("A channel has been unspecified for behavior!")
            for item in hit_pattern:
                t[item] = hit_pattern[item]

        self.__post(self.__config_url("global", "Coincidence"), t, print_failure=False)

    def getCoincidenceSettings(self):
        """
        Obtain the current Coincidence settings.

        Look at the FemtoDAQ web docs for more information on that packet, this function returns the "data" field of that packet
        """
        return self.__get(self.__config_url("global", "Coincidence"))["data"]

    def configureRecording(
        self,
        channels: Sequence[int],
        run_name: str = "API_Recording",
        format_type: str = "gretina",
        record_waves: bool = True,
        record_summaries: bool = False,
        directory: Optional[str] = None,
        seq_file_size_MB: int = 100,
        only_record_triggered_channels: bool = False,
    ):
        """
        Configures file recording prior to an experimental run.

        :param channels: list of channels to record during this experimental run
        :param run_name: The name of this experimental run. This string will be
            pre-pended along with a date code to all to the names of all data files
            generated during this run
        :param format_type: The file format to use. Call `getRecordingFormatInfo`
            for a full list of data formats and the data products they support
        :param record_waves: True to save waveforms. This will raise an
            error if the specified file format doesn't support waveform recording.
            Default is True.
        :param record_summaries: True to save pulse summaries. This will
            raise an error if the specified file format doesn't support pulse
            summary recording. Default is False.
        :param directory: The remote directory on your FemtoDAQ unit to save data
            to. If left as None, then defaults to the data partition directory
            on the FemtoDAQ unit. SkuTek recommends keeping this as it's default
            unless you want the FemtoDAQ unit to save data over an NFS mount.
        :param seq_file_size_MB: Maximum size data file in MB before a new file
            is created. 100MB by default.
        :param only_record_triggered_channels: If True, then only record the channels
            in the `channels` list that triggered in the event. This is more efficient
            and reduces the liklihood of noise waveforms ending up in your data files.
            If left as False, the default, then all specified channels will be written
            to disk even if no trigger was detected. This is less efficient, but ensures
            that the same channels will be in each event.

            *warning* Setting this to True can result in varying event sizes and in
            some cases can result in empty cells in row/column type file formats
            such the IGOR Pulse Height format.


        :raise RuntimeError: if record_waves is True, but the specified file format
            does not support waveform recording.
        :raise RuntimeError: if record_summaries is True, but the specified file format
            does not support pulse summary recording.
        :raise RuntimeError: if directory is specified, but does not exist or is inaccessible
            from your FemtoDAQ digitizer.
        """
        t: Dict[str, Any] = {
            "channels_to_record": channels,
            "run_name": run_name,
            "format_type": format_type.lower(),
            "record_waves": record_waves,
            "record_summaries": record_summaries,
            "directory": directory,
            "seq_file_size_MB": seq_file_size_MB,
            "only_record_triggered": only_record_triggered_channels,
        }
        self.__post(self.__config_url("global", "RecordingSettings"), t)

    def getRecordingSettings(self):
        """
        Get the current recording settings, for more information, look at the FemtoDAQ WebAPI docs for what the exact return is.
        The function specifically returns the "data" portion of the packet.
        """
        return self.__get(self.__config_url("global", "RecordingSettings"))["data"]

    def configureSoftwareStreaming(
        self,
        channels: Sequence[int],
        format: str,
        target_ip: str,
        target_port: Union[int, str],
        only_stream_triggered_channels: bool = False,
    ):
        """
        Configures streaming readout from software prior to an experimental run.

        :param channels: list of channels to stream during this experimental run
        :param target_ip: The IP address to stream to.
        :param target_port: The network port at the specified IP address to stream to.
        :param only_stream_triggered_channels: If True, then only record the channels
            in the `channels` list that triggered in the event. This is more efficient
            and reduces the liklihood of noise waveforms ending up in your data files.
            If left as False, the default, then all specified channels will be written
            to disk even if no trigger was detected. This is less efficient, but ensures
            that the same channels will be in each event.

        """

        ENDPOINT = self.__config_url("global", "SoftwareStreamSettings")
        self.__post(
            ENDPOINT,
            {
                "soft_stream_channels": channels,
                "soft_stream_dest_ip": target_ip,
                "soft_stream_dest_port": target_port,
                "soft_stream_format": format,
                "only_stream_triggered": only_stream_triggered_channels,
            },
        )

    def getSoftwareStreamSettings(self):
        """
        Retrieve the stream settings currently made for the Vireo.
        :returns: Dict of a json packet
        The JSON packet should look like this:

        .. code-block::

            {
                "soft_stream_channels": channels,
                "soft_stream_dest_ip": target_ip,
                "soft_stream_dest_port": int | str,
                "only_stream_triggered": bool
            }

        """
        return self.__get(self.__config_url("global", "SoftwareStreamSettings"))["data"]

    def getRunStatistics(self) -> Dict[str, Any]:
        """returns a dictionary which contains at least the following keys

        'run_time' : duration of run
        'number_of_packets_streamed_from_software' : number of packets that have been streamed from
        from our software streaming system
        'number_of_events_recorded' : number of events saved to disk via the Recording System

        """
        raise NotImplementedError()

    # #########################################################################
    #                       Per-Channel Settings
    # #########################################################################

    # _________________________________________________________________________
    # AnalogOffsetPercent
    # def getAnalogOffsetPercent(self, channel):
    #     route = self.__config_url(channel, "AnalogOffsetPercent")
    #     resp = self.__get(route)
    #     return resp['data']

    def setAnalogOffsetPercent(self, channel: int, offset_percent: int):
        """
        Set the analog offset as a percentage for a given channel.
        This value is unable to be read back.

        :param channel: Channel to set the offset
        :param offset_percent: The percent offset for analog baseline offset ranging from -100 to 100 as an integer
        :raise ValueError: If the offset percentage is not in the valid range
        """
        if offset_percent not in range(-100, 100):
            raise ValueError("Offset percent not in valid range!")
        route = self.__config_url(channel, "AnalogOffsetPercent")
        data = {"offset_percent": offset_percent}
        self.__post(route, data)

    # _________________________________________________________________________
    # DigitalOffset
    def getDigitalOffset(self, channel: int):
        """
        Get the digital offset for a specified channel in ADC counts difference from the value to be displayed.
        This means that the offset is **not** inverted when you enable inverting waveforms.

        :param channel: channel to get the offset from
        """
        route = self.__config_url(channel, "DigitalOffset")
        resp = self.__get(route)
        return resp["data"]

    def setDigitalOffset(self, channel: int, offset: int):
        """
        Set the digital offset of a specified channel in ADC counts difference from the value to be displayed.
        This means that the offset is **not** inverted when you enable inverting waveforms.

        :param channel: channel to get the offset from
        :param offset: Offset in ADC counts
        """
        route = self.__config_url(channel, "DigitalOffset")
        data = {"offset": offset}
        self.__post(route, data)

    # _________________________________________________________________________
    # EnableTrigger
    def getEnableTrigger(self, channel: int):
        """
        Get whether a trigger is specified for a channel

        :param channel: Channel to get the trigger enabled status from.
        """
        route = self.__config_url(channel, "EnableTrigger")
        resp = self.__get(route)
        return resp["data"]

    def setEnableTrigger(self, channel: int, enable: bool):
        """
        Set the status of a trigger for a specified channel.

        :param channel: Channel to enable or disable the triggering on.
        :param enable: Enable or disable triggering on this channel
        """
        route = self.__config_url(channel, "EnableTrigger")
        data = {"enable": enable}
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerEdge
    def getTriggerEdge(self, channel: int):
        """
        Get what edge a trigger happens for a specified channel.
        :param channel: channel to get the trigger edge data from.
        """
        route = self.__config_url(channel, "TriggerEdge")
        resp = self.__get(route)
        return resp["data"]

    def setTriggerEdge(
        self,
        channel: int,
        direction: Union[Union[Literal["rising"], Literal["falling"]], int],
    ):
        """
        Set whether the trigger is to be on the rising or falling edge of a waveform.
        This applies *AFTER* inversion.

        :param channel: Channel to set the trigger edge detection on.
        :param direction: Direction of travel, rising or falling edge.
        """
        route = self.__config_url(channel, "TriggerEdge")
        data = {"direction": direction}
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerSensitivity
    def getTriggerSensitivity(self, channel: int):
        """
        Get the trigger threshold of the specified channel.

        :param channel: channel to obtain the trigger threshold of.
        """
        route = self.__config_url(channel, "TriggerSensitivity")
        resp = self.__get(route)
        return resp["data"]

    def setTriggerSensitivity(self, channel: int, sensitivity: int):
        """
        Set the trigger threshold of the specified channel

        :param channel: channel to set the trigger threshold of.
        :param sensitivity: Threshold of the trigger in ADC counts.
        """
        route = self.__config_url(channel, "TriggerSensitivity")
        data = {"sensitivity": sensitivity}
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerAveraging
    def getTriggerAveragingWindow(self, channel: int):
        """
        Get the duration of the leading and trailing summation windows in ADC samples.
        :param channel: channel to get the trigger averaging window of.
        """
        route = self.__config_url(channel, "TriggerAveragingWindow")
        resp = self.__get(route)
        return resp["data"]

    def setTriggerAveragingWindow(self, channel: int, window_width: int):
        """
        Set the trigger averaging window, the valid range is determined by the device, but a typical valid range would be:
        [1, 2, 4, 8, 16, 32] in terms of ADC samples to average for triggering.

        :param channel: channel to set the trigger averaging window
        :param window_width: width of the trigger averaging window
        """
        route = self.__config_url(channel, "TriggerAveragingWindow")
        data = {"window_width": window_width}
        self.__post(route, data)

    # _________________________________________________________________________
    # HistogramScaling
    def getHistogramScaling(self, channel: int):
        """
        Get the state of the histogram scaling for a specified channel
        :param channel: Channel to get the histogram scaling state from.
        """
        route = self.__config_url(channel, "HistogramScaling")
        resp = self.__get(route)
        return resp["data"]

    def setHistogramScaling(self, channel: int, state: int):
        """
        Set the histogram scaling for a specified channel, if state is 1, this bins by 2, otherwise for 0, do not bin.
        To cover the whole ADC range state must be one

        :param channel: Channel to set the histogram scaling state
        :param state: State to set the histogram scaling in, typically 1 for bin by 2 or 0 for no binning.
        """
        route = self.__config_url(channel, "HistogramScaling")
        data = {"scale_factor": state}
        self.__post(route, data)

    # _________________________________________________________________________
    # HistogramQuantity
    def getHistogramQuantity(self, channel: int):
        """
        Get the quantity histogrammed at each event, check setHistogramQuantity for the meanings of values

        :param channel: Channel to get the quantity histogrammed per event
        """
        route = self.__config_url(channel, "HistogramQuantity")
        resp = self.__get(route)
        return resp["data"]

    def setHistogramQuantity(self, channel: int, quantity: int):
        """
        Set the quantity histogrammed at each event.

        0 is the maximum value of a trace after averaging

        1 is the running sum over the PulseHeight window without averaging

        2 for running average of the PulseHeight window sum (AKA the average of mode 1)

        3 for the maximum value of the trigger waveform after averaging.

        :param channel: channel to set what quantity is being histogrammed
        :param quantity: What quantity do we want to histogram on this channel.
        """
        route = self.__config_url(channel, "HistogramQuantity")
        data = {"quantity": quantity}
        self.__post(route, data)

    # #########################################################################
    #        Runtime Functions not present in GUI
    # #########################################################################
    # ClearTimestamp
    def clearTimestamp(self):
        """
        Clear the device's FPGA timestamp
        """
        route = self.__runtime_url("ClearTimestamp")
        data = {"clear_timestamp": True}
        self.__post(route, data)

    # GetTimestamp
    def getTimestamp(self):
        """
        Get the device's FPGA timestamp
        """
        route = self.__runtime_url("GetTimestamp")
        self.__get(route)

    # #########################################################################
    #        Functions that call routes already present in GUI
    # #########################################################################
    # _________________________________________________________________________
    def Start(self) -> None:
        raise NotImplementedError("This feature is not yet supported")
        # # WARNING: NO SPY Support at this time

        # gui_setup_args = {}
        # gui_setup_args['trigger_mode'] = trigger_mode
        # gui_setup_args['trigger_multiplicity'] = trigger_multiplicity
        # gui_setup_args['channels'] = {}
        # for channel in range(self.num_channels):
        #     gui_setup_args['channels'][channel] = {}
        #     if channel in coincidence_channels:
        #         gui_setup_args['channels'][channel]['trigger_hit_pattern'] = "COINCIDENCE"
        #     elif channel in anticoincidence_channels:
        #         gui_setup_args['channels'][channel]['trigger_hit_pattern'] = "ANTICOINCIDENCE"
        #     else:
        #         gui_setup_args['channels'][channel]['trigger_hit_pattern'] = "IGNORE"

    # _________________________________________________________________________
    def Stop(self) -> None:
        raise NotImplementedError("This feature is not yet supported")

    # *************************************************************************
    # Recording Control
    # _________________________________________________________________________
    def getListOfDataFiles(self, last_run_only: bool = False) -> Sequence[str]:
        """
        Get the list of all remote data files.

        :param last_run_only: If true, only gets the data files recorded in the last run.
        """
        json_data = {"file_extension": "ALL"}
        route = self.__gui_url("GET_LIST_OF_FILES")
        resp = self.__post(route, json_data)
        files: List[str] = []
        for filedata in resp["data"]:
            if last_run_only:
                if filedata.get("collected_during_last_run", False):
                    files.append(filedata["filename"])
            else:
                files.append(filedata["filename"])
        return files

    # _________________________________________________________________________
    def downloadFile(
        self, filename: str, save_to: Optional[str] = None, silent: bool = False
    ):
        """
        Download a file from a given path, save to a location on disk, and optionally print out values

        :param filename: Remote file to download
        :param save_to: location to save that file to, or the local destionation
        :param silent: Don't print values out
        """
        # default to the current working directory
        save_to = os.getcwd() if (save_to is None) else save_to
        # make sure we have write permissions to the directory
        assert os.access(save_to, os.W_OK), (
            f"Unable to write files to directory '{save_to}'"
        )
        # Download the file
        download_url = self.__download_url(filename)
        try:
            dest_path = os.path.join(save_to, filename)
            urllib.request.urlretrieve(download_url, dest_path)
        except Exception:
            if not silent:
                print(
                    f"unable to download data file '{filename}' at url '{download_url}'"
                )
            raise

        if not silent:
            print(f"{str(self)} Controller : downloaded `{filename}` to '{dest_path}'")

    # _________________________________________________________________________
    def downloadLastRunDataFiles(self, save_to: Optional[str] = None):
        # iterate through all run files and download them one by one
        """
        Iterate through all data files from the last run and download them.

        :param save_to: an optional parameter specifying where to save the data.
        """
        for filename in self.getListOfDataFiles(True):
            self.downloadFile(filename, save_to)

    def isReserved(self) -> bool:
        """
        Determine if the FemtoDAQ is reserved
        """
        return self.__post(
            self.__gui_url("LOAD_JSON_FROM_FILE"),
            {"filepath": "/var/www/data/config/reserve_info.json"},
        )["data"]["reserved"]

    def getReservedInfo(self):
        """
        Get the reservation information of a FemtoDAQ device
        """
        return self.__post(
            self.__gui_url("LOAD_JSON_FROM_FILE"),
            {"filepath": "/var/www/data/config/reserve_info.json"},
        )["data"]

    def setReservedInfo(
        self,
        reserved_status: bool,
        reserver_name: str,
        reserve_contact: str,
        reserve_message: str,
    ):
        """
        Set the reservation status of a FemtoDAQ device.
        Note: This is not strictly enforced
        """
        self.__post(
            self.__gui_url("SAVE_JSON_TO_FILE"),
            {
                "data": {
                    "reserved": reserved_status,
                    "reserve_name": reserver_name,
                    "reserve_contact": reserve_contact,
                    "reserve_message": reserve_message,
                },
                "filepath": "/var/www/data/config/reserve_info.json",
            },
        )

    # def start_waveform_capture():
    #     route = self.__gui_url('START_WAVEFORM_CAPTURE')
    #     payload = {'data': {}}

    # def stop_waveform_capture():

    # def force_trigger():

    # def start_histogram_capture():

    # def stop_histogram_capture():

    # def zero_histograms():

    # #########################################################################
    #        General User Properties and Magic
    # #########################################################################

    # _________________________________________________________________________
    @property
    def num_channels(self):
        """The number of channels in the product"""
        return self.fpga_data["num_channels"]

    # _________________________________________________________________________
    @property
    def channels(self):
        """A list of all channels in the product"""
        return list(range(0, self.num_channels))

    # _________________________________________________________________________
    @property
    def num_wave_samples(self):
        """Number of samples in a max-size waveform"""
        return self.fpga_data["num_wave_samples"]

    # _________________________________________________________________________
    @property
    def wave_max_val(self):
        """Maximum value in the wave"""
        return self.fpga_data["constraints"]["wave_max_val"]

    # _________________________________________________________________________
    @property
    def wave_min_val(self):
        """Minimum value in the wave"""
        return self.fpga_data["constraints"]["wave_min_val"]

    # _________________________________________________________________________
    @property
    def adc_max_val(self):
        """Maximum ADC value of the product"""
        return self.fpga_data["constraints"]["adc_max_val"]

    # _________________________________________________________________________
    @property
    def adc_min_val(self):
        """Minimum ADC value of the product"""
        return self.fpga_data["constraints"]["adc_min_val"]

    # _________________________________________________________________________
    @property
    def trigger_sensitivity_max(self):
        """Maximum trigger sensitivity"""
        return self.adc_max_val

    # _________________________________________________________________________
    @property
    def trigger_sensitivity_min(self):
        """Minimum trigger sensitivity"""
        return self.adc_min_val

    # _________________________________________________________________________
    @property
    def product_name(self):
        """Get the short name of the FemtoDAQ product"""
        return self.fpga_data["product_short"]

    # _________________________________________________________________________
    @property
    def serial_number(self):
        """Get the serial name of the product"""
        return self.fpga_data["serial_num_str"]

    # _________________________________________________________________________
    @property
    def name(self):
        """Get the whole name of the product, being product-serial number"""
        return f"{self.product_name}-{self.serial_number}"

    # _________________________________________________________________________
    def __str__(self):
        return f"{self.name} ({self.url})"

    # _________________________________________________________________________
    def __repr__(self):
        return str(self)


# Image Version
# Software Version
# Firmware Version
