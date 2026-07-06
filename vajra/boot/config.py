from dataclasses import dataclass
PARTITION_SCHEMES=("Auto","GPT","MBR")
TARGET_SYSTEMS=("Auto","UEFI","BIOS / Legacy","UEFI + CSM")
FILE_SYSTEMS=("Auto","FAT32","NTFS","exFAT")
IMAGE_OPTIONS=("Auto","Raw image write","Extract ISO to prepared USB")
@dataclass(frozen=True)
class BootConfig:
    partition_scheme:str="Auto"
    target_system:str="Auto"
    file_system:str="Auto"
    image_option:str="Auto"
    volume_label:str=""
    def validate(self):
        if self.partition_scheme not in PARTITION_SCHEMES: raise ValueError("Unsupported partition scheme.")
        if self.target_system not in TARGET_SYSTEMS: raise ValueError("Unsupported target system.")
        if self.file_system not in FILE_SYSTEMS: raise ValueError("Unsupported file system.")
        if self.image_option not in IMAGE_OPTIONS: raise ValueError("Unsupported image option.")
        if self.image_option in ("Auto","Raw image write") and any(x!="Auto" for x in (self.partition_scheme,self.target_system,self.file_system)):
            raise ValueError("Raw image mode preserves the image layout. Keep Partition Scheme, Target System and File System on Auto. Custom preparation backends come in later Phase 7 steps.")
        return True
