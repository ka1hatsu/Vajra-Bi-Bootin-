from vajra.writer.recovery import assess_interruption

def test_prewrite_is_likely_untouched():
    x=assess_interruption("preflight")
    assert x.state=="likely_untouched" and x.safe_to_retry is True

def test_partition_interruption_is_incomplete():
    x=assess_interruption("Creating partition table...")
    assert x.state=="incomplete_media" and x.safe_to_retry is False

def test_copy_interruption_is_incomplete():
    assert assess_interruption("Copying files...").state=="incomplete_media"

def test_unknown_stage_is_conservative():
    x=assess_interruption("custom backend action")
    assert x.state=="unknown" and x.safe_to_retry is False
