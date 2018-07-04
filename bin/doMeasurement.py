#! /usr/bin/env python3

from subprocess import Popen, run, PIPE, STDOUT
from shlex import split
import logging
from os import setpgrp, getpgrp, killpg, kill
from signal import SIGKILL, signal
from random import randint

FORMAT = '%(levelname)-5s-%(asctime)-8s-%(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler('log.txt')
handler.setLevel(logging.DEBUG)
log.addHandler(handler)

serverip = '10.161.68.210'
sleepTime = '60'
INTERVAL = '2500'
DELAY_MIN = 0
DELAY_MAX = 100
DELAY_SCALE = 10
DELAY_OFFSET = 1500

#EVENTS = [
#    "cycles",
#    "L1-dcache-load-misses",
#    "L1-dcache-loads",
#    "branch-load-misses",
#    "branch-loads",
#    ]

# TRM A72: Chapitre 11.8
#
# 0x11: cpu_cycles
# 0x12: Predicatvle branch speculatively executed
# 0x10: Mispredicted or not predicted branch speculatively executed
# 0x42: L1 data cache refill read
# 0x43: L1 data cache refill write
# 0x46: L1 data cache back write back victim
# 0x47: L1 data cache back write back clean
# 0x48: L1 data cache invalidate
# 0x70: Operation speculatively executed: load
# 0x71: Operation speculatively executed: store
# 0x72: Operation speculatively executed: load/store

EVENTS = [
        "r11",
        "r10",
        "r12",
        "r42",
        "r48",
        "r72" 
    ]

USECASES = [
    {
        "name" : "sleep",
        "args" : ["/bin/sleep", "180"],
    },
    {
        "name" : "iozone",
        "args" : ["iozone", "-a"],
    },

    {
        "name" : "iozone_sdcard",
        "args" : ["iozone", "-a", "-g", "128M", "-f", "/run/media/mmcblk1p2/tmp/test.bin"],
    },
    {
        "name" : "glmark2",
        "args" : ["glmark2-es2-wayland", "--fullscreen"],
    },
    {
        "name" : "iperf",
        "args" : ["iperf3", "-c", serverip, "-t", "240"],
    },
    {
        "name" :"fio",
        "args" : ["fio",
            "--randrepeat=1",
            "--ioengine=libaio",
            "--direct=1",
            "--gtod_reduce=1",
            "--name=test",
            "--filename=random_read_write.fio",
            "--bs=4k",
            "--iodepth=64",
            "--size=256M",
            "--readwrite=randrw",
            "--rwmixread=75"
        ],
    },
    {
        "name" : "openssl",
        "args" : ["openssl", "speed", "aes-256-cbc", "rsa4096", "ecdsap521", "sha512", "dsa2048"],
    },
    {
        "name" : "lmbench",
        "args" : ["lmbench-run"],
    },
    {
        "name" : "Spectre",
        "args" : ["/home/root/spectre-HW"],
    }
]

PERF_CMD = "perf \
        stat \
        -x \',\' \
        -a \
        --append \
        --delay {:} \
        --interval-print {:s} \
        -o {:s} \
        -e {:s} \
        {:s}"


cmd_usecase = None
LOOP=10
try:
    # Set the process group ID
    setpgrp()
    for loop in range(LOOP):
        log.info("Measurement iteration {}".format(loop))
        for usecase in USECASES:
            delay = str((randint(DELAY_MIN, DELAY_MAX) * DELAY_SCALE) + DELAY_OFFSET)
            log.info("Exercising usecase {} with {} ms of delay".format(usecase['name'], delay))
            REPORT="reports/report-{:s}ms-{}-{:s}.csv".format(delay, loop, usecase['name'])
    #        cmd_usecase = Popen(usecase['args'], stdout=PIPE, stderr=PIPE, start_new_session=True)
            cmd_str = PERF_CMD.format(delay, INTERVAL, REPORT, ','.join(EVENTS), ' '.join(usecase['args']))
            cmd_args = split(cmd_str)
            log.debug("Running cmd {}".format(cmd_args))
            retCode = run(cmd_args, stdout=PIPE, stderr=STDOUT)
            retCode.check_returncode()
            # Terminate the usecase running if still running
    #        if cmd_usecase.poll() is None:
    #            log.info("killing process {}-{}".format(cmd_usecase.args, cmd_usecase.pid))
    #            killpg(cmd_usecase.pid, SIGKILL)
finally:
    # Kill all remaining processes of the process group
    killpg(getpgrp(), SIGKILL)
