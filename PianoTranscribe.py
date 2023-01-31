from IPython.display import display, SVG
from matplotlib      import pyplot as plt
#%config InlineBackend.figure_format = 'retina'
#pip install ffmpeg (for codec)
#ffmpeg -i test.mp4 -acodec pcm_u8 -ar 22050 test.wav
#not exactly what we wanted.  Need to be able to read mp4.  What do we do from here?  

import numpy       as np
import pretty_midi as pm
import librosa     as lbr
from   librosa.display     import specshow

from keras.models          import load_model
from keras.utils.vis_utils import model_to_dot

rate, songName = 22050, './input/test.wav'


song = lbr.effects.trim(lbr.load(songName, rate)[0])[0]
songLen = int(lbr.get_duration(song, rate))
print('Song duration\t{} min : {} sec'.format(songLen // 60, songLen % 60))

melsMinMin, melsMinMax, melsMeanMin, melsMeanMax, melsMaxMin, melsMaxMax = -43, -36, -26, -3, 37, 44

mels = lbr.power_to_db(lbr.magphase(lbr.feature.melspectrogram(song, rate, n_mels=229, fmin=30, htk=True))[0])
#assert melsMinMin < mels.min() < melsMinMax and melsMeanMin < mels.mean() < melsMeanMax \
#    and melsMaxMin < mels.max() < melsMaxMax, 'Wrong mels decibels range'
print('{} frames,\tmels decibels in range [{:.0f} ... {:.0f} ... {:.0f}]'.format(
    mels.shape[1], mels.min(), mels.mean(), mels.max()))

def PlotMelSpectrum(title):
    plt.title(title)
    specshow(mels, x_axis='time', y_axis='mel')
    plt.hlines([lbr.note_to_hz('C0'), lbr.note_to_hz('C1'), lbr.note_to_hz('C2'), lbr.note_to_hz('C3'), lbr.note_to_hz('C4'),
                lbr.note_to_hz('C5'), lbr.note_to_hz('C6'), lbr.note_to_hz('C7'), lbr.note_to_hz('C8')], 0, 10, linewidth=2)
    plt.xlim(0, 10)

plt.figure(figsize=(16, 10))
PlotMelSpectrum('Power spectrogram')
plt.show()

