import assemblyai as aai
from better_profanity import profanity
import os
from pydub import AudioSegment
import imageio_ffmpeg
import ffmpeg
import httpcore
import time
import librosa
import numpy as np

def transcribe_audio(audio_url, api_key):
    aai.settings.api_key = api_key
    transcriber = aai.Transcriber(config=aai.TranscriptionConfig(filter_profanity=True))
    try:
        transcript = transcriber.transcribe(audio_url)
    except httpcore.WriteTimeout:
        print("Write timeout occurred. Retrying after 5 seconds...")
        time.sleep(5)
        transcript = transcriber.transcribe(audio_url)
    while transcript.status != 'completed':
        transcript = transcriber.get_transcription(transcript.id)
    
    # Normalize timings
    max_time = max(word.end for word in transcript.words)
    for word in transcript.words:
        word.start = (word.start / max_time) * 297  # 297 seconds is the duration of the audio
        word.end = (word.end / max_time) * 297

    print("First 5 words of transcript (after normalization):")
    for i, word in enumerate(transcript.words[:5]):
        print(f"Word: {word.text}, Start: {word.start:.3f}, End: {word.end:.3f}")
    
    return transcript

def censor_profanity(transcript):
    censored_text = profanity.censor(transcript.text)
    return censored_text

def load_audio_file(audio_url, ffmpeg_path):
    try:
        audio = AudioSegment.from_file(audio_url, format="mp3")
        print("Audio loaded successfully")
        return audio
    except Exception as e:
        print(f"Error loading audio: {e}")
        # If loading fails, try to print more info about the file
        import subprocess
        result = subprocess.run([ffmpeg_path, "-i", audio_url], capture_output=True, text=True)
        print("FFmpeg output:", result.stderr)
        return None

def split_audio_into_segments(audio, transcript):
    audio_segments = []
    for word in transcript.words:
        start_time = max(0, int(word.start * 1000))
        end_time = min(len(audio), int(word.end * 1000))
        if start_time < end_time:
            segment = audio[start_time:end_time]
            audio_segments.append(segment)
            print(f"Word: {word.text}, Start: {start_time}, End: {end_time}, Duration: {len(segment)} ms")
        else:
            print(f"Skipping word: {word.text} due to invalid timing (start: {start_time}, end: {end_time})")
    print(f"Split {len(audio_segments)} segments. Total duration: {sum(len(seg) for seg in audio_segments)} ms")
    return audio_segments

def create_silent_segment(duration, frame_rate=44100, sample_width=2, channels=2):
    """Create a silent audio segment with the given duration."""
    print(f"Creating silent segment with duration: {duration} seconds")
    if duration <= 0:
        print(f"Warning: Attempting to create silent segment with non-positive duration: {duration}")
        duration = 0.001  # Set a minimum duration of 1 millisecond
    samples = int(duration * frame_rate * sample_width * channels)
    if samples == 0:
        samples = frame_rate * sample_width * channels // 1000  # Minimum 1 ms of silence
    silent_segment = AudioSegment(
        data=b"\x00" * samples,
        frame_rate=frame_rate,
        sample_width=sample_width,
        channels=channels,
    )
    print(f"Created silent segment with duration: {len(silent_segment)} ms")
    return silent_segment

def replace_profanity_with_silence(audio_segments, transcript, censored_text):
    censored_segments = []
    censored_words = censored_text.split()
    for i, segment in enumerate(audio_segments):
        if i < len(censored_words) and '*' in censored_words[i]:
            silent_segment = AudioSegment.silent(duration=len(segment))
            censored_segments.append(silent_segment)
        else:
            censored_segments.append(segment)
    print(f"Replaced {len(censored_segments)} segments. Total duration: {sum(len(seg) for seg in censored_segments)} ms")
    return censored_segments
    
    
def combine_segments_into_single_audio(censored_segments, original_duration):
    censored_audio = sum(censored_segments, AudioSegment.empty())
    if len(censored_audio) < original_duration:
        silence = AudioSegment.silent(duration=original_duration - len(censored_audio))
        censored_audio += silence
    print(f"Combined audio duration: {len(censored_audio)} ms")
    return censored_audio


def main():
    audio_url = "song.mp3"
    api_key = "api_key"
    ffmpeg_path = "ffmpeg.exe"
    print(f"FFmpeg path: {ffmpeg_path}")

    # Set FFmpeg path for pydub
    AudioSegment.converter = ffmpeg_path
    os.environ["FFMPEG_BINARY"] = ffmpeg_path

    # Create a new folder for the clean audio file
    clean_folder = "clean_audio"
    if not os.path.exists(clean_folder):
        os.makedirs(clean_folder)

    # Transcribe the audio file
    print("Transcribing audio...")
    transcript = transcribe_audio(audio_url, api_key)
    print(f"Transcription complete. Number of words: {len(transcript.words)}")

    # Censor the transcript text
    print("Censoring transcript...")
    censored_text = censor_profanity(transcript)
    print(f"Censoring complete. Censored text length: {len(censored_text)}")

    # Load the original audio file
    print("Loading audio file...")
    audio = load_audio_file(audio_url, ffmpeg_path)
    if audio is None:
        print("Error loading audio file")
        return
    print(f"Audio loaded. Duration: {len(audio)} ms ({len(audio)/1000:.2f} seconds)")

    # Split the audio into segments
    print("Splitting audio into segments...")
    audio_segments = split_audio_into_segments(audio, transcript)
    print(f"Splitting complete. Number of segments: {len(audio_segments)}")

    # Replace profanity with silence
    print("Replacing profanity with silence...")
    censored_segments = replace_profanity_with_silence(audio_segments, transcript, censored_text)
    print(f"Replacement complete. Number of censored segments: {len(censored_segments)}")

    # Combine the segments into a single audio file
    print("Combining segments into single audio...")
    censored_audio = combine_segments_into_single_audio(censored_segments,len(audio))
    print(f"Combination complete. Censored audio length: {len(censored_audio)} ms")

    # Export the censored audio to the new folder
    censored_audio_file = f"{clean_folder}/clean_audio1.wav"
    print(f"Exporting censored audio to {censored_audio_file}...")
    censored_audio.export(censored_audio_file, format="wav")

    print(f"Clean audio file saved to {censored_audio_file}")
    print(f"Censored text: {censored_text[:100]}...")  # Print first 100 characters

if __name__ == "__main__":
    main()