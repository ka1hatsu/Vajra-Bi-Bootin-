from types import SimpleNamespace
from vajra.writer.unmount import mounted_partition_paths, unmount_partitions

def test_mounted_partition_paths():
    d={"mounted_children":[{"path":"/dev/sdz1","mountpoints":["/media/test"]},{"path":"/dev/sdz2","mountpoints":[]}]}
    assert mounted_partition_paths(d)==["/dev/sdz1"]

def test_unmount_uses_partition_path():
    calls=[]
    def runner(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0,stdout="",stderr="")
    d={"mounted_children":[{"path":"/dev/sdz1","mountpoints":["/media/test"]}]}
    assert unmount_partitions(d,runner=runner)
    assert calls==[["udisksctl","unmount","-b","/dev/sdz1"]]
