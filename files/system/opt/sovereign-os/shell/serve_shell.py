"""
Sovereign OS - Canlı Arayüz ve Kontrol Merkezi Sunucusu
Yerel ağ radarı ve donanım maskeleme motorunu görsel bir masaüstü arayüzüne bağlar.
"""

import os
import sys
import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

PORT = 4242
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OS_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
WIFI_MODULE = os.path.join(OS_ROOT, "modules", "wifi_radar")
HWID_MODULE = os.path.join(OS_ROOT, "modules", "hwid_mask")

sys.path.append(WIFI_MODULE)
sys.path.append(HWID_MODULE)

try:
    from radar import scan_network, save_to_json
    from hwid_engine import HWIDEngine
    hw_engine = HWIDEngine()
except Exception as e:
    print(f"Modül yükleme uyarısı: {e}")
    hw_engine = None


class SovereignHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # API: Canlı Wi-Fi Cihazları
        if parsed.path == "/api/radar":
            json_file = os.path.join(WIFI_MODULE, "radar_devices.json")
            if os.path.exists(json_file):
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"devices": [], "count": 0}
            self.send_json(data)
            return

        # API: Yeniden Ağ Tara
        elif parsed.path == "/api/radar/rescan":
            try:
                devices, local_ip, subnet = scan_network()
                save_to_json(devices)
                self.send_json({"status": "success", "count": len(devices), "devices": devices})
            except Exception as e:
                self.send_json({"status": "error", "message": str(e)}, status=500)
            return

        # API: HWID Durumu (Gerçek vs Sahte)
        elif parsed.path == "/api/hwid":
            profile_file = os.path.join(HWID_MODULE, "active_spoof_profile.json")
            spoofed_data = {}
            if os.path.exists(profile_file):
                with open(profile_file, "r", encoding="utf-8") as f:
                    spoofed_data = json.load(f)
            
            real_data = hw_engine.get_real_hardware_fingerprint() if hw_engine else {}
            self.send_json({
                "real": real_data,
                "spoofed": spoofed_data.get("spoofed_values", {})
            })
            return

        # API: Yeni Sahte HWID Üret
        elif parsed.path == "/api/hwid/randomize":
            if hw_engine:
                new_profile = hw_engine.generate_spoofed_identity()
                hw_engine.generate_linux_kernel_rules(new_profile)
                real_data = hw_engine.get_real_hardware_fingerprint()
                self.send_json({
                    "status": "success",
                    "real": real_data,
                    "spoofed": new_profile["spoofed_values"]
                })
            else:
                self.send_json({"status": "error"}, status=500)
            return

        # Statik dosyaları sun
        return super().do_GET()

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_server():
    os.chdir(os.path.join(BASE_DIR, "ui"))
    server = HTTPServer(("127.0.0.1", PORT), SovereignHandler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"\033[96m[+] Sovereign OS Masaüstü Kabuğu çalışıyor: {url}\033[0m")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Sunucu kapatıldı.")

if __name__ == "__main__":
    run_server()
