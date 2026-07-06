from vajra.sources.fedora import walk_json,first_string
def test_walk_json_nested():
    assert any(x.get("variant")=="Workstation" for x in walk_json({"a":[{"variant":"Workstation"}]}))
def test_first_string():
    assert first_string({"url":"x"},"link","url")=="x"
