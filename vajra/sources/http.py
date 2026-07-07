import urllib.request

from vajra.sources.security import open_download_url

USER_AGENT = "Vajra-Bi/8.3 (+ISO resolver)"


class SourceNetworkError(RuntimeError):
    pass


def fetch_bytes(url, timeout=20, max_bytes=8 * 1024 * 1024):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with open_download_url(req, timeout=timeout) as response:
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise SourceNetworkError("Resolver response exceeded safety size limit.")
            return data
    except Exception as exc:
        if isinstance(exc, SourceNetworkError):
            raise
        raise SourceNetworkError(str(exc)) from exc


def fetch_text(url, timeout=20, max_bytes=8 * 1024 * 1024):
    return fetch_bytes(url, timeout, max_bytes).decode("utf-8", "replace")
