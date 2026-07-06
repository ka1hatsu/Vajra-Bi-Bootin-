import hashlib
from pathlib import Path


class VerificationCancelled(Exception):
    pass


def _hash(
    stream,
    limit,
    progress=None,
    cancel_check=None,
    chunk_size=1024 * 1024,
):
    digest = hashlib.sha256()
    done = 0

    while done < limit:
        if cancel_check and cancel_check():
            raise VerificationCancelled("Verification cancelled.")

        chunk = stream.read(min(chunk_size, limit - done))

        if not chunk:
            break

        digest.update(chunk)
        done += len(chunk)

        if progress:
            progress(done, limit)

    return digest.hexdigest(), done


def verify_written_image(
    image_path,
    device_path,
    progress_callback=None,
    cancel_check=None,
):
    image_path = Path(image_path)
    size = image_path.stat().st_size

    with image_path.open("rb") as image:
        image_hash, image_bytes = _hash(
            image,
            size,
            cancel_check=cancel_check,
        )

    with open(device_path, "rb", buffering=0) as device:
        device_hash, device_bytes = _hash(
            device,
            size,
            progress=progress_callback,
            cancel_check=cancel_check,
        )

    return (
        image_bytes == size
        and device_bytes == size
        and image_hash == device_hash
    )
