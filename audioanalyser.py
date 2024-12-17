import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import os

def extract_audio_from_video(video_file, audio_file):
    video = mp.VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(audio_file)

    print(f"Audio extracted and saved as {audio_file}")

def audio_to_text(audio_file):
    audio = AudioSegment.from_file(audio_file)
    wav_file = "temp_audio.wav"
    audio.export(wav_file, format="wav")
    recognizer = sr.Recognizer()

    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio_data)
            print("Audio to Text:")
            print(text)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

    os.remove(wav_file)

def main(video_file, audio_file="extracted_audio.mp3"):
    extract_audio_from_video(video_file, audio_file)
    audio_to_text(audio_file)

if __name__ == "__main__":
    video_file = "web.mp4"  
    main(video_file)