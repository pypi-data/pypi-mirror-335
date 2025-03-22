import ctypes
import json
from typing import (
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
    IO,
    Union,
)

# Python 3.8 minimum because of this
from functools import cached_property
import numpy as np
import warnings
from . import GretinaLoader  # type: ignore

# OurNumpyArrType = np.ndarray[tuple[int, ...], np.dtype[np.int16]]
OurNumpyArrType = np.ndarray


###############################################################################
class ChannelData:
    """
    All data related to a single channel, could be as part of an event or not as part of an event, and may or may not have a pulse summary or wave

    Check self.has_wave and self.has_summary to see if either are present.
    """

    def __init__(
        self,
        channel: int,
        timestamp: int,
        pulse_summary: Optional[Dict[str, Any]],
        wave: Optional[OurNumpyArrType],
    ):
        # General / Tracking Variables
        self.channel: int = channel
        self.timestamp: int = timestamp
        self.has_wave: bool = isinstance(wave, np.ndarray)
        self.has_summary: bool = isinstance(pulse_summary, dict)

        self.wave: Optional[OurNumpyArrType] = wave if self.has_wave else None
        # Yes I know this is a restatement of self.has_summary in this check, but it shuts up the analyzer and doesn't particularly matter here
        self.pulse_summary: Dict[str, Any] = (
            pulse_summary if isinstance(pulse_summary, dict) else {}
        )

        # Filter outputs
        self.pulse_height: Optional[int] = self.pulse_summary.get("pulse_height", None)
        self.trigger_height: Optional[int] = self.pulse_summary.get(
            "trigger_height", None
        )
        if self.trigger_height is None:
            self.trigger_height = self.pulse_summary.get("trig_height", None)
        self.quadqdc_base: Optional[int] = self.pulse_summary.get("quadqdc_base", None)
        self.quadqdc_fast: Optional[int] = self.pulse_summary.get("quadqdc_fast", None)
        self.quadqdc_slow: Optional[int] = self.pulse_summary.get("quadqdc_slow", None)
        self.quadqdc_tail: Optional[int] = self.pulse_summary.get("quadqdc_tail", None)
        if self.quadqdc_base is None:
            self.quadqdc_base = self.pulse_summary.get("qdc_base_sum", None)
        if self.quadqdc_fast is None:
            self.quadqdc_fast = self.pulse_summary.get("qdc_fast_sum", None)
        if self.quadqdc_slow is None:
            self.quadqdc_slow = self.pulse_summary.get("qdc_slow_sum", None)
        if self.quadqdc_tail is None:
            self.quadqdc_tail = self.pulse_summary.get("qdc_tail_sum", None)
        # Trigger variables
        self.triggered: Optional[bool] = self.pulse_summary.get("triggered", None)
        self.trigger_multiplicity: Optional[int] = self.pulse_summary.get(
            "trigger_count", None
        )
        if self.trigger_multiplicity is None:
            self.trigger_multiplicity = self.pulse_summary.get("trig_count", None)
        # Future:
        # self.qdc_rect     : int
        # self.qdc_tri      : int
        # self.mwd          : int

    # _________________________________________________________________________
    @cached_property
    def pileup(self) -> bool:
        """
        Returns true if there have been multiple triggers in this channel
        """
        if self.trigger_multiplicity:
            return True
        return False

    # _________________________________________________________________________
    @cached_property
    def num_wave_samples(self) -> int:
        """
        Returns the number of samples in the wave, 0 if this has no wave
        """
        if self.has_wave:
            if self.wave is not None:
                return self.wave.size
        return 0


###############################################################################
class EventInfo:
    """
    Information related to a group of channels collated as an "Event" as defined by either the file format or a rebuilt coincidence window.
    """

    def __init__(self, channel_data: Sequence[ChannelData]):
        """
        :channel_data: A list of more than one channel constituting an event
        """
        self.num_channels = len(channel_data)
        assert self.num_channels > 0, "At least one channel must be provided"
        # Ensure channel data is homogenous
        assert all(
            channel_data[0].has_wave == channel_data[i].has_wave
            for i in range(self.num_channels)
        )
        assert all(
            channel_data[0].has_summary == channel_data[i].has_summary
            for i in range(self.num_channels)
        )

        self.channel_data = sorted(channel_data, key=lambda cd: cd.channel)
        self.has_waves = self.channel_data[0].has_wave
        self.has_summary = self.channel_data[0].has_summary

    # _________________________________________________________________________
    def wavedata(self) -> OurNumpyArrType:
        """
        An np.ndarray of waves in the events
        """
        if self.has_waves:
            # stack multiple waves into a single array. Each channel is one column
            arrays: List[OurNumpyArrType] = [cd.wave for cd in self.channel_data]
            return np.stack(arrays=arrays, axis=1)

        raise RuntimeError("No Waveform waves found for this Event!")

    # _________________________________________________________________________
    # Channels
    # _________________________________________________________________________
    @property
    def channels(self) -> Sequence[int]:
        """
        List of all channels in the event
        """
        return list(set([cd.channel for cd in self.channel_data]))

    # _________________________________________________________________________
    # Timestamps
    # _________________________________________________________________________
    @property
    def timestamps(self) -> Sequence[int]:
        """
        All timestamps found throughout all of the channels we have
        """
        return [cd.timestamp for cd in self.channel_data]

    # .........................................................................
    @cached_property
    def min_timestamp(self) -> int:
        """
        The smallest timestamp found in the list of timestamps
        """
        return min(self.timestamps)

    # .........................................................................
    @cached_property
    def max_timestamp(self) -> int:
        """
        The largest timestamp found in the list of timestamps
        """
        return max(self.timestamps)

    # .........................................................................
    @property
    def timestamp_range(self) -> int:
        """
        Range of timestamps from the maximum and minimum
        """
        return self.max_timestamp - self.min_timestamp

    # _________________________________________________________________________
    # Pulse Heights
    # _________________________________________________________________________
    @property
    def pulse_heights(self) -> Union[Sequence[int], Sequence[None]]:
        """Returns the pulse heights on each channel."""
        return [cd.pulse_height for cd in self.channel_data]

    # _________________________________________________________________________
    # Trigger Data
    # _________________________________________________________________________
    @property
    def trigger_heights(self) -> Union[Sequence[int], Sequence[None]]:
        """Returns the trigger heights trigger on each channel."""
        return [cd.trigger_height for cd in self.channel_data]

    # .........................................................................
    @cached_property
    def channel_multiplicity(self) -> int:
        """Returns the number of channels that triggered at least once in this event"""
        return sum(cd.triggered for cd in self.channel_data)

    # .........................................................................
    @property
    def pileup_count(self) -> Union[Sequence[int], Sequence[None]]:
        """Returns a list of the number of triggers fired for each channel"""
        return [cd.trigger_multiplicity for cd in self.channel_data if cd.triggered]

    # .........................................................................
    @cached_property
    def total_triggers(self) -> int:
        """Returns the total number of triggers that fired across all channels.
        AKA Hit Multiplicity
        """
        return sum(self.pileup_count)

    # .........................................................................


###############################################################################
class BaseLoader:
    """
    The base class that all Loader types are an extension of, Loaders extending this subclass this class and then implement load_channel_batch

    All BaseLoader derived classes can be used as a context manager, i.e.:

    with <loader>(file) as loader:
        # Do whatever

    NOTE:
        An individual BaseLoader instance is able to run exactly *once* before needing to -reopen the file, please keep this in mind.
    """

    # _________________________________________________________________________
    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        """

        :fpath: filepath to the data file
        :rebuild_events_with_window: timestamp window where channel data is considered part of the same event. If None, then it will return events as they are defined in the file.

        FUTURE:
            Add a parameter `resort_by_timestamp` that resorts all data
            by the timestamp in the rare case that data isn't written to disk in
            sequence. This is a slow and memory intensive operation that is never required
            if your data is generated using the UI of a SkuTek digitizer. So it's not
            worth doing at this time

        """
        self.fpath = fpath
        self.rebuild_events_with_window = rebuild_events_with_window
        self.active_event_building = self.rebuild_events_with_window is not None
        self.values: Sequence[ChannelData] | None = []
        self.current_chan_in_values: int = 0
        self.channel_ran: bool = False
        self.file_handle: IO  # type: ignore

    def __enter__(self):
        return self

    def __exit__(self, type: Any, value: Any, traceback: Any):
        self.file_handle.close()  # type: ignore

    # _________________________________________________________________________
    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        """
        The base method for loading channels, this loads a sequence of channels (events) or individual channels.

        This is specialized for all loader types.
        """
        # Many file formats save channels in columns and samples in rows
        # which means it's nigh impossible to just load in one channel at a time
        # For file formats where this is possible this function will return a single
        # ChannelData. For file formats (like IGOR or EventCSV) where it's not,
        # then we'll return a list of ChannelData
        raise NotImplementedError("required overload")

    # _________________________________________________________________________
    def channelByChannel(self) -> Generator[ChannelData, Any, None]:
        """
        Get the individual channels, loaded one at a time
        """
        # This code is less complex than it looks, the first repeated while statement is basically just the previous one, but again
        while True:
            # Does a "Not none" check and also is just an entry-point to finish a list for an unfinished generator
            while (
                self.channel_ran
                and self.values is not None
                and self.current_chan_in_values < len(self.values)
            ):
                yield self.values[self.current_chan_in_values]
                self.current_chan_in_values += 1

            # Load in the batch to a class-based variable
            self.current_chan_in_values = 0
            self.values = self.loadChannelBatch()
            self.channel_ran = True
            if self.values is None:
                return

            # Yield as many channels as we can yield before we return
            while self.current_chan_in_values < len(self.values):
                yield self.values[self.current_chan_in_values]
                self.current_chan_in_values += 1

    # _________________________________________________________________________
    def nextEvent(self) -> Optional[EventInfo]:
        """
        Obtain the next event by loading the next batch.
        """
        # .....................................................................
        # if we are not actively event building then we just define
        # an event as it is defined in the file as a batch of channels
        # i.e. no timestamp coincidence window checking
        if not self.active_event_building:
            channel_batch = self.loadChannelBatch()
            if channel_batch is None:
                return None

            return EventInfo(channel_batch)

        # .....................................................................
        # Otherwise we go through the data channel by channel
        # and define an event by it's timestamp and coincidence window
        else:
            # grab the next channel data first to make sure we're not
            # at the end of the file
            channel_data_generator = self.channelByChannel()
            try:
                first_cd = next(channel_data_generator)
            except StopIteration:
                return None

            # There's probably a smart walrus operator way to do this
            channels_in_event: List[ChannelData] = []
            cd = first_cd
            if self.rebuild_events_with_window is None:
                self.rebuild_events_with_window = 0
            while True:
                # check to make sure the timestamp is in the event's coincidence window
                if cd.timestamp <= (
                    first_cd.timestamp + self.rebuild_events_with_window
                ):
                    channels_in_event.append(cd)
                else:
                    break
                try:
                    cd = next(channel_data_generator)
                except StopIteration:
                    break
            return EventInfo(channels_in_event)

    # _________________________________________________________________________
    def lazyLoad(self) -> Generator[EventInfo, Any, None]:
        """
        Lazily yield events, returns the next event in a generator fashion for iterating
        """
        # The while will be false if it's None, otherwise it's true
        while event_tuple := self.nextEvent():
            yield event_tuple

    # _________________________________________________________________________
    def __iter__(self) -> Generator[EventInfo, Any, None]:
        """
        Iterate over a lazy-loading of events
        """
        return self.lazyLoad()


class EventCSVLoader(BaseLoader):
    """
    Loader for the TSV-type format for the Vireo EventCSV Format
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[str] = open(fpath)
        super().__init__(fpath, rebuild_events_with_window)

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        # The way this works is we have a file made up of lines, if the line starts with a pound sign it's a comment
        # Technically, the file is a TSV, but I didn't know that at the time, thus, I may eventually swap this to use a "CSV" reader in TSV mode
        if self.file_handle.closed:
            return None
        line = self.file_handle.readline()
        if line == "":
            self.file_handle.close()
            return None
        line = line.strip()
        while line.startswith("#"):
            line = self.file_handle.readline()
        # Splitting the line here is fine, because what we're doing is going through a space-separated value here.
        separated = line.split()
        # Timestamp being first is fine....
        timestamp = int(separated[0])
        # Here's where it's no longer fine, we need to find the systems where the start and end are brackets, not spaces, as a temporary measure, we can
        try:
            channel_list: Sequence[int] = json.loads(separated[1])
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"It is likely that you somehow inserted a space into the bracket array, this will cause the file to not be parsed, the underlying error: {e}"
            )
        data_list: List[ChannelData] = []
        start = 2
        for channel in channel_list:
            array = None
            try:
                array = np.asarray(json.loads(separated[start]))
                data = ChannelData(
                    channel=channel,
                    timestamp=timestamp,
                    pulse_summary=None,
                    wave=array,
                )
                data_list.append(data)
                start += 1
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"It is likely that you somehow inserted a space into the bracket array, this will cause the file to not be parsed, the underlying error: {e}"
                )
        return data_list


class IGORPulseHeightLoader(BaseLoader):
    """
    IGOR pulse height loader, this type of loader does not actually have waveforms, but only the height and timestamp of a summary

    Only the pulse_height section of ChannelData and the timestamp will be filled
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[str] = open(fpath)
        # First line starts with IGOR
        self.file_handle.readline()
        super().__init__(fpath, rebuild_events_with_window)
        self.in_waves = False
        self.timestamp_col = 0
        self.column_to_channel_map: Dict[int, str] = {}

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        if self.in_waves:
            line = self.file_handle.readline()
            if line == "" or line.startswith("END"):
                return None
            channels_to_load: List[ChannelData] = []
            # Begin parsing!
            split_line = line.split()
            timestamp = int(split_line[self.timestamp_col])
            for column, channel_name in self.column_to_channel_map.items():
                channel_called = int(channel_name)
                channels_to_load.append(
                    ChannelData(
                        channel_called,
                        timestamp,
                        {"pulse_height": int(split_line[column])},
                        None,
                    )
                )
            if len(channels_to_load) == 0:
                return None
            return channels_to_load
        if self.file_handle.closed:
            return None
        line = self.file_handle.readline()
        if line == "":
            return None
        while line.startswith("X") and line.split()[1] == "//":
            line = self.file_handle.readline()

        splitlines = line.split()
        column_to_channel_map: Dict[int, str] = {}
        assert splitlines[0].startswith("WAVES/o/D")
        timestamp_column = (
            list(
                filter(
                    lambda x: x,
                    [
                        splitlines[i].startswith("timestamp")
                        for i in range(len(splitlines))
                    ],
                )
            )
        )[0] - 1
        # Map a column to a channel, remember, we
        self.timestamp_col = timestamp_column

        def mapping_func() -> Generator[Tuple[int, str], Any, None]:
            for i in range(len(splitlines)):
                if splitlines[i].startswith("chan"):
                    yield (i - 1, splitlines[i].removeprefix("chan").removesuffix(","))

        for index, chan_name in mapping_func():
            column_to_channel_map[index] = chan_name
        self.column_to_channel_map = column_to_channel_map
        line = self.file_handle.readline()
        # Begin seeking the waveform, we're going to be looping from here-on-out
        if line.startswith("BEGIN"):
            line = self.file_handle.readline()
            self.in_waves = True

        channels_to_load: List[ChannelData] = []
        # Begin parsing!
        split_line = line.split()
        timestamp = int(split_line[timestamp_column])
        self.saved_timestamp = timestamp
        for column, channel_name in column_to_channel_map.items():
            channel_called = int(channel_name)
            channels_to_load.append(
                ChannelData(
                    channel_called,
                    timestamp,
                    {"pulse_height": int(split_line[column])},
                    None,
                )
            )

        if len(channels_to_load) == 0:
            return None

        return channels_to_load


class WrappedGretinaLoader(BaseLoader):
    """
    Different from the original GretinaLoader, this wraps that to the standard BaseLoader interface for consistency purposes.
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.loader = GretinaLoader(fpath)  # type: ignore
        super().__init__(fpath, rebuild_events_with_window)

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        # contain all of the code without typing and get it into a typed set of code, sucks but, what can you do.
        metadata, event = self.loader.next_event()
        if metadata is None and event is None:
            return None
        assert metadata is not None
        chan_list = metadata["channels"]
        summaries = metadata["summaries"]
        timestamp = metadata["timestamp"]
        channel_list: List[ChannelData] = []
        for i in range(len(chan_list)):
            channel = chan_list[i]
            summary = None
            if summaries:
                summary = summaries[i]
            if event is not None:
                event_array = event[:, i]
                channel_list.append(
                    ChannelData(channel, timestamp, summary, event_array)
                )
        return channel_list

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self.loader.__exit__(type, value, traceback)  # type: ignore


# Directly translate the C structures here
class GretaPacketRoutingHeader(ctypes.LittleEndianStructure):
    _pack_ = 1
    _align_ = 4
    _fields_ = [
        ("version", ctypes.c_uint8),
        ("flags", ctypes.c_uint8),
        ("type", ctypes.c_uint8),
        ("subtype", ctypes.c_uint8),
        ("length", ctypes.c_uint16),
        ("sequence_number", ctypes.c_uint16),
        ("timestamp", ctypes.c_uint64),
        ("checksum", ctypes.c_uint64),
    ]


class GretaPacketWaveSubheader(ctypes.LittleEndianStructure):
    _pack_ = 1
    _align_ = 4
    _fields_ = [
        ("subheader_version", ctypes.c_int8),
        ("trig_count", ctypes.c_uint8),
        ("triggered", ctypes.c_int8),
        ("reserved_0", ctypes.c_int8),
        ("trigger_height", ctypes.c_int16),
        ("pulse_height", ctypes.c_int16),
        ("module_number", ctypes.c_uint16),
        ("channel", ctypes.c_uint16),
        ("start_location", ctypes.c_int16),
        ("reserved_1", ctypes.c_int16),
        ("qdc_base_sum", ctypes.c_int32),
        ("qdc_fast_sum", ctypes.c_int32),
        ("qdc_slow_sum", ctypes.c_int32),
        ("qdc_tail_sum", ctypes.c_int32),
        ("size", ctypes.c_uint32),
    ]


class GretaPacketTotal(ctypes.LittleEndianStructure):
    _pack_ = 1
    _align_ = 4
    _fields_ = [
        ("header", GretaPacketRoutingHeader),
        ("subheader", GretaPacketWaveSubheader),
    ]


class GretaLoader(BaseLoader):
    """
    Loader for the SkuTek GRETA single-packet format
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[bytes] = open(fpath, "rb")
        super().__init__(fpath, rebuild_events_with_window)

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        packet_initial_bytes = self.file_handle.read(ctypes.sizeof(GretaPacketTotal))
        if len(packet_initial_bytes) == 0:
            return None
        total_initial_packet = GretaPacketTotal.from_buffer_copy(packet_initial_bytes)
        flexible_member_bytes: bytes | None = None

        if total_initial_packet.subheader.size > 0:
            flexible_member_bytes = self.file_handle.read(
                ctypes.sizeof(ctypes.c_uint16 * total_initial_packet.subheader.size)
            )
        # Building the actual ChannelData
        if flexible_member_bytes is not None:
            flex_member_array_for_use = np.frombuffer(
                flexible_member_bytes, dtype=np.int16
            )
        else:
            flex_member_array_for_use = None
        channel = total_initial_packet.subheader.channel
        assert isinstance(total_initial_packet.subheader, GretaPacketWaveSubheader)
        build_dict: Dict[str, Any] = {}
        for item in total_initial_packet.subheader._fields_:
            build_dict[item[0]] = getattr(total_initial_packet.subheader, item[0])
        return [
            ChannelData(
                channel,
                total_initial_packet.header.timestamp,
                build_dict,
                flex_member_array_for_use,
            )
        ]


class IGORWaveLoader(BaseLoader):
    """
    A loader for the IGOR wave format type, this is an event type format and will consistently have events correctly built so long as the orignial event was made.
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[str] = open(fpath)
        # First line starts with IGOR
        self.file_handle.readline()
        super().__init__(fpath, rebuild_events_with_window)

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        # externally defined functions that we just skip

        # Items that we need to parse to get information such as timestamps
        event_num_start = "X evt_num ="
        timestamp_start = "X timestamp ="
        executed_comment = "X //"
        end_line = "END"
        waves_start = "WAVES/o/D"

        # Parsing logic
        def is_timestamp_line(line: str) -> bool:
            return line.startswith(timestamp_start)

        def parse_timestamp(line: str) -> int:
            if not is_timestamp_line(line):
                return -1
            return int(line.removeprefix(timestamp_start))

        def is_event_num_line(line: str) -> bool:
            return line.startswith(event_num_start)

        def parse_event_num(line: str) -> int:  # type: ignore
            if not is_event_num_line(line):
                return -1
            return int(line.removeprefix(event_num_start))

        def is_comment(line: str) -> bool:
            return line.startswith(executed_comment)

        def is_waves_line(line: str) -> bool:
            return line.startswith(waves_start)

        def read_until_non_comment() -> Optional[str]:
            line = self.file_handle.readline()
            while is_comment(line):
                line = self.file_handle.readline()
                if line == "":
                    return None
            return line

        def is_end(line: str) -> bool:
            return line.startswith(end_line)

        def mapping_func(
            splitlines: Sequence[str],
        ) -> Generator[Tuple[int, str], Any, None]:
            for i in range(len(splitlines)):
                if splitlines[i].startswith("chan"):
                    yield (i, splitlines[i].removeprefix("chan").removesuffix(","))

        # load_channel_batch again

        # Starting the parse
        line = read_until_non_comment()
        if (line == "" or line is None) or is_end(line):
            return None
        # timestamp & more check, if it's not one of timestamp or event number, skip
        if (
            line.startswith("X")
            and not is_event_num_line(line)
            and not is_timestamp_line(line)
        ):
            line = read_until_non_comment()

        if line == "" or line is None:
            return None

        if is_event_num_line(line):
            line = read_until_non_comment()

        if line == "" or line is None:
            return None

        # -1 is an invalid timestamp time as far as I'm aware
        this_event_timestamp = -1
        if is_timestamp_line(line):
            this_event_timestamp = parse_timestamp(line)

        while not is_waves_line(line):
            line = read_until_non_comment()
            if line is None or line == "":
                return None
        # moved here for simplicity's sake
        assert this_event_timestamp != -1, "The timestamp should exist!"

        # Parse what column after begin belonds in what channel
        column_to_channel_map: Dict[int, str] = {}
        splitline = line.split()
        for index, channel_name in mapping_func(splitline[1:]):
            column_to_channel_map[index] = channel_name

        # remove the BEGIN\n line
        line = self.file_handle.readline()

        # Load the channel waves
        wave_lines: List[str] = []
        line = self.file_handle.readline()
        while not is_end(line):
            wave_lines.append(line)
            line = self.file_handle.readline()

        raw_waves = " ".join(wave_lines)

        # convert from a string to wave using numpy parser
        waveforms = np.fromstring(raw_waves, dtype=np.int16, sep=" ")
        # reshape from flattened view into a N rows and columns for each channel.
        # This is a view, not a copy. So is a fast operation
        waveforms = waveforms.reshape((-1, len(column_to_channel_map)))

        # Collate each waveform into a distinct wave
        channel_data_to_return: List[ChannelData] = []
        for i in range(waveforms.shape[1]):
            channel_value = column_to_channel_map[i]
            channel_data_to_return.append(
                # If this_event_timestamp doesn't exist, crash out
                ChannelData(
                    int(channel_value), this_event_timestamp, None, waveforms[:, i]
                )
            )

        return channel_data_to_return
