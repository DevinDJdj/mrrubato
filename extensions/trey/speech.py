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



# 3. Define text pipeline:
@sb.utils.data_pipeline.takes("words")
@sb.utils.data_pipeline.provides(
        "words", "tokens_list", "tokens_bos", "tokens_eos", "tokens")
def text_pipeline(words):
      global asr_model
      yield words
      tokens_list = asr_model.tokenizer.encode_as_ids(words)
      yield tokens_list
      tokens_bos = torch.LongTensor([asr_model.hparams.bos_index] + (tokens_list))
      yield tokens_bos
      tokens_eos = torch.LongTensor(tokens_list + [asr_model.hparams.eos_index]) # we use same eos and bos indexes as in pretrained model
      yield tokens_eos
      tokens = torch.LongTensor(tokens_list)
      yield tokens


# Define fine-tuning procedure
class EncDecFineTune(sb.Brain):

    def on_stage_start(self, stage, epoch):
        # enable grad for all modules we want to fine-tune
        if stage == sb.Stage.TRAIN:
            for module in [self.modules.enc, self.modules.emb, self.modules.dec, self.modules.seq_lin]:
                for p in module.parameters():
                    p.requires_grad = True

    def compute_forward(self, batch, stage):
        """Forward computations from the waveform batches to the output probabilities."""
        batch = batch.to(self.device)
        wavs, wav_lens = batch.signal
        tokens_bos, _ = batch.tokens_bos
        wavs, wav_lens = wavs.to(self.device), wav_lens.to(self.device)

        # Forward pass
        feats = self.modules.compute_features(wavs)
        feats = self.modules.normalize(feats, wav_lens)
        #feats.requires_grad = True
        x = self.modules.enc(feats)

        e_in = self.modules.emb(tokens_bos)  # y_in bos + tokens
        h, _ = self.modules.dec(e_in, x, wav_lens)

        # Output layer for seq2seq log-probabilities
        logits = self.modules.seq_lin(h)
        p_seq = self.hparams.log_softmax(logits)

        return p_seq, wav_lens

    def compute_objectives(self, predictions, batch, stage):
        """Computes the loss (CTC+NLL) given predictions and targets."""


        p_seq, wav_lens = predictions

        ids = batch.id
        tokens_eos, tokens_eos_lens = batch.tokens_eos
        tokens, tokens_lens = batch.tokens

        loss = self.hparams.seq_cost(
            p_seq, tokens_eos, tokens_eos_lens)


        return loss


def parse_to_json(basedir="../testing/data/mini_librispeech/LibriSpeech/", type="dev-clean-2", out='data.json'):
    #parse a directory of audio files and create a json file for training.  
#    "test-clean"
#    "train-clean-5"
    #https://speechbrain.readthedocs.io/en/latest/tutorials/basics/data-loading-pipeline.html#install-dependencies
    import glob
    import json
    import os
    import torchaudio
    from pathlib import Path

    dev_clean_root = basedir + type
    print(dev_clean_root)
    flac_files = glob.glob(os.path.join(dev_clean_root, "**/*.flac"), recursive=True)
    print("tot flac audio files {}".format(len(flac_files)))

    flac_files[0]
    # in this dataset files names are spk_id-chapter_id-utterance_id.flac
    text_files = glob.glob(os.path.join(dev_clean_root, "**/*.txt"), recursive=True)
    # we build a dictionary with words for each utterance
    words_dict = {}
    for txtf in text_files:
        with open(txtf, "r") as f:
            lines = f.readlines()
        for l in lines:
            l = l.strip("\n")
            utt_id = l.split(" ")[0]
            words = " ".join(l.split(" ")[1:])
            words_dict[utt_id] = words

    # we now build JSON examples

    examples = {}
    for utterance in flac_files:
        utt_id = Path(utterance).stem
        examples[utt_id] = {"file_path": utterance,
                            "words": words_dict[utt_id],
                            "spkID": utt_id.split("-")[0],
                            "length": torchaudio.info(utterance).num_frames}


    with open(dev_clean_root + "/" + out, "w") as f:
        json.dump(examples, f, indent=4)

    print(examples[list(examples.keys())[0]])
    #filename for json_file
    return dev_clean_root + "/" + out

def train_model():
    #set up JSON files for training.  
    global asr_model

    asr_model = EncoderDecoderASR.from_hparams(source="./models/pretrained_ASR", savedir="./models/pretrained_ASR", hparams_file="hyperparams.yaml")    
#    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech", savedir="./models/pretrained_ASR", hparams_file="hyperparams.yaml")
    fname = parse_to_json()
    from speechbrain.dataio.dataset import DynamicItemDataset
    dataset = DynamicItemDataset.from_json(fname)
    dataset = dataset.filtered_sorted(sort_key="length", select_n=100)
    dataset.add_dynamic_item(sb.dataio.dataio.read_audio, takes="file_path", provides="signal")
    dataset.add_dynamic_item(text_pipeline)
    dataset.set_output_keys(["id", "signal", "words", "tokens_list", "tokens_bos", "tokens_eos", "tokens"])
    print(dataset[0])


    
    """
    modules = {"enc": asr_model.mods.encoder.transformer_encoder,
#            "emb": asr_model.hparams.emb,
            "dec": asr_model.hparams.decoder,
            "compute_features": asr_model.mods.encoder.compute_features, # we use the same features
            "normalize": asr_model.mods.encoder.normalize,
            "seq_lin": asr_model.hparams.seq_lin,

            }   
    """
    modules = {"enc": asr_model.mods.encoder.model,
            "emb": asr_model.hparams.emb,
            "dec": asr_model.hparams.dec,
            "compute_features": asr_model.mods.encoder.compute_features, # we use the same features
            "normalize": asr_model.mods.encoder.normalize,
            "seq_lin": asr_model.hparams.seq_lin,

            }

    hparams = {"seq_cost": lambda x, y, z: sb.nnet.losses.nll_loss(x, y, z, label_smoothing = 0.1),
                "log_softmax": sb.nnet.activations.Softmax(apply_log=True)}

    brain = EncDecFineTune(modules, hparams=hparams, opt_class=lambda x: torch.optim.SGD(x, 1e-5))
    brain.tokenizer = asr_model.tokenizer

    brain.fit(range(2), train_set=dataset,
            train_loader_kwargs={"batch_size": 8, "drop_last":True, "shuffle": False})


#default 10 seconds for comment
def record_audio(duration=10, fname="example.wav", stop_event=None):
    samplerate = 16000  # Sample rate (Hz)
    #no easy way to stop early with sounddevice, so just record fixed time for now.
    print("Recording...")
    from pycaw.pycaw import AudioUtilities
    device = AudioUtilities.GetSpeakers()
    volume = device.EndpointVolume
    currentvolume = volume.GetMasterVolumeLevel()
    volume.SetMasterVolumeLevel(currentvolume-20, None) #reduce volume to 20% for recording.
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='float32')
    winsound.Beep(2000, 200) #beep to start
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    audio_tensor = torch.from_numpy(recording.squeeze()) # Remove channel dimension if mono
    wav.write(fname, samplerate, (recording * 32767).astype(np.int16)) # Save as int16 WAV file

    volume.SetMasterVolumeLevel(currentvolume, None) #return to normal volume.  

    winsound.Beep(1000, 200) #beep to end
    return fname

def listen_audio(duration=10, fname="example.wav"):
    if os.path.exists(fname):
        os.remove(fname)
    audio_stop_event = threading.Event()  # Event to signal stopping

    audio_thread = threading.Thread(target=record_audio, args=(duration, f'{fname}', audio_stop_event))
    audio_thread.start()


    return audio_thread

def download_file(mediafile):
    OUTPUT_DIR = "./temp/"
    mediafile = mediafile.replace(" ", "%20")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    import urllib.request
    urllib.request.urlretrieve(mediafile, OUTPUT_DIR + "test.mp4")
    fname = OUTPUT_DIR + "test.mp4"
    return fname

def convert_mp4_to_wav(mp4_fname):
    from moviepy.editor import VideoFileClip
    from pydub import AudioSegment
    # Load the video clip
    video_clip = VideoFileClip(mp4_fname)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio

    # Write the audio to a separate file
    mp3_file = mp4_fname[:-4] + '.mp3'
    print(f"Converting mp4 to audio: {mp3_file}")
    audio_clip.write_audiofile(mp3_file)

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()

    print(f"Converting mp3 to wav: {mp3_file}")
    sound = AudioSegment.from_mp3(mp3_file)
    mono_sound = sound.set_channels(1)
    resampled_audio = mono_sound.set_frame_rate(16000)
    wav_fname = mp4_fname[:-4] + '.wav'
    resampled_audio.export(wav_fname, format="wav")
#    sound.export(wav_fname, format="wav")
    return wav_fname

def getTimeFromSecs(secs):
    minutes = secs // 60
    seconds = secs % 60
    return f"{minutes:02}:{seconds:02}"


def init_asr_model():
    model_w2v2 = EncoderDecoderASR.from_hparams(
        source="speechbrain/asr-wav2vec2-commonvoice-en",
        savedir="pretrained_models/asr-wav2vec2-commonvoice-en"
    )
    return model_w2v2
    
    from speechbrain.inference.ASR import WhisperASR
    model_whisper = WhisperASR.from_hparams(
        source="speechbrain/asr-whisper-small",
        savedir="pretrained_models/asr-whisper-small"
    )
    return model_whisper

    asr_model = EncoderDecoderASR.from_hparams(source="./models/pretrained_ASR")
    return asr_model

def transcribe_audio(fname="example2.wav", start_times=[], end_times=[], use_timestamps=True):

    asr_model = init_asr_model()
    print(f"Transcribing audio... {fname}")

    if (fname.startswith('http://') or fname.startswith('https://')):
        #download first
        fname = download_file(fname)



#    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-conformer-transformerlm-librispeech", savedir="./models/pretrained_models/asr-transformer-transformerlm-librispeech")
    if (fname.endswith('.mp4')):
        #convert to wav first
        fname = convert_mp4_to_wav(fname)

    if (use_timestamps and len(start_times) > 0 and len(end_times) > 0 and len(start_times) == len(end_times)):
        full_transcript = ""
        for i in range(len(start_times)):
            segment_fname = f'segment_{i}.wav'
            #extract segment
            samplerate, data = wav.read(fname)
            st = 0
            if (i > 0):
                st = end_times[i-1]
            et = start_times[i]
            if (et <= st+4 or et > st+300): #min 5 sec segments, max 5 min segments
                print(f"Skipping invalid segment {st} to {et}")
                continue


            start_sample = int((st) * samplerate)
            end_sample = int((et) * samplerate)
            segment_data = data[start_sample:end_sample]
            wav.write(segment_fname, samplerate, segment_data)
            result  = asr_model.transcribe_file(segment_fname)
                # Process the words_with_timestamps list
                #for now just use segment time..
            if (len(result) > 8): #sometimes get garbage like "mm" or "dont" during silence..
                full_transcript += result + " (" + getTimeFromSecs(st) + ")\n"
        return full_transcript.strip()         
    else:   
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

