#!/bin/bash

echo "Installing packages..."
sudo apt update
sudo apt install -y bpfcc-tools linux-headers-$(uname -r) python3-bcc python3-psutil

echo "Run tracing application..."
sudo python3 trace_sys_read_write.py