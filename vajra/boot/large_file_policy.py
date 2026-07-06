class LargeFilePolicyError(ValueError): pass

def choose_strategy(info,fs):
    if info["fat32_compatible"]: return "direct_extract"
    if fs=="FAT32" and info["windows_install_media"]: return "split_windows_wim"
    if fs=="FAT32": raise LargeFilePolicyError("ISO contains a file larger than FAT32 supports. Use raw mode or another supported backend.")
    return "direct_extract"
