import urllib.request

USER_AGENT = "Vajra-Bi/8.3 (+ISO resolver)"

class SourceNetworkError(RuntimeError):
    pass

def fetch_bytes(url, timeout=20, max_bytes=8*1024*1024):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise SourceNetworkError("Resolver response exceeded safety size limit.")
            return data
    except Exception as e:
        if isinstance(e, SourceNetworkError):
            raise
        raise SourceNetworkError(str(e)) from e

def fetch_text(url, timeout=20, max_bytes=8*1024*1024):
    return fetch_bytes(url, timeout, max_bytes).decode("utf-8", "replace")
