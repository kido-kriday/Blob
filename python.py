import pyaudio
import wave
import speech_recognition as sr
import tkinter as tk
from threading import Thread

class AudioRecorder:
    def __init__(self, filename):
        self.filename = filename
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False

    def start_recording(self):
        self.stream = self.audio.open(format=self.format, channels=self.channels,
                                      rate=self.rate, input=True,
                                      frames_per_buffer=self.chunk)
        self.is_recording = True
        self.frames = []

        print("Recording...")

        while self.is_recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def stop_recording(self):
        if self.is_recording:
            print("Finished recording.")
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recorder")
        self.filename = "recorded_audio.wav"
        self.recorder = AudioRecorder(self.filename)
        self.recording_thread = None

        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.text_widget = tk.Text(self.root, wrap=tk.WORD, height=10, width=50)
        self.text_widget.pack(pady=10)

    def start_recording(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.recording_thread = Thread(target=self.recorder.start_recording)
        self.recording_thread.start()

    def stop_recording(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.recorder.stop_recording()

        # Once recording stops, transcribe audio and summarize
        text = self.transcribe_audio()
        audio_blobs = self.summarize_text(text)

        print("Audio Blobs:")
        for idx, blob in enumerate(audio_blobs):
            self.text_widget.insert(tk.END, f"Blob {idx + 1}: {blob}\n")
            self.text_widget.see(tk.END)  # Scroll to the end of the text widget

    def transcribe_audio(self):
        recognizer = sr.Recognizer()

        with sr.AudioFile(self.filename) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

    def summarize_text(self, text):
        # Split text into sentences
        sentences = text.split('.')

        # Remove empty strings
        sentences = [s.strip() for s in sentences if s.strip()]

        # Create 2-second audio blobs
        audio_blobs = []
        current_blob = ""
        for sentence in sentences:
            if len(current_blob) + len(sentence) + 1 <= 160:
                current_blob += sentence + ". "
            else:
                audio_blobs.append(current_blob)
                current_blob = sentence + ". "
        audio_blobs.append(current_blob)

        return audio_blobs

def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
