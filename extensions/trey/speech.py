import time
#pip install -q kokoro>=0.9.4 soundfile
#> espeak-ng.msi
#> pip install git+https://github.com/cheuerde/kokoro-tts-cli.git
#$$KOKORO_PATH=C:\devinpiano\music\models

import shutil

from kokoro import KPipeline
import soundfile as sf
import pygame
import os
import threading
from playsound3 import playsound

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
import queue
import winsound
import subprocess

import extensions.trey.synth as synth


import logging

logger = logging.getLogger(__name__)

asr_model = None
whisper_model = None
kokoro_pipeline = None

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


def wav_to_flac(wav_file, flac_file):
    """
    Converts a WAV file to a FLAC file using pydub.
    """
    if not os.path.exists(wav_file):
        print(f"Error: {wav_file} not found")
        return

    print(f"Converting {wav_file} to {flac_file}...")
    try:
        # Load the WAV file
        audio = AudioSegment.from_wav(wav_file)
        
        # Export as FLAC file (pydub automatically uses ffmpeg for the conversion)
        audio.export(flac_file, format="flac")
        print("Conversion successful!")
    except Exception as e:
        print(f"An error occurred: {e}")


def speech_load_feedback(allcmds):
    totalcmds = len(allcmds)
    numloaded = 0
    examples = {}
    words_dict = {}
    for c in allcmds:
      if (c['cmd'] == 'Record Feedback'):
        print(f'Found Record Feedback {c}')
        feedback = c['vars'].get('FEEDBACK', '')
        o = c['vars'].get('ORIGINAL', '')
        s = c['vars'].get('SCORE', '')
        f = c['vars'].get('FILE', '')
        print(f'Feedback: {feedback}\nOriginal: {o}\nScore: {s}\n')        
        #change file to flac for model.  
        flac_file = f.replace(".wav", ".flac")
        wav_to_flac(f, flac_file)

        numloaded += 1
        #use original assuming user actually read what was written..
        words = " ".join(o.split(" ")[1:])
        utt_id = Path(flac_file).stem
        words_dict[utt_id] = words
            
        
        examples[utt_id] = {"file_path": flac_file,
                            "words": words_dict[utt_id],
                            "spkID": "0",
                            "length": torchaudio.info(flac_file).num_frames}


    print(examples[list(examples.keys())[0]])

    logger.info(f'Loaded {numloaded} feedback from {totalcmds} commands')
    return examples

def speech_parse_to_json2(lang="hotkeys"):
    import languages.helpers.transcriber as transcriber
    trans = transcriber.Transcriber()
    allcmds = trans.read(lang, None, None) #default 7 days
    logger.info(f'Loaded {len(allcmds)} command transcripts for {lang}')
    #filter commands for > Record Feedback

    #filter commands for bookmarks.  
    examples = speech_load_feedback(allcmds)
    if (len(examples) > 0):
        out = 'feedback_data.json'
        with open(out, "w") as f:
            import json
            json.dump(examples, f, indent=4)
        logger.info(f'Saved feedback data to {out}')
        return out


    return ""

def speech_parse_to_json(basedir="../testing/data/mini_librispeech/LibriSpeech/", type="dev-clean-2", out='data.json'):
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

def speech_train_model():
    #set up JSON files for training.  
    global asr_model

    asr_model = EncoderDecoderASR.from_hparams(source="./models/pretrained_ASR", savedir="./models/pretrained_ASR", hparams_file="hyperparams.yaml")    
#    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech", savedir="./models/pretrained_ASR", hparams_file="hyperparams.yaml")
    fname = speech_parse_to_json()
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

global recording
global rec_stop_event
rec_stop_event = threading.Event()

global audio_queue
audio_queue = queue.Queue()

# Audio settings
STEP_IN_SEC: int = 1    # We'll increase the processable audio data by this
LENGHT_IN_SEC: int = 6    # We'll process this amount of audio data together maximum
NB_CHANNELS = 1
RATE = 16000
CHUNK = RATE
MAX_SENTENCE_CHARACTERS = 80


import re
def transcribe_now():
    global rec_stop_event
    global recording
    global audio_queue
    global whisper_model

    whisper_model = init_whisper_model()
    working_buffer = b""
    if (audio_queue.empty()):
        return ""
    audio_data = []
    while (not audio_queue.empty()):
        audio_data.append(audio_queue.get())
    working_buffer = np.concatenate(audio_data).astype(np.float32)

    transcription_start_time = time.time()

    # convert the bytes data toa  numpy array
    audio_data_array: np.ndarray = np.frombuffer(working_buffer, np.float32)
    # audio_data_array = np.expand_dims(audio_data_array, axis=0)

    segments, _ = whisper_model.transcribe(audio_data_array,
                                        language=WHISPER_LANGUAGE,
                                        beam_size=5,
                                        vad_filter=True,
                                        vad_parameters=dict(min_silence_duration_ms=1000))
    segments = [s.text for s in segments]

    transcription_end_time = time.time()

    transcription = " ".join(segments)
    # remove anything from the text which is between () or [] --> these are non-verbal background noises/music/etc.
    transcription = re.sub(r"\[.*\]", "", transcription)
    transcription = re.sub(r"\(.*\)", "", transcription)
    # We do this for the more clean visualization (when the next transcription we print would be shorter then the one we printed)
    transcription = transcription.ljust(MAX_SENTENCE_CHARACTERS, " ")

    transcription_postprocessing_end_time = time.time()

    print(transcription, end='\r', flush=True)

    audio_queue.task_done()
    print(f"Transcription: {transcription}")
    print(f"Transcription time: {transcription_end_time - transcription_start_time:.2f} seconds")
    return transcription



def record_audio_callback(indata, frames, time, status):
    global recording, rec_stop_event, audio_queue
#    print("Hello from callback")
    if status:
        print(status)
    # Check if the stop event has been set
    if rec_stop_event.is_set():
        raise sd.CallbackStop # Stops the stream gracefully from within the callback
    recording.append(indata.copy())
    audio_queue.put(indata.copy())

def record_audio2(duration=30, fname="example.wav", stop_event=None, seq=[77, 81, 84, 89]):
    #no easy way to stop early with sounddevice, so just record fixed time for now.
    global recording
    samplerate = 16000  # Sample rate (Hz)
    print("Recording...")
#    logger.info("Recording...")
    from pycaw.pycaw import AudioUtilities
    device = AudioUtilities.GetSpeakers()
#    winsound.Beep(2000, 200) #beep to start
    synth.play_synth(seq, 12) #C major chord to start
    volume = device.EndpointVolume
    currentvolume = volume.GetMasterVolumeLevel()
    volume.SetMasterVolumeLevel(currentvolume-20, None) #reduce output volume to 20% for recording.
    total_duration = 0
    """
    consumer = threading.Thread(target=consumer_thread, args=())
    consumer.start()

    try:
        consumer.join()
    except Exception as e:
        print(f"Error in consumer thread: {e}")

    """

    with sd.InputStream(samplerate=samplerate, channels=1, callback=record_audio_callback, blocksize=samplerate): #blocksize is how often the callback is called, set to 1 second of audio.
        # This loop runs as long as the stream is active
        while not stop_event.is_set():
#            time.sleep(0.1)
            total_duration += 0.1
            if total_duration >= duration:
                if (not stop_event.set()):
                    stop_event.set()
                else:
                    break #never make it here?  
            sd.sleep(100)  # Sleep briefly to allow other operations
    print("Recording completeA.")
#    logger.info("Recording complete.")
    recording = np.concatenate(recording, axis=0)
    audio_tensor = torch.from_numpy(recording.squeeze()) # Remove channel dimension if mono
#    audio_tensor = torch.from_numpy(recording.squeeze()) # Remove channel dimension if mono
    #triple volume.  
#    recording = recording * 3
    wav.write(fname, samplerate, (recording * 32767).astype(np.int16)) # Save as int16 WAV file

    volume.SetMasterVolumeLevel(currentvolume, None) #return to normal volume.  

#    winsound.Beep(1000, 200) #beep to end
    synth.play_synth(seq) #C major chord to start
    return fname



def get_duration(fname):
    samplerate, data = wav.read(fname)
    duration = data.shape[0] / samplerate
    return int(duration)

#default 10 seconds for comment
def record_audio(duration=10, fname="example.wav", stop_event=None, seq=[77,81,84,89]):
    samplerate = 16000  # Sample rate (Hz)
    #no easy way to stop early with sounddevice, so just record fixed time for now.
    print("Recording...")
    logger.info("Recording...")
    from pycaw.pycaw import AudioUtilities
    device = AudioUtilities.GetSpeakers()
    volume = device.EndpointVolume
    currentvolume = volume.GetMasterVolumeLevel()
    volume.SetMasterVolumeLevel(currentvolume-20, None) #reduce volume to 20% for recording.
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='float32')
    synth.play_synth(seq, 12) #C major chord to start
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    audio_tensor = torch.from_numpy(recording.squeeze()) # Remove channel dimension if mono
    wav.write(fname, samplerate, (recording * 32767).astype(np.int16)) # Save as int16 WAV file

    volume.SetMasterVolumeLevel(currentvolume, None) #return to normal volume.  

    synth.play_synth(seq) #C major chord to start
    return fname

def listen_audio(duration=30, fname="example.wav", seq=[77,81,84,89]): #default C major chord
    if os.path.exists(fname):
        os.remove(fname)
    global rec_stop_event
    global recording
    rec_stop_event = threading.Event()
    recording = []
    rec_stop_event.clear()
    audio_thread = threading.Thread(target=record_audio2, args=(duration, f'{fname}', rec_stop_event, seq))
#    audio_thread = threading.Thread(target=record_audio2, args=(duration, f'{fname}', rec_stop_event, seq, qr_queue))
    audio_stop_event = threading.Event()  # Event to signal stopping
#    audio_thread = threading.Thread(target=record_audio, args=(duration, f'{fname}', audio_stop_event))
    audio_thread.start()
#    time.sleep(3)
#    rec_stop_event.set()  # Signal the recording thread to stop


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
    """
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
    """
    global asr_model
    if (asr_model is not None):
        return asr_model
    print(f"Loading ASR model...")
    asr_model = EncoderDecoderASR.from_hparams(source="./models/pretrained_ASR")
    return asr_model


# Whisper settings
WHISPER_LANGUAGE = "en"
WHISPER_THREADS = 4
from faster_whisper import WhisperModel

def init_whisper_model():
    global whisper_model
    if (whisper_model is not None):
        return whisper_model
    print(f"Loading Whisper model...")
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8", cpu_threads=WHISPER_THREADS)
    return whisper_model


def get_speech_(fname):
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
    (get_speech_timestamps, _, read_audio, _, _) = utils

    wav = read_audio(fname, sampling_rate=16000)
    speech_timestamps = get_speech_timestamps(
    wav,
    model,
    return_seconds=True,  # Return speech timestamps in seconds (default is samples)
    )


def transcribe_audio_whisper(fname="example2.wav", start_times=[], end_times=[], use_timestamps=False):
    global whisper_model, recording
    global rec_stop_event, asr_model
    print("Stopping any existing audio recording...")
    logger.info("Stopping any existing audio recording...")
    rec_stop_event.set() #stop any existing recording
    time.sleep(0.3) #give time to stop

    whisper_model = init_whisper_model()
    #sd.stop() #stop any existing playback/recording
    print(f"Transcribing audio... {fname}")
    logger.info(f"Transcribing audio... {fname}")

    if (fname.startswith('http://') or fname.startswith('https://')):
        #download first
        fname = download_file(fname)



#    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-conformer-transformerlm-librispeech", savedir="./models/pretrained_models/asr-transformer-transformerlm-librispeech")
    if (fname.endswith('.mp4')):
        #convert to wav first
        fname = convert_mp4_to_wav(fname)

    full_transcript = ""
    if (use_timestamps):
        if (len(start_times) > 0 and len(end_times) > 0 and len(start_times) == len(end_times)):
            print(f"Starting Transcription.. {len(start_times)} segments found.")
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


#                speech_stamps = get_speech_(segment_fname)
#                print(f"Segment {i}: {st} to {et}, speech timestamps: {speech_stamps}")
                start_sample = int((st) * samplerate)
                end_sample = int((et) * samplerate)
                segment_data = data[start_sample:end_sample]
                wav.write(segment_fname, samplerate, segment_data)
                result  = whisper_model.transcribe_file(segment_fname)
                    # Process the words_with_timestamps list
                    #for now just use segment time..
                if (len(result) > 8): #sometimes get garbage like "mm" or "dont" during silence..
                    full_transcript += result + " (" + getTimeFromSecs(st) + ")\n"
        return full_transcript.strip()         

    if (os.path.exists(fname)):
        segments, info = whisper_model.transcribe(fname, beam_size=5)
    else:
        recording = np.concatenate(recording, axis=0)
        audio_data = np.frombuffer(recording, np.float32)
        segments, info = whisper_model.transcribe(audio_data, language=WHISPER_LANGUAGE, beam_size=5, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=1000))

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        full_transcript += segment.text + " (" + getTimeFromSecs(int(segment.start)) + ")\n"
    return full_transcript.strip()



def transcribe_audio(fname="example2.wav", start_times=[], end_times=[], use_timestamps=False):
    global rec_stop_event, asr_model
    print("Stopping any existing audio recording...")
    logger.info("Stopping any existing audio recording...")
    rec_stop_event.set() #stop any existing recording
    time.sleep(0.3) #give time to stop

    asr_model = init_asr_model()
    #sd.stop() #stop any existing playback/recording
    print(f"Transcribing audio... {fname}")
    logger.info(f"Transcribing audio... {fname}")

    if (fname.startswith('http://') or fname.startswith('https://')):
        #download first
        fname = download_file(fname)



#    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-conformer-transformerlm-librispeech", savedir="./models/pretrained_models/asr-transformer-transformerlm-librispeech")
    if (fname.endswith('.mp4')):
        #convert to wav first
        fname = convert_mp4_to_wav(fname)

    if (use_timestamps):
        full_transcript = ""
        if (len(start_times) > 0 and len(end_times) > 0 and len(start_times) == len(end_times)):
            print(f"Starting Transcription.. {len(start_times)} segments found.")
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


                speech_stamps = get_speech_(segment_fname)
                print(f"Segment {i}: {st} to {et}, speech timestamps: {speech_stamps}")
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
        if (not os.path.exists(fname)):
            print(f"!! {fname} not found.")
            logger.error(f"!! {fname} not found.")
            return ""
        result = asr_model.transcribe_file(fname)
        #result = asr_model.transcribe_file("speechbrain/asr-conformer-transformerlm-librispeech/example.wav")
        print(result)
        return result


def set_volume(fname="example_tts.wav", volume=1.0):
    # Load the audio file
    samplerate, data = wav.read(fname)

    # Adjust the volume
    adjusted_data = (data * volume).astype(np.int16)

    # Save the adjusted audio back to a file
    wav.write(fname, samplerate, adjusted_data)
    return fname

def speak_cmd(text="", fname="example_tts.wav", voice='af_heart', vol=1.0, speed=1.0, skip=0, engine='kokoro-tts'):
#    thread1 = threading.Thread(target=speak, args=(f'{text}',f'{fname}',f'{voice}',vol,speed,'kokoro-tts'))
#    thread1.start()
    #why we have to do this.. if we call directly it is far too slow..
    infile = ""
    if (fname == ""):
        #special case for generating all
        infile = f"./temp/tts_{int(time.time())}.txt"
        with open(infile, "w", encoding="utf-8") as f:
            f.write(text)
        cmd = f'python ./generate/generatetts.py --infile "{infile}" --fname "{fname}" --voice "{voice}" --vol {vol} --speed {speed} --skip {skip} --engine {engine}'
        subprocess.Popen(
            cmd,
            shell=True
        )
        suc = ""
                
        #suc = os.system(cmd)
    else:
        suc = os.system(f'python ./generate/generatetts.py --text "{text}" --fname "{fname}" --voice "{voice}" --vol {vol} --speed {speed} --skip {skip} --engine {engine}')
#    thread1.join() #wait for completion..
    if (suc == 0):
        return fname
    else:
        return ""
#    return speak(text, fname, voice, vol, speed)


def get_kokoro_pipeline():
    global kokoro_pipeline
    if (kokoro_pipeline is not None):
        return kokoro_pipeline
    print(f"Loading Kokoro pipeline...")
    num_devices = torch.cuda.device_count()
    device_names = [torch.cuda.get_device_name(i) for i in range(num_devices)]
    print(f"Available CUDA devices: {device_names}")

    kokoro_pipeline = KPipeline(lang_code='a',device='cuda:0') 
    print(f"Kokoro pipeline loaded.")
    return kokoro_pipeline

def speak(text="", fname="example_tts.wav", voice='af_heart', vol=1.0, speed=1.0, engine='kokoro-tts'):
    # Initialize pipeline (lang_code 'a' for American English)
    try:
        pipeline = get_kokoro_pipeline()
        if (text == ""):
            text = "Kokoro is a lightweight and natural text-to-speech model."


        # Generate and save audio
        generator = pipeline(text, voice=voice, speed=speed)
        with sf.SoundFile(fname, mode='w', samplerate=24000, channels=1) as f:
            for i, (gs, ps, audio) in enumerate(generator):
    #            sf.write(f'kokoro_{i}.wav', audio, 24000)    
                f.seek(0, sf.SEEK_END)  # Move to the end of the file for appending
                adjusted_data = (audio * vol)
                f.write(adjusted_data)  # Append the adjusted audio data to the file
        print(f"Audio saved to '{fname}'")
        return fname #return first segment for now
    except Exception as e:
        print(f"Error in speak function: {e}")
        return ""

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

