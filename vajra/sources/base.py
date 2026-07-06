class ResolverError(RuntimeError):
    pass

class UnsupportedArchitecture(ResolverError):
    pass

class Resolver:
    distro_ids = ()

    def resolve(self, architecture):
        raise NotImplementedError
