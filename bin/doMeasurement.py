#! /usr/bin/env python3
import sys
from subprocess import Popen, run, PIPE, STDOUT
from shlex import split
import logging
from os import setpgrp, getpgrp, killpg, kill, mkdir
from os.path import dirname, realpath, join, isdir
from signal import SIGKILL, signal
from random import randint
from argparse import ArgumentParser

RUNPATH = dirname(realpath(__file__))
sys.path.append(join(RUNPATH, "../etc"))

import config

argparser = ArgumentParser(description='Ghostbuster measurement collect')

argparser.add_argument(
    '-m',
    '--machine',
    choices=config.Config.MACHINES,
    default=config.Config.MACHINE_DEFAULT,
    required=True,
    help='Machine')

argparser.add_argument(
    '-v',
    '--verbose',
    action='store_const',
    const=logging.DEBUG,
    default=logging.INFO,
    help='Be verbose...')

args = argparser.parse_args()

FORMAT = '%(levelname)-5s-%(asctime)-8s-%(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(args.verbose)
handler = logging.FileHandler('log.txt')
handler.setLevel(logging.DEBUG)
log.addHandler(handler)


cfgs = {
        'i6950x' : config.i6950x,
        'a72' : config.a72,
}

cfg = cfgs[args.machine]
reportdir = join('reports', args.machine)
if not isdir(reportdir):
    mkdir(reportdir)

cmd_usecase = None
try:
    # Set the process group ID
    setpgrp()
    for loop in range(cfg.LOOP):
        log.info("Measurement iteration {}".format(loop))
        for usecase in cfg.USECASES:
            delay = str((randint(cfg.DELAY_MIN, cfg.DELAY_MAX) * cfg.DELAY_SCALE) + cfg.DELAY_OFFSET)
            log.info("Exercising usecase {} with {} ms of delay".format(usecase['name'], delay))
            REPORT="reports/{:s}/report-{:s}ms-{}-{:s}.csv".format(args.machine, delay, loop, usecase['name'])
    #        cmd_usecase = Popen(usecase['args'], stdout=PIPE, stderr=PIPE, start_new_session=True)

            cmd_str = cfg.PERF_CMD.format(delay, cfg.INTERVAL, REPORT, ','.join(cfg.EVENTS), ' '.join(usecase['args']))
            cmd_args = split(cmd_str)
            log.debug("Running cmd {}".format(' '.join(cmd_args)))
            retCode = run(cmd_args, stdout=PIPE, stderr=STDOUT)
            retCode.check_returncode()
            # Terminate the usecase running if still running
    #        if cmd_usecase.poll() is None:
    #            log.info("killing process {}-{}".format(cmd_usecase.args, cmd_usecase.pid))
    #            killpg(cmd_usecase.pid, SIGKILL)
finally:
    # Kill all remaining processes of the process group
    killpg(getpgrp(), SIGKILL)
