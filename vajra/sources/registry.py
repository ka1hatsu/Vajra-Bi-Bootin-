from vajra.sources.lubuntu import LubuntuResolver
from vajra.sources.ubuntu_family import UbuntuFamilyResolver
from vajra.sources.debian import DebianXfceResolver
from vajra.sources.mint import LinuxMintXfceResolver
from vajra.sources.mxlinux import MXLinuxXfceResolver
from vajra.sources.fedora import FedoraWorkstationResolver

RESOLVERS={
    "lubuntu":LubuntuResolver(),
    "ubuntu":UbuntuFamilyResolver("ubuntu","Ubuntu Desktop","https://releases.ubuntu.com/","ubuntu"),
    "xubuntu":UbuntuFamilyResolver("xubuntu","Xubuntu","https://cdimage.ubuntu.com/xubuntu/releases/","xubuntu"),
    "debian-xfce":DebianXfceResolver(),
    "linux-mint-xfce":LinuxMintXfceResolver(),
    "mx-linux-xfce":MXLinuxXfceResolver(),
    "fedora-workstation":FedoraWorkstationResolver(),
}

OFFICIAL_FALLBACK_PAGES={
    "lubuntu":"https://lubuntu.me/downloads/",
    "ubuntu":"https://ubuntu.com/download/desktop",
    "xubuntu":"https://xubuntu.org/download/",
    "debian-xfce":"https://www.debian.org/CD/live/",
    "linux-mint-xfce":"https://www.linuxmint.com/download.php",
    "mx-linux-xfce":"https://mxlinux.org/download-links/",
    "fedora-workstation":"https://fedoraproject.org/workstation/download/",
}

def get_resolver(distro_id): return RESOLVERS.get(distro_id)
def get_official_fallback(distro_id): return OFFICIAL_FALLBACK_PAGES.get(distro_id,"")
def resolve_images(distro_id,architecture):
    resolver=get_resolver(distro_id)
    return [] if resolver is None else resolver.resolve(architecture)
