from types import SimpleNamespace
from vajra.downloads.history import DownloadHistory
from vajra.downloads.session import DownloadSession

def test_session_lifecycle(tmp_path):
    image=SimpleNamespace(
        distro="Test",version="1",architecture="amd64",filename="test.iso",
        image_url="https://example.invalid/test.iso",sha256="a"*64
    )
    h=DownloadHistory(tmp_path/"h.json")
    s=DownloadSession("test",image,tmp_path/"test.iso",h)
    s.progress(50,100)
    assert h.load()[0].state=="downloading"
    s.cancelled()
    assert h.load()[0].state=="cancelled"
    s.completed(tmp_path/"test.iso","a"*64,True)
    assert h.load()[0].verified
