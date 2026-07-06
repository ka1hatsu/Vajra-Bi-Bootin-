from vajra.writer.session import TargetIdentity


def test_target_identity_snapshot():
    device = {
        "path": "/dev/sdz",
        "serial": "TEST123",
        "size_bytes": 16000000000,
    }
    identity = TargetIdentity.from_device(device)
    assert identity.path == "/dev/sdz"
    assert identity.serial == "TEST123"
    assert identity.size_bytes == 16000000000
