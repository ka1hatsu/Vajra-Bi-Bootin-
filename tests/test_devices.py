from vajra.writer.devices import format_size

def test_format_size():
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 ** 3) == "1.0 GB"
