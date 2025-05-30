#!/usr/bin/env python3

import os
import sys
import subprocess

VFIO_CONF_PATH = "/etc/modprobe.d/vfio.conf"
XORG_CONF_PATH = "/etc/X11/xorg.conf.d/10-intel.conf"
INITRAMFS_CMD = "mkinitcpio -P"  # regenerate all presets

GPU_IDS = "10de:2783,10de:22bc"

HEADER = """
🧰 VFIO GPU Toggle Script (Arch Linux)
---------------------------------------
This script enables or disables NVIDIA GPU passthrough.
Ensure you've followed all setup steps (GRUB, mkinitcpio, vfio.conf).
Run this script as root (sudo).
"""

def check_root():
    if os.geteuid() != 0:
        print("❌ This script must be run with sudo or as root.")
        sys.exit(1)

def prompt():
    print(HEADER)
    print("Current PCI IDs set in script:", GPU_IDS)
    print("[1] Enable passthrough (bind GPU to vfio-pci)")
    print("[2] Disable passthrough (unbind GPU from vfio-pci)")
    return input("Enter choice [1/2]: ").strip()

def toggle_vfio(enable: bool):
    if not os.path.isfile(VFIO_CONF_PATH):
        print(f"⚠️ File not found: {VFIO_CONF_PATH}")
        print("Creating new vfio.conf...")
        with open(VFIO_CONF_PATH, 'w') as f:
            f.write(f"options vfio-pci ids={GPU_IDS}\n")
            f.write("softdep nvidia pre: vfio-pci\n")
        return

    with open(VFIO_CONF_PATH, 'r') as f:
        lines = f.readlines()

    out = []
    for line in lines:
        stripped = line.lstrip('#').strip()
        if not stripped:
            continue
        if enable:
            out.append(stripped + '\n')
        else:
            out.append('#' + stripped + '\n')

    with open(VFIO_CONF_PATH, 'w') as f:
        f.writelines(out)

def toggle_xorg(enable: bool):
    if enable:
        os.makedirs(os.path.dirname(XORG_CONF_PATH), exist_ok=True)
        with open(XORG_CONF_PATH, 'w') as f:
            f.write(
                'Section "Device"\n'
                '    Identifier "Intel GPU"\n'
                '    Driver "modesetting"\n'
                '    BusID  "PCI:0:2:0"\n'
                'EndSection\n'
            )
    else:
        if os.path.exists(XORG_CONF_PATH):
            os.remove(XORG_CONF_PATH)

def regenerate_initramfs():
    print("🔄 Regenerating initramfs...")
    subprocess.run(INITRAMFS_CMD, shell=True, check=True)

def main():
    check_root()
    choice = prompt()
    if choice not in ["1", "2"]:
        print("❌ Invalid input. Exiting.")
        sys.exit(1)

    enable = (choice == "1")
    toggle_vfio(enable)
    toggle_xorg(enable)
    regenerate_initramfs()

    print(f"\n✅ {'Enabled' if enable else 'Disabled'} VFIO passthrough.")
    print("💡 Please reboot for changes to take effect.")

if __name__ == "__main__":
    main()
