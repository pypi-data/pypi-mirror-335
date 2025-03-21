"""Recall EOS files

Copyright © 2024 CERN for the benefit of the LHCb collaboration
Frédéric Hemmer - CERN/Experimental Physics Department

"""

import argparse
import logging
import os
import sys

from lbCta import __version__
from lbCta.cta import Xrd

CTA_ENDPOINT_ENV = "LBCTA_ENDPOINT"


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
        description="Interface to CTA disk pools - recall files from tape"
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
    parser.add_argument("-p", "--path", dest="path", help="EOS absolute path")
    parser.add_argument("-e", "--endpoint", dest="endpoint", help="EOS root end point")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=False,
        help="handle recursively directories",
    )
    parser.add_argument(
        "-d",
        "--directory",
        action="store_true",
        default=False,
        help="also prints directory entries",
    )

    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level,
        format="%(levelname)s: %(message)s",
    )
    if CTA_ENDPOINT_ENV in os.environ and not args.endpoint:
        args.endpoint = os.environ[CTA_ENDPOINT_ENV]

    check_arguments(args)

    xrd = Xrd(args.endpoint)
    files = xrd.not_on_disk(args.path, recursive=args.recursive)
    if not files:
        logging.info("All files are on disk or are already being recalled")
        sys.exit(0)
    for file in files:
        reqid = xrd.recall(file.path)
        logging.info("recall request id: %s", reqid)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt, exiting ...")
