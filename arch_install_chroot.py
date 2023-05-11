import fileinput
import re
import os
import json


with open("./config.json", "r", encoding="utf8") as config_file:
    config_data = json.loads(config_file)

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
::1             localhost ip6-localhost ip6-loopback
"""
with open(r"/etc/hosts", "a", encoding="utf-8") as f:
    f.write(hostname)

# add btrfs to mkinitcpio modules
for line in fileinput.input('/etc/mkinitcpio.conf', inplace=True):
    if re.match(r'^MODULES=\(.*\)$', line):
        line = re.sub(r'\((.*?)\)', r'(btrfs \1)', line.rstrip()) + '\n'
    print(line, end='')

os.system(f"mkinitcpio -P")

os.system(f"pacman -S grub efibootmgr")
os.system(f"grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB")
os.system(f"grub-mkconfig -o /boot/grub/grub.cfg")

# add a normal user
username = config_data["user_name"]
os.system(f"useradd -m -G wheel -s /bin/fish user")
os.system(f"chsh -s /usr/bin/fish")

#set passwd
user_passwd = config_data["user_passwd"]
root_passwd = config_data["root_passwd"]
os.system(f"echo '{root_passwd}' | passwd --stdin root")
os.system(f"echo '{user_passwd}' | passwd --stdin {username}")

# add user  to sudoers
for line in fileinput.input("/etc/sudoers", inplace=True):
    if re.match(r'^#\s*%wheel\s+ALL=\(ALL:ALL\)\s+ALL$', line):
        line = line.lstrip('#').lstrip()
    print(line, end='')
