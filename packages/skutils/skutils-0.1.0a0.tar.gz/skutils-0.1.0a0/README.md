# Skutils

skutils (SkuTek Utilities) contains tools to control SkuTek digitizers and process data files.

## Controlling a FemtoDAQ Digitizer

Your FemtoDAQ family digitizer can be controlled programmatically remotely the skutils `FemtoDAQController` class. This class provides a convienent set of functions to interact with the digitizers REST API in pythonic format.

### Connect to your digitizer

Your FemtoDAQ family digitizer can be controlled programmatically remotely the skutils `FemtoDAQController` class. This class provides a convienent set of functions to interact with the digitizers REST API in pythonic format.

### Connect to your digitizer

```python
import skutils
# replace the URL with your unit's hostname or ip address
digitizer = skutils.FemtoDAQController('http://vireo-000001')
```
### Configuration before data collection

```python
# Apply Global Settings (applies to all channels)
# Trigger Settings (all channels)
digitizer.setTriggerXPosition(64)
digitizer.setTriggerActiveWindow(512)
digitizer.setPulseHeightWindow(512)
# PulseHeight
digitizer.setPulseHeightAveragingWindow(16)
# Detector Bias Voltage
digitizer.setBiasVoltage(29)
# Baseline Restoration
digitizer.setEnableBaselineRestoration(True)   # Feature not available on all units
digitizer.setBaselineRestorationExclusion(512) # Feature not available on all units
# QuadQDC
digitizer.setQuadQDCWindows(128,32,64,128)      # Feature not available on all units
 
# Channel Settings (Independent settings for every channel)
for channel in digitizer.channels:
  # Analog Offset
  digitizer.setAnalogOffsetPercent(channel, 0)
  # Digital Offset
  digitizer.setDigitalOffset(channel, -40)
  # Trigger Controls
  digitizer.setEnableTrigger(channel, true)
  digitizer.setTriggerEdge(channel, "rising")
  digitizer.setTriggerSensitivity(channel, 128)
  digitizer.setTriggerAveragingWindow(channel, 1)
  # Histogramming Controls
  digitizer.setHistogramScaling(channel, 2)
  digitizer.setHistogramQuantity(channel, "pulse_height")


```
#### Set Global Id 

The global id is a number (between 0 and 255) which can be set 
for each digitizer in your experiment. The global id is stored in the header

of recorded data files and packet streaming so the user can determine 
which digitizer their data came from during post processing.

In multi-digitizer DAQ configurations, set this to something unique for
each digitizer.

**Only Available on FemtoDAQ Software v5.4.0 and above**


```python
digitizer.setGlobalID(1)
```

### Reading back Configuration

In addition, there are complimentry functions to readback the current configuration of your unit. The only exception is `AnalogOffsetPercent` which cannot be read back, but can be measured as the baseline of your traces.

Globals
- getTriggerXPosition
- getTriggerActiveWindow
- getPulseHeightWindow
- getEnableBaselineRestoration
- getBaselineRestorationExclusion
- getPulseHeightAveragingWindow
- getQuadQDCWindows
- getBiasVoltage
- getBiasVoltageRaw
- getGlobalId

Per-Channel
- getDigitalOffset
- getEnableTrigger
- getTriggerEdge
- getTriggerSensitivity
- getTriggerAveragingWindow
- getHistogramScaling
- getHistogramQuantity
- getDigitalOffset
- getEnableTrigger
- getTriggerEdge
- getTriggerSensitivity
- getHistogramScaling
- getHistogramQuantity


### Reset the timestamp
```python
last_event_timestamp = digitizer.getTimestamp()
digitizer.clearTimestamp()
```

### Starting/Stopping Data Collection

_This feature is planned, but not yet implemented._


### Downloading Data Files to your Computer Programmatically


**Only Available on FemtoDAQ Software v5.4.0 and above**

Several functions are available to download data files recorded with
your FemtoDAQ digitizer directly to your machine. This is useful for 
automated data collection runs controlled via a script

NOTE: file deletion cannot be performed programmatically, but can 
be performed in your FemtoDAQ's graphical interface

```python
# Get list of all data filenames that were recored during the most recent
# experimental run. set last_run_only to False to grab all filenames
last_run_filenames = digitizer.getListOfDataFiles(last_run_only=True)

# download any data file existing on your FemtoDAQ directly with the downloadFile function. We'll download all json configuration files as an example
all_filenames = digitizer.getListOfDataFiles(last_run_only=False)
for fname in last_run_filenames:
  if '.json' in fname:
    digitizer.downloadFile(fname, save_to="./")

# automatically the last run data files to your computer
digitizer.downloadLastRunDataFiles(save_to="./")
```


## Reading data from files

###### simplest use case
```python
import skutils
loader = skutils.GretinaLoader("path/to/your/.geb")

metadata,event = loader.next_event()
```

###### Load all events at once
```python
all_metadata, all_events = loader.load_and_sort_all_events()
```

###### Iterate through all events
```python
loader.seek_event(0) # reset to first event
for metadata,event in loader:
  print(f"Event {metadata['event_number']} timestamp is {metadata['timestamp']}")
```

###### Fetch specific event
```python
# this will not advance the file position internally
metadata,event = loader.fetch_event(10)
```


The `GretinaLoader` can be used to quickly load events from Skutek Gretina
formatted data.

Events are defined as a series of contiguous packets with the same timestamp.
Only requested events are loaded into memory by default. the `GretinaLoader` will return two objects every time an event is loaded. One is a dictionary called "metadata", and the other is a Panda DataFrame containing the raw event data

### the `metadata` dictionary

`metadata` contains the following fields with ancillary information about the event:


| Field Name         | Description                                                                                                 |
|--------------------|-------------------------------------------------------------------------------------------------------------|
| "timestamp"        | Timestamp of the trigger in FPGA clock cycles                                                               |
| "event_number"     | the index of this event in the file                                                                         |
| "channels"         | A list of the channels in this event. In the order in which they are saved in the event columns             |
| "number_samples"   | number of samples per channel                                                                               |
| "wave_type"        | wave type as a Gretina Numerical indicator                                                                  |
| "wave_type_string" | a human-readable string indicating the type of information in this event. either  "histogram" or "waveform" |
| "signed"           | boolean indicating whether the data in this  event is signed or unsigned                                    |
| "bitdepth"         | the bitdepth of the data                                                                                    |         
| "module_num"       | Alias for Global_ID. Can be set to distinquish digitizers from each other in multi-unit DAQ experiments     |
| "version_num"      | Used by SkuTek for internal development                                                                     |
| "packets"          | PacketMetadata objects associated with this event.  Used by SkuTek for internal development                 |
| "histogram"        | Histograms tagged with this timestamp if they exist                                                         |
| "summaries"        | list of pulse summary dictionaries for each channel in this event                                           |

#### Pulse Summary Information
Some data collection may store Pulse Summaries ("summaries" in the above metadata key) which is summary data about the pulse on each channel. Such as the
the pulse_height, trigger_height, and trigger_count.

Pulse Summary data is stored as a a dictionary and is accessible in the larger `metadata` dictionary


- "pulse_height" : Maximum height of this pulse
- "trig_height"  : The height/slope at which the trigger fired
- "trig_count"   : The number of triggers on this channel
- "triggered"    : Boolean indicating whether the trigger on this channel fired
- "qdc_base_sum" : QuadQDC BASE sum or 0 on units where this feature isn't supported
- "qdc_fast_sum" : QuadQDC FAST sum or 0 on units where this feature isn't supported
- "qdc_slow_sum" : QuadQDC SLOW sum or 0 on units where this feature isn't supported
- "qdc_tail_sum" : QuadQDC TAIL sum or 0 on units where this feature isn't supported


### the `event` data

Event data is returned as a Numpy Array. This is a tabular representation of the event data. Each column represents a channel in the event and rows are the samples for that channel. 

To fetch data from a specific channel
```python
# grab channel 4
ch4_column_index = metadata['channels'].index(4)
channel4_array = event_array[:, ch4_column_index]
```

### Speed/Efficiency Options

###### Basic

```python
loader = skutils.GretinaLoader("path/to/your/.bin")
```

###### memory efficient, but slower
```python
# Don't cache the location of events in the file.
loader = skutils.GretinaLoader("path/to/your/.bin", cache_event_metadata=False)
```

###### faster, but more memory intensive
```python
# Load the entire file into memory first, so fetching events is much faster
loader = skutils.GretinaLoader("path/to/your/.bin", memmap=True)
```



----

## GretinaFileWriter

simplest usage

```python
import skutils
from skutils import GebTypes
import numpy as np
import time
# Event can be a pandas DataFrame with samples as rows, and channels as columns
# columns names must be integer channel numbers
# OR a numpy array shaped (n_samples, n_channels). In this latter case, column 0
# is assumed to be channel 0, column 1 to be channel 1, etc
NUM_EVENTS = 1000
FILENAME = "test.bin"
with skutils.GretinaFileWriter(FILENAME) as writer:
  for i in range(NUM_EVENTS):
    # make random event data for 32channel digitizer
    event_data = (np.random.randint(0,2048,4096) ).astype(np.int16)

    # Write a wave
    #                  (data,      integer_timestamp,       integer wave_type)
    writer.write_event(event_data, time.monotonic_ns(), GebTypes.raw_waveform)
    # writing a histogram
    writer.write_event(event_data, time.monotonic_ns(), GebTypes.raw_histogram)
    print("saved waveform and histogram")

```
