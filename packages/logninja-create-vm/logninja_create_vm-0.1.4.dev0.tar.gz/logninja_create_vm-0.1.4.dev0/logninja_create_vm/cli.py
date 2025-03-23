import subprocess
import logging
import os
from pathlib import Path
from shutil import which
from datetime import datetime
import argparse

__version__ = "0.1.4-dev"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("vm_provision.log"),
        logging.StreamHandler()
    ]
)

def run_command(command):
    logging.info(f"Running: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info("✅ Command executed successfully.")
    except subprocess.CalledProcessError as e:
        if "libvirt-sock" in str(e):
            logging.critical(
                "\n💥 Libvirt daemon is not installed or not running.\n"
                "👉 To fix it, run:\n\n"
                "   sudo apt install -y libvirt-daemon-system libvirt-clients\n"
                "   sudo systemctl enable --now libvirtd\n"
            )
        elif "Disk" in str(e) and "is already in use" in str(e):
            logging.critical(
                "\n💥 Disk is still associated with an existing guest.\n"
                "👉 Try using a different VM name or manually remove the leftover VM:\n\n"
                "   sudo virsh destroy <vm-name>\n"
                "   sudo virsh undefine <vm-name>\n"
            )
        else:
            logging.error(f"❌ Failed: {e}")
        raise

def ensure_virt_install_installed():
    if not which("virt-install"):
        logging.warning("⚠️  'virt-install' not found. Installing now...")
        run_command("sudo apt update && sudo apt install -y virtinst")
    else:
        logging.info("✅ 'virt-install' is already installed.")

def display_guide():
    guide_text = """
    📝 **Post-Installation Guide:**

    1. **Snapshot Your VM**:
       After creating the VM, you can take a snapshot to preserve its current state. 
       This is helpful for rollback or creating a backup.
       ```bash
       sudo virsh snapshot-create-as <vm-name> <snapshot-name>
       ```

    2. **Backup the VM Image**:
       It's always a good idea to backup the VM disk image before proceeding with further changes.
       ```bash
       sudo cp /var/lib/libvirt/images/<vm-name>.qcow2 /var/backups/<vm-name>.qcow2
       ```

    3. **Join Docker Swarm**:
       After installation, you may want to join the VM to a Docker Swarm for orchestration.
       SSH into the VM and run:
       ```bash
       docker swarm join ...
       ```

    4. **Reconnecting to the VM Console**:
       If you need to interact with the VM's text-based console (especially useful for headless VMs), use the following command:
       ```bash
       sudo virsh console <vm-name>
       ```

    5. **Manage Your VM**:
       Here are some other useful commands to manage the VM lifecycle:
       
       - **Start the VM**:
         ```bash
         sudo virsh start <vm-name>
         ```

       - **Shutdown the VM gracefully**:
         ```bash
         sudo virsh shutdown <vm-name>
         ```

       - **Force stop the VM** (if it doesn't respond to shutdown):
         ```bash
         sudo virsh destroy <vm-name>
         ```

       - **Delete the VM configuration** (keeps disk unless manually removed):
         ```bash
         sudo virsh undefine <vm-name>
         ```

    """
    print(guide_text)

def create_vm_interactive():
    ensure_virt_install_installed()

    print("\n🛡️  LOGNINJA VM Provisioning")
    print("🔧 Interactive Mode")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    name = input("🖥️  VM Name: ").strip() or f"logninja-vm-{timestamp}"
    ram = input("💾 RAM (MB) [2048]: ").strip() or "2048"
    vcpus = input("🧠 VCPUs [2]: ").strip() or "2"
    iso_path = input("📀 ISO Path [/var/lib/libvirt/images/ubuntu-22.04.iso]: ").strip() or "/var/lib/libvirt/images/ubuntu-22.04.iso"
    disk_size = input("🗃️  Disk Size (GB) [20]: ").strip() or "20"
    os_variant = input("🐧 OS Variant [ubuntu22.04]: ").strip() or "ubuntu22.04"
    network = input("🌐 Network [default]: ").strip() or "default"
    headless = input("🕶️  Headless mode? [y/N]: ").strip().lower() == "y"
    tag = input("🏷️  Optional tag (e.g. logninja): ").strip()

    disk_path = f"/var/lib/libvirt/images/{name}.qcow2"

    if not Path(iso_path).exists():
        logging.critical(f"❌ ISO not found at {iso_path}")
        return

    if Path(disk_path).exists():
        confirm = input(f"⚠️  Disk {disk_path} already exists. Delete and recreate it? (Y/n): ").strip().lower()
        if confirm == "y" or confirm == "":
            logging.info(f"🧹 Deleting existing disk: {disk_path}")
            try:
                run_command(f"virsh destroy {name} || true")
                run_command(f"virsh undefine {name} || true")
                run_command(f"sudo rm -f {disk_path}")
            except Exception as ex:
                logging.error(f"❌ Could not remove old VM or disk: {ex}")
                return
        else:
            logging.info("❌ Aborting VM creation.")
            return

    graphics_flag = "--graphics none" if headless else "--graphics vnc"

    cmd = (
        f"sudo virt-install "
        f"--name={name} "
        f"--ram={ram} "
        f"--vcpus={vcpus} "
        f"--os-variant={os_variant} "
        f"--cdrom={iso_path} "
        f"--disk size={disk_size},path={disk_path} "
        f"--network network={network} "
        f"{graphics_flag} "
        f"--noautoconsole"
    )

    try:
        run_command(cmd)
        if tag:
            logging.info(f"🏷️  VM '{name}' tagged as: {tag}")
        logging.info("📦 To snapshot: sudo virsh snapshot-create-as {name} {name}-init")
        logging.info("🔄 To backup image: sudo cp {disk_path} /var/backups/{name}.qcow2")
        logging.info("🐳 To join Docker Swarm inside the VM, use SSH and run 'docker swarm join ...'")
    except Exception as ex:
        logging.critical(f"💥 VM creation failed: {ex}")

def main():
    parser = argparse.ArgumentParser(description="🚀 LogNinja VM Provisioner")
    parser.add_argument('--name', help="VM name", required=False)
    parser.add_argument('--ram', type=int, help="RAM in MB", required=False)
    parser.add_argument('--vcpus', type=int, help="Number of CPUs", required=False)
    parser.add_argument('--disk', type=int, help="Disk size in GB", required=False)
    parser.add_argument('--iso', help="Path to ISO file", required=False)
    parser.add_argument('--os-variant', default="ubuntu22.04", help="OS variant")
    parser.add_argument('--network', default="default", help="Network to attach")
    parser.add_argument('--version', action='store_true', help="Show version and exit")
    parser.add_argument('--guide', action='store_true', help="Show the VM creation guide")

    args = parser.parse_args()

    if args.version:
        print(f"🔖 logninja_create_vm version {__version__}")
        return

    if args.guide:
        display_guide()
        return

    create_vm_interactive()

if __name__ == "__main__":
    main()
