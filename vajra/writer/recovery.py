from dataclasses import dataclass

@dataclass(frozen=True)
class RecoveryAssessment:
    state: str
    message: str
    safe_to_retry: bool

def assess_interruption(last_stage):
    stage=(last_stage or "").lower()
    if not stage or stage in {"ready","preflight","validating target"}:
        return RecoveryAssessment("likely_untouched","Writing had not started. Refresh the device list before retrying.",True)
    markers=("partition","format","extract","copy","sync","writ","verify","mount")
    if any(x in stage for x in markers):
        return RecoveryAssessment("incomplete_media","The USB may contain incomplete or inconsistent data. Refresh device state before retrying or reformatting.",False)
    return RecoveryAssessment("unknown","The final device state could not be determined. Refresh device state before another operation.",False)
