from setuptools import setup, find_packages

setup(
    name="audio_recorder_k",
    version="0.1.0",
    author="Keshab Kumar",
    description="A simple Python library for recording audio",
   long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Keshab-Kumar/audio_recorder",
    packages=find_packages(),
    install_requires=["pyaudio"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
