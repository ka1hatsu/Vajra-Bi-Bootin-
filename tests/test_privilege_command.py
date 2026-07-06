from vajra.writer.session import TargetIdentity
import vajra.writer.privilege as privilege
def test_command(monkeypatch):
    monkeypatch.setattr(privilege.shutil,"which",lambda _: "/usr/bin/pkexec")
    i=TargetIdentity("/dev/sdz","ABC",1000)
    assert privilege.build_privileged_command("/helper","/image.iso",i)==["/usr/bin/pkexec","/helper","--image","/image.iso","--device","/dev/sdz","--serial","ABC","--size","1000"]
