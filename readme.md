# Audio Censor

This Python script takes an audio file, transcribes the audio using the AssemblyAI API, censors any profanity found in the transcript, and creates a new audio file with the profanity replaced by silence.

## Features
- Transcribes audio using the AssemblyAI API
- Censors profanity in the transcript using the better_profanity library
- Splits the audio into segments based on the transcript
- Replaces the profanity segments with silence
- Combines the censored segments back into a single audio file
- Exports the censored audio to a new folder

## Requirements
- Python 3.6 or higher
- The following Python libraries:
  - `assemblyai`
  - `better_profanity`
  - `os`
  - `pydub`
  - `imageio_ffmpeg`
  - `ffmpeg`
  - `httpcore`
  - `time`
  - `librosa`
  - `numpy`
- An AssemblyAI API key
- FFmpeg installed and the path set in the `ffmpeg_path` variable

## Usage
1. Install the required Python libraries: `pip install -r requirements.txt`
2. Set the `audio_url`, `api_key`, and `ffmpeg_path` variables in the `main()` function.
3. Run the script: `python audio_censor.py`
4. The censored audio file will be saved in the `clean_audio` folder.

## Notes
- The script assumes the audio file is in MP3 format. If your audio file is in a different format, you may need to modify the `load_audio_file()` function.
- The script uses the `pydub` library to load and manipulate the audio file. Make sure you have FFmpeg installed and the path set correctly.
- The script creates a new folder called `clean_audio` to store the censored audio file.
- The script prints out various progress messages and the first 100 characters of the censored text.

Feel free to modify the script to fit your specific needs.
