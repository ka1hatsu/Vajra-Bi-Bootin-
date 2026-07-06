from dataclasses import dataclass


class VerificationPolicyError(RuntimeError):
    pass


@dataclass(frozen=True)
class VerificationDecision:
    can_flash: bool
    state: str
    message: str


def evaluate_download_verification(expected_sha256, actual_sha256):
    expected = (expected_sha256 or "").strip().lower()
    actual = (actual_sha256 or "").strip().lower()

    if not expected:
        return VerificationDecision(
            False,
            "untrusted",
            "No trusted upstream SHA-256 is available; automatic flashing is disabled.",
        )

    if len(expected) != 64:
        return VerificationDecision(
            False,
            "invalid-metadata",
            "The upstream SHA-256 metadata is malformed; automatic flashing is disabled.",
        )

    if not actual:
        return VerificationDecision(
            False,
            "pending",
            "The image has not been verified yet.",
        )

    if expected != actual:
        return VerificationDecision(
            False,
            "mismatch",
            "Downloaded image checksum does not match trusted upstream metadata.",
        )

    return VerificationDecision(
        True,
        "verified",
        "SHA-256 verification passed. The image may be flashed.",
    )


def require_verified_download(expected_sha256, actual_sha256):
    decision = evaluate_download_verification(expected_sha256, actual_sha256)
    if not decision.can_flash:
        raise VerificationPolicyError(decision.message)
    return decision
