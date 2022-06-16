import pyaudio
import time
import numpy as np
from api import Traffects, Pin

# frequency ranges for each important audio group
# https://www.teachmeaudio.com/mixing/techniques/audio-spectrum
class Frequency:
  SUB_BASS        = (  20,    60)
  BASS            = (  60,   250)
  LOW_MIDRANGE    = ( 250,   500)
  MIDRANGE        = ( 500,  2000)
  UPPER_MIDRANGE  = (2000,  4000)
  PRESENCE        = (4000,  6000)
  BRILLIANCE      = (6000, 20000)

# simple processor you can use
def process_blink(api: Traffects, triggered: set[Frequency, Pin], primary_freq: int):
  for (_, pin) in triggered:
    api.blink(pin)

def process_toggle(api: Traffects, triggered: set[Frequency, Pin], primary_freq: int):
  pins = [pin for (_, pin) in triggered]
  for pin in Pin.range():
    api.set(pin, pin in pins)

def process_primary(api: Traffects, triggered: set[Frequency, Pin], primary_freq: int):
  pins = set()
  if primary_freq >= 25 and primary_freq <= 250:
    pins.add(Pin.GREEN)
  elif primary_freq >= 250 and primary_freq <= 3000:
    pins.add(Pin.YELLOW)
  elif primary_freq >= 3000:
    pins.add(Pin.RED)

  for pin in Pin.range():
    api.set(pin, pin in pins)

# config values
threshold = .915
cooldown = .995
processor = process_toggle
mapping = [
  (Frequency.SUB_BASS,       Pin.GREEN),
  (Frequency.BASS,           Pin.GREEN),
  (Frequency.LOW_MIDRANGE,   Pin.YELLOW),
  (Frequency.MIDRANGE,       Pin.YELLOW),
  (Frequency.UPPER_MIDRANGE, Pin.YELLOW),
  (Frequency.PRESENCE,       Pin.RED),
  (Frequency.BRILLIANCE,     Pin.RED),
]

# init managers
p = pyaudio.PyAudio()
api = Traffects("COM8")

# find virtual cable
mic = None
for i in range(p.get_device_count()):
  info = p.get_device_info_by_index(i)
   
  if "vb-audio virtual" in info["name"].lower() and "output" in info["name"].lower():
    print(f"Found Vritual Cable {i} = '{info['name']}': {info['maxOutputChannels']} channels, {int(info['defaultSampleRate'])} samplerate")
    mic = info

# declare device specs
device_index = mic["index"]
rate = int(mic["defaultSampleRate"])
channels = 1
bytes_per_sample = 2**12

# keeps track of the last maximum volume for each frequency of mapping (init with 0)
maximum = [0 for _ in range(len(mapping))] 

def beat_detect(input):
  audio_fft = np.abs(np.fft.fft(input))
  freqs = rate * np.arange(len(audio_fft)) / len(audio_fft)
  primary_freq = freqs[np.argmax(audio_fft)]  

  triggered = set()
  if primary_freq == 0:
    processor(api, triggered, primary_freq)
    return

  for i in range(len(mapping)):
    ((min_freq, max_freq), pin) = mapping[i]

    indices = [idx for idx, val in enumerate(freqs) if val >= min_freq and val <= max_freq]
    value = np.max(audio_fft[indices])
    maximum[i] = max_value = max(value, maximum[i]) * cooldown

    # value / max_value: the percentage from maximum
    if value / max_value >= threshold:
      triggered.add(mapping[i])
   
    processor(api, triggered, primary_freq)


# define callback
def callback(in_data, frame_count, time_info, status):
  data = np.fromstring(in_data, dtype=np.int16)
  beat_detect(data)
  return (in_data, pyaudio.paContinue)

# open stream using callback
stream = p.open(format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                frames_per_buffer=bytes_per_sample,
                input=True,
                input_device_index=device_index,
                stream_callback=callback)

# start the stream
stream.start_stream()

# wait for stream to finish
while stream.is_active():
  time.sleep(0.1)

# stop stream and terminate
stream.stop_stream()
stream.close()
p.terminate()