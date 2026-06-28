import os
import json
import requests
import gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

SHEET_ID = "18Af7MohqKRIOlU9XuGCCmXeSaPfqOv8_DWrGH65Zqtc"
LINK_APP = "https://kas-masjid-alfalah.streamlit.app"
MODE = os.getenv("REMINDER_MODE", "pengajian_salasaan")
FONNTE_TOKEN = os.getenv("FONNTE_TOKEN") or os.getenv("FONTE_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8951538688")

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

def normalisasi_wa(nomor):
    nomor = str(nomor).replace("+", "").replace("-", "").replace(" ", "").strip()
    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    return nomor

def minggu():
    return waktu_wib().isocalendar()[1]

def penutup():
    return PENUTUP[minggu() % len(PENUTUP)]

def ambil_service_account_info():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT") or os.getenv("GCP_SERVICE_ACCOUNT")
    if raw:
        return json.loads(raw)
    keys = ["type", "project_id", "private_key_id", "private_key", "client_email", "client_id", "auth_uri", "token_uri", "auth_provider_x509_cert_url", "client_x509_cert_url", "universe_domain"]
    info = {k: os.getenv(k) for k in keys if os.getenv(k)}
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")
    if "client_email" in info and "private_key" in info:
        info.setdefault("type", "service_account")
        info.setdefault("token_uri", "https://oauth2.googleapis.com/token")
        return info
    return None

def buka_sheet():
    info = ambil_service_account_info()
    if not info:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT belum ada di GitHub Secrets")
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds).open_by_key(SHEET_ID)

def baca_setting(sh, worksheet="Setting WA"):
    try:
        rows = sh.worksheet(worksheet).get_all_records()
        hasil = {}
        for r in rows:
            key = str(r.get("Key", "")).strip()
            val = str(r.get("Value", "")).strip()
            if key:
                hasil[key] = val
        return hasil
    except Exception as e:
        print(f"Gagal membaca {worksheet}:", e)
        return {}

def baca_setting_pengajian(sh):
    try:
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

def baca_jamaah(sh):
    rows = sh.worksheet("Jamaah").get_all_records()
    hasil = []
    for r in rows:
        r = {str(k).strip(): v for k, v in r.items()}
        r["Nama"] = str(r.get("Nama", "")).strip()
        r["JenisKelamin"] = str(r.get("JenisKelamin", "")).strip()
        r["NoWA"] = normalisasi_wa(r.get("NoWA", ""))
        r["Aktif"] = str(r.get("Aktif", "")).strip()
        r["Catatan"] = str(r.get("Catatan", "")).strip()
        if r["Nama"] and r["NoWA"]:
            hasil.append(r)
    return hasil

def is_khusus_aang(row):
    nama = row.get("Nama", "").lower()
    aktif = row.get("Aktif", "").lower()
    catatan = row.get("Catatan", "").lower()
    return "aang deden" in nama or (aktif == "khusus" and "pengisi" in catatan)

def tambah_aang_jika_pengisi(target, rows, pengisi_text):
    if "aang deden" not in str(pengisi_text).lower():
        return target
    hasil = list(target)
    sudah = {r["NoWA"] for r in hasil}
    for r in rows:
        if is_khusus_aang(r) and r["NoWA"] not in sudah:
            hasil.append(r)
            sudah.add(r["NoWA"])
    return hasil

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
    pesan = f"""🕌 PENGAJIAN MALAM REBO

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
    return pesan, ustadz

def pesan_senenan(settings):
    default = pengajian_senin[(minggu() - 1) % 4]
    ustadz = get_setting(settings, "Pengajian Senenan Ibu-Ibu", "PengisiManual", default)
    pesan = f"""🌸 PENGAJIAN SENENAN IBU-IBU

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
    return pesan, ustadz

def buat_pesan_dan_target(rows, settings):
    if MODE == "pengajian_salasaan":
        pesan = pesan_salasaan()
        target = [r for r in rows if r["JenisKelamin"] == "Laki-laki" and r["Aktif"].lower() == "ya" and not is_khusus_aang(r)]
        return "Pengajian Salasaan", pesan, target
    if MODE == "pengajian_laki":
        pesan, ustadz = pesan_malam_rebo(settings)
        target = [r for r in rows if r["JenisKelamin"] == "Laki-laki" and r["Aktif"].lower() == "ya" and not is_khusus_aang(r)]
        target = tambah_aang_jika_pengisi(target, rows, ustadz)
        return "Pengajian Malam Rebo", pesan, target
    if MODE == "pengajian_senin":
        pesan, ustadz = pesan_senenan(settings)
        target = [r for r in rows if r["JenisKelamin"] == "Perempuan" and r["Aktif"].lower() == "ya" and not is_khusus_aang(r)]
        target = tambah_aang_jika_pengisi(target, rows, ustadz)
        return "Pengajian Senenan Ibu-Ibu", pesan, target
    print("REMINDER_MODE tidak dikenal:", MODE)
    raise SystemExit(0)

def kirim_fonnte(nomor, pesan):
    if not FONNTE_TOKEN:
        return False, "FONNTE_TOKEN belum ada di GitHub Secrets"
    r = requests.post("https://api.fonnte.com/send", headers={"Authorization": FONNTE_TOKEN}, data={"target": normalisasi_wa(nomor), "message": pesan, "countryCode": "62"}, timeout=30)
    try:
        detail = r.json()
    except Exception:
        detail = r.text
    if r.status_code == 200:
        return True, str(detail)
    return False, f"HTTP {r.status_code}: {detail}"

def simpan_log(sh, nama, nowa, jenis, status, ket):
    try:
        ws = sh.worksheet("Log WA")
        ws.append_row([waktu_wib().strftime("%Y-%m-%d %H:%M:%S"), nama, nowa, jenis, status, str(ket)[:500]], value_input_option="USER_ENTERED")
    except Exception as e:
        print("Gagal simpan Log WA:", e)

def kirim_ringkasan_telegram(text):
    if not TELEGRAM_BOT_TOKEN:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=30)
    except Exception as e:
        print("Gagal kirim ringkasan Telegram:", e)

sh = buka_sheet()
setting_wa = baca_setting(sh, "Setting WA")
wa_auto = setting_wa.get("WA_AUTO", "OFF").strip().upper()
print("WA_AUTO:", wa_auto)
if wa_auto != "ON":
    print("WA otomatis dinonaktifkan dari Google Sheet Setting WA.")
    raise SystemExit(0)

setting_pengajian = baca_setting_pengajian(sh)
rows = baca_jamaah(sh)
jenis, pesan, target = buat_pesan_dan_target(rows, setting_pengajian)

unik, seen = [], set()
for r in target:
    if r["NoWA"] and r["NoWA"] not in seen:
        unik.append(r)
        seen.add(r["NoWA"])
target = unik
print(f"Mode: {MODE} | Jenis: {jenis} | Target: {len(target)}")

sukses = gagal = 0
for r in target:
    ok, info = kirim_fonnte(r["NoWA"], pesan)
    status = "Terkirim" if ok else "Gagal"
    sukses += 1 if ok else 0
    gagal += 0 if ok else 1
    simpan_log(sh, r["Nama"], r["NoWA"], f"WA Otomatis {jenis}", status, info)
    print(r["Nama"], r["NoWA"], status, str(info)[:120])

ringkasan = f"""🕌 AL-FALAH DIGITAL V20

WA Otomatis selesai.
Jenis: {jenis}
Target: {len(target)}
✅ Berhasil: {sukses}
❌ Gagal: {gagal}
Waktu: {waktu_wib().strftime('%d-%m-%Y %H:%M:%S')} WIB"""
print(ringkasan)
kirim_ringkasan_telegram(ringkasan)
