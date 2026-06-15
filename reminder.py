
import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8951538688"

mode = os.getenv("REMINDER_MODE", "pengajian_laki")

week = datetime.now().isocalendar()[1]

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

if mode == "pengajian_laki":
    ustadz = pengajian_laki[(week - 1) % 4]

    pesan = f"""
📢 PENGINGAT PENGAJIAN MALAM RABU

Assalamu'alaikum Warahmatullahi Wabarakatuh

Insya Allah besok malam Rabu akan dilaksanakan pengajian rutin laki-laki.

🎙 Pengisi:
{ustadz}

🕌 Masjid Jami Al-Falah
Kp. Caringin

Mohon hadir tepat waktu.

Jazakumullahu khairan.
"""

elif mode == "pengajian_senin":
    ustadz = pengajian_senin[(week - 1) % 4]

    pesan = f"""
📢 PENGINGAT PENGAJIAN HARI SENIN

Assalamu'alaikum Warahmatullahi Wabarakatuh

Insya Allah besok akan dilaksanakan pengajian rutin.

🎙 Pengisi:
{ustadz}

🕌 Masjid Jami Al-Falah
Kp. Caringin

Mohon hadir tepat waktu.

Jazakumullahu khairan.
"""

else:
    pesan = """
📢 PENGINGAT SYAHRIAHAN SHOLAWAT

Assalamu'alaikum Warahmatullahi Wabarakatuh

Insya Allah malam Jumat akan dilaksanakan Syahriahan Sholawat.

🎙 Pengisi:
Aang Deden Kasyful Anwar

🕗 Waktu:
20.00 WIB - 21.30 WIB

🕌 Masjid Jami Al-Falah
Kp. Caringin

Mohon hadir dan ajak keluarga.

Jazakumullahu khairan.
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(
    url,
    json={
        "chat_id": CHAT_ID,
        "text": pesan
    }
)

print("Pesan terkirim")
