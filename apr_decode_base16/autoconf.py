import time

from autogen import *
import yaml
import os
import re
import subprocess
import argparse


if __name__ == '__main__':
    # Args configuration

    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-i', '--input', metavar='DIRECTORY', type=str, required=True)
    parser.add_argument('-f', '--file', type=str, required=True)
    args = parser.parse_args()

    generate_harness(args.input, args.file)
