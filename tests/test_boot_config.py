import pytest
from vajra.boot.config import BootConfig
def test_default_valid(): assert BootConfig().validate()
def test_raw_override_blocked():
    with pytest.raises(ValueError): BootConfig(partition_scheme="GPT").validate()
