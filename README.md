## About the application
The application is a user plan in python, working with ebpf via bcc. It was tested in GCP Compute Engine VMs with Ubuntu 24.10 and Debian 12. The application demonstrates:
- attaching kprobes to sys_read and sys_write
- reporting to stdout READ or WRITE, time of the hook execution, pid and command name. Data is passed from ebpf to the application via BPF_PERF_OUTPUT
- ability to pass pid and uid into ebpf via BPF_HASH to filter for report only events related to the specific process or specific user
## Installation instructions
1. Copy the repository to your Linux machine. You should get `install_and_start.sh` script, and several `*.py` files. Regarding `requirements.txt` - it is not a part of the default installation way, however it's a good practice for python applications to have dependencies listed there.
2. To install required dependencies and run the application:
```commandline
chmod +x install_and_start.sh
./install_and_start.sh
```
3. If you want to run the application without dependencies installation, run:
```commandline
sudo python3 app/trace_sys_read_write.py
```
## Running parameters
There are several parameters to customize the application usage.
   1. `-t, --time`: CLI parameter to set application running time in seconds.
   2. Environment variables `UID_TO_TRACE`, `PID_TO_TRACE`. If set, the application will only report sys_read and sys_write calls related to particular process and/or user
## Suggested test scenario
1. In one terminal window run:
```commandline
python3 simple_writer.py
```
This script gets user input and writes to `output.txt` file in the same location where script is.
2. In the second terminal window find the id of the running `simple_writer.py` python script.
```commandline
ps aux | grep simple_writer
```
3. Run application **(with sudo)** with this pid passed via environment variable:
```commandline
sudo PID_TO_TRACE=XXXX python3 trace_sys_read_write.py
```
Every time user enters the input for the `simple_writer.py` script, ebpf hook will be triggered and data will be printed in the application console output