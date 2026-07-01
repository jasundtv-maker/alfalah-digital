```python
import os
import json
import requests
import gspread

from google.oauth2.service_account import Credentials

SHEET_ID = "18Af7MohqKRI0IU9XuGCCmXeSaPfqOv8_DWrGH65Zqtc"

FONNTE_TOKEN = os.getenv("FONNTE_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def normalisasi_wa(nomor):
    nomor = str(nomor).replace("+", "").replace("-", "").replace(" ", "").strip()

    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]

    return nomor


def buka_sheet():
    creds_json = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        creds_json,
        scopes=scopes
    )

    gc = gspread.authorize(creds)

    return gc.open_by_key(SHEET_ID)


def hitung_kas_madrasah(sh):
    ws = sh.worksheet("Kas Madrasah")

    data = ws.get_all_records()

    masuk = 0
    keluar = 0

    for row in data:
        masuk += float(row.get("Masuk", 0) or 0)
        keluar += float(row.get("Keluar", 0) or 0)

    return masuk - keluar


def hitung_kas_rajaban(sh):
    ws = sh.worksheet("Kas Rajaban")

    data = ws.get_all_records()

    masuk = 0
    keluar = 0

    for row in data:
        masuk += float(row.get("Masuk", 0) or 0)
        keluar += float(row.get("Keluar", 0) or 0)

    return masuk - keluar


def hitung_kas_masjid(sh):
    ws = sh.worksheet("Kas Masjid")

    data = ws.get_all_records()

    pemasukan = 0
    pengeluaran = 0

    for row in data:

        jenis = str(row.get("Jenis", "")).strip().lower()
        jumlah = float(row.get("Jumlah", 0) or 0)

        if jenis == "pemasukan":
            pemasukan += jumlah

        elif jenis == "pengeluaran":
            pengeluaran += jumlah

    return pemasukan - pengeluaran


def format_rupiah(nilai):
    return f"Rp {int(nilai):,}".replace(",", ".")


def kirim_wa(nomor, pesan):
    headers = {
        "Authorization": FONNTE_TOKEN
    }

    data = {
        "target": nomor,
        "message": pesan
    }

    requests.post(
        "https://api.fonnte.com/send",
        headers=headers,
        data=data,
        timeout=30
    )


def kirim_telegram(pesan):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": pesan
        },
        timeout=30
    )


def ambil_penerima(sh):
    ws = sh.worksheet("Jamaah")

    data = ws.get_all_records()

    hasil = []

    for row in data:

        aktif = str(row.get("Aktif", "")).strip().lower()

        if aktif != "ya":
            continue

        nomor = normalisasi_wa(row.get("NoWA", ""))

        if len(nomor) < 10:
            continue

        hasil.append(nomor)

    return list(set(hasil))


def buat_pesan(kas_masjid, kas_madrasah, kas_rajaban):
    return f"""
📊 LAPORAN KAS BULANAN
🕌 MASJID JAMI AL-FALAH

Assalamu'alaikum Warahmatullahi Wabarakatuh.

Alhamdulillah, berikut kami sampaikan laporan kas saat ini:

💰 Kas Masjid
{format_rupiah(kas_masjid)}

🎓 Kas Madrasah
{format_rupiah(kas_madrasah)}

🏮 Kas Rajaban
{format_rupiah(kas_rajaban)}

🙏 Kami mengucapkan terima kasih kepada seluruh jamaah, masyarakat, para donatur, pengurus DKM, serta semua pihak yang telah berpartisipasi dalam memakmurkan Masjid Jami Al-Falah.

Semoga setiap infak, sedekah, tenaga, dan dukungan yang diberikan menjadi amal jariyah yang terus mengalir pahalanya serta mendapat balasan terbaik dari Allah SWT.

🌐 Informasi lengkap:
https://kas-masjid-alfalah.streamlit.app

Wassalamu'alaikum Warahmatullahi Wabarakatuh.
""".strip()


def main():
    sh = buka_sheet()

    kas_masjid = hitung_kas_masjid(sh)
    kas_madrasah = hitung_kas_madrasah(sh)
    kas_rajaban = hitung_kas_rajaban(sh)

    pesan = buat_pesan(
        kas_masjid,
        kas_madrasah,
        kas_rajaban
    )

    penerima = ambil_penerima(sh)

    print("Jumlah penerima:", len(penerima))

    for nomor in penerima:
        try:
            kirim_wa(nomor, pesan)
            print("Terkirim:", nomor)

        except Exception as e:
            print("Gagal:", nomor, e)

    kirim_telegram(pesan)

    print("Laporan bulanan selesai.")


if __name__ == "__main__":
    main()
```
