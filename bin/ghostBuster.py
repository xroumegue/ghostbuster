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
from ghostbuster import GhostBuster

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

    args = argparser.parse_args()

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
    agent.hunt()

if __name__ == '__main__':
    main()
    exit(0)
