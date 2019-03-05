#! /usr/bin/env python3
"""
    Implements GhostBuster agent: A real ghost hunter !
"""
from os.path import dirname, realpath, join
import sys
from argparse import ArgumentParser
import logging

RUNPATH = dirname(realpath(__file__))
sys.path.append(join(RUNPATH, "../lib"))
sys.path.append(join(RUNPATH, "../etc"))
from ghostbuster import GhostBuster
import config

def main():
    """
        The main routine
    """
    #
    # Argument parser
    #
    argparser = ArgumentParser(description='GhostBuster server')

    argparser.add_argument(
        '-p',
        '--port',
        type=int,
        default=12345,
        help='port to listen')

    argparser.add_argument(
        '-a',
        '--address',
        type=str,
        default='127.0.0.1',
        help='Firehouse ip address')


    argparser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        const=logging.DEBUG,
        default=logging.INFO,
        help='Be verbose...')

    argparser.add_argument(
        '-m',
        '--machine',
        choices=config.Config.MACHINES,
        default=config.Config.MACHINE_DEFAULT,
        required=True,
        help='Machine')

    args = argparser.parse_args()

    cfgs = {
        'i6950x' : config.i6950x,
        'a72' : config.a72,
    }

    cfg = cfgs[args.machine]



    #
    # Logger
    #

    format_str = '%(levelname)-5s-%(funcName)-4s-%(lineno)-4s-%(message)s'
    logging.basicConfig(format=format_str)
    log = logging.getLogger()
    log.setLevel(args.verbose)

    #
    # Do the real job
    #
    agent = GhostBuster(port=args.port, addr=args.address)
    agent.load(cfg)
    agent.hunt()

if __name__ == '__main__':
    main()
    exit(0)
