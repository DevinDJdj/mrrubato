#book/20240703.txt

#try to generate piano notes from wav file.  
#this will allow us to automate i.e. Text -> TTS -> WAV -> Midi Sequence.  

import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft, fftfreq
import scipy.io.wavfile as wav
import json

NOTES_MAP = json.load(open("notes-frequencies.json", "r"))

WAVE_LOCATION = "./new-home-in-the-stars-16k.wav"
WAVE_LOCATION = "./Article Sample.wav"
#WAVE_LOCATION = "./arctic_a0024.wav"

DURATION = 3  # Seconds
wav_file = open(WAVE_LOCATION, "rb")
SAMPLE_RATE, data = wav.read(wav_file)

# Plot the time domain
t = 1 * np.arange(SAMPLE_RATE*DURATION)
plt.plot(t, data[:SAMPLE_RATE*DURATION])

yy = data[:SAMPLE_RATE*DURATION]
if (len(yy.shape) > 1):
  yy = yy[:,0]

print(yy)

yf = fft(yy)
xf = fftfreq(SAMPLE_RATE*DURATION, 1 / SAMPLE_RATE)
plt.plot(xf, np.abs(yf))
plt.xlim([0, 3e3])
plt.show()



print(xf)
print(yf)
# Map frequencies to magnitude
y = np.abs(yf)

print(y)

d = {}
for i in range(0, len(y)):
  if xf[i] > 0:
    d[f"{xf[i]}"] = y[i]

# Sort the dict so highest frequencies are at the top
#print(d)
d = sorted(d, key=d.get, reverse=True)

# Get the top 10 notes
bucket = []
for i in d:
  if len(bucket) == 10:
    break
  i = round(float(i))
  if i not in bucket:
    bucket.append(i)

# Map to notes
notes = []
for i in bucket:
  for note in NOTES_MAP:
    note_freq = NOTES_MAP[note]

    l_r = i - 4
    h_r = i + 4
    if l_r < note_freq and h_r > note_freq:
      notes.append(note)
      break

print(list(set(notes)))

