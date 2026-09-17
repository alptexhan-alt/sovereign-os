"""
Wi-Fi Ağ Radarı - Üretici (OUI) Tanımlayıcı
MAC adresinin ilk 3 baytına göre cihazın markasını (Apple, Samsung, Intel vb.) tespit eder.
"""

OUI_DATABASE = {
    # Apple
    "00:17:F2": "Apple", "00:1E:52": "Apple", "00:23:12": "Apple", "00:25:00": "Apple",
    "00:26:08": "Apple", "00:88:65": "Apple", "04:0C:CE": "Apple", "04:15:52": "Apple",
    "04:26:65": "Apple", "04:4B:ED": "Apple", "04:54:53": "Apple", "08:66:98": "Apple",
    "0C:4D:E9": "Apple", "10:1C:0C": "Apple", "10:40:F3": "Apple", "14:10:9F": "Apple",
    "14:20:5E": "Apple", "14:7D:C5": "Apple", "18:AF:61": "Apple", "18:E7:28": "Apple",
    "20:A2:E4": "Apple", "24:F0:94": "Apple", "28:0B:5C": "Apple", "28:CF:E9": "Apple",
    "30:07:4D": "Apple", "34:36:3B": "Apple", "3C:06:30": "Apple", "40:6C:8F": "Apple",
    "48:60:5F": "Apple", "58:55:CA": "Apple", "64:20:0C": "Apple", "6C:40:08": "Apple",
    "70:3E:AC": "Apple", "7C:04:D0": "Apple", "88:66:5A": "Apple", "98:01:A7": "Apple",
    "A4:83:E7": "Apple", "B8:78:26": "Apple", "C8:69:CD": "Apple", "D4:90:9C": "Apple",
    "E4:CE:8F": "Apple", "F0:18:98": "Apple", "F4:F1:5A": "Apple",
    
    # Samsung
    "00:07:AB": "Samsung", "00:12:47": "Samsung", "00:15:99": "Samsung", "00:17:C9": "Samsung",
    "00:21:4C": "Samsung", "00:23:D7": "Samsung", "00:26:37": "Samsung", "08:37:3D": "Samsung",
    "0C:14:20": "Samsung", "14:89:FD": "Samsung", "1C:5A:3E": "Samsung", "24:4B:03": "Samsung",
    "34:BE:00": "Samsung", "44:78:3E": "Samsung", "50:01:D9": "Samsung", "5C:A3:9D": "Samsung",
    "60:A1:0A": "Samsung", "78:47:1D": "Samsung", "84:25:19": "Samsung", "90:18:7C": "Samsung",
    "A8:7C:01": "Samsung", "BC:44:86": "Samsung", "CC:07:AB": "Samsung", "D0:B1:28": "Samsung",
    
    # Xiaomi / POCO / Redmi
    "00:9E:C8": "Xiaomi", "04:CF:8C": "Xiaomi", "10:2A:B3": "Xiaomi", "14:F6:5A": "Xiaomi",
    "18:59:36": "Xiaomi", "28:6C:07": "Xiaomi", "34:80:B3": "Xiaomi", "38:A4:ED": "Xiaomi",
    "50:64:2B": "Xiaomi", "54:48:E6": "Xiaomi", "64:CC:2E": "Xiaomi", "78:11:DC": "Xiaomi",
    "8C:BE:BE": "Xiaomi", "AC:C1:EE": "Xiaomi", "D4:97:0B": "Xiaomi", "F4:8E:92": "Xiaomi",
    
    # Huawei / Honor
    "00:1E:10": "Huawei", "00:25:68": "Huawei", "08:19:A6": "Huawei", "10:1B:54": "Huawei",
    "14:D1:1F": "Huawei", "20:F4:78": "Huawei", "28:6E:D4": "Huawei", "34:2E:B6": "Huawei",
    "48:46:FB": "Huawei", "70:72:3C": "Huawei", "78:D7:52": "Huawei", "AC:E2:15": "Huawei",
    
    # Router / Network Equipment
    "00:1D:0F": "TP-Link", "14:CF:92": "TP-Link", "18:A6:F7": "TP-Link", "50:C7:BF": "TP-Link",
    "70:4F:57": "TP-Link", "98:DA:C4": "TP-Link", "C0:06:C3": "TP-Link", "EC:08:6B": "TP-Link",
    "00:11:D8": "Asus", "04:D9:F5": "Asus", "10:7B:44": "Asus", "1C:87:2C": "Asus",
    "2C:4D:54": "Asus", "38:2C:4A": "Asus", "50:46:5D": "Asus", "60:A4:4C": "Asus",
    "00:14:BF": "Cisco-Linksys", "F0:9F:C2": "Ubiquiti", "04:18:D6": "Ubiquiti",
    
    # PC & Hardware
    "00:1B:21": "Intel", "00:1E:67": "Intel", "00:26:C6": "Intel", "08:11:96": "Intel",
    "3C:F8:62": "Intel", "48:51:B7": "Intel", "68:05:CA": "Intel", "7C:5C:F8": "Intel",
    "80:86:F2": "Intel", "84:A9:3E": "Intel", "A0:36:9F": "Intel", "E8:D8:D1": "Intel",
    "00:1A:4B": "Realtek", "00:E0:4C": "Realtek", "52:54:00": "QEMU Virtual",
    "00:05:69": "VMware", "00:0C:29": "VMware", "00:50:56": "VMware",
    "08:00:27": "VirtualBox", "00:15:5D": "Microsoft Hyper-V",
    
    # IoT / Smart TV
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi", "E4:5F:01": "Raspberry Pi",
    "24:0A:C4": "Espressif (ESP32/IoT)", "30:AE:A4": "Espressif (ESP32/IoT)",
    "84:F3:EB": "Espressif (ESP32/IoT)", "CC:50:E3": "Espressif (ESP32/IoT)",
    "00:FC:8B": "Amazon (Echo/FireTV)", "44:65:0D": "Amazon", "68:54:5A": "Amazon",
    "00:22:98": "Sony (PlayStation/Bravia)"
}

def identify_vendor(mac_address: str) -> str:
    """Verilen MAC adresine göre cihaz üreticisini tespit eder."""
    if not mac_address or mac_address == "Bilinmiyor":
        return "Bilinmiyor"
    
    clean_mac = mac_address.replace("-", ":").upper().strip()
    parts = clean_mac.split(":")
    if len(parts) >= 3:
        prefix = f"{parts[0]}:{parts[1]}:{parts[2]}"
        if prefix in OUI_DATABASE:
            return OUI_DATABASE[prefix]
            
    # Rastgele veya özel donanım maskesi (Locally Administered Address)
    if len(parts) > 0 and len(parts[0]) == 2:
        try:
            second_hex = int(parts[0][1], 16)
            if second_hex in [2, 6, 0xA, 0xE]:
                return "Gizlenmiş / Rastgele MAC (Mobil/Özel)"
        except ValueError:
            pass
            
    return "Ağ Cihazı"
