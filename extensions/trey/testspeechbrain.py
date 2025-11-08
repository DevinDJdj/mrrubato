#> pip install speechbrain
#> pip install sounddevice
from speechbrain.inference import EncoderDecoderASR
import speechbrain as sb
import sounddevice as sd
import numpy as np
import torch
import scipy.io.wavfile as wav
import json
#from parse_data import parse_to_json

asr_model = None

def parse_to_json(basedir="../testing/speechbrain/templates/speech_recognition/mini_librispeech/LibriSpeech/", type="dev-clean-2", out='data.json'):
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


def train_tts():
    #train text to speech model.  
#    tts_model = sb.inference.TTS.Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="./models/pretrained_tts")
    tts_model = sb.inference.TTS.Tacotron2.from_hparams(source="./models/pretrained_tts", savedir="./models/pretrained_tts")
    


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



def transcribe_audio(fname):

    asr_model = EncoderDecoderASR.from_hparams(source="./models/pretrained_ASR")
#    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-conformer-transformerlm-librispeech", savedir="./models/pretrained_models/asr-transformer-transformerlm-librispeech")
    result = asr_model.transcribe_file("example2.wav")
    #result = asr_model.transcribe_file("speechbrain/asr-conformer-transformerlm-librispeech/example.wav")
    print(result)




def generate_audio(text="Mary had a little lamb."):
    # Load pretrained models for text-to-spectrogram (Tacotron2) and spectrogram-to-waveform (HiFiGAN).
    tacotron2 = sb.inference.TTS.Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="./models/pretrained_tts")
    hifi_gan = sb.inference.vocoders.HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="./models/pretrained_vocoder")

    # Define the text input.

    # Convert text to a mel-spectrogram using Tacotron2.
    mel_output, mel_length, alignment = tacotron2.encode_text(text)

    # Convert the mel-spectrogram to an audio waveform using HiFiGAN.
    waveforms = hifi_gan.decode_batch(mel_output)

    # Save the resulting audio waveform to a file.
#    torchaudio.save('example_tts.wav', waveforms.squeeze(1), 22050)
    samplerate = 22050
    scaled = np.int16(waveforms.squeeze() * 32767)
    wav.write("example_tts.wav", samplerate, scaled) # Save as int16 WAV file

    print("Audio saved to 'example_tts.wav'")



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



from speechbrain.lobes.features import Fbank
import torch

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
    
if (__name__ == "__main__"):

    samplerate = 16000  # Sample rate (Hz)
    duration = 5       # Recording duration (seconds)

    print("Recording...")
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    audio_tensor = torch.from_numpy(recording.squeeze()) # Remove channel dimension if mono
    wav.write("example2.wav", samplerate, (recording * 32767).astype(np.int16)) # Save as int16 WAV file

    transcribe_audio("example2.wav")

    generate_audio("This is a test of the text to speech system.")


    #train_model()



    #parse_to_json(type="train-clean-5", out='train.json')
    #parse_to_json(type="test-clean", out='test.json')

    """
    source = sb.dataio.dataio.read_audio('example2.wav').squeeze()
    from speechbrain.lobes.models.huggingface_transformers.wav2vec2 import Wav2Vec2
    from speechbrain.lobes.models.huggingface_transformers.whisper import Whisper

    # HuggingFace model hub
    model_hub_w2v2 = "facebook/wav2vec2-base-960h"
    #model_hub_whisper = "openai/whisper-tiny"

    model_w2v2 = Wav2Vec2(model_hub_w2v2, save_path='/content/pretrained/')
    #model_whisper = Whisper(model_hub_whisper, save_path='/content/pretrained/')

    """