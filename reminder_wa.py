import os
import json
import requests
import gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

SHEET_ID = "18Af7MohqKRIOlU9XuGCCmXeSaPfqOv8_DWrGH65Zqtc"
LINK_APP = "https://kas-masjid-alfalah.streamlit.app"
MODE = os.getenv("REMINDER_MODE", "pengajian_laki")
FONNTE_TOKEN = os.getenv("FONNTE_TOKEN") or os.getenv("FONTE_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8951538688")

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


def normalisasi_wa(nomor):
    nomor = str(nomor).replace("+", "").replace("-", "").replace(" ", "").strip()
    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    return nomor


def ambil_service_account_info():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT") or os.getenv("GCP_SERVICE_ACCOUNT")
    if raw:
        return json.loads(raw)

    # fallback kalau key ditaruh satu-satu sebagai GitHub Secrets
    keys = [
        "type", "project_id", "private_key_id", "private_key", "client_email",
        "client_id", "auth_uri", "token_uri", "auth_provider_x509_cert_url",
        "client_x509_cert_url", "universe_domain",
    ]
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
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)


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


def target_aktif_umum(rows):
    # Hanya Aktif=Ya. Data Khusus seperti Aang Deden tidak ikut semua pesan.
    return [r for r in rows if r.get("Aktif", "").lower() == "ya" and not is_khusus_aang(r)]


def tambah_aang_jika_pengisi(target, rows, pengisi_text):
    if "aang deden" not in str(pengisi_text).lower():
        return target
    hasil = list(target)
    nomor_sudah = {r["NoWA"] for r in hasil}
    for r in rows:
        if is_khusus_aang(r) and r["NoWA"] not in nomor_sudah:
            hasil.append(r)
            nomor_sudah.add(r["NoWA"])
    return hasil


def besok_awal_bulan_hijriah():
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


def buat_pesan_dan_target(rows):
    week = waktu_wib().isocalendar()[1]

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
        target = [r for r in rows if r["JenisKelamin"] == "Laki-laki" and r["Aktif"].lower() == "ya" and not is_khusus_aang(r)]
        target = tambah_aang_jika_pengisi(target, rows, ustadz)
        return "Pengajian Malam Rabu", pesan, target

    if MODE == "pengajian_senin":
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
        target = [r for r in rows if r["JenisKelamin"] == "Perempuan" and r["Aktif"].lower() == "ya" and not is_khusus_aang(r)]
        target = tambah_aang_jika_pengisi(target, rows, ustadz)
        return "Pengajian Senenan", pesan, target

    if MODE == "syahriahan":
        if not besok_awal_bulan_hijriah():
            print("Besok bukan tanggal 1 Hijriah. WA syahriahan tidak dikirim.")
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
        target = target_aktif_umum(rows)
        target = tambah_aang_jika_pengisi(target, rows, "Aang Deden")
        return "Syahriahan Sholawat", pesan, target

    raise RuntimeError(f"REMINDER_MODE tidak dikenal: {MODE}")


def kirim_fonnte(nomor, pesan):
    if not FONNTE_TOKEN:
        return False, "FONNTE_TOKEN belum ada di GitHub Secrets"
    res = requests.post(
        "https://api.fonnte.com/send",
        headers={"Authorization": FONNTE_TOKEN},
        data={"target": normalisasi_wa(nomor), "message": pesan, "countryCode": "62"},
        timeout=30,
    )
    try:
        detail = res.json()
    except Exception:
        detail = res.text
    if res.status_code == 200:
        return True, str(detail)
    return False, f"HTTP {res.status_code}: {detail}"


def simpan_log(sh, nama, nowa, jenis, status, ket):
    try:
        ws = sh.worksheet("Log WA")
        ws.append_row(
            [waktu_wib().strftime("%Y-%m-%d %H:%M:%S"), nama, nowa, jenis, status, str(ket)[:500]],
            value_input_option="USER_ENTERED",
        )
    except Exception as e:
        print("Gagal simpan Log WA:", e)


def kirim_ringkasan_telegram(text):
    if not TELEGRAM_BOT_TOKEN:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=30,
        )
    except Exception as e:
        print("Gagal kirim ringkasan Telegram:", e)


sh = buka_sheet()
rows = baca_jamaah(sh)
jenis, pesan, target = buat_pesan_dan_target(rows)

# Hilangkan nomor duplikat
unik = []
seen = set()
for r in target:
    if r["NoWA"] and r["NoWA"] not in seen:
        unik.append(r)
        seen.add(r["NoWA"])
target = unik

print(f"Mode: {MODE} | Jenis: {jenis} | Target: {len(target)}")

sukses = 0
gagal = 0
for r in target:
    ok, info = kirim_fonnte(r["NoWA"], pesan)
    status = "Terkirim" if ok else "Gagal"
    if ok:
        sukses += 1
    else:
        gagal += 1
    simpan_log(sh, r["Nama"], r["NoWA"], f"WA Otomatis {jenis}", status, info)
    print(r["Nama"], r["NoWA"], status, str(info)[:120])

ringkasan = f"""🕌 AL-FALAH DIGITAL V17

WA Otomatis selesai.
Jenis: {jenis}
Target: {len(target)}
✅ Berhasil: {sukses}
❌ Gagal: {gagal}
Waktu: {waktu_wib().strftime('%d-%m-%Y %H:%M:%S')} WIB"""
print(ringkasan)
kirim_ringkasan_telegram(ringkasan)

