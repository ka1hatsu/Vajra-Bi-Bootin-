from vajra.boot.prepared_helper import sanitize_label, partition_path

def test_label():
    assert sanitize_label("My Linux USB!") == "My_Linux_US"

def test_sd():
    assert partition_path("/dev/sdz") == "/dev/sdz1"

def test_nvme():
    assert partition_path("/dev/nvme0n1") == "/dev/nvme0n1p1"
