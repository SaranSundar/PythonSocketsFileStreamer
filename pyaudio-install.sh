#!/bin/bash

# Installs the pyaudio module for python3
# Requires sudo! May have user confirmation prompts

sudo apt-get update
sudo apt-get -y install git
git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
sudo apt-get -y install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
cd pyaudio
sudo python3 setup.py install
