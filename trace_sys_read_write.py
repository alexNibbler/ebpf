import time
from bcc import BPF
import logging

import config
from ebpf_program import ebpf_program_text
from listener import Listener

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

def safe_attach(bpf: BPF, event_name: str, func_name: str) -> None:
    try:
        bpf.attach_kprobe(event=event_name, fn_name=func_name)
        logging.debug(f"Attached function {func_name} to event {event_name}")
    except Exception as e:
        logging.warning(f"Failed to attach to {event_name}: {e}")

def init_kprobes(bpf: BPF) -> None:
    # Attach kprobes, trying for both 32 and 64-bit systems with try-except
    # so would not crash due to wrong naming
    safe_attach(bpf, event_name="__x64_sys_read", func_name="trace_sys_read")
    safe_attach(bpf, event_name="sys_read", func_name="trace_sys_read")
    safe_attach(bpf, event_name="__x64_sys_write", func_name="trace_sys_write")
    safe_attach(bpf, event_name="sys_write", func_name="trace_sys_write")

def replace_program_placeholders(input_program_text: str) -> str:
    program_with_replaced_params = input_program_text.replace("%PID_TO_TRACE%", config.PID_TO_TRACE)
    program_with_replaced_params = program_with_replaced_params.replace("%UID_TO_TRACE%", config.UID_TO_TRACE)
    return program_with_replaced_params

b = BPF(text = replace_program_placeholders(ebpf_program_text))
init_kprobes(b)
listener_thread = Listener(bpf = b)
logging.info("Tracing sys_read and sys_write... Ctrl+C to exit.")
listener_thread.start()

if config.timeout > 0:
    time.sleep(config.timeout)
    listener_thread.interrupted = True
    logging.info(f"Exit by timeout {config.timeout}s")

try:
    listener_thread.join()
except KeyboardInterrupt:
    print("Exiting main thread...")
