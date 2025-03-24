# setup.py
import os
from setuptools import setup, find_packages

setup(
    name='audio_recorder_1',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'sounddevice',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'record-audio=audio_recorder.main:record_audio'
        ]
    },
    author='Your Name',
    description='A simple audio recording library.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/audio_recorder',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
