from vajra.boot.compatibility import evaluate

def test_img_requires_auto():
    assert not evaluate("IMG","GPT","Auto","Auto").compatible

def test_legacy_gpt_blocked():
    r=evaluate("ISO","GPT","BIOS / Legacy","FAT32")
    assert not r.compatible and r.severity=="error"

def test_uefi_ntfs_warns():
    r=evaluate("ISO","GPT","UEFI","NTFS")
    assert r.compatible and r.severity=="warning"

def test_uefi_hint_recommends_gpt():
    r=evaluate("ISO","Auto","Auto","Auto",uefi_hint=True)
    assert r.recommended_scheme=="GPT"
    assert r.recommended_target=="UEFI"
