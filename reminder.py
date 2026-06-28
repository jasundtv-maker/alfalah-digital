import os
import json
import requests
import gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

SHEET_ID = "18Af7MohqKRIOlU9XuGCCmXeSaPfqOv8_DWrGH65Zqtc"
LINK_APP = "https://kas-masjid-alfalah.streamlit.app"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8951538688")
MODE = os.getenv("REMINDER_MODE", "pengajian_salasaan")

pengajian_laki = ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden Kasyful Anwar"]
pengajian_senin = ["Ustadz Nanang", "Aang Deden Kasyful Anwar", "Ustadz Ihin", "Ustadz Ihin"]
PENUTUP = [
    "Mari kita luangkan waktu untuk menghadiri majelis ilmu, mempererat ukhuwah Islamiyah, serta bersama-sama menambah ilmu agama demi meraih ridha Allah SWT.",
    "Majelis ilmu adalah salah satu jalan menuju rahmat Allah. Semoga Allah SWT memudahkan langkah kita untuk menghadirinya.",
    "Semoga setiap langkah menuju majelis ilmu menjadi sebab bertambahnya keberkahan hidup kita.",
    "Dengan penuh kerendahan hati, mari kita hidupkan majelis ilmu sebagai sarana memperkuat iman dan silaturahmi.",
    "Semoga Allah SWT menggerakkan hati kita untuk mencintai majelis ilmu dan memudahkan langkah menuju kebaikan.",
]

def waktu_wib():
    return datetime.utcnow() + timedelta(hours=7)

def minggu():
    return waktu_wib().isocalendar()[1]

def penutup():
    return PENUTUP[minggu() % len(PENUTUP)]

def ambil_service_account_info():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT") or os.getenv("GCP_SERVICE_ACCOUNT")
    if raw:
        return json.loads(raw)
    return None

def buka_sheet():
    info = ambil_service_account_info()
    if not info:
        return None
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds).open_by_key(SHEET_ID)

def baca_setting_pengajian():
    try:
        sh = buka_sheet()
        if sh is None:
            return {}
        rows = sh.worksheet("Setting Pengajian").get_all_records()
        hasil = {}
        for r in rows:
            kegiatan = str(r.get("Kegiatan", "")).strip().lower()
            if kegiatan:
                hasil[kegiatan] = {str(k).strip(): str(v).strip() for k, v in r.items()}
        return hasil
    except Exception as e:
        print("Setting Pengajian tidak terbaca:", e)
        return {}

def get_setting(settings, kegiatan, kolom, default=""):
    row = settings.get(kegiatan.lower().strip(), {})
    val = str(row.get(kolom, "")).strip()
    return val if val else default

def pesan_salasaan():
    return f"""🕌 PENGAJIAN SALASAAN

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah malam ini akan dilaksanakan Pengajian Salasaan untuk bapak-bapak.

📍 Tempat:
Madrasah Al-Mutmainnah

🕢 Waktu:
Ba'da Shalat Isya

{penutup()}

Semoga Allah SWT memberikan kemudahan langkah, kesehatan, dan keberkahan kepada kita semua.

Jazakumullahu khairan katsiran.

Wassalamu'alaikum Warahmatullahi Wabarakatuh.

🕌 DKM Masjid Jami Al-Falah"""

def pesan_malam_rebo(settings):
    default = pengajian_laki[(minggu() - 1) % 4]
    ustadz = get_setting(settings, "Pengajian Malam Rebo", "PengisiManual", default)
    return f"""🕌 PENGAJIAN MALAM REBO

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah malam ini akan dilaksanakan Pengajian Malam Rebo untuk bapak-bapak.

👳 Pengisi:
{ustadz}

🕢 Waktu:
19.30 WIB - 21.30 WIB

📍 Tempat:
Masjid/Madrasah Al-Falah

{penutup()}

Semoga Allah SWT memberikan kemudahan langkah, kesehatan, dan keberkahan kepada kita semua.

Jazakumullahu khairan katsiran.

Wassalamu'alaikum Warahmatullahi Wabarakatuh.

🕌 DKM Masjid Jami Al-Falah"""

def pesan_senenan(settings):
    default = pengajian_senin[(minggu() - 1) % 4]
    ustadz = get_setting(settings, "Pengajian Senenan Ibu-Ibu", "PengisiManual", default)
    return f"""🌸 PENGAJIAN SENENAN IBU-IBU

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Insya Allah besok pagi akan dilaksanakan Pengajian Senenan Ibu-Ibu.

👳 Pengisi:
{ustadz}

🕢 Waktu:
07.30 WIB - 09.00 WIB

📍 Tempat:
Madrasah Al-Falah

{penutup()}

Semoga Allah SWT memberikan kemudahan langkah, kesehatan, dan keberkahan kepada kita semua.

Jazakumullahu khairan katsiran.

Wassalamu'alaikum Warahmatullahi Wabarakatuh.

🕌 DKM Masjid Jami Al-Falah"""

def kirim_telegram(pesan):
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN belum ada")
        return False
    r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": pesan}, timeout=30)
    print(r.text)
    return r.status_code == 200

settings = baca_setting_pengajian()
if MODE == "pengajian_salasaan":
    pesan = pesan_salasaan()
elif MODE == "pengajian_laki":
    pesan = pesan_malam_rebo(settings)
elif MODE == "pengajian_senin":
    pesan = pesan_senenan(settings)
else:
    print("REMINDER_MODE tidak dikenal:", MODE)
    raise SystemExit(0)

kirim_telegram(pesan)
