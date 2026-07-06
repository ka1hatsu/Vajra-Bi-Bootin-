from vajra.sources.registry import RESOLVERS
from vajra.sources.mint import LinuxMintXfceResolver
from vajra.sources.mxlinux import MXLinuxXfceResolver
from vajra.sources.fedora import FedoraWorkstationResolver

def test_dedicated_phase85_resolvers():
    assert isinstance(RESOLVERS["linux-mint-xfce"],LinuxMintXfceResolver)
    assert isinstance(RESOLVERS["mx-linux-xfce"],MXLinuxXfceResolver)
    assert isinstance(RESOLVERS["fedora-workstation"],FedoraWorkstationResolver)
