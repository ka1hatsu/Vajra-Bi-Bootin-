from pathlib import Path

def test_progress_signal_is_not_32_bit_int():
    text=Path("vajra/downloader/worker.py").read_text()
    assert "progress=Signal(int,int,float,float)" not in text
    assert "progress=Signal(object,object,float,float)" in text

def test_large_iso_byte_count_exceeds_signed_32_bit():
    total=3918290944
    assert total > 2**31-1
    assert int(total)==3918290944
