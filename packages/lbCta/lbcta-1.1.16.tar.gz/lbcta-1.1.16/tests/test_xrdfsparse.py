"""Test xrdfs stat output parsing"""

from lbCta.cta import Xrd


def test_parse_long():
    """Test xrdfs stat parsing long format"""
    stat_output = """"

Path:   /eos/ctalhcbdisk/archive/lhcbcolddata/hist/Savesets/2024/CALO/EBPass/02/01/EBPass-282945-20240201T152216.root
Id:     -6917529027641029889
Size:   4233
MTime:  2024-02-01 14:22:16
CTime:  2025-01-24 08:26:11
ATime:  2025-01-23 09:58:04
Flags:  128 (BackUpExists)
Mode:   0640
Owner:  lhcbdaq
Group:  z5
"""

    # pylint: disable=protected-access,no-member
    stat_dict = Xrd._parse_xrdfsstat(stat_output)
    assert stat_dict["path"] == (
        "/eos/ctalhcbdisk/"
        "archive/lhcbcolddata"
        "/hist/Savesets/2024/"
        "CALO/EBPass/02/01/"
        "EBPass-282945-20240201T152216.root"
    )
    assert stat_dict["id"] == -6917529027641029889
    assert stat_dict["size"] == 4233
    assert stat_dict["mtime"] == "2024-02-01 14:22:16"
    assert stat_dict["ctime"] == "2025-01-24 08:26:11"
    assert stat_dict["atime"] == "2025-01-23 09:58:04"
    assert stat_dict["flags"] == 128
    assert stat_dict["mode"] == int("0640", 8)
    assert stat_dict["owner"] == "lhcbdaq"
    assert stat_dict["group"] == "z5"


def test_parse_short():
    """Test xrdfs stat parsing short format"""
    stat_output = """

Path:   /eos/ctalhcbdisk/archive/lhcbcolddata/hlt2/LHCb/0000240040/Run_0000240040_HLT20137_20220729-173327-643.mdf
Id:     -5764607523034182913
Size:   442066844
MTime:  2024-10-10 11:23:38
Flags:  144 (IsReadable|BackUpExists)" \
"""

    # pylint: disable=protected-access,no-member
    stat_dict = Xrd._parse_xrdfsstat(stat_output)
    assert stat_dict["path"] == (
        "/eos/ctalhcbdisk/"
        "archive/lhcbcolddata"
        "/hlt2/LHCb/0000240040/"
        "Run_0000240040_HLT20137_20220729-173327-643.mdf"
    )
    assert stat_dict["id"] == -5764607523034182913
    assert stat_dict["size"] == 442066844
    assert stat_dict["mtime"] == "2024-10-10 11:23:38"
    assert stat_dict["flags"] == 144
