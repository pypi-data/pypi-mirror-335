import sys

from docker_utils.cli.dkrutil import dkrutil

if __name__ == '__main__':
    dkrutil(sys.argv[1:])
