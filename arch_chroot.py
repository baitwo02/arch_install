import re
import os
import json
import fileinput


with open("./config.json", "r", encoding="utf8") as config_file:
    config_data = json.load(config_file)

# set timezone
os.system(f"ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime")
os.system(f"hwclock --systohc")

# set lang
for line in fileinput.input('/etc/locale.gen', inplace=True):
    if re.match(r'^#\s*en_US\.UTF-8\s+UTF-8$', line):
        line = re.sub(r'^#\s*', '', line)
    elif re.match(r'^#\s*en_GB\.UTF-8\s+UTF-8$', line):
        line = re.sub(r'^#\s*', '', line)
    elif re.match(r'^#\s*zh_CN\.UTF-8\s+UTF-8$', line):
        line = re.sub(r'^#\s*', '', line)
    print(line, end='')

os.system(f"locale-gen")

locale_conf = """\
LANG=en_GB.UTF-8
"""

with open(r"/etc/locale.conf", "a", encoding="utf-8") as f:
    f.write(locale_conf)

hostname = config_data["hostname"]
with open(r"/etc/hostname", "a", encoding="utf-8") as f:
    f.write(hostname)

hosts = """\
127.0.0.1    localhost
::1          localhost ip6-localhost ip6-loopback
"""
with open(r"/etc/hosts", "a", encoding="utf-8") as f:
    f.write(hostname)

# add btrfs to mkinitcpio modules
for line in fileinput.input('/etc/mkinitcpio.conf', inplace=True):
    if re.match(r'^MODULES=\(.*\)$', line):
        line = re.sub(r'\((.*?)\)', r'(btrfs \1)', line.rstrip()) + '\n'
    print(line, end='')

os.system(f"mkinitcpio -P")

os.system(f"pacman --noconfirm -S grub efibootmgr")
os.system(f"grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB")
os.system(f"grub-mkconfig -o /boot/grub/grub.cfg")

# add a normal user
username = config_data["username"]
os.system(f"useradd -m -G wheel {username}")
os.system(f"chsh -s /usr/bin/fish")
os.system(f"chsh -s /usr/bin/fish {username}")

# link nvim to vi, vim and nano
os.system(f"ln -sf /usr/bin/nvim /usr/bin/vi")
os.system(f"ln -sf /usr/bin/nvim /usr/bin/vim")
os.system(f"ln -sf /usr/bin/nvim /usr/bin/nano")

# add user  to sudoers
for line in fileinput.input("/etc/sudoers", inplace=True):
    if re.match(r'^#\s*%wheel\s+ALL=\(ALL:ALL\)\s+ALL$', line):
        line = line.lstrip('#').lstrip()
    print(line, end='')

# setting password for user and root
username = config_data["username"]
root_passwd = config_data["root_passwd"]
user_passwd = config_data["user_passwd"]
os.system("echo '{}:{}' | chpasswd".format("root", root_passwd))
os.system("echo '{}:{}' | chpasswd".format(username, user_passwd))
