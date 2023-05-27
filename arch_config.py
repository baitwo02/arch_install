import os
import json
import fileinput
import re

with open("./config.json", "r", encoding="utf8") as config_file:
    config_data = json.load(config_file)

username = config_data["username"]

# 配置 archlinuxcn 源
archlinuxcn = """\
[archlinuxcn]
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch
"""
with open(r"/etc/pacman.conf", "a", encoding="utf-8") as f1:
    f1.write(archlinuxcn)
os.system("pacman --noconfirm -Sy")
os.system("pacman --noconfirm -S archlinuxcn-keyring")

#  配置快照
os.system("pacman --noconfirm -S timeshift grub-btrfs inotify-tools rsync")
os.system("systemctl enable cronie.service --now")
os.system("systemctl enable grub-btrfsd.service --now")
path1 = "/usr/lib/systemd/system/grub-btrfsd.service"
path2 = "/etc/systemd/system/grub-btrfsd.service"
os.system(f"cp {path1} {path2}")

for line in fileinput.input("/etc/systemd/system/grub-btrfsd.service", inplace=True):
    if re.match(r'^ExecStart=/usr/bin/grub-btrfsd --syslog /.snapshots$', line):
        line = re.sub(r'--syslog /.snapshots', '--syslog --timeshift-auto', line)
    print(line, end='')

for line in fileinput.input('/etc/mkinitcpio.conf', inplace=True):
    if re.match(r'^HOOKS\s*=\s*\(.+\)$', line):
        line = re.sub(r'\)$', ' grub-btrfs-overlayfs)', line)
    print(line, end='')
os.system(f"mkinitcpio -P")

# 安装及配置登陆管理器
os.system("pacman --noconfirm -S sddm")
os.system("systemctl enable sddm.service")

# 安装桌面环境及wm, 默认只安装xfce4, 因为xfce4 非常小
os.system("pacman --noconfirm -S xfce4 xfce4-goodies")

# 配置中文输入法
os.system("pacman --noconfirm -S fcitx5-im fcitx5-chinese-addons fcitx5-pinyin-zhwiki")
fictx5_config = """
EDITOR=nvim
VISUAL=nvim
GTK_IM_MODULE=fcitx5
QT_IM_MODULE=fcitx5
XMODIFIERS=@im=fcitx5
SDL_IM_MODULE=fcitx5
GLFW_IM_MODULE=ibus
"""

with open("/etc/environment", "a", encoding="utf-8") as environment_f:
    environment_f.write(fictx5_config)
os.system("pacman --noconfirm -S ttf-lxgw-wenkai ttf-lxgw-wenkai-mono nerd-fonts-hack")
os.system(f"mkdir /home/{username}/.config/autostart")
os.system(f"cp /usr/share/applications/org.fcitx.Fcitx5.desktop /home/{username}/.config/autostart/")

# 配置代理及aur
os.system("pacman --noconfirm -S yay paru clash-verge clash-meta")
os.system("systemctl enable clash-meta.service")

# 配置电源管理
os.system("pacman --noconfirm -S tlp")
os.system("systemctl enable tlp.service")

# 配置蓝牙
os.system("pacman --noconfirm -S bluez bluez-utils blueberry")
os.system("systemctl enable bluetooth.service")


# 安装必备包
packages = [
    "firefox",
    "git",
    "kitty",
    "grub-customizer",
    "ntfs-3g",
    "feh",
    "network-manager-applet",
    "noto-fonts-emoji",
    "neofetch",
]

for package in packages:
    os.system(f"pacman --noconfirm -S {package}")

# 统一 user 和 root 配置
os.system(f"rm -rf /root/.config")
os.system(f"rm -rf /root/.local")
os.system(f"ln -sf /home/{username}/.config /root/.config")
os.system(f"ln -sf /home/{username}/.local /root/.local")

# 转换用户目录权限
os.system(f"usermod -aG video,audio {username}")
os.system(f"chown -R {username}:{username} /home/{username}")