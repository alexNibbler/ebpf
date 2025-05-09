import time
from bcc import BPF
import logging
from enum import Enum
from ctypes import c_int

import config
from listener import Listener

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

def safe_attach(bpf: BPF, event_name: str, func_name: str) -> None:
    try:
        bpf.attach_kprobe(event=event_name, fn_name=func_name)
        logging.info(f"Attached function {func_name} to event {event_name}")
    except Exception as e:
        logging.info(f"Failed to attach {func_name} to {event_name}: {e}")

def safe_detach(bpf: BPF, event_name: str, func_name: str) -> None:
    try:
        bpf.detach_kprobe(event=event_name, fn_name=func_name)
        logging.info(f"Detached function {func_name} from event {event_name}")
    except Exception as e:
        logging.info(f"Failed to detach {func_name} from {event_name}: {e}")

def init_kprobes(bpf: BPF) -> None:
    # Attach kprobes, trying for both 32 and 64-bit systems with try-except
    # so would not crash due to wrong naming
    safe_attach(bpf, event_name="__x64_sys_read", func_name="trace_sys_read")
    safe_attach(bpf, event_name="sys_read", func_name="trace_sys_read")
    safe_attach(bpf, event_name="__x64_sys_write", func_name="trace_sys_write")
    safe_attach(bpf, event_name="sys_write", func_name="trace_sys_write")

def finalize_kprobes(bpf: BPF) -> None:
    # Detach kprobes for clean application exit
    safe_detach(bpf, event_name="__x64_sys_read", func_name="trace_sys_read")
    safe_detach(bpf, event_name="sys_read", func_name="trace_sys_read")
    safe_detach(bpf, event_name="__x64_sys_write", func_name="trace_sys_write")
    safe_detach(bpf, event_name="sys_write", func_name="trace_sys_write")


class InputParam(Enum):
    UID = 1
    PID = 2

def pass_input_params_to_ebpf(bpf: BPF) -> None:
    try:
        if config.UID_TO_TRACE != "-1":
            bpf["input_table"][c_int(InputParam.UID.value)] = c_int(int(config.UID_TO_TRACE))
    except ValueError:
        logging.warning(f"UID_TO_TRACE environment variable should be an non-negative integer.")
    try:
        if config.PID_TO_TRACE != "-1":
            bpf["input_table"][c_int(InputParam.PID.value)] = c_int(int(config.PID_TO_TRACE))
    except ValueError:
        logging.warning(f"PID_TO_TRACE environment variable should be an non-negative integer.")


b = BPF(src_file = config.EBPF_C_FILE_PATH)
pass_input_params_to_ebpf(bpf = b)
init_kprobes(b)

# creating a listener - thread that polls the PERF_BUFFER and prints results to stdout via callback
listener_thread = Listener(bpf = b)
logging.info("Tracing sys_read and sys_write... Ctrl+C to exit.")

try:
    listener_thread.start()

    if config.timeout > 0:
        # if cli parameter --time was passed to the application on start,
        # the app should terminate after that amount of seconds
        time.sleep(config.timeout)
        listener_thread.is_interrupted = True
        logging.info(f"Exit by timeout {config.timeout}s")

    # waiting for the listener to finish work
    while listener_thread.is_alive():
        listener_thread.join(timeout = 0.5)
except KeyboardInterrupt:
    # handle ctrl+C
    print("Exiting main thread...")
finally:
    listener_thread.is_interrupted = True
    listener_thread.join()
    finalize_kprobes(b)
