import urllib.request
from urllib.parse import urlparse

ALLOWED_DOWNLOAD_HOSTS = {
    "dl.fedoraproject.org",
    "download.fedoraproject.org",
    "fedoraproject.org",
    "cdimage.debian.org",
    "releases.ubuntu.com",
    "cdimage.ubuntu.com",
    "linuxmint.com",
    "www.linuxmint.com",
    "mirrors.kernel.org",
    "sourceforge.net",
    "downloads.sourceforge.net",
}

ALLOWED_DOWNLOAD_HOST_SUFFIXES = (
    ".dl.sourceforge.net",
)


def host_allowed(url):
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return host in ALLOWED_DOWNLOAD_HOSTS or any(
        host.endswith(suffix) and host != suffix.lstrip(".")
        for suffix in ALLOWED_DOWNLOAD_HOST_SUFFIXES
    )


def require_https(url):
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError("Resolver rejected a non-HTTPS source.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Resolver rejected a URL containing credentials.")
    return url


def validate_download_url(url):
    require_https(url)
    if not host_allowed(url):
        raise ValueError(f"Resolver rejected unapproved download host: {url}")
    return url


class SafeDownloadRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirect hops that leave Vajra's HTTPS download allowlist."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_download_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_SAFE_OPENER = urllib.request.build_opener(SafeDownloadRedirectHandler())


def open_download_url(request, timeout=30):
    url = request.full_url if isinstance(request, urllib.request.Request) else str(request)
    validate_download_url(url)
    return _SAFE_OPENER.open(request, timeout=timeout)
