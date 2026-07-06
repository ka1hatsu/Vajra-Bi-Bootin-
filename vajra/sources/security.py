from urllib.parse import urlparse

ALLOWED_DOWNLOAD_HOSTS = {
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

def host_allowed(url):
    host = (urlparse(url).hostname or "").lower()
    return host in ALLOWED_DOWNLOAD_HOSTS

def require_https(url):
    if urlparse(url).scheme.lower() != "https":
        raise ValueError("Resolver rejected a non-HTTPS source.")
    return url

def validate_download_url(url):
    require_https(url)
    if not host_allowed(url):
        raise ValueError(f"Resolver rejected unapproved download host: {url}")
    return url
