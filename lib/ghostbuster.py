#! /usr/bin/env python3
"""
    Implements GhostBuster server
"""

from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, run, PIPE
from struct import pack, unpack
from threading import Timer
from logging import getLogger
from os import kill, getpid
from signal import SIGKILL
import shlex


EVENTS = [
    "r11",
    "r10",
    "r12",
    "r42",
    "r48",
    "r72"
]
CYCLES="r11"

#CYCLES = "cycles"
#EVENTS = ["cycles",
#        "l1d.replacement",
#        "l2_lines_out.demand_clean",
#        "LLC-load-misses",
#        "cache-misses",
#        "L1-dcache-load-misses"
#    ]

DELAY = '0'
PERIOD = '500'
MEASUREMENT_DURATION = 3

PERF_CMD = "perf \
        stat \
        -x \',\' \
        --delay {:s} \
        --interval-print {:s} \
        -e {:s} \
        --log-fd 1 \
        -p {:s}"

CSV_SEPARATOR = ','

KEYS = [
    "timestamp",
    "counter",
    "unit",
    "event",
    "run time",
    "percentage",
    "metric",
    "unit metric",
    "NA"
    ]

PS_CMD = "ps -Ao \"%p,%U,%c,%C\" --sort=-pcpu --no-headers"
NR_PS = 3

class Ghost():
    """
        A Ghost ?
    """
    def __init__(self, pid, user, cmd, pcpu):
        self.pid = pid
        self.user = user
        self.cmd = cmd.strip()
        self.pcpu = pcpu
        self.log = getLogger()
        self.proc = None
        self.watchdog = None

    def __str__(self):
        _str = "Ghost:\n"
        _str += "\tpid: {:s}\n".format(self.pid)
        _str += "\tuser: {:s}\n".format(self.user)
        _str += "\tcmd: {:s}\n".format(self.cmd)
        _str += "\tpcpu: {:s}\n".format(self.pcpu)
        return _str

    def kill(self):
        """
            Kill the ghost, and stop its measurement
        """
        pid_int = int(self.pid)
        self.log.debug("Stopping scan on pid {:d}".format(self.proc.pid))
        self.watchdog.cancel()
        self._stop_scan()
        self.proc.wait()
        self.log.info("Sending SIGKILL signal to pid {:d}".format(pid_int))
        kill(pid_int, SIGKILL)

    def _stop_scan(self):
        """
            private: Stop the on going scan
        """
        self.log.debug("Stopping {}".format(self))

        proc_status = self.proc.poll()
        if proc_status is None:
            self.proc.kill()

    def scan(self):
        if self.proc is None:
            try:
                kill(int(self.pid), 0)
            except OSError:
                return None

            self.log.info("Scanning process {:s} - {:s}".format(self.pid, self.cmd))
            cmd_str = PERF_CMD.format(DELAY, PERIOD, ','.join(EVENTS), self.pid)
            self.log.debug("Executing {:s}".format(cmd_str))
            self.proc = Popen(shlex.split(cmd_str), stderr=None, stdout=PIPE)
            proc_status = self.proc.poll()
            if proc_status:
                self.log.debug("Process {} exited with error code {}".format(
                        self.pid,
                        proc_status)
                        )
                return None
            self.watchdog = Timer(MEASUREMENT_DURATION, self._stop_scan, [])
            self.watchdog.start()

        timestamp = None
        data = {}
        events = {}
        for line in iter(self.proc.stdout.readline, ''):
            proc_status = self.proc.poll()
            if proc_status and proc_status != 0:
                self.log.debug("Process {} exited with error code {}".format(
                    self.pid,
                    proc_status)
                    )
                self.watchdog.cancel()
                break
            if line:
                msg_str = line.decode('utf-8')
                self.log.debug("Received: {}".format(msg_str))
                values = msg_str.split(CSV_SEPARATOR)
                if timestamp \
                        and timestamp != values[0] \
                        and len(data.keys()) == len(EVENTS):
                    # A measurement is complete, use it
                    valid = True
                    for key in data.keys():
                        if not data[key]['counter'].isdigit():
                            self.log.debug("Wrong counter")
                            valid = False
                            break

                    if valid is False:
                        self.log.debug("Wrong measurement: skipping")
                        data = {}
                        events = {}
                        # Keep alive the connection
                        return pack("I", 0)

                    events_export = sorted(events)
                    events_export.remove(CYCLES)
                    cycles = int(data[CYCLES]['counter'])
                    x_predict = []
                    for key in events_export:
                        event = data[key]
                        counter = int(event['counter'])
                        ratio = counter / cycles
                        x_predict.append(ratio)
                    self.log.debug("New measurement {:}".format(x_predict))
                    return pack("I{}f".format(len(x_predict)), len(x_predict), *x_predict)
                timestamp = values[0]
                dataline = {}
                for (key, value) in list(zip(KEYS, values)):
                    dataline[key] = value
                data[dataline['event']] = dataline
                events[dataline["event"]] = 1

class GhostBuster():
    """
        A GhostBuster seeking for ghosts
    """
    def __init__(self, port=12345, addr='127.0.0.1'):
        self.port = port
        self.addr = addr
        self.log = getLogger()
        self.connection = socket()
        self.current = getpid()

    def identify(self, nr_candidates=NR_PS):
        """
            Identify the list of candidates for hiding a ghost
        """
        self.log.debug("PS command: {:s}".format(PS_CMD))
        ps_cmd = run(shlex.split(PS_CMD), stderr=None, stdout=PIPE)
        if ps_cmd.returncode != 0:
            self.log.error("Error while listing the most active process")
            self.connection.close()
            # TODO: Raise an exception
            exit(1)

        ghosts = []
        blacklist = ['perf']
        for ps_line in ps_cmd.stdout.split(b'\n')[:nr_candidates]:
            ps_line_str = ps_line.decode('utf-8').strip()
            ghost = Ghost(*ps_line_str.split(','))
            if not ghost.cmd in blacklist and int(ghost.pid) != self.current:
                ghosts.append(ghost)

        return ghosts

    def shoot(self, ghost):
        self.log.info("\n*********>\nShooting {:s} - {:s}\n*********>".format(ghost.cmd, ghost.pid))
        ghost.kill()

    def hunt(self):
        """
            Hunt the ghost
        """
        self.connection.connect((self.addr, self.port))
        while True:
            for ghost in self.identify():
                for measurement in iter(ghost.scan, None):
                    self.connection.send(measurement)
                    rsp = self.connection.recv(1024)
                    is_ghost = unpack("I", rsp)[0]
                    self.log.debug("Classification received: {:}".format(is_ghost))
                    if is_ghost == 1:
                        self.shoot(ghost)
                        break
