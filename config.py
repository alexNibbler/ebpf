import os
from argparse import Namespace, ArgumentParser

import psutil

def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="Application to trace sys_read and sys_write."
    )
    parser.add_argument(
        "-t", "--time",
        type=int,
        help="time in seconds after which the application will be terminated. If not set or negative, the application runs until ctrl+C is pressed",
        default=-1
    )

    return parser.parse_args()

EBPF_C_FILE_PATH = "ebpf_c/ebpf_program.c"

# Set env variables to trace kernal events only related to specific system user or process
UID_TO_TRACE = os.getenv("UID_TO_TRACE", default="-1")
PID_TO_TRACE = os.getenv("PID_TO_TRACE", default="-1")

cli_args = parse_args()
timeout = cli_args.time
system_start_ts = psutil.boot_time()