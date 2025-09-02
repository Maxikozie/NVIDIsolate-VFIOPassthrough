# Isolate NVIDIA GPU for VFIO Passthrough (Arch Linux)

This guide helps you identify your NVIDIA GPU's PCI IDs, enable IOMMU, configure VFIO, and confirm the GPU is detached from the host OS.

---

### Optional: Automate Binding/Unbinding with Python Script

Once you’ve successfully followed this guide, you can use a Python script to **automatically bind or unbind your NVIDIA GPU** from the host system with a simple command-line toggle.

➡️ [View the script here](https://github.com/Maxikozie/NVIDIsolate-VFIOPassthrough/blob/main/gpu-vfio-toggle.py) 

Make it executable and run with `sudo`:

```bash
chmod +x gpu-vfio-toggle.py
sudo ./gpu-vfio-toggle.py
```

This saves you from manually editing config files and regenerating initramfs every time.

---

##  Prerequisites:


###  Dual GPU Requirement

Your computer **must have two GPUs**:
→ a **dedicated GPU** (e.g. NVIDIA 4070)
→ and an **integrated GPU (iGPU)** (like Intel or AMD iGPU)

> ❗ Without both, GPU passthrough to a VM will not work — the host needs a separate GPU to stay usable.


###  Virtualization

Before starting, ensure your CPU supports virtualization and that it's **enabled in your BIOS**.

You must have:

* **AMD-V** (for AMD CPUs), or
* **VT-x** (for Intel CPUs)

### Check if it's enabled:

Run:

```bash
lscpu | grep "Virtualization"
```

**Expected output:**

```
Virtualization:   AMD-V   # or "VT-x" for Intel
```

If you see nothing or it's blank:

* **Reboot your machine**
* Enter BIOS/UEFI (usually by pressing `F2`, `Del`, or `Esc`)
* Enable **SVM Mode** (for AMD) or **Intel VT-x**

---


##  Step 1: Identify PCI IDs

Run the following command to list NVIDIA devices with their PCI IDs:

```bash
lspci -nn | grep -E "NVIDIA"
```

**Example output:**

```
01:00.0 VGA compatible controller [0300]: NVIDIA Corporation AD104 [GeForce RTX 4070 SUPER] [10de:2783] (rev a1)
01:00.1 Audio device [0403]: NVIDIA Corporation AD104 High Definition Audio Controller [10de:22bc] (rev a1)
```

Extract the PCI IDs from the output. In this example:

```
10de:2783,10de:22bc
```

Copy and save these values into a text editor.

---

##  Step 2: Enable IOMMU

### Edit GRUB config:

```bash
sudo nano /etc/default/grub
```

Find the line that starts with:

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
```

**Replace it with:**

```bash
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu=pt vfio-pci.ids=XXXX:XXXX,XXXX:XXXX"
```
XXXX:XXXX,XXXX:XXXX = Your PCI IDs

Remove `quiet splash` if present.

> For AMD users, use `amd_iommu=on` instead of `intel_iommu=on`.

---

### Reload GRUB:

```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

---

### Reboot:

```bash
sudo reboot
```

---

##  Step 3: Isolate GPU from Host

### Create VFIO config file:

```bash
sudo touch /etc/modprobe.d/vfio.conf
sudo nano /etc/modprobe.d/vfio.conf
```

**Add the following content (replace IDs if needed):**

```bash
options vfio-pci ids=10de:2783,10de:22bc
softdep nvidia pre: vfio-pci
```

---

### Regenerate initramfs:
Arch
```bash
sudo mkinitcpio -p linux
```
> For other non-Arch LinuxOS users, use `sudo update-initramfs -c -k $(uname -r)`
---

### Reboot again:

```bash
sudo reboot
```

---

## Step 4: Confirm VFIO Driver is in Use

Run the following to check kernel drivers in use:

```bash
lspci -k | grep -E "vfio-pci|NVIDIA"
```

**Expected output snippet:**

```
Kernel driver in use: vfio-pci
Kernel driver in use: vfio-pci
```


