#!/usr/bin/env python3
import argparse,json,os,signal
from vajra.writer.devices import list_storage_devices
from vajra.writer.flash import write_image
from vajra.writer.unmount import unmount_partitions
from vajra.writer.verify import verify_written_image
from types import SimpleNamespace
from vajra.boot.prepared_helper import prepare_fat32_media, PreparedMediaError

_cancel_requested=False

def request_cancel(signum, frame):
    global _cancel_requested
    _cancel_requested=True

def cancel_requested():
    return _cancel_requested

signal.signal(signal.SIGTERM, request_cancel)
signal.signal(signal.SIGINT, request_cancel)

def emit(event,**fields): print(json.dumps({"event":event,**fields}),flush=True)
def fail(msg): emit("error",message=msg); raise SystemExit(1)
def find(path):
    for d in list_storage_devices():
        if d["path"]==path:return d
    fail("Target device is not present.")
def validate_target(d, serial, size):
    if not d.get("eligible") or d.get("system_disk"):fail("Target failed removable-device safety checks.")
    if d.get("read_only"):fail("Target is read-only.")
    if serial and d.get("serial","")!=serial:fail("Target serial number changed.")
    if int(d.get("size_bytes",0))!=size:fail("Target capacity changed.")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--image",required=True); p.add_argument("--device",required=True)
    p.add_argument("--serial",default=""); p.add_argument("--size",required=True,type=int)
    p.add_argument("--mode", default="raw")
    p.add_argument("--scheme", default="Auto")
    p.add_argument("--target-system", default="Auto")
    p.add_argument("--file-system", default="Auto")
    p.add_argument("--volume-label", default="VAJRA_BOOT")
    a=p.parse_args()
    if os.geteuid()!=0:fail("Helper must run as root.")
    if not os.path.isfile(a.image):fail("Image file does not exist.")
    d=find(a.device); validate_target(d, a.serial, a.size)
    if os.path.getsize(a.image)>d["size_bytes"]:fail("Image is larger than target.")
    emit("stage",message="Unmounting target partitions..."); unmount_partitions(d)
    d=find(a.device); validate_target(d, a.serial, a.size)
    if a.mode == "prepared_fat32":
        plan = SimpleNamespace(
            partition_scheme=a.scheme,
            target_system=a.target_system,
            file_system=a.file_system,
            volume_label=a.volume_label,
        )
        try:
            prepare_fat32_media(
                a.image, a.device, plan,
                progress=lambda value, message: (
                    emit("stage", message=message),
                    emit("progress", value=value),
                ),
                cancel_check=cancel_requested,
            )
        except PreparedMediaError as e:
            fail(str(e))
        emit("complete")
        return

    emit("stage",message="Writing image...")
    write_image(a.image,a.device,lambda x,t:emit("progress",value=int(x*80/t) if t else 0))
    emit("stage",message="Verifying written data...")
    ok=verify_written_image(a.image,a.device,lambda x,t:emit("progress",value=80+int(x*20/t) if t else 80))
    if not ok:fail("Post-write verification failed.")
    emit("progress",value=100); emit("complete")
if __name__=="__main__":main()
