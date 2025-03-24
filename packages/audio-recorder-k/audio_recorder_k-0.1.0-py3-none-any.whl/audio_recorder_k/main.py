import os
import pyaudio
import wave

# Ensure the output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class AudioRecorder:
    def __init__(self, duration=5, sample_rate=44100, channels=2, output_file=None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration = duration
        self.format = pyaudio.paInt16  # 16-bit audio format
        self.chunk = 1024  # Buffer size
        self.output_file = output_file or os.path.join(OUTPUT_DIR, "recorded_audio.wav")

    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        print(f"Recording for {self.duration} seconds...")
        frames = []

        for _ in range(0, int(self.sample_rate / self.chunk * self.duration)):
            data = stream.read(self.chunk)
            frames.append(data)

        print("Recording complete. Saving file...")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save audio as a WAV file
        with wave.open(self.output_file, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

        print(f"Saved recording to {self.output_file}")

# Example usage
if __name__ == "__main__":
    recorder = AudioRecorder(duration=5)
    recorder.record()
