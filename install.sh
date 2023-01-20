#!/bin/bash
sudo pacman -Sy python
sudo steamos-readonly disable
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py
export PATH="$PATH:/home/deck/.local/bin"
source ~/.bashrc
pip install -r requirements.txt
sudo steamos-readonly enable