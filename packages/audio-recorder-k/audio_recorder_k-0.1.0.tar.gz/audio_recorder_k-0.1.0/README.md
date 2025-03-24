# 🎙️ Audio Recorder - Python Library for Recording Audio  

[![PyPI version](https://badge.fury.io/py/audio-recorder.svg)](https://pypi.org/project/audio-recorder/)  
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Python Version](https://img.shields.io/badge/python-3.6+-brightgreen.svg)](https://www.python.org/)  

## 🚀 Introduction  
**Audio Recorder** is a simple and lightweight Python package that allows you to record audio and save it as a WAV file.  
Built using `pyaudio`, it provides a convenient way to capture audio with minimal setup.  

## 🎯 Features  
✅ Record audio using Python  
✅ Save recordings as WAV files  
✅ Adjustable recording duration and sample rate  
✅ Supports different audio channels  

## 📦 Installation  

### **1️⃣ Install from PyPI**  
```sh
pip install audio-recorder
2️⃣ Install from Source (GitHub)
sh
Copy
Edit
git clone https://github.com/Keshab-Kumar/audio_recorder.git
cd audio_recorder
pip install -e .
🎤 Usage
Basic Example
python
Copy
Edit
from audio_recorder import AudioRecorder

recorder = AudioRecorder(duration=5)  # Records for 5 seconds
recorder.record()  # Saves the recording in the "output" folder
Custom Settings
python
Copy
Edit
recorder = AudioRecorder(duration=10, sample_rate=48000, channels=1, output_file="output/custom_audio.wav")
recorder.record()
📂 Output
All recorded files will be stored in the output/ directory.

🛠 How It Works
1️⃣ Opens an audio input stream.
2️⃣ Records audio for the given duration.
3️⃣ Saves the audio as a .wav file in the output/ folder.

🐞 Troubleshooting
If you encounter issues with pyaudio, try installing it manually:

sh
Copy
Edit
pip install pipwin
pipwin install pyaudio
📝 License
This project is licensed under the MIT License.

🔗 Links
📂 GitHub: audio_recorder

📖 PyPI (after publishing): audio_recorder