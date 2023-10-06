#!/bin/sh
# run in dev mode
 apt-get update
 apt-get install -y software-properties-common 
 add-apt-repository ppa:deadsnakes/ppa
 apt update
 apt install python3.9-distutils
 apt install -y python3.9
 update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2