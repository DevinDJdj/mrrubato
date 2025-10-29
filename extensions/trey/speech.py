from speechbrain.inference import EncoderDecoderASR
from speechbrain.inference.TTS import FastSpeech2
import speechbrain as sb
import sounddevice as sd
import numpy as np
import torch
import scipy.io.wavfile as wav
import argparse

import os
import threading
import winsound




#default 10 seconds for comment
def record_audio(duration=10, fname="example.wav", stop_event=None):
    samplerate = 16000  # Sample rate (Hz)
    #no easy way to stop early with sounddevice, so just record fixed time for now.
    print("Recording...")
    winsound.Beep(2000, 200) #beep to start
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    audio_tensor = torch.from_numpy(recording.squeeze()) # Remove channel dimension if mono
    wav.write(fname, samplerate, (recording * 32767).astype(np.int16)) # Save as int16 WAV file
    winsound.Beep(1000, 200) #beep to end
    return fname

def listen_audio(duration=10, fname="example.wav"):
    if os.path.exists(fname):
        os.remove(fname)
    audio_stop_event = threading.Event()  # Event to signal stopping

    audio_thread = threading.Thread(target=record_audio, args=(duration, f'{fname}', audio_stop_event))
    audio_thread.start()

    return audio_thread

def transcribe_audio(fname="example2.wav"):

    asr_model = EncoderDecoderASR.from_hparams(source="./models/pretrained_ASR")
#    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-conformer-transformerlm-librispeech", savedir="./models/pretrained_models/asr-transformer-transformerlm-librispeech")
    result = asr_model.transcribe_file(fname)
    #result = asr_model.transcribe_file("speechbrain/asr-conformer-transformerlm-librispeech/example.wav")
    print(result)
    return result


def generate_audio(text, fname="example_tts.wav", fast=True):

    tts_model = None
    if (fast):
        #parallel = True
        tts_model = FastSpeech2.from_hparams(
            source="speechbrain/tts-fastspeech2-ljspeech",
            savedir="./models/pretrained_tts_fastspeech2"
        )
    else:
        tts_model = sb.inference.TTS.Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="./models/pretrained_tts")

#    tacotron2 = sb.inference.TTS.Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="./models/pretrained_tts")

    hifi_gan = sb.inference.vocoders.HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="./models/pretrained_vocoder")

    # Define the text input.

    # Convert text to a mel-spectrogram using Tacotron2.
    mel_output, mel_length, alignment = tts_model.encode_text(text)

    # Convert the mel-spectrogram to an audio waveform using HiFiGAN.
    waveforms = hifi_gan.decode_batch(mel_output)

    # Save the resulting audio waveform to a file.
#    torchaudio.save('example_tts.wav', waveforms.squeeze(1), 22050)
    samplerate = 22050
    scaled = np.int16(waveforms.squeeze() * 32767)
    wav.write(fname, samplerate, scaled) # Save as int16 WAV file

    print("Audio saved to '" + fname + "'")
    return fname

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="A sample Python script with arguments.")
    parser.add_argument("--text", type=str, help="Your name", default="This is a test of the text to speech system.")
    parser.add_argument("--fname", type=str, help="Output filename", default="example_tts.wav")
    parser.add_argument("--fast", action='store_true', help="Use FastSpeech2 model", default=False)
    #fast not working..

    args = parser.parse_args()    
    print(f"Text: {args.text}, Filename: {args.fname}, Fast: {args.fast}")
    generate_audio(args.text, fname=args.fname, fast=args.fast)

