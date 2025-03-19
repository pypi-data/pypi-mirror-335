"""Interface to the spinners disk Tape backend of EOS (EOSCTADISK)

Copyright © 2022-2024 CERN for the benefit of the LHCb collaboration
Frédéric Hemmer - CERN/Experimental Physics Department

"""

import json
import logging
import pathlib
import re
import shlex
import subprocess
from collections import namedtuple
from enum import IntFlag
from stat import S_IFDIR, S_IFREG, filemode

XRD_TIMEOUT = 60


class _StatInfoFlags(IntFlag):
    X_BIT_SET = 1
    IS_DIR = 2
    OTHER = 4
    OFFLINE = 8
    IS_READABLE = 16
    IS_WRITABLE = 32
    POSC_PENDING = 64
    BACKUP_EXISTS = 128


class XRDFile(
    namedtuple(
        "File",
        [
            "id",
            "path",
            "size",
            "mtime",
            "flags",
            # the following fields are not always present
            "ctime",
            "atime",
            "mode",
            "owner",
            "group",
            "permission",  # permission in the form "drwxrw-r--"
        ],
        # defaults are assigned right to left
        defaults=["", "", 0, "", "", "???????"],
    )
):
    """XROOTD file with its attributes"""

    def isdir(self) -> bool:
        """Check whether a file is a directory"""
        return bool(self.flags & _StatInfoFlags.IS_DIR)

    def isfile(self) -> bool:
        """Check whether a file is a plain file"""
        return not bool(self.flags & _StatInfoFlags.IS_DIR)

    def ontape(self) -> bool:
        """Check whether a file is a plain file"""
        return bool(self.flags & _StatInfoFlags.BACKUP_EXISTS)

    def ondisk(self) -> bool:
        """Check whether a file is a plain file"""
        return not bool(self.flags & _StatInfoFlags.OFFLINE)

    def __str__(self):
        """print an XRD file"""

        return f"{self.permission}" f" {self.mtime} {self.size}" f" {self.path}"


class Xrd:
    """Methods interfacing with CTA (xrootd)"""

    def __init__(self, endpoint: str):
        """Inits Xrd class

        Args:
            endpoint: xrootd endpoint

        """
        self.endpoint = endpoint
        # format must be in the form root://hostname
        if not re.match(r"^root://", endpoint):
            raise ValueError(f"{endpoint}: invalid root endpoint")

    @staticmethod
    def _command(command: str) -> list:
        """Issue an EOS or XRootD command in a subproces

        Args:
            command: the XRootd command string

        Raises:
            Nothing

        Returns:
            the XRootD result or None
        """
        logging.debug("%s(%s)", Xrd, command)
        try:
            output = subprocess.run(
                shlex.split(command),
                stdin=None,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                timeout=XRD_TIMEOUT,
                universal_newlines=True,
                shell=False,
                check=True,
            ).stdout.rstrip()  # strip the last newline
            if len(output) == 0:
                return 0, None
            return 0, output
        except subprocess.CalledProcessError as exc:
            return -exc.returncode, f"{exc.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return -1, "Timed out"

    @staticmethod
    def _xrdfsres2list(text: str) -> list:
        """convert an xrdfs command result text to a list

        Args:
            text: an  command output separated by newlines

        Returns:
            a list of EOS output lines
        """
        entries = text.split("\n")
        if len(entries) > 0:
            return entries
        return None

    @staticmethod
    def _parse_xrdfsstat(text: str):
        """Parse an xrdfs stat command"""
        tokens = [
            ("Path", r"(?<=Path:)(\s+).*"),
            ("Id", r"(?<=Id:)(\s+)-?\d+"),
            ("Size", r"(?<=Size:)(\s+)\d+"),
            ("Atime", r"(?<=ATime:)(\s+)\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"),
            ("Ctime", r"(?<=CTime:)(\s+)\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"),
            ("Mtime", r"(?<=MTime:)(\s+)\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"),
            ("Flags", r"(?<=Flags:)(\s+)\d+"),
            ("Mode", r"(?<=Mode:)(\s+)[0-7]+"),
            ("Owner", r"(?<=Owner:)(\s+)\w+"),
            ("Group", r"(?<=Group:)(\s+)\w+"),
        ]
        regexp = "|".join(f"(?P<{t.lower()}>{r})" for t, r in tokens)
        logging.debug("%s", regexp)

        pairs = {}
        for match_object in re.finditer(regexp, text):
            name = match_object.lastgroup
            value = match_object.group().lstrip()
            if name in ["id", "size", "flags"]:
                value = int(value)
            elif name == "mode":
                value = int(value, 8)
            pairs[name] = value
        return pairs

    @staticmethod
    def _xrdstat2tuple(text: str) -> tuple:
        """Convert xrdfs stat text to a Xrdfile tuple

        Normal version (all fields returned bx xrdfs stat)

        Args:
            entry: string as returned by xrdfs stat

        Returns:
            conversion to an Xrdfile tuple

        Raises:
            ValueError if xrdfs stat short format is encountered
        """

        stat_dict = Xrd._parse_xrdfsstat(text)
        if stat_dict["flags"] & _StatInfoFlags.IS_DIR:
            permission = filemode(stat_dict["mode"] | S_IFDIR)
        else:
            permission = filemode(stat_dict["mode"] | S_IFREG)

        return XRDFile(
            path=stat_dict["path"],
            id=stat_dict["id"],
            size=stat_dict["size"],
            atime=stat_dict["atime"],
            ctime=stat_dict["ctime"],
            mtime=stat_dict["mtime"],
            flags=stat_dict["flags"],
            owner=stat_dict["owner"],
            group=stat_dict["group"],
            mode=stat_dict["mode"],
            permission=permission,
        )

    def _stat(self, path: pathlib.Path) -> list:
        """stat an XRootD file

        Note: xrdfs stat may return different information depending on the
        file group ownership.

        Only Path, Id, Size, MTime and Flags seem to be always present

        """
        command = f"/usr/bin/xrdfs {self.endpoint} stat {path}"
        rc, result = self._command(command)
        if rc == 0:  # command succeeded
            try:
                result.index("Mode")  # find which format is used
                xrdfile = self._xrdstat2tuple(result)
            except ValueError:
                raise ValueError("xrdfs short format not supported") from None

            logging.debug("%s", repr(xrdfile))

            return xrdfile

        raise ValueError(f"{result}")

    @staticmethod
    def status(file: XRDFile) -> str:
        """Converts file status to eos-style text"""
        if file.ontape():
            t_str = "t1"
        else:
            t_str = "t0"
        if file.ondisk():
            d_str = "d1"
        else:
            d_str = "d0"
        return d_str + "::" + t_str

    def list_files(self, path: pathlib.Path, recursive=None) -> list:
        """List file an XRootD path"""
        rflag = "-R" if recursive else ""
        command = f"/usr/bin/xrdfs {self.endpoint} ls -l {rflag} {path}"
        rc, result = self._command(command)
        if rc == 0:
            xrdfiles = []
            if result:
                files = self._xrdfsres2list(result)
                for file in files:
                    fields = file.split()
                    # the last field is the full path name
                    xrdfiles.append(self._stat(fields[-1]))
                return xrdfiles
            return []

        raise RuntimeError(f"{rc}: {result}")

    def prepare_status(self, path: pathlib.Path) -> str:
        """Query the prepare status of a single file

        Args:
            path: absolute file path

        Returns:
            return_code, output tuple. Output is xrdfs stderr in case of error
        """
        command = f"/usr/bin/xrdfs {self.endpoint} query prepare 0 {path}"
        rc, result = self._command(command)
        if rc == 0:
            return json.loads(result)

        raise RuntimeError(f"{rc}: {result}")

    def recall(self, path: pathlib.Path) -> str:
        """Query the prepare status of a single file

        Args:
            path: absolute file path

        Returns:
            return_code, output tuple. Output is xrdfs stderr in case of error
        """
        command = f"/usr/bin/xrdfs {self.endpoint} prepare -s {path}"
        rc, result = self._command(command)
        if rc == 0:
            return result

        raise RuntimeError(f"{rc}: {result}")

    def requested(self, path, recursive=False):
        """returns all files that have been requested to be recalled

        Args:
            path: absolute file path to be queried
            recursive: walk recurivively through all sub directories

        Returns:
            A (possible empty) list of files not being recalled
        """
        files = Xrd(self.endpoint).list_files(path, recursive=recursive)
        files_on_disk = []
        for file in files:
            if not file.ondisk():
                status = self.prepare_status(file.path)
                if not status["responses"][0]["on_tape"]:
                    logging.warning("%s: has no tape copy (yet)", file.path)
                if status["responses"][0]["requested"] is True:
                    files_on_disk.append(
                        {"path": file, "reqtime": status["responses"][0]["req_time"]}
                    )
        return files_on_disk

    def not_on_disk(self, path, recursive=False):
        """returns all files that do not have a disk copy and are not being recalled

        Args:
            path: absolute file path to be queried

        Returns:
            A (possible empty) list of files not on disk nor being recalled
        """
        files = Xrd(self.endpoint).list_files(path, recursive=recursive)
        files_on_disk = []
        for file in files:
            if not file.ondisk():
                status = self.prepare_status(file.path)

                if not status["responses"][0]["on_tape"]:
                    logging.warning("%s: has no tape copy (yet)", file.path)
                if (
                    status["responses"][0]["online"]
                    or status["responses"][0]["has_reqid"]
                ):
                    continue
                files_on_disk.append(file)
        return files_on_disk
