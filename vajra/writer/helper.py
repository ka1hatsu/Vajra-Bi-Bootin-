#!/usr/bin/env python3
import argparse,json,os
from vajra.writer.devices import list_storage_devices
from vajra.writer.flash import write_image
from vajra.writer.unmount import unmount_partitions
from vajra.writer.verify import verify_written_image

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
    a=p.parse_args()
    if os.geteuid()!=0:fail("Helper must run as root.")
    if not os.path.isfile(a.image):fail("Image file does not exist.")
    d=find(a.device); validate_target(d, a.serial, a.size)
    if os.path.getsize(a.image)>d["size_bytes"]:fail("Image is larger than target.")
    emit("stage",message="Unmounting target partitions..."); unmount_partitions(d)
    d=find(a.device); validate_target(d, a.serial, a.size)
    emit("stage",message="Writing image...")
    write_image(a.image,a.device,lambda x,t:emit("progress",value=int(x*80/t) if t else 0))
    emit("stage",message="Verifying written data...")
    ok=verify_written_image(a.image,a.device,lambda x,t:emit("progress",value=80+int(x*20/t) if t else 80))
    if not ok:fail("Post-write verification failed.")
    emit("progress",value=100); emit("complete")
if __name__=="__main__":main()
