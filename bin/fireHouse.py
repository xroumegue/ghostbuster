#! /usr/bin/env python3
"""
    Implements GhostBuster server
"""
from os.path import dirname, realpath, join
import sys
import logging
from argparse import ArgumentParser, FileType

import pandas as pd

RUNPATH = dirname(realpath(__file__))
sys.path.append(join(RUNPATH, "../lib"))
from protonpack import ProtonPackSvm
from firehouse import FireHouse

def main():
    """
        The main routine
    """
    #
    # Argument parser
    #
    argparser = ArgumentParser(description='GhostBuster \'s firehouse jail')

    argparser.add_argument(
        '-p',
        '--port',
        type=int,
        default=12345,
        help='port to listen')

    argparser.add_argument(
        '-i',
        '--input',
        type=FileType('r'),
        default='dataset.txt',
        required=True,
        help='Classsified dataset in CSV format')

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

    format_log = '%(levelname)-5s-%(funcName)-4s-%(lineno)-4s-%(message)s'
    logging.basicConfig(format=format_log)
    log = logging.getLogger()
    log.setLevel(args.verbose)

    #
    # Do the real job
    #
    log.debug("Using {:s} as dataset".format(args.input.name))

    dataset = pd.read_csv(args.input.name)
    log.debug(dataset.head())
    protonPack = ProtonPackSvm()
    protonPack.load(dataset)
    protonPack.train()
    protonPack.validate()

    firehouse = FireHouse(port=args.port)
    firehouse.set_classifier(protonPack)
    firehouse.start()

if __name__ == '__main__':
    main()
    exit(0)
