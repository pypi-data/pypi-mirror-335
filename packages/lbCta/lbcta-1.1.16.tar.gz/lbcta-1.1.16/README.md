# lbCta - Interface to the CERN Tape Archive spinner disks service


[![pipeline status](https://gitlab.cern.ch/lhcb-online/lhcb-online-cta/badges/main/pipeline.svg)](https://gitlab.cern.ch/lhcb-online/lhcb-online-cta/-/commits/main)

This package implements a set of console scripts to interface with the CERN Tape
Archive (CTA) in view of listing and recalling files and directories from tape.

## Name
lhcb-online-cta

## Description
Interface to EOS/XROOTD suitable for use with the EOSCTA spinner disks tape archiving

The EOSCTA spinner disks pool is a EOS disk pool that can be used for recalling files
that are stored on the CERN Tape Archive service. These files, once recalled can be
copied to usable locations using XRootD (e.g. with xrdcp). Files on the EOSCTA spinner
disks are not directly usable.

## Usage

```
$ lbcta-status -h
usage: lbcta-status [-h] [-l LOG_LEVEL] [--version] -e ENDPOINT -p PATH [-r] [-d]

Interface to CTA disk pools - list files

optional arguments:
  -h, --help            show this help message and exit
  -l LOG_LEVEL, --loglevel LOG_LEVEL
                        logging level (default = INFO)
  --version             print version and exits
  -e ENDPOINT, --endpoint ENDPOINT
                        EOS root end point
  -p PATH, --path PATH  EOS absolute path
  -r, --recursive       handle recursively directories
  -d, --directory       also prints directory entries
```

```
$ lbcta-recall -h
usage: lbcta-recall [-h] [-l LOG_LEVEL] [--version] -p PATH -e ENDPOINT [-r] [-d]

Interface to CTA disk pools - recall files from tape

optional arguments:
  -h, --help            show this help message and exit
  -l LOG_LEVEL, --loglevel LOG_LEVEL
                        logging level (default = INFO)
  --version             print version and exits
  -p PATH, --path PATH  EOS absolute path
  -e ENDPOINT, --endpoint ENDPOINT
                        EOS root end point
  -r, --recursive       handle recursively directories
  -d, --directory       also prints directory entries
```

```
$ lbcta-query -h
usage: lbcta-query [-h] [-l LOG_LEVEL] [--version] -e ENDPOINT -p PATH [-r] [--wait] [--silent]

Interface to CTA disk pools - query status of files without disk replica

optional arguments:
  -h, --help            show this help message and exit
  -l LOG_LEVEL, --loglevel LOG_LEVEL
                        logging level (default = INFO)
  --version             print version and exits
  -e ENDPOINT, --endpoint ENDPOINT
                        CTA root end point
  -p PATH, --path PATH  CTA absolute path
  -r, --recursive       handle recursively directories
  --wait                wait for all requested file(s) to be copied to disk
  --silent              silently wait for all requested file(s) to be available to disk
```

## Examples
Detailed usage examples can be found in https://lbtwiki.cern.ch/bin/view/Online/OnlineOfflineEOSCTA

## Installation
pip install lhcb-online-cta

## Authors and acknowledgment
Frédéric Hemmer - CERN/Experimental Physics Department

## License
Copyright © 2024-2025 CERN for the benefit of the LHCb collaboration
