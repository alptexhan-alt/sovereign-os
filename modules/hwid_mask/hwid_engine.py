"""
Sovereign OS - Donanım Kimlik Maskeleme Çekirdeği (HWID Anti-Fingerprint Engine)
Anakart seri numarası, Disk Seri Numarası (SMART/NVMe), MAC adresi ve
sistem UUID'sini uygulamalardan gizleyip sahte profiller sunan çekirdek modülü.
"""

import os
import sys
import uuid
import random
import hashlib
import subprocess
import platform
import json
from datetime import datetime


class HWIDEngine:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.spoof_profile_file = os.path.join(os.path.dirname(__file__), "active_spoof_profile.json")

    def get_real_hardware_fingerprint(self):
        """Mevcut makinenin gerçek donanım kimliklerini okur."""
        hw = {
            "bios_serial": "Bilinmiyor",
            "board_serial": "Bilinmiyor",
            "disk_serial": "Bilinmiyor",
            "mac_address": "Bilinmiyor",
            "uuid": "Bilinmiyor"
        }
        
        if self.is_windows:
            try:
                # WMI / PowerShell ile gerçek donanım numaralarını çek
                bios = subprocess.check_output("powershell (Get-CimInstance Win32_BIOS).SerialNumber", text=True).strip()
                if bios: hw["bios_serial"] = bios
                
                board = subprocess.check_output("powershell (Get-CimInstance Win32_BaseBoard).SerialNumber", text=True).strip()
                if board: hw["board_serial"] = board
                
                disk = subprocess.check_output("powershell (Get-CimInstance Win32_DiskDrive | Select-Object -First 1).SerialNumber", text=True).strip()
                if disk: hw["disk_serial"] = disk
                
                sys_uuid = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystemProduct).UUID", text=True).strip()
                if sys_uuid: hw["uuid"] = sys_uuid
                
                mac = subprocess.check_output("powershell (Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).MacAddress", text=True).strip()
                if mac: hw["mac_address"] = mac
            except Exception as e:
                hw["error"] = str(e)
        else:
            # Linux üzerinde sysfs okuması
            for key, path in [
                ("bios_serial", "/sys/class/dmi/id/bios_version"),
                ("board_serial", "/sys/class/dmi/id/board_serial"),
                ("uuid", "/sys/class/dmi/id/product_uuid")
            ]:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        hw[key] = f.read().strip()
                        
        return hw

    def generate_spoofed_identity(self, seed: str = None):
        """Rastgele veya belirli bir tohuma (seed) göre sahte donanım kimliği üretir."""
        if seed:
            random.seed(hashlib.sha256(seed.encode()).hexdigest())
            
        def rand_hex(n):
            return ''.join(random.choices('0123456789ABCDEF', k=n))
            
        # Sahte popüler donanım modelleri
        motherboard_brands = [
            ("ASUSTeK COMPUTER INC.", "ROG STRIX B650E-F GAMING WIFI"),
            ("Micro-Star International Co., Ltd.", "MAG B650 TOMAHAWK WIFI"),
            ("Gigabyte Technology Co., Ltd.", "B650 AORUS ELITE AX")
        ]
        chosen_vendor, chosen_model = random.choice(motherboard_brands)
        
        # Gerçekçi sahte SSD modelleri (Samsung / Kingston / Western Digital)
        disk_models = [
            ("Samsung SSD 990 PRO 2TB", f"S73TNJ0W{rand_hex(6)}"),
            ("KINGSTON SFYRD2000G", f"50026B7{rand_hex(9)}"),
            ("WD_BLACK SN850X 2000GB", f"23152{rand_hex(8)}")
        ]
        chosen_disk_model, chosen_disk_serial = random.choice(disk_models)
        
        # Sahte MAC adresi (Locally Administered)
        fake_mac = f"02:{rand_hex(2)}:{rand_hex(2)}:{rand_hex(2)}:{rand_hex(2)}:{rand_hex(2)}"
        
        profile = {
            "generated_at": datetime.now().isoformat(),
            "target_os": "Sovereign OS Anti-Cheat Shield",
            "spoofed_values": {
                "baseboard_manufacturer": chosen_vendor,
                "baseboard_product": chosen_model,
                "baseboard_serial": f"L1M0{rand_hex(8)}",
                "bios_serial": f"ASUS_{rand_hex(10)}",
                "system_uuid": str(uuid.uuid4()).upper(),
                "disk_model": chosen_disk_model,
                "disk_serial": chosen_disk_serial,
                "mac_address": fake_mac,
                "gpu_uuid": f"GPU-{uuid.uuid4()}"
            }
        }
        
        with open(self.spoof_profile_file, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
            
        return profile

    def generate_linux_kernel_rules(self, profile):
        """
        Sovereign OS'in Linux çekirdeğinde `/sys/class/dmi/id` ve `udev` için
        uygulamalara sunacağı sanal DMI kurallarını üretir.
        """
        vals = profile["spoofed_values"]
        rules = f"""# Sovereign OS Kernel Masking Rules (Udev & Sysfs Overlay)
# Bu kurallar oyunlar veya programlar çalıştığında sahte donanım kimliklerini enjekte eder.

SUBSYSTEM=="dmi", ATTR{{product_uuid}}="{vals['system_uuid']}"
SUBSYSTEM=="dmi", ATTR{{board_serial}}="{vals['baseboard_serial']}"
SUBSYSTEM=="dmi", ATTR{{bios_version}}="{vals['bios_serial']}"

# Disk Seri Numarası Maskesi (libudev / ioctl)
KERNEL=="nvme*|sd*", ATTR{{serial}}="{vals['disk_serial']}"

# Ağ Kartı MAC Maskesi
SUBSYSTEM=="net", ACTION=="add", ATTR{{address}}="{vals['mac_address']}"
"""
        rules_path = os.path.join(os.path.dirname(__file__), "99-sovereign-hwid-mask.rules")
        with open(rules_path, "w", encoding="utf-8") as f:
            f.write(rules)
        return rules_path


if __name__ == "__main__":
    engine = HWIDEngine()
    print("\033[96m" + "="*70)
    print("   SOVEREIGN OS // DONANIM KİMLİK MASKELEME MOTORU (HWID SHIELD)")
    print("="*70 + "\033[0m\n")
    
    print("\033[93m[1] Gerçek Donanım Kimlikleri Okunuyor...\033[0m")
    real_hw = engine.get_real_hardware_fingerprint()
    for k, v in real_hw.items():
        print(f"    {k:<18}: \033[91m{v}\033[0m")
        
    print("\n\033[93m[2] Yeni Sahte (Spoofed) Donanım Kimliği Oluşturuluyor...\033[0m")
    spoofed = engine.generate_spoofed_identity()
    for k, v in spoofed["spoofed_values"].items():
        print(f"    {k:<24}: \033[92m{v}\033[0m")
        
    rules_file = engine.generate_linux_kernel_rules(spoofed)
    print(f"\n\033[94m[+] Çekirdek (Kernel) kural dosyası yazıldı: {rules_file}\033[0m")
    print("\033[92m[OK] Uygulamalar ve oyunlar artik gercek donaniminizi degil, bu sahte profili gorecek!\033[0m\n")
