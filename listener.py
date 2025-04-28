import threading
from bcc import BPF
from datetime import datetime
import config
from enum import Enum


class Operation(Enum):
    READ = 1
    WRITE = 2


class Listener(threading.Thread):

    def __init__(self, bpf: BPF):
        threading.Thread.__init__(self)
        self.interrupted = False
        self.bpf = bpf

    @staticmethod
    def convert_operation_enum_to_string(op_int: int) -> str:
        if op_int == Operation.READ.value:
            return "READ"
        elif op_int == Operation.WRITE.value:
            return "WRITE"

    def print_event(self, cpu, data, size) -> None:
        """
        Callback to be executed on polling the ring buffer
        """
        data = self.bpf["events"].event(data)
        event_datetime = datetime.fromtimestamp(config.system_start_ts + data.ts / 1_000_000_000)
        operation = self.convert_operation_enum_to_string(data.op)
        print(operation.rjust(5), repr(data.pid).rjust(6), event_datetime, data.comm.decode())

    def run(self):
        """
        Loop with polling the ring buffer and printing the data captured by probes
        """
        self.bpf["events"].open_perf_buffer(self.print_event)
        while not self.interrupted:
            try:
                self.bpf.perf_buffer_poll(timeout=500)
            except KeyboardInterrupt:
                print("Exiting listener thread...")
                break