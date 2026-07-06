import re
from urllib.parse import urljoin

from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import (
    Resolver,
    ResolverError,
    UnsupportedArchitecture,
)
from vajra.sources.checksums import parse_sha256sums
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url


class UbuntuFamilyResolver(Resolver):

    def __init__(
        self,
        distro_id,
        name,
        index_url,
        filename_prefix,
    ):
        self.distro_ids = (distro_id,)
        self.name = name
        self.index_url = index_url
        self.filename_prefix = filename_prefix


    def resolve(self, architecture):

        arch = normalize_architecture(architecture)

        if arch != "amd64":
            raise UnsupportedArchitecture(
                f"{self.name} desktop images are "
                f"not resolved for {arch}."
            )


        index = fetch_text(self.index_url)


        versions = sorted(
            set(
                re.findall(
                    r'href="(\d+\.\d+(?:\.\d+)?)/"',
                    index,
                )
            ),
            key=lambda version: tuple(
                int(part)
                for part in version.split(".")
            ),
            reverse=True,
        )


        errors = []


        for version in versions[:10]:

            candidate_pages = [

                # Ubuntu Desktop layout
                urljoin(
                    self.index_url,
                    version + "/",
                ),

                # Ubuntu flavour layout
                urljoin(
                    self.index_url,
                    version + "/release/",
                ),
            ]


            for page in candidate_pages:

                try:

                    html = fetch_text(page)


                    pattern = (
                        rf'href="('
                        rf'{re.escape(self.filename_prefix)}-'
                        rf'{re.escape(version)}-'
                        rf'desktop-amd64\.iso'
                        rf')"'
                    )


                    names = re.findall(
                        pattern,
                        html,
                    )


                    if not names:
                        continue


                    filename = names[0]


                    sums_url = urljoin(
                        page,
                        "SHA256SUMS",
                    )


                    sums = parse_sha256sums(
                        fetch_text(sums_url)
                    )


                    image_url = validate_download_url(
                        urljoin(
                            page,
                            filename,
                        )
                    )


                    return [
                        ReleaseImage(
                            distro=self.name,
                            version=version,
                            architecture="amd64",
                            image_url=image_url,
                            filename=filename,
                            sha256=sums.get(
                                filename,
                                "",
                            ),
                            checksum_url=sums_url,
                            source_page=page,
                        )
                    ]


                except Exception as error:

                    errors.append(
                        f"{version} @ {page}: {error}"
                    )


        raise ResolverError(
            f"No usable {self.name} image resolved. "
            + "; ".join(errors[:5])
        )
