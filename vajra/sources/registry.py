from vajra.sources.lubuntu import LubuntuResolver
from vajra.sources.generic_page import OfficialPageResolver

RESOLVERS = {
    "lubuntu": LubuntuResolver(),
    "linux-mint-xfce": OfficialPageResolver(
        "linux-mint-xfce", "Linux Mint Xfce",
        "https://www.linuxmint.com/download.php"
    ),
    "mx-linux-xfce": OfficialPageResolver(
        "mx-linux-xfce", "MX Linux Xfce",
        "https://mxlinux.org/download-links/"
    ),
}

def get_resolver(distro_id):
    return RESOLVERS.get(distro_id)

def resolve_images(distro_id, architecture):
    resolver = get_resolver(distro_id)
    if resolver is None:
        return []
    return resolver.resolve(architecture)
