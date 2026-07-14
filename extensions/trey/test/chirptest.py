import os
#pip install google-cloud-speech
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

import sys
sys.path.insert(0, 'c:/devinpiano/')
import config

MAX_AUDIO_LENGTH_SECS = 60 * 60


def run_batch_recognize():
  # Instantiates a client.
  client = SpeechClient(
      client_options=ClientOptions(
          api_endpoint="us-speech.googleapis.com",
      ),
  )

  # The output path of the transcription result.
  
  storagebucket = config.cfg['firebase']['fbconfig']['storageBucket']
  gcs_output_folder = f"gs://{storagebucket}/transcripts/test/transcripts"

  # The name of the audio file to transcribe:
  audio_gcs_uri = f"gs://{storagebucket}/transcripts/test/audio-files/segment_0.wav"

  configr = cloud_speech.RecognitionConfig(
      explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
        encoding="LINEAR16",
        sample_rate_hertz=16000,
        audio_channel_count=1
      ),
      features=cloud_speech.RecognitionFeatures(
          enable_word_time_offsets=True,
        ),
      model="chirp_3",
      language_codes=["auto"],
  )

  output_config = cloud_speech.RecognitionOutputConfig(
      gcs_output_config=cloud_speech.GcsOutputConfig(uri=gcs_output_folder),
  )

  files = [cloud_speech.BatchRecognizeFileMetadata(uri=audio_gcs_uri)]

  projectid = config.cfg['firebase']['fbsettings']['project_id']
  request = cloud_speech.BatchRecognizeRequest(
      recognizer=f"projects/{projectid}/locations/us/recognizers/_",
      config=configr,
      files=files,
      recognition_output_config=output_config,
  )
  operation = client.batch_recognize(request=request)

  print("Waiting for operation to complete...")
  response = operation.result(timeout=3 * MAX_AUDIO_LENGTH_SECS)
  print(response)

run_batch_recognize()