from vajra.sources.registry import RESOLVERS,OFFICIAL_FALLBACK_PAGES
EXPECTED={"lubuntu","linux-mint-xfce","mx-linux-xfce","xubuntu","fedora-workstation","ubuntu","debian-xfce"}
def test_registry_complete(): assert EXPECTED <= set(RESOLVERS)
def test_fallbacks_complete(): assert EXPECTED <= set(OFFICIAL_FALLBACK_PAGES)
