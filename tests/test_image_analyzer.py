from vajra.boot.analyzer import analyze_image
def test_img(tmp_path):
    p=tmp_path/"x.img"; p.write_bytes(b"0"*32)
    assert analyze_image(p).image_type=="IMG"
