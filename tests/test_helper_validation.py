import pytest
from vajra.writer.helper import validate_target


def good_device():
    return {
        "eligible": True,
        "system_disk": False,
        "read_only": False,
        "serial": "ABC",
        "size_bytes": 1000,
    }


def test_valid_target():
    validate_target(good_device(),"ABC",1000)


def test_serial_change_is_blocked():
    with pytest.raises(SystemExit):
        validate_target(good_device(),"WRONG",1000)


def test_capacity_change_is_blocked():
    with pytest.raises(SystemExit):
        validate_target(good_device(),"ABC",999)
