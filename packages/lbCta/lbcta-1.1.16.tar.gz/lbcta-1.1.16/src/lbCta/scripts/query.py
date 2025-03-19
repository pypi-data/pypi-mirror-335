"""Tape (De)Archiving tools

Copyright © 2024 CERN for the benefit of the LHCb collaboration
Frédéric Hemmer - CERN/Experimental Physics Department

"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime

from lbCta import __version__
from lbCta.cta import Xrd

CTA_ENDPOINT_ENV = "LBCTA_ENDPOINT"
WAIT_INTERVAL = 15 * 60


def check_arguments(args: argparse.Namespace):
    """Check command arguments

    Check command arguments and eventually exits

    Args:
        args: arguments as returned by argparse.parse_args()

    Raises:
        Nothing

    Returns:
        Nothing
    """
    if args.version:
        print(f"{os.path.basename(sys.argv[0])}: {__version__}")
        sys.exit(0)
    else:
        if not args.endpoint or not args.path:
            logging.error(
                "the following arguments are required: -e/--endpoint, -p/--path"
            )
            sys.exit(1)


def main():
    """Main console script"""
    parser = argparse.ArgumentParser(
        description=(
            "Interface to CTA disk pools - "
            "query status of files without disk replica"
        )
    )

    parser.add_argument(
        "-l",
        "--loglevel",
        dest="log_level",
        default="INFO",
        help="logging level (default = INFO)",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="print version and exits",
    )
    parser.add_argument("-e", "--endpoint", dest="endpoint", help="CTA root end point")
    parser.add_argument("-p", "--path", dest="path", help="CTA absolute path")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=False,
        help="handle recursively directories",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        default=False,
        help="wait for all requested file(s) to be copied to disk",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        default=False,
        help="silently wait for all requested file(s) to be available to disk",
    )

    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level,
        format="%(levelname)s: %(module)s(%(funcName)s): %(message)s",
    )
    if CTA_ENDPOINT_ENV in os.environ and not args.endpoint:
        args.endpoint = os.environ[CTA_ENDPOINT_ENV]
    check_arguments(args)

    xrd = Xrd(args.endpoint)
    while True:
        files = xrd.requested(args.path, recursive=args.recursive)
        for file in files:
            date_recalled = datetime.fromtimestamp(int(file["reqtime"])).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if not args.silent:
                print(file["path"], date_recalled)
        if not args.wait or not files:
            break
        time.sleep(WAIT_INTERVAL)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt, exiting ...")
