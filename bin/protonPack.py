#! /usr/bin/env python3
"""
    Implements ProtonPack: The ghostbuster favourite weapon
"""
import logging
from argparse import ArgumentParser, FileType
from os.path import dirname, realpath, join
import sys
import pandas as pd

RUNPATH = dirname(realpath(__file__))
sys.path.append(join(RUNPATH, "../lib"))
from protonpack import ProtonPackSvm

def main():
    """
        The main routine
    """
    #
    # Argument parser
    #
    FORMAT = '%(levelname)-5s-%(funcName)-4s-%(lineno)-4s-%(message)s'
    argparser = ArgumentParser(description='GhostBuster server')

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
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(args.verbose)

    #
    # Do the real job
    #
    log.debug("Using {:s} as dataset".format(args.input.name))

    dataset = pd.read_csv(args.input.name)
    log.debug(dataset.head())
    proton_pack = ProtonPackSvm()
    proton_pack.load(dataset)
    proton_pack.train()
    proton_pack.validate()

if __name__ == '__main__':
    main()
    exit(0)
