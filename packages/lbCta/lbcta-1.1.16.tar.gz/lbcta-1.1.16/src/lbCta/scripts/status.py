"""Reports status of XROOTD files

Copyright © 2024 CERN for the benefit of the LHCb collaboration
Frédéric Hemmer - CERN/Experimental Physics Department

"""

import argparse
import logging
import os
import sys
from datetime import datetime

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


def _list(endpoint="", path="", directory=False, recursive=False):
    """List XROOTD files with their extended attributes"""
    files = Xrd(endpoint=endpoint).list_files(path, recursive=recursive)
    for file in files:
        if file.isdir():
            if directory:
                msg = Xrd.status(file) + " " + str(file)
                print(msg)
        elif file.isfile():
            msg = Xrd.status(file) + " " + str(file)
            reqstatus = Xrd(endpoint).prepare_status(file.path)
            if reqstatus["responses"][0]["requested"]:
                reqtime = reqstatus["responses"][0]["req_time"]
                date_recalled = datetime.fromtimestamp(int(reqtime)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                msg += f" recalled on {date_recalled}"
            print(msg)
        else:
            raise TypeError(f"{file.path}: {file.flags}")


def main():
    """Main console script"""
    parser = argparse.ArgumentParser(
        description="Interface to CTA disk pools - list files"
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
    parser.add_argument(
        "-e",
        "--endpoint",
        dest="endpoint",
        help="EOS XRootD end point",
    )
    parser.add_argument("-p", "--path", dest="path", help="EOS absolute path")
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
        format="%(levelname)s: %(module)s(%(funcName)s): %(message)s",
    )

    if CTA_ENDPOINT_ENV in os.environ:
        args.endpoint = os.environ[CTA_ENDPOINT_ENV]

    check_arguments(args)

    try:
        _list(args.endpoint, args.path, args.directory, args.recursive)
    except RuntimeError as exc:
        logging.error(exc)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt, exiting ...")
