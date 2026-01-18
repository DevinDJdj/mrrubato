#list details of recorded data..
#create JSON file with snippets of recorded data for training
import os
import json
from glob import glob
from scipy.io import wavfile
from pydub import AudioSegment
from tinytag import TinyTag
from datetime import datetime
from pymediainfo import MediaInfo
#> pip install mutagen
#> pip install pydub
#> pip install pymediainfo


def get_media_created_date(file_path):
    """
    Retrieves the media creation date from an MP4 file using mutagen.
    """
    try:
        # Open the MP4 file
#        mp4_file = TinyTag.get(file_path)
#        print(mp4_file.as_dict())
        media_info = MediaInfo.parse(file_path)
#        print(media_info.to_data())
        print(media_info.tracks[0].encoded_date)

        # The 'creation_time' attribute contains the date/time in UTC
        # It's a datetime.datetime object
        creation_date = media_info.tracks[0].encoded_date

        if creation_date:
            print(f"Media created date (UTC): {creation_date}")
            # You can convert it to a different timezone if needed, for example local time
            # local_creation_date = creation_date.astimezone(datetime.timezone.natime())
            # print(f"Media created date (Local): {local_creation_date}")
            input_format = "%Y-%m-%d %H:%M:%S %Z"
            datetime_object = datetime.strptime(creation_date, input_format)
            output_format = "%Y%m%d%H%M%S"
            formatted_string = datetime_object.strftime(output_format)
            return formatted_string
        else:
            print("No media creation date found in metadata.")
            return None

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def convert_m4a_to_wav(m4a_file_path, wav_file_path):
    """
    Converts an M4A audio file to a WAV format file using pydub.

    Args:
        m4a_file_path (str): The path to the input .m4a file.
        wav_file_path (str): The path for the output .wav file.
    """
    if not os.path.exists(m4a_file_path):
        print(f"Error: Input file not found at {m4a_file_path}")
        return

    print(f"Starting conversion of {m4a_file_path}...")
    try:
        # Load the m4a file
        sound = AudioSegment.from_file(m4a_file_path, format="m4a")

        # Export the file to wav format
        sound.export(wav_file_path, format="wav")
        
        print(f"Successfully converted to {wav_file_path}")

    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        print("Please ensure ffmpeg is correctly installed and accessible in your system's PATH.")


def get_spoken_words(summary_text):
    words = [[] for _ in range(10)]
    wordidx = [-1] * 10
    speaker_num = -1
    prev_speaker = -1

    if summary_text:
        lines = summary_text.splitlines()
        for line in lines:
            if (speaker_num > -1 and speaker_num < 10):
                prev_speaker = speaker_num
            if line.startswith("Speaker "):
                line = line.replace("Speaker ", "").strip()
                sn = line.split(' ')[0]
                speaker_num = int(sn) #assume less than 10 speakers..
                line = line[2:]
            line = line.strip()
            if (speaker_num < 0) or (speaker_num > 9):
                continue
            if len(line) == 5 and line[2] == ':' and line[0:2].isdigit() and line[3:5].isdigit():
                #assume timestamp
                time = line[0:5]
                #convert to seconds
                minutes = int(line[0:2])
                seconds = int(line[3:5])
                total_seconds = minutes * 60 + seconds                
                if (prev_speaker > -1 and wordidx[prev_speaker] > -1):
                    words[prev_speaker][ wordidx[prev_speaker] ]['end_time'] = total_seconds
                wordidx[speaker_num] += 1
                words[speaker_num].append( {} )
                words[speaker_num][ wordidx[speaker_num] ]['start_time'] = total_seconds
                words[speaker_num][ wordidx[speaker_num] ]['words'] = ""
            elif(len(line) == 7 and line[1] == ':' and line[4] == ':'and line[0:1].isdigit() and line[2:4].isdigit() and line[5:7].isdigit()):
                #assume timestamp with space after, hour:min:sec, nothing over 10 hours..
                hours = int(line[0:1])
                minutes = int(line[2:4])
                seconds = int(line[5:7])
                total_seconds = hours * 3600 + minutes * 60 + seconds                
                if (prev_speaker > -1 and wordidx[prev_speaker] > -1):
                    words[prev_speaker][ wordidx[prev_speaker] ]['end_time'] = total_seconds
                wordidx[speaker_num] += 1
                words[speaker_num].append( {} )
                words[speaker_num][ wordidx[speaker_num] ]['start_time'] = total_seconds
                words[speaker_num][ wordidx[speaker_num] ]['words'] = ""     
            else:
                words[speaker_num][ wordidx[speaker_num] ]['words'] += "\n" + line.strip()

    #for now just return the words of the primary speaker
    #get longest list
    primary_speaker = 1
    for i in range(1,10):
        if len(words[i]) > len(words[primary_speaker]):
            primary_speaker = i

    return words[primary_speaker]

def prepare_recorder_data(data_folder, json_path, force=False):
    #create training data from google recorder app data, 
    #for sample, just assuming they got it right..
    #a lot of this is still wrong, but it's a start to get at least a TTS assimilated to the voice.
    data = []
    m4a_files = glob(os.path.join(data_folder, '**', '*.m4a'), recursive=True)
    
    for m4a_file in m4a_files:
        # Convert M4A to WAV
        wav_file = m4a_file.replace('.m4a', '.wav')
        if not os.path.exists(wav_file) or force:
            convert_m4a_to_wav(
                m4a_file,
                wav_file
            )
        sample_rate, signal = wavfile.read(wav_file)
        duration = len(signal) / sample_rate

        #get date created
        created_str = get_media_created_date(m4a_file)
        print(f"Created date: {created_str}")
        print(wav_file)

        if duration < 1.0:
            continue
        
        # Get relative path and uttid
        path_parts = m4a_file.split(os.path.sep)
        uttid, _ = os.path.splitext(path_parts[-1])
        
        summary_text_path = os.path.join(
            "/", *path_parts[:-1], uttid + "_summary.txt"
        )
        
        try:
            with open(summary_text_path, encoding="utf-8") as f:
                summary_text = f.read()
        except FileNotFoundError:
            continue
        
        #get primary speaker text only
        mywords = get_spoken_words(summary_text)

        entry = {
            "uttid": uttid,
            "wav": wav_file,
            "created": created_str,
            "duration": duration,
            "text": summary_text.strip(),
            "words": mywords
        }
        
        data.append(entry)
    
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

if (__name__ == "__main__"):
    #use speechvenv
    data_folder = '/mnt/c/private/Recorder'
    json_path = '/mnt/c/private/recorder_data.json'
    prepare_recorder_data(data_folder, json_path)

    print(f"Data preparation completed. JSON file saved at {json_path}")