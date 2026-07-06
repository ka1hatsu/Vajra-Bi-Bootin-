#!/usr/bin/env python3
import argparse
import json
import os
import sys

from vajra.writer.devices import list_storage_devices
from vajra.writer.flash import write_image
from vajra.writer.session import TargetIdentity
from vajra.writer.unmount import unmount_partitions


def fail(message, code=1):
    print(json.dumps({"event": "error", "message": message}), flush=True)
    raise SystemExit(code)


def find_target(path):
    for device in list_storage_devices():
        if device["path"] == path:
            return device
    fail("Target device is not present.")


def validate_target(device, serial, size):
    if not device.get("eligible"):
        fail("Target is not an eligible removable device.")
    if device.get("system_disk"):
        fail("Refusing to write to the system disk.")
    if device.get("read_only"):
        fail("Target is read-only.")
    if serial and device.get("serial", "") != serial:
        fail("Target serial number changed.")
    if int(device.get("size_bytes", 0)) != int(size):
        fail("Target capacity changed.")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--serial", default="")
    parser.add_argument("--size", required=True, type=int)
    args=parser.parse_args()

    if os.geteuid() != 0:
        fail("Privileged writer helper must run as root.")

    if not os.path.isfile(args.image):
        fail("Image file does not exist.")

    device=find_target(args.device)
    validate_target(device,args.serial,args.size)

    if os.path.getsize(args.image) > device["size_bytes"]:
        fail("Image is larger than target device.")

    unmount_partitions(device)

    # Revalidate after unmount, immediately before opening the block device.
    device=find_target(args.device)
    validate_target(device,args.serial,args.size)

    print(json.dumps({"event":"stage","message":"writing"}),flush=True)

    def progress(done,total):
        percent=int(done*100/total) if total else 0
        print(json.dumps({"event":"progress","value":percent}),flush=True)

    write_image(args.image,args.device,progress_callback=progress)
    print(json.dumps({"event":"complete"}),flush=True)


if __name__ == "__main__":
    main()
