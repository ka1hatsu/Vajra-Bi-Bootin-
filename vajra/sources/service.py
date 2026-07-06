from vajra.architecture.normalize import normalize_architecture
from vajra.sources.cache import ResolverCache
from vajra.sources.registry import resolve_images

class ResolverService:
    def __init__(self, cache=None):
        self.cache = cache or ResolverCache()

    def resolve(self, distro_id, architecture, refresh=False):
        arch = normalize_architecture(architecture)
        key = f"{distro_id}:{arch}"
        if not refresh:
            cached = self.cache.get(key)
            if cached is not None:
                return cached
        images = resolve_images(distro_id, arch)
        if images:
            self.cache.put(key, images)
        return images
