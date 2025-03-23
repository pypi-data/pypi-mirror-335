import subprocess
import os
import logging
import argparse
from pathlib import Path

__version__ = "v0.1.3-dev"

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
        logging.error(f"❌ Failed: {e}")
        raise

def download_iso(iso_path):
    url = "https://releases.ubuntu.com/22.04/ubuntu-22.04.4-live-server-amd64.iso"
    logging.info(f"🌐 Downloading Ubuntu ISO from {url}...")
    os.makedirs(os.path.dirname(iso_path), exist_ok=True)
    run_command(f"sudo wget -O {iso_path} {url}")

def validate_iso(iso_path):
    if not Path(iso_path).exists():
        logging.warning(f"📁 ISO not found at {iso_path}")
        download = input("❓ ISO not found. Download it now? [Y/n]: ").strip().lower() or "y"
        if download == "y":
            download_iso(iso_path)
        else:
            raise FileNotFoundError("❌ Cannot continue without ISO.")

def create_vm(args):
    validate_iso(args.iso)

    disk_path = f"/var/lib/libvirt/images/{args.name}.qcow2"

    virt_cmd = (
        f"sudo virt-install "
        f"--name={args.name} "
        f"--ram={args.ram} "
        f"--vcpus={args.vcpus} "
        f"--os-variant={args.os_variant} "
        f"--cdrom={args.iso} "
        f"--disk size={args.disk},path={disk_path} "
        f"--network network={args.network} "
        f"--graphics vnc "
        f"--noautoconsole"
    )

    run_command(virt_cmd)

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

    args = parser.parse_args()

    if args.version:
        print(f"🔖 logninja_create_vm version {__version__}")
        return

    # Prompt interactively if not passed
    if not args.name:
        args.name = input("🖥️  Enter VM name: ").strip()
    if not args.ram:
        args.ram = int(input("💾 RAM (MB): ").strip())
    if not args.vcpus:
        args.vcpus = int(input("🧠 Number of vCPUs: ").strip())
    if not args.disk:
        args.disk = int(input("🗄️  Disk size (GB): ").strip())
    if not args.iso:
        args.iso = input("📀 Path to ISO file: ").strip()

    try:
        create_vm(args)
    except Exception as ex:
        logging.critical(f"💥 VM creation failed: {ex}")

if __name__ == "__main__":
    main()
