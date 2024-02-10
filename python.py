import pyaudio
import wave
import speech_recognition as sr

def record_audio(filename, duration):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=format, channels=channels,
                        rate=rate, input=True,
                        frames_per_buffer=chunk)

    print("Recording...")

    frames = []

    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(filename):
    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def summarize_text(text):
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
    filename = "recorded_audio.wav"
    duration = 2  # seconds

    record_audio(filename, duration)
    text = transcribe_audio(filename)
    audio_blobs = summarize_text(text)

    print("Audio Blobs:")
    for idx, blob in enumerate(audio_blobs):
        print(f"Blob {idx+1}: {blob}")

if __name__ == "__main__":
    main()
