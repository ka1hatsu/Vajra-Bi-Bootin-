import pytest
from vajra.boot.large_file_policy import choose_strategy,LargeFilePolicyError

def test_direct():
    assert choose_strategy({"fat32_compatible":True,"windows_install_media":False},"FAT32")=="direct_extract"

def test_windows_split():
    assert choose_strategy({"fat32_compatible":False,"windows_install_media":True},"FAT32")=="split_windows_wim"

def test_other_large_blocked():
    with pytest.raises(LargeFilePolicyError):
        choose_strategy({"fat32_compatible":False,"windows_install_media":False},"FAT32")
