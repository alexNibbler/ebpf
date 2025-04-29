#!/bin/bash

echo "Installing packages..."
sudo apt update
sudo apt install -y bpfcc-tools linux-headers-$(uname -r) python3-pip python3-psutil
pip3 install bcc

echo "Run tracing application..."
sudo python3 trace_sys_read_write.py -t 5