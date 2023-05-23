import os
import json

with open("./config.json", "r", encoding="utf8") as config_file:
    config_data = json.load(config_file)


disk = config_data["disk"]
efi_size = config_data["efi_size"]
swap_size = config_data["swap_size"] + efi_size

# partition the disks
os.system(f"parted {disk} mklabel gpt")
os.system(f"parted {disk} mkpart primary 0GB {efi_size}GB")
os.system(f"parted {disk} mkpart primary {efi_size}GB {swap_size}GB")
os.system(f"parted {disk} mkpart primary {swap_size}GB 100%")

efi_partition = disk + "p1"
swap_partition = disk + "p2"
root_partition = disk + "p3"

# format the partitions
os.system(f"mkfs.fat -F 32 {efi_partition}")
os.system(f"mkswap {swap_partition}")
os.system(f"mkfs.btrfs {root_partition}")

# mount the btrfs file systems
os.system(f"mount {root_partition} /mnt")
os.system(f"btrfs subvolume create /mnt/@")
os.system(f"btrfs subvolume create /mnt/@home")
os.system(f"btrfs subvolume create /mnt/@log")
os.system(f"btrfs subvolume create /mnt/@pkg")
os.system(f"umount {root_partition}")

# mount the subvol of btrfs
os.system(f"mount {root_partition} /mnt -o subvol=@,noatime,discard=async,compress=zstd")
os.system(f"mkdir /mnt/home")
os.system(f"mount {root_partition} /mnt/home -o subvol=@home,noatime,discard=async,compress=zstd")
os.system(f"mkdir -p /mnt/var/log")
os.system(f"mount {root_partition} /mnt/var/log -o subvol=@log,noatime,discard=async,compress=zstd")
os.system(f"mkdir -p /mnt/var/cache/pacman/pkg")
os.system(f"mount {root_partition} /mnt/var/cache/pacman/pkg -o subvol=@pkg,noatime,discard=async,compress=zstd")

# mount the other file systems
os.system(f"mkdir /mnt/boot")
os.system(f"mount {efi_partition} /mnt/boot")
os.system(f"swapon {swap_partition}")

# install essential packages
ucode = config_data["ucode"]
os.system(f"pacstrap -K /mnt base base-devel linux linux-firmware {ucode} btrfs-progs git neovim python fish")

# fstab
os.system(f"genfstab -U /mnt >> /mnt/etc/fstab")

# chroot
os.system(f"arch-chroot /mnt")
