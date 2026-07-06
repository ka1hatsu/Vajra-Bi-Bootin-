from vajra.sources.service import ResolverService

image = ResolverService().resolve(
    "mx-linux-xfce",
    "x86_64",
    refresh=True,
)[0]

print("Distro:", image.distro)
print("Version:", image.version)
print("File:", image.filename)
print("URL:", image.image_url)
print("Checksum URL:", image.checksum_url)
print("SHA256:", image.sha256)

assert len(image.sha256) == 64
print("MX trusted checksum resolution: PASS")
