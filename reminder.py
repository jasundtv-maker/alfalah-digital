import os
import requests
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8951538688"
mode = os.getenv("REMINDER_MODE", "pengajian_laki")

LINK_APP = "https://kas-masjid-alfalah.streamlit.app"

pengajian_laki = [
    "Ustadz Ihin",
    "Ustadz Nanang",
    "Ustadz Jujun",
    "Aang Deden Kasyful Anwar"
]

pengajian_senin = [
    "Ustadz Nanang",
    "Aang Deden Kasyful Anwar",
    "Ustadz Ihin",
    "Ustadz Ihin"
]

def kirim_telegram(pesan):
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN belum ada")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": pesan
    }, timeout=30)

    print(response.text)


def minggu_ke_rotasi():
    # Pakai WIB, bukan UTC
    sekarang_wib = datetime.utcnow() + timedelta(hours=7)
    return sekarang_wib.isocalendar()[1]


def besok_awal_bulan_hijriah():
    """
    Cek apakah besok sekitar tanggal 1 Hijriah.
    Jika gagal cek API, jangan kirim syahriahan supaya aman.
    """
    try:
        besok = datetime.utcnow() + timedelta(hours=7, days=1)
        tanggal_api = besok.strftime("%d-%m-%Y")
        url = f"https://api.aladhan.com/v1/gToH/{tanggal_api}"
        r = requests.get(url, timeout=20).json()
        hari_hijriah = int(r["data"]["hijri"]["day"])
        return hari_hijriah == 1
    except Exception as e:
        print("Gagal cek Hijriah:", e)
        return False


week = minggu_ke_rotasi()

if mode == "pengajian_laki":
    ustadz = pengajian_laki[(week - 1) % 4]

    pesan = f"""
📢 PENGINGAT PENGAJIAN MALAM RABU

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah besok malam Rabu akan dilaksanakan pengajian rutin laki-laki.

🎙 Pengisi:
{ustadz}

🕢 Waktu:
19.30 WIB - 21.30 WIB

🕌 Tempat:
Madrasah Al-Falah / Masjid Jami Al-Falah
Kp. Caringin

🌐 Info aplikasi:
{LINK_APP}

Mohon hadir tepat waktu.

Jazakumullahu khairan.
"""

elif mode == "pengajian_senin":
    ustadz = pengajian_senin[(week - 1) % 4]

    pesan = f"""
📢 PENGINGAT PENGAJIAN SENENAN

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah besok pagi akan dilaksanakan pengajian rutin Senenan.

🎙 Pengisi:
{ustadz}

🕢 Waktu:
07.30 WIB - 09.00 WIB

🕌 Tempat:
Madrasah Al-Falah
Kp. Caringin

🌐 Info aplikasi:
{LINK_APP}

Mohon hadir tepat waktu.

Jazakumullahu khairan.
"""

elif mode == "syahriahan":
    if not besok_awal_bulan_hijriah():
        print("Besok bukan tanggal 1 Hijriah. Syahriahan tidak dikirim.")
        raise SystemExit(0)

    pesan = f"""
📢 PENGINGAT SYAHRIAHAN SHOLAWAT

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah malam Jumat ini akan dilaksanakan Syahriahan Sholawat awal bulan Hijriah.

🎙 Pimpinan:
Aang Deden Kasyful Anwar

🕗 Waktu:
20.00 WIB - 21.30 WIB

🕌 Tempat:
Masjid Jami Al-Falah
Kp. Caringin

🌐 Info aplikasi:
{LINK_APP}

Mohon hadir dan ajak keluarga.

Jazakumullahu khairan.
"""

else:
    print("REMINDER_MODE tidak dikenal:", mode)
    raise SystemExit(1)

kirim_telegram(pesan)
