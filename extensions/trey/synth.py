#> pip install pyaudio
import pyaudio
import argparse
import itertools
import math
import numpy as np
import time
import matplotlib.pyplot as plt

BUFFER_SIZE = 256
SAMPLE_RATE = 44100
NOTE_AMP = 0.1

global stream
stream = None
# -- HELPER FUNCTIONS --
global notes_dict
notes_dict = {}
global last_freq
last_freq = 440

def get_audio_stream():
    
    global stream
    if stream is not None:
        return stream
    
    p = pyaudio.PyAudio()
    stream = p.open(
        rate=SAMPLE_RATE,
        channels=1,
        format=pyaudio.paFloat32,
        output=True,
#        frames_per_buffer=BUFFER_SIZE,

    )
    return stream

def get_sin_oscillator(freq=55, amp=1, start=0, duration=0.1, sample_rate=SAMPLE_RATE):

    t = np.linspace(start, start+duration, int(SAMPLE_RATE * duration), endpoint=False)
    sine_wave = amp * np.sin(2 * np.pi * freq * t) 
    return sine_wave

#    increment = (2 * math.pi * freq) / sample_rate
#    return (
#        math.sin(v) * amp * NOTE_AMP for v in itertools.count(start=0, step=increment)
#    )


#dont call from thread..
def plot_signal(signal: np.ndarray, steps: int = SAMPLE_RATE/20):
    plt.plot(np.arange(0, len(signal), 1), signal)
    if steps:
        plt.xlim(0, steps)
    plt.hlines(0, 0, len(signal), color='red')
    plt.show()

def midi_to_freq(midiNum, velocity = 127):
    if (velocity > 0):
        return 440 * math.pow(2, (midiNum - 69) / 12)
    return 0


def play_stream(stop_event):
    play_count = 0
    while (not stop_event.is_set()):
        play(play_count)
        play_count += 1
#        time.sleep(0.05)

def play(play_count): #default each 0.1 seconds
    global notes_dict, last_freq
    stream = get_audio_stream()   
    localnotes = notes_dict.copy()
    if localnotes:
        # Play any of the notes
        
        mystep = 1 / last_freq #time for one wave cycle
        mydur = mystep * 4  #at least 4 wave cycles
        while (mydur+mystep < 0.1):
            mydur += mystep
        
        sample_len = int(mydur*SAMPLE_RATE)  # 0.1 second buffer
        final = np.zeros(sample_len , dtype=np.float32)  

        for key,value in localnotes.items():
            note = key
            freq = midi_to_freq(note)
            time_elapsed = time.time() - value['start_time']
            time_elapsed = 0
#            time_elapsed = play_count * 1000  # in ms

            #base this on frequency and not time_elapsed?  
            value = get_sin_oscillator(freq=freq, amp=value['vel']/127, start=time_elapsed/1000, duration=mydur)
#            final += value[:sample_len]  # Mix the notes together  
            value = np.pad(value, (0, max(0, sample_len - len(value))), 'constant')  # Pad or truncate to sample_len
            final += value

        final = final / len(localnotes)  # Normalize the mixed audio
        samples = final

        audio = samples.astype(np.float32).tobytes()
        print(final)
#        plot_signal(final, steps=200)
        stream.write(audio)

def note_off(note):
    if note in notes_dict:
        del notes_dict[note]

def note_on(note, velocity=127):
    global last_freq
    last_freq = midi_to_freq(note)
    notes_dict[note] = {"vel": velocity, "start_time": time.time()}


def play_note(note, duration=0.1, amp=0.5):
    stream = get_audio_stream()   
    freq = midi_to_freq(note)
    samples = get_sin_oscillator(freq=freq, amp=amp, duration=duration)
    audio = samples.astype(np.float32).tobytes()
    stream.write(audio)

def test_sound():
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    # Generate a 1-second 440 Hz sine wave
    frequency = 440
    duration = 1.0

    t = np.linspace(0, duration, int(RATE * duration), endpoint=False)
    sine_wave = 0.5 * np.sin(2 * np.pi * frequency * t) # Amplitude 0.5
    print(len(sine_wave))
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)

    print("Playing test tone...")
    stream.write(sine_wave.astype(np.float32).tobytes())
    print("Test tone finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()


if (__name__ == "__main__"):

    parser = argparse.ArgumentParser(description="A sample Python script with arguments.")
    parser.add_argument("--note", type=int, help="Your name", default=60)

    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"Index: {i}, Name: {dev['name']}, Max Output Channels: {dev['maxOutputChannels']}")

#    output_device_index = int(input("Select output device index: "))

    args = parser.parse_args()    
    print(f"Freq: {args.note}")
    print("Testing Sound...")
    test_sound()
    print("Test Sound Finished.")
    print("Playing Note...")
    stream = p.open(
        rate=SAMPLE_RATE,
        channels=1,
        format=pyaudio.paFloat32,
        output=True,
    )
    note = args.note
    vel = 127
    freq = midi_to_freq(note, vel)
    notes_dict[note] = get_sin_oscillator(freq=freq, amp=vel / 127)
    notes_dict[note+12] = get_sin_oscillator(freq=freq*2, amp=vel / 127)  # One octave higher

    if notes_dict:
        # Play any of the notes
        final = np.zeros(SAMPLE_RATE , dtype=np.float32)  # 2 seconds of silence
        for key,value in notes_dict.items():
            final += value[:SAMPLE_RATE]  # Mix the notes together  
            print(f"Playing note {note} at frequency {midi_to_freq(note)} Hz")
            samples = value[:SAMPLE_RATE]
            audio = samples.astype(np.float32).tobytes()
            stream.write(audio)    
        final = final / len(notes_dict)  # Normalize the mixed audio
        samples = final

        print(len(samples))
        audio = samples.astype(np.float32).tobytes()
        stream.write(audio)    


