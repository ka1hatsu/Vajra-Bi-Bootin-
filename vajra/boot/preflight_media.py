from dataclasses import dataclass
from vajra.boot.backend import check_backend_available
from vajra.boot.iso_inspector import inspect_iso
from vajra.boot.large_file_policy import choose_strategy, LargeFilePolicyError

class MediaPreflightError(RuntimeError): pass

@dataclass(frozen=True)
class MediaPreflightResult:
    extracted_bytes:int
    required_bytes:int
    strategy:str
    windows_install_media:bool
    large_file_count:int
    summary:str

def estimate_required_bytes(files,overhead_ratio=0.08,reserve_bytes=256*1024**2):
    total=sum(max(0,int(size)) for _,size in files)
    return int(total*(1.0+overhead_ratio))+reserve_bytes

def run_media_preflight(image,target_size_bytes,plan):
    check_backend_available(plan)
    info=inspect_iso(image)
    files=info.get("files",[])
    extracted=sum(max(0,int(size)) for _,size in files)
    required=estimate_required_bytes(files)
    try: strategy=choose_strategy(info,plan.file_system)
    except LargeFilePolicyError as e: raise MediaPreflightError(str(e)) from e
    if required>int(target_size_bytes):
        raise MediaPreflightError(f"Estimated requirement is {required} bytes but selected USB reports {target_size_bytes} bytes.")
    summary=(f"Estimated extracted data: {extracted} bytes\n"
             f"Estimated required capacity: {required} bytes\n"
             f"Large files: {len(info['large_files'])}\n"
             f"Strategy: {strategy}")
    return MediaPreflightResult(extracted,required,strategy,info["windows_install_media"],len(info["large_files"]),summary)
