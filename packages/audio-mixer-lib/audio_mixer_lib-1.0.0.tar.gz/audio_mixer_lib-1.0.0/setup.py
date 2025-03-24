from setuptools import setup, find_packages

setup(
    name="audio_mixer_lib",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A library to mix audio files using Pydub",
    packages=find_packages(),
    install_requires=[
        "pydub",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)