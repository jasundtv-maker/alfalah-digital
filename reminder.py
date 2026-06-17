import os
import requests
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8951538688")
MODE = os.getenv("REMINDER_MODE", "pengajian_laki")
LINK_APP = "https://kas-masjid-alfalah.streamlit.app"

pengajian_laki = [
    "Ustadz Ihin",
    "Ustadz Nanang",
    "Ustadz Jujun",
    "Aang Deden Kasyful Anwar",
]

pengajian_senin = [
    "Ustadz Nanang",
    "Aang Deden Kasyful Anwar",
    "Ustadz Ihin",
    "Ustadz Ihin",
]


def waktu_wib():
    return datetime.utcnow() + timedelta(hours=7)


def minggu_ke_rotasi():
    return waktu_wib().isocalendar()[1]


def besok_awal_bulan_hijriah():
    """Untuk notifikasi Kamis siang: malam Jumat mengikuti tanggal Hijriah besok."""
    try:
        besok = waktu_wib() + timedelta(days=1)
        tanggal_api = besok.strftime("%d-%m-%Y")
        url = f"https://api.aladhan.com/v1/gToH/{tanggal_api}"
        r = requests.get(url, timeout=20).json()
        hari_hijriah = int(r["data"]["hijri"]["day"])
        print("Hijriah besok:", hari_hijriah)
        return hari_hijriah == 1
    except Exception as e:
        print("Gagal cek Hijriah:", e)
        return False


def kirim_telegram(pesan):
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN belum ada")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": pesan, "disable_web_page_preview": False},
        timeout=30,
    )
    print(response.text)
    return response.status_code == 200


week = minggu_ke_rotasi()

if MODE == "pengajian_laki":
    ustadz = pengajian_laki[(week - 1) % 4]
    pesan = f"""
📢 PENGINGAT PENGAJIAN MALAM RABU

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah malam ini akan dilaksanakan pengajian rutin laki-laki.

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

elif MODE == "pengajian_senin":
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

elif MODE == "syahriahan":
    if not besok_awal_bulan_hijriah():
        print("Besok bukan tanggal 1 Hijriah. Telegram syahriahan tidak dikirim.")
        raise SystemExit(0)

    pesan = f"""
📢 PENGINGAT SYAHRIAHAN SHOLAWAT

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah malam ini akan dilaksanakan Syahriahan Sholawat awal bulan Hijriah.

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
    print("REMINDER_MODE tidak dikenal:", MODE)
    raise SystemExit(1)

kirim_telegram(pesan)
