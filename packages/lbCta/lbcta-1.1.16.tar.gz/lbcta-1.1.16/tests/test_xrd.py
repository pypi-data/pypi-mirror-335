"""Test Python Interface to EOS/CTA

Copyright © 2024 CERN for the benefit of the LHCb collaboration
Frédéric Hemmer - CERN/Experimental Physics Department

"""

import logging
import os
import string
from datetime import datetime, timedelta
from random import choices, randint, random

import pytest

from lbCta.cta import Xrd, _StatInfoFlags

FILECOUNT = 5  # file count in a directory
DIRCOUNT = 3  # subdirectory count
TREEDEPTH = 3  # Tree depth for ls -l -R


def _random_date():
    """Generate a random date in the last year"""
    end = datetime.now()
    start = end - timedelta(days=365)
    random_date = start + (end - start) * random()
    return random_date


def mock_xrd_file_entry(path="", isdir=False, offline=False, backupexists=False):
    """Mock an xrdfs stat output

    Args:
        path: EOS absolute file path
        isdir: mock a directory entry
        offline: pretend the entry is offline
        backupexists: pretend there is a backup"""

    ident = randint(10 ** (19 - 1), (10**19) - 1)  # random 19 digits number
    size = str(randint(42, 120 * 1024**3))
    date = _random_date()
    ctime = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
    mtime = datetime.strftime(date + timedelta(hours=2), "%Y-%m-%d %H:%M:%S")
    atime = "1970-01-01 00:00:00"  # access times are usually not used
    mode = "0640"
    owner = "lhcb"
    group = "z5"
    flags = isdir * int(_StatInfoFlags.IS_DIR)
    flags += offline * int(_StatInfoFlags.OFFLINE)
    flags += backupexists * int(_StatInfoFlags.BACKUP_EXISTS)
    assert not (isdir and offline)  # a dir cannot be offline
    assert not (isdir and backupexists)  # a dir cannot be on tape

    text = (
        "\n"  # xrdfs stat first print a new line...
        f"Path:   {path}\n"
        f"Id:     {ident}\n"
        f"Size:   {size}\n"
        f"MTime:  {mtime}\n"
        f"CTime:  {ctime}\n"
        f"ATime:  {atime}\n"
        f"Flags:  {flags}\n"
        f"Mode:   {mode}\n"
        f"Owner:  {owner}\n"
        f"Group:  {group}\n"
    )
    return text


def mock_file_entry(path, fmt=None, directory=False):
    """Mock a xrdls file entry"""
    filename = "".join(
        choices(
            string.ascii_lowercase + string.digits + string.ascii_uppercase + "_-",
            k=randint(25, 50),
        )
    )
    if not directory:
        filepath = os.path.join(path, filename) + ".mdf"
    else:
        filepath = path + "/"
    size = str(randint(42, 120 * 1024**3))
    date = _random_date()
    mtime = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
    perm = "-rw-r--r--"
    user = "lhcbtest"
    group = "online"
    if fmt == "normal":
        perm = "dr-xr-xr-x" if directory else "-rw-r--r--"
        user = "lhcbtest"
        group = "online"
        entry = f"{perm} {user} {group} {mtime} {size} {filepath}"
    elif fmt == "short":
        perm = "dr-x" if directory else "-r--"
        entry = f"{perm} {size}   {mtime} {filepath}"
    else:
        raise ValueError(f"Invalid format: {fmt}")
    # pylint: disable=possibly-used-before-assignment
    logging.debug("mock_xrdfs_ls_dir: %s", entry)
    return entry


def mock_xrdfs_ls_dir(path, fmt=None):
    # pylint: disable=line-too-long
    """Mock a xrdfs ls -l on a directory

    xrdfs ls -l returns file lists in 2 formats:
    -rw-r--r-- lhcbdaq z5 466893736 2024-10-10 11:23:41 /eos/.../...-173329-039.mdf (normal case)
    -r-- 2024-10-10 11:23:41   466893736 /eos/.../...-173329-039.mdf (group mapping invalid)
    """

    text = []
    # mock FILECOUNT entries
    for _ in range(0, FILECOUNT):
        line = mock_file_entry(path=path, fmt=fmt)
        text.append(line)
    text = "\n".join(text)
    return text


def mock_xrdfs_ls_subtree(path, fmt=None):
    # pylint: disable=line-too-long
    """Mock a xrdfs ls -l -R on a directory

    xrdfs ls -l returns file directory entries in 2 formats:
        dr-x 2024-07-04 10:48:51  469215763188 /eos/.../LHCb/0000279254
        dr-xr-xr-x lhcbdaq  z5  469215763188 2024-07-04 10:48:51 /eos/.../LHCb/0000279254

    """

    def mock_dirname():
        """Build a random directory name"""
        dirname = "".join(
            choices(string.ascii_letters + string.digits, k=randint(5, 10))
        )
        return dirname

    entries = []
    for _ in range(0, DIRCOUNT):
        dirpath = path + "/" + mock_dirname()
        entries.append(mock_file_entry(path=dirpath, fmt=fmt, directory=True))
        for _ in range(0, FILECOUNT):
            entries.append(mock_file_entry(path=path, fmt=fmt))
    text = "\n".join(entries)

    return text


@pytest.fixture(
    name="mock__command",
    params=["normal", "short"],
    ids=["xrdfs ls -l (normal format)", "xrdfs ls -l (short format)"],
)
def mock__command_fixture(request, monkeypatch):
    """Mock lbCta _command()"""

    def mock_command(me, command):
        logging.debug("Mocking: %s %s", me, command)
        args = command.split()
        assert args[0] == "/usr/bin/xrdfs"

        if args[2] == "ls":
            assert "-l" in args
            if "-R" not in args:
                return 0, mock_xrdfs_ls_dir(args[-1], fmt=request.param)
            # Mock a subdir tree
            return 0, mock_xrdfs_ls_subtree(args[-1], fmt=request.param)
        if args[2] == "stat":
            return 0, mock_xrd_file_entry(
                args[-1], isdir=False, offline=True, backupexists=False
            )

        raise NotImplementedError(args[2])

    monkeypatch.setattr(Xrd, "_command", mock_command)


# Real tests start here


def test_invalid_root_endpoint():
    """Test XRootD invalid syntax"""
    with pytest.raises(ValueError, match=r".*invalid root endpoint"):
        _ = Xrd("/An/Invalid/Root/Endpoint")


def test_list_files(mock__command):  # pylint: disable=unused-argument
    """doc"""
    xrd = Xrd("root://lhcxxx.cern.ch")
    files = xrd.list_files("/eos/a/b", recursive=False)
    assert len(files) == FILECOUNT


def test_list_dirs(mock__command):  # pylint: disable=unused-argument
    """doc"""
    xrd = Xrd("root://lhcxxx.cern.ch")
    files = xrd.list_files("/eos/a/b", recursive=True)
    assert len(files) == DIRCOUNT * (FILECOUNT + 1)
