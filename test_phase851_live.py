from vajra.sources.service import ResolverService
service=ResolverService()
for distro in ("mx-linux-xfce","fedora-workstation"):
    print("\n===",distro,"===")
    try:
        for image in service.resolve(distro,"x86_64",refresh=True):
            print("Version:",image.version); print("File:",image.filename)
            print("URL:",image.image_url); print("SHA256:",image.sha256 or "not supplied by resolver")
    except Exception as e: print("Resolver error:",e)
