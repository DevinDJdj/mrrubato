#> pip install pyaudio
import pyaudio
import argparse
import itertools
import math
import numpy as np

BUFFER_SIZE = 256
SAMPLE_RATE = 44100
NOTE_AMP = 0.1

# -- HELPER FUNCTIONS --
def get_sin_oscillator(freq=55, amp=1, duration=1.0, sample_rate=SAMPLE_RATE):

    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    sine_wave = 0.5 * np.sin(2 * np.pi * freq * t) # Amplitude 0.5
    return sine_wave

#    increment = (2 * math.pi * freq) / sample_rate
#    return (
#        math.sin(v) * amp * NOTE_AMP for v in itertools.count(start=0, step=increment)
#    )


def midi_to_freq(midiNum, velocity = 127):
    if (velocity > 0):
        return 440 * math.pow(2, (midiNum - 69) / 12)
    return 0


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
    notes_dict = {}
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

    if notes_dict:
        # Play any of the notes
        final = np.zeros(SAMPLE_RATE , dtype=np.float32)  # 2 seconds of silence
        for key,value in notes_dict.items():
            final += value[:SAMPLE_RATE]  # Mix the notes together  
            print(f"Playing note {note} at frequency {midi_to_freq(note)} Hz")
        final = final / len(notes_dict)  # Normalize the mixed audio
        samples = final

        print(len(samples))
        audio = samples.astype(np.float32).tobytes()
        stream.write(audio)    


