"""
Sovereign OS - Wi-Fi & Yerel Ağ Radarı (Sentinel Core)
Aynı Wi-Fi ağına bağlı tüm cihazları, IP'leri, MAC adreslerini,
üretici markalarını ve aktiflik durumlarını tespit eden çekirdek servis.
"""

import os
import sys
import time
import json
import socket
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# OUI modülünü yükle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from oui_lookup import identify_vendor


def get_local_ip_and_subnet():
    """Mevcut cihazın yerel IP adresini ve alt ağını tespit eder."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Dışarıya bağlantı açmadan yerel IP'yi öğren
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
        
    parts = local_ip.split('.')
    subnet_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}"
    return local_ip, subnet_prefix


def ping_host(ip: str):
    """Belirli bir IP'ye tek bir hızlı ping atar (ARP tablosunu uyandırmak için)."""
    is_win = platform.system() == "Windows"
    cmd = ["ping", "-n", "1", "-w", "250", ip] if is_win else ["ping", "-c", "1", "-W", "1", ip]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def fast_subnet_sweep(subnet_prefix: str):
    """Alt ağdaki tüm 1-254 IP'lerini hızlıca yoklar (Multithreaded)."""
    print(f"\033[94m[*] {subnet_prefix}.0/24 alt ağı taranıyor (254 hedef)... \033[0m", end="", flush=True)
    targets = [f"{subnet_prefix}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=64) as executor:
        executor.map(ping_host, targets)
    print("\033[92m [TAMAMLANDI]\033[0m")


def get_arp_table(subnet_prefix: str):
    """İşletim sisteminin ARP önbelleğini okuyup bağlı cihazları çıkarır."""
    devices = []
    is_win = platform.system() == "Windows"
    
    try:
        if is_win:
            output = subprocess.check_output(["arp", "-a"], text=True, encoding="cp857", errors="ignore")
            lines = output.splitlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1].replace("-", ":").upper()
                    entry_type = parts[2].lower()
                    
                    # Sadece dinamik ve hedef alt ağdaki cihazlar
                    if ip.startswith(subnet_prefix) and ("dinamik" in entry_type or "dynamic" in entry_type):
                        if mac != "FF:FF:FF:FF:FF:FF":
                            devices.append({"ip": ip, "mac": mac})
        else:
            # Linux uyumluluğu (/proc/net/arp)
            if os.path.exists("/proc/net/arp"):
                with open("/proc/net/arp", "r") as f:
                    for line in f.readlines()[1:]:
                        parts = line.split()
                        if len(parts) >= 4:
                            ip = parts[0]
                            mac = parts[3].upper()
                            if mac != "00:00:00:00:00:00" and ip.startswith(subnet_prefix):
                                devices.append({"ip": ip, "mac": mac})
    except Exception as e:
        print(f"\033[91m[!] ARP tablosu okunamadı: {e}\033[0m")
        
    return devices


def resolve_hostname(ip: str) -> str:
    """IP adresinin ağ adını (Hostname) çözer."""
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        return "Bilinmeyen İsim"


def measure_ping(ip: str) -> str:
    """Hedef cihaza ping atıp gecikme süresini (ms) ölçer."""
    is_win = platform.system() == "Windows"
    cmd = ["ping", "-n", "1", "-w", "500", ip] if is_win else ["ping", "-c", "1", "-W", "1", ip]
    try:
        start = time.time()
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elapsed = round((time.time() - start) * 1000, 1)
        if res.returncode == 0:
            return f"{elapsed} ms"
    except Exception:
        pass
    return "Aktif"


def scan_network():
    """Tam ağ taraması yapar ve sonuçları formatlar."""
    local_ip, subnet_prefix = get_local_ip_and_subnet()
    fast_subnet_sweep(subnet_prefix)
    arp_entries = get_arp_table(subnet_prefix)
    
    results = []
    
    # Kendi cihazımızı da ekleyelim
    results.append({
        "ip": local_ip,
        "mac": "YEREL MAKİNE (SEN)",
        "vendor": "Sovereign OS Düğümü",
        "hostname": socket.gethostname(),
        "latency": "0.1 ms",
        "status": "Ev Sahibi"
    })
    
    for dev in arp_entries:
        if dev["ip"] == local_ip:
            continue
        vendor = identify_vendor(dev["mac"])
        hostname = resolve_hostname(dev["ip"])
        latency = measure_ping(dev["ip"])
        
        results.append({
            "ip": dev["ip"],
            "mac": dev["mac"],
            "vendor": vendor,
            "hostname": hostname,
            "latency": latency,
            "status": "Bağlı"
        })
        
    # IP adresine göre sırala
    results.sort(key=lambda x: [int(p) if p.isdigit() else 0 for p in x["ip"].split(".")])
    return results, local_ip, subnet_prefix


def print_dashboard(devices, local_ip, subnet):
    """Terminalde siber-radar tarzı şık bir gösterge basar."""
    os.system("cls" if platform.system() == "Windows" else "clear")
    
    print("\033[96m" + "="*85)
    print(f"   SOVEREIGN OS // WI-FI SENTINEL AĞ RADARI [AKTİF]")
    print(f"   Yerel IP: {local_ip}  |  Alt Ağ: {subnet}.0/24  |  Tespit Edilen Cihaz: {len(devices)}")
    print(f"   Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*85 + "\033[0m")
    
    print(f"\033[93m{'IP ADRESİ':<16} {'MAC ADRESİ':<20} {'ÜRETİCİ / MARKA':<26} {'CİHAZ ADI':<15} {'DURUM':<8}\033[0m")
    print("-" * 85)
    
    for d in devices:
        status_color = "\033[92m" if "ms" in d["latency"] or d["status"] == "Ev Sahibi" else "\033[90m"
        vendor_display = d['vendor'][:24]
        host_display = d['hostname'][:14]
        
        print(f"{status_color}{d['ip']:<16} {d['mac']:<20} {vendor_display:<26} {host_display:<15} {d['latency']:<8}\033[0m")
        
    print("-" * 85)
    print("\033[94m[*] Bilgiler 'radar_devices.json' dosyasına canlı aktarıldı.\033[0m\n")


def save_to_json(devices):
    """Web/Shell arayüzümüzün canlı okuması için JSON dosyasına yazar."""
    output_path = os.path.join(current_dir, "radar_devices.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "count": len(devices),
            "devices": devices
        }, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print("\033[95m[+] Sovereign OS Wi-Fi Radarı başlatılıyor...\033[0m")
    devices, local_ip, subnet = scan_network()
    save_to_json(devices)
    print_dashboard(devices, local_ip, subnet)
