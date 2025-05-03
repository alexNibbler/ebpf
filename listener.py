import threading
from bcc import BPF
from datetime import datetime
import config
from enum import Enum


class Operation(Enum):
    READ = 1
    WRITE = 2
    UNKNOWN = 0

    @classmethod
    def from_value(cls, value: int) -> "Operation":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN

    def __str__(self):
        return self.name

class Listener(threading.Thread):
    def __init__(self, bpf: BPF):
        threading.Thread.__init__(self)
        self._interrupted = False
        self.bpf = bpf
        self.lock = threading.Lock()

    @property
    def is_interrupted(self):
        with self.lock:
            return self._interrupted

    @is_interrupted.setter
    def is_interrupted(self, val: bool):
        with self.lock:
            self._interrupted = val

    def print_event(self, cpu, data, size) -> None:
        """
        Callback to be executed on polling the ring buffer
        """
        data = self.bpf["events"].event(data)
        event_datetime = datetime.fromtimestamp(config.system_start_ts + data.ts / 1_000_000_000)
        operation = Operation.from_value(data.op)
        print(str(operation).rjust(7), str(event_datetime).rjust(28), str(data.pid).rjust(6), data.comm.decode())

    def run(self):
        """
        Loop with polling the ring buffer and printing the data captured by probes
        """
        self.bpf["events"].open_perf_buffer(self.print_event)
        while not self.is_interrupted:
            self.bpf.perf_buffer_poll(timeout=500)