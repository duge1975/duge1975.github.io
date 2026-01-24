---
title: eweOS在QEMU中的安装
date: 2026-01-24
slug: eweos-qemu-installation
---

## 介绍
这是我在QEMU中安装eweOS的过程。

## 安装教程
创建一个 20GB 的虚拟磁盘（QEMU Copy-On-Write version 2，qcow2格式，支持快照和压缩）：

```bash
qemu-img create -f qcow2 eweos-disk.qcow2 20G
```

按照eweOS官网命令运行eweOS的live iso：

```bash
VCPU=4
VRAM=8G
DISK=eweos-disk.qcow2
ISO=eweos-x86_64-liveimage-desktop-xfce.iso

sudo qemu-system-x86_64 \
	-smp $VCPU -m $VRAM -cpu host \
	-machine type=q35,accel=kvm \
	-drive file=$DISK,format=qcow2,if=virtio,id=disk0 \
	-cdrom $ISO \
	-drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd \
	-vga virtio -display gtk \
	-device virtio-net,netdev=ewe -netdev user,id=ewe,hostfwd=tcp:127.0.0.1:10022-:22 \
	-device ac97 \
	-device qemu-xhci,id=xhci \
	-device usb-tablet,bus=xhci.0 \
	-device usb-kbd,bus=xhci.0
```

启动后，打开终端，修改/etc/pacman.d/mirrorlist，修改镜像，我这里改成了nju的镜像，根据情况自己选择：

```bash
Server = https://mirrors.nju.edu.cn/eweos/$repo/os/$arch
```
更新pacman数据库：

```bash
sudo pacman -Syu
```

安装必要的软件包：

```bash
sudo pacman -S dosfstools e2fsprogs
```

使用 `lsblk` 查看磁盘分区情况，会看到/dev/vda即为虚拟磁盘：

```bash
/dev/vda 20G
```

然后运行`sudo cfdisk /dev/vda`来对虚拟磁盘进行分区，我这里分了两个分区：

- /dev/vda1 ：EFI System，FAT32 格式，用于引导，512M

- /dev/vda2 ：Linux filesystem，ext4 格式，用于根文件系统，剩余空间

格式化分区：

```bash
sudo mkfs.fat -F32 /dev/vda1
sudo mkfs.ext4 /dev/vda2
```

挂载分区：

```bash
sudo mount /dev/vda2 /mnt
sudo mkdir -p /mnt/boot
sudo mount /dev/vda1 /mnt/boot
```

使用 pacstrap 安装基本系统，Pacstrap 是用于在 Arch Linux 安装过程中引导系统安装的工具。它用于将基础系统软件包安装到指定的目录（通常是挂载的目标分区）：

```bash
sudo pacstrap /mnt base-baremetal linux efibootmgr e2fsprogs
```

进入 chroot 环境配置系统

```bash
sudo arch-chroot /mnt
```

修复 tinyramfs 配置

```bash
/etc/tinyramfs/config
hooks="mdev"
rootfs_type="ext4"
root="UUID=根文件分区的UUID(blkid /dev/vda2)"
compress="zstd"
```

安装 limine 引导程序

```bash
limine-install /boot --removable
limine-mkconfig -o /boot/limine.conf
```

创建用户 ewe

```bash
adduser -D ewe
adduser ewe wheel
passwd ewe
passwd root
```

退出 chroot 环境

```bash
exit
sudo umount --recursive /mnt
```

启动eweOS

```bash
VCPU=4
VRAM=8G
DISK=eweos-disk.qcow2
sudo qemu-system-x86_64 \
	-smp $VCPU -m $VRAM -cpu host \
	-machine type=q35,accel=kvm \
	-drive file=$DISK,format=qcow2,if=virtio,id=disk0 \
	-drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd \
	-vga virtio -display gtk \
	-device virtio-net,netdev=ewe -netdev user,id=ewe,hostfwd=tcp:127.0.0.1:10022-:22 \
	-device ac97 \
	-device qemu-xhci,id=xhci \
	-device usb-tablet,bus=xhci.0 \
	-device usb-kbd,bus=xhci.0
```

使用scp将文件传到qemu中

```bash
scp -P 10022 /home/duge/eweOS/*.zip ewe@127.0.0.1:/home/ewe/
```