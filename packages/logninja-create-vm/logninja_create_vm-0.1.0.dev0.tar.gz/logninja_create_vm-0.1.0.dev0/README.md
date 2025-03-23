# 🧰 logninja-create-vm

A secure, interactive CLI utility for creating virtual machines using `virt-install`, built for the **LOGGIE** decentralized infrastructure stack.

> 🔐 Part of the LogNinja Ecosystem  
> 👤 Maintained by: [loggie.eth](https://etherscan.io/address/0xF62E1F6193FD0b3d8eD7B3198915D3b0c9bd3f99)  
> 🪙 Powered by: [LOGGIE Token](https://sepolia.etherscan.io/token/0x0bDB1e28D64b080892c5A7f9D56b1F98E5Cbf576)

---

## 🚀 What is this?

This tool makes it easy to provision Ubuntu-based VMs on any machine running KVM/QEMU and `libvirt`. Perfect for:
- Building secure test environments
- Spawning decentralized AI workers
- Automating node deployment in a Docker Swarm cluster

---

## ⚙️ Features

- ✅ Interactive prompts for VM config
- ✅ Optional CLI flag automation
- ✅ Logging to both terminal and `vm_provision.log`
- ✅ Validates ISO path before provisioning
- ✅ Compatible with `virt-manager` and headless VNC

---

## 📦 Installation

```bash
pip install logninja-create-vm

```
## Flag	Description	Required
--name	Name of the VM	✅
--ram	RAM in MB	✅
--vcpus	Number of virtual CPUs	✅
--disk	Disk size in GB	✅
--iso	Path to ISO image	✅
--os-variant	OS variant (default: ubuntu22.04)	❌
--network	Network to attach to (default: default)	❌
