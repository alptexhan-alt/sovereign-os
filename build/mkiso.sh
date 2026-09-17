#!/usr/bin/env bash
# ==============================================================================
# Sovereign OS - Otomatik ISO İnşa ve Dağıtım Reçetesi (Archiso Tabanlı)
# Bu betik; ZSTD sıkıştırmalı Btrfs, HWID maskeleme, Wi-Fi Sentinel ve
# Proton uyumluluk katmanını birleştirip önyüklenebilir (bootable) .ISO üretir.
# ==============================================================================

set -e

WORK_DIR="/tmp/sovereign-iso-build"
PROFILE_DIR="$WORK_DIR/archiso-profile"
OUTPUT_DIR="$WORK_DIR/out"

echo -e "\033[96m[*] Sovereign OS ISO İnşa Süreci Başlatılıyor...\033[0m"

# 1. Gerekli Paketlerin Kurulması (Archiso & Çekirdek Araçları)
sudo pacman -Sy --noconfirm archiso git btrfs-progs zstd

# 2. Temel Profilin Klonlanması
mkdir -p "$WORK_DIR"
cp -r /usr/share/archiso/configs/releng/ "$PROFILE_DIR"

# 3. Paket Listesine Sovereign Çekirdek Bileşenlerinin Eklenmesi
cat <<EOF >> "$PROFILE_DIR/packages.x86_64"
# Temel Sistem & Btrfs Sıkıştırma
btrfs-progs
zstd
linux-zen
linux-zen-headers

# Ağ ve Wi-Fi Sentinel Araçları
networkmanager
wireless_tools
iw
ethtool
tcpdump
ebpf-tools

# Windows & Oyun Uyumluluğu (Proton & DXVK)
wine-staging
winetricks
vulkan-icd-loader
vulkan-tools
mesa
lib32-mesa
lib32-vulkan-icd-loader

# Masaüstü ve Hafif Wayland Kabuğu
wayland
sway
xorg-xwayland
alacritty
firefox
python
python-pip
EOF

# 4. Btrfs ZSTD Sıkıştırma Kök Ayarları
mkdir -p "$PROFILE_DIR/airootfs/etc"
cat <<EOF > "$PROFILE_DIR/airootfs/etc/fstab"
# Sovereign OS Transparent ZSTD Mount
LABEL=SOVEREIGN_OS / btrfs defaults,compress=zstd:3,noatime,subvol=@ 0 0
LABEL=SOVEREIGN_OS /home btrfs defaults,compress=zstd:3,noatime,subvol=@home 0 0
EOF

# 5. HWID Maskeleme Çekirdek Kurallarının Enjekte Edilmesi
mkdir -p "$PROFILE_DIR/airootfs/etc/udev/rules.d/"
cp ../modules/hwid_mask/99-sovereign-hwid-mask.rules "$PROFILE_DIR/airootfs/etc/udev/rules.d/"

# 6. Wi-Fi Sentinel ve Masaüstü Kabuğu Servisinin Eklenmesi
mkdir -p "$PROFILE_DIR/airootfs/opt/sovereign-os"
cp -r ../modules "$PROFILE_DIR/airootfs/opt/sovereign-os/"
cp -r ../shell "$PROFILE_DIR/airootfs/opt/sovereign-os/"

cat <<EOF > "$PROFILE_DIR/airootfs/etc/systemd/system/sovereign-shell.service"
[Unit]
Description=Sovereign OS Sentinel & Shell Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sovereign-os/shell
ExecStart=/usr/bin/python serve_shell.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Servisi Canlı İmajda Aktifleştir
ln -sf /etc/systemd/system/sovereign-shell.service "$PROFILE_DIR/airootfs/etc/systemd/system/multi-user.target.wants/"

# 7. ISO İmajının Derlenmesi
echo -e "\033[92m[*] ISO İmajı Oluşturuluyor (mkarchiso)... Lütfen bekleyin.\033[0m"
mkarchiso -v -w "$WORK_DIR/work" -o "$OUTPUT_DIR" "$PROFILE_DIR"

echo -e "\033[92m[✓] TEBRİKLER! Sovereign-OS-v1.0-x86_64.iso başarıyla üretildi: $OUTPUT_DIR\033[0m"
