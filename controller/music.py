import pyaudio
import time
import numpy as np
from api import Traffects, Pin

# config values
threshold = .9
cooldown = .99

# initialize with start values
global sub_bass_max, bass_max, low_midrange_max, midrange_max, upper_midrange_max, presence_max, brilliance_max
sub_bass_max = 10
bass_max = 10
low_midrange_max = 10
midrange_max = 10
upper_midrange_max = 10
presence_max = 10
brilliance_max = 10

p = pyaudio.PyAudio()
api = Traffects("COM4")

# find virtual cable
vc = None
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
   
    if "vb-audio virtual" in info["name"].lower() and "output" in info["name"].lower():
        vc = info
        print(f"Found Vritual Cable {i} = '{info['name']}': {info['maxOutputChannels']} channels, {int(info['defaultSampleRate'])} samplerate")

rate = int(vc['defaultSampleRate'])
channels = 1
bytes_per_sample = 2**12

def beat_detect(in_data):
    audio_fft = np.abs(np.fft.fft(in_data))
    freqs = rate * np.arange(len(audio_fft)) / len(audio_fft)

    # frequency ranges for each important audio group
    sub_bass_indices = [idx for idx,val in enumerate(freqs) if val >= 20 and val <= 60]
    bass_indices = [idx for idx,val in enumerate(freqs) if val >= 60 and val <= 250]
    low_midrange_indices = [idx for idx,val in enumerate(freqs) if val >= 250 and val <= 500]
    midrange_indices = [idx for idx,val in enumerate(freqs) if val >= 500 and val <= 2000]
    upper_midrange_indices = [idx for idx,val in enumerate(freqs) if val >= 2000 and val <= 4000]
    presence_indices = [idx for idx,val in enumerate(freqs) if val >= 4000 and val <= 6000]
    brilliance_indices = [idx for idx,val in enumerate(freqs) if val >= 6000 and val <= 20000]

    # find max value for each frequency range
    sub_bass = np.max(audio_fft[sub_bass_indices])
    bass = np.max(audio_fft[bass_indices])
    low_midrange = np.max(audio_fft[low_midrange_indices])
    midrange = np.max(audio_fft[midrange_indices])
    upper_midrange = np.max(audio_fft[upper_midrange_indices])
    presence = np.max(audio_fft[presence_indices])
    brilliance = np.max(audio_fft[brilliance_indices])

    global sub_bass_max, bass_max, low_midrange_max, midrange_max, upper_midrange_max, presence_max, brilliance_max
    sub_bass_max = max(sub_bass_max, sub_bass)
    bass_max = max(bass_max, bass) * cooldown*cooldown
    low_midrange_max = max(low_midrange_max, low_midrange) * cooldown*cooldown
    midrange_max = max(midrange_max, midrange) * cooldown
    upper_midrange_max = max(upper_midrange_max, upper_midrange) * cooldown
    presence_max = max(presence_max, presence) * cooldown
    brilliance_max = max(brilliance_max, brilliance) * cooldown
    
    # print("Max:", sub_bass_max)
    # print("Bass:", sub_bass)

    # use set to keep track of target pins
    pins = set(())

    if sub_bass >= sub_bass_max * threshold:
        pins.add(Pin.GREEN)
        print("Sub Bass Beat")

    if bass >= bass_max * threshold:
        pins.add(Pin.GREEN)
        print("Bass Beat")

    if low_midrange >= low_midrange_max * threshold:
        pins.add(Pin.YELLOW)
        print("Low Midrange Beat")

    if midrange >= midrange_max*.9 :
        pins.add(Pin.YELLOW)
        print("Midrange Beat")

    if upper_midrange >= upper_midrange_max * threshold:
        pins.add(Pin.YELLOW)
        print("Upper Midrange Beat")

    if presence >= presence_max * threshold:
        pins.add(Pin.RED)
        print("Presence Beat")

    if brilliance >= brilliance_max * threshold:
        pins.add(Pin.RED)
        print("Brilliance Beat")

    primary_freq = freqs[np.argmax(audio_fft)]

    """ pins.clear();
    if primary_freq >= 25 and primary_freq <= 250:
        pins.add(Pin.GREEN)
    elif primary_freq >= 250 and primary_freq <= 3000:
        pins.add(Pin.YELLOW)
    elif primary_freq >= 3000:
        pins.add(Pin.RED) """
    
    for pin in pins:
      api.blink(pin)
    #for pin in Pin.range():
    #  api.send(pin, pin in pins)


# define callback (2)
def callback(in_data, frame_count, time_info, status):
    """ data = wf.readframes(frame_count)
    beat_detect(data) """
    data = np.fromstring(in_data, dtype=np.int16)
    beat_detect(data)
    return (in_data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                frames_per_buffer=bytes_per_sample,
                input=True,
                input_device_index=vc['index'],
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()

# close PyAudio (7)
p.terminate()