from vajra.writer.verify import verify_written_image

def test_verify_written_image(tmp_path):
    a=tmp_path/"a.img"; b=tmp_path/"b.bin"; data=b"vajra"*4096
    a.write_bytes(data); b.write_bytes(data)
    assert verify_written_image(a,b)

def test_verify_detects_difference(tmp_path):
    a=tmp_path/"a.img"; b=tmp_path/"b.bin"
    a.write_bytes(b"A"*4096); b.write_bytes(b"B"*4096)
    assert not verify_written_image(a,b)
