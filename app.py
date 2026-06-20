import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import os
import urllib.parse
import requests
import base64
import json
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="APP MASJID JAMI AL-FALAH V21.3", page_icon="🕌", layout="wide")

KAS_FILE = "kas_masjid.csv"
PENGUMUMAN_FILE = "pengumuman.csv"
BANNER_FILE = "banner.png"
JAMAAH_FILE = "jamaah.csv"
CHAT_ID = "8951538688"
LINK_APP = "https://kas-masjid-alfalah.streamlit.app"
GRUP_AL_BARZANJI = "https://chat.whatsapp.com/JWobEDYP9MXEfDYHt8zlLR"
GRUP_AL_BARZAJI = GRUP_AL_BARZANJI
GRUP_AL_BARZANJI = GRUP_AL_BARZANJI
NOMOR_MASJID = "087742958453"
SHEET_ID = "18Af7MohqKRIOlU9XuGCCmXeSaPfqOv8_DWrGH65Zqtc"

KOLOM_KAS = ["Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Petugas"]
KOLOM_PENGUMUMAN = ["Tanggal", "Judul", "Isi"]
KOLOM_JAMAAH = ["Nama", "JenisKelamin", "NoWA", "Aktif", "Catatan"]

pengurus = {
    "Pelindung": ["Dadan Haris"],
    "Pembina": ["Aah Hj Encep Bahrul Ulum"],
    "Penasihat": ["Pih Uce"],
    "Ketua DKM": ["Aang Deden Kasyful Anwar"],
    "Wakil Ketua": ["Iden Tazuni"],
    "Sekretaris": ["Ustadz Ihin"],
    "Bendahara": ["Aceng Abdul Roup"],
    "Pendidikan & Pengajian": ["Usep", "Bim-Bim", "Dede Adol", "M. Oleh"],
    "Humas & Informasi": ["Wa Hamid", "Ahmad Fauzi", "Ruslan Abdul Gani", "Yudi"],
    "Sosial & Kemanusiaan": ["Wa Adu", "M. Ajang", "M. Ece Abda", "M. Iman", "Ceng Sasa"],
    "Sarana & Prasarana": ["Agus Sobur", "Dede Eon", "Jiun", "Dede Ro’i", "Andri", "Empay"],
    "Kebersihan": ["Baba", "Ujang", "Endat"],
    "Ibadah & Dakwah": ["Aang Deden", "Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Pih Uce"],
    "Keamanan": ["Ace Pu’ad", "Nyanyang (Gonyol)", "M. Emon"]
}

pengajian_malam_rabu = ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden"]
pengajian_senin = ["Ustadz Nanang", "Aang Deden", "Ustadz Ihin", "Ustadz Ihin"]

agenda_tetap = [
    ["Pengajian Malam Rabu", "Malam Rabu", "19:30 - 21:30 WIB"],
    ["Pengajian Senenan", "Senin", "07:30 - 09:00 WIB"],
    ["Syahriahan Sholawat", "Malam Jumat awal bulan Hijriah", "20:00 - 21:30 WIB"],
]

DATA_KAS_AWAL = [
    {"Tanggal": "2026-05-01", "Jenis": "Pemasukan", "Kategori": "Saldo Awal", "Keterangan": "Serah terima dari bendahara lama", "Jumlah": 7080000, "Petugas": "Aceng Abdul Roup"},
    {"Tanggal": "2026-05-15", "Jenis": "Pemasukan", "Kategori": "Kotak Amal", "Keterangan": "Setoran kotak amal diterima bendahara", "Jumlah": 1661500, "Petugas": "Aceng Abdul Roup"},
    {"Tanggal": "2026-05-31", "Jenis": "Pemasukan", "Kategori": "Kotak Amal", "Keterangan": "Pembukaan kotak amal", "Jumlah": 942500, "Petugas": "Aceng Abdul Roup"},
    {"Tanggal": "2026-06-01", "Jenis": "Pengeluaran", "Kategori": "Perlengkapan", "Keterangan": "White board 2 buah dan spidol", "Jumlah": 358000, "Petugas": "Aceng Abdul Roup"},
]

DATA_JAMAAH_AWAL = [
    ["Usep", "Laki-laki", "6285871353759", "Ya", "-"],
    ["Elan", "Laki-laki", "6281916018461", "Ya", "-"],
    ["Joni", "Laki-laki", "628562287257", "Ya", "-"],
    ["Aang Kipl", "Laki-laki", "6285722764887", "Ya", "-"],
    ["Ustadz Ihin", "Laki-laki", "6287799541295", "Ya", "-"],
    ["Mang Ade Jiban", "Laki-laki", "6285927979070", "Ya", "-"],
    ["Dede Ro'i", "Laki-laki", "6281912607968", "Ya", "-"],
    ["Yudi", "Laki-laki", "6287708449234", "Ya", "-"],
    ["Amoy", "Perempuan", "6285794505300", "Ya", "-"],
    ["Zuri", "Perempuan", "6285220812225", "Ya", "-"],
    ["Mang Emon", "Laki-laki", "6283893804659", "Ya", "-"],
    ["Wawan", "Laki-laki", "6283113138008", "Ya", "-"],
    ["Hj. Uus", "Perempuan", "6283869494725", "Ya", "-"],
    ["Hanah", "Perempuan", "6287875612116", "Ya", "-"],
    ["Th. Ai Warung", "Perempuan", "6281911421598", "Ya", "-"],
    ["Th. Ai", "Perempuan", "6285603226828", "Ya", "-"],
    ["Neng", "Perempuan", "6283833418940", "Ya", "-"],
    ["Aang Deden", "Laki-laki", "6285722090778", "Khusus", "Hanya jika beliau pengisi acara"],
]


def rupiah(angka):
    try:
        return "Rp {:,.0f}".format(float(angka)).replace(",", ".")
    except:
        return "Rp 0"

def init_kas():
    if not os.path.exists(KAS_FILE):
        pd.DataFrame(DATA_KAS_AWAL, columns=KOLOM_KAS).to_csv(KAS_FILE, index=False)

def load_kas():
    init_kas()
    try:
        df = pd.read_csv(KAS_FILE)
        # dukung file lama yang pakai huruf kecil dari V12
        rename_map = {
            "tanggal": "Tanggal",
            "jenis": "Jenis",
            "kategori": "Kategori",
            "keterangan": "Keterangan",
            "jumlah": "Jumlah",
            "petugas": "Petugas",
        }
        df = df.rename(columns=rename_map)
        for k in KOLOM_KAS:
            if k not in df.columns:
                df[k] = 0 if k == "Jumlah" else ""
        df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)
        return df[KOLOM_KAS]
    except Exception:
        return pd.DataFrame(DATA_KAS_AWAL, columns=KOLOM_KAS)

def save_kas(df):
    df.to_csv(KAS_FILE, index=False)

def load_pengumuman():
    if os.path.exists(PENGUMUMAN_FILE):
        try:
            df = pd.read_csv(PENGUMUMAN_FILE)
            for k in KOLOM_PENGUMUMAN:
                if k not in df.columns:
                    df[k] = ""
            return df[KOLOM_PENGUMUMAN]
        except:
            return pd.DataFrame(columns=KOLOM_PENGUMUMAN)
    return pd.DataFrame(columns=KOLOM_PENGUMUMAN)

def save_pengumuman(df):
    df.to_csv(PENGUMUMAN_FILE, index=False)

def init_jamaah():
    if not os.path.exists(JAMAAH_FILE):
        pd.DataFrame(DATA_JAMAAH_AWAL, columns=KOLOM_JAMAAH).to_csv(JAMAAH_FILE, index=False)

def load_sheet_csv(sheet_name):
    """Baca Google Sheet publik via CSV. Jika gagal, return DataFrame kosong."""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
        return pd.read_csv(url, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame()

def rapikan_jamaah_df(df):
    for k in KOLOM_JAMAAH:
        if k not in df.columns:
            df[k] = ""
    df = df[KOLOM_JAMAAH].copy()
    df["Nama"] = df["Nama"].astype(str).str.strip()
    df["JenisKelamin"] = df["JenisKelamin"].astype(str).str.strip()
    df["JenisKelamin"] = df["JenisKelamin"].replace({
        "L": "Laki-laki", "l": "Laki-laki", "LAKI-LAKI": "Laki-laki", "Laki Laki": "Laki-laki",
        "P": "Perempuan", "p": "Perempuan", "PEREMPUAN": "Perempuan"
    })
    df["NoWA"] = df["NoWA"].astype(str).apply(normalisasi_wa)
    df["Aktif"] = df["Aktif"].astype(str).str.strip().replace({"": "Ya", "YA": "Ya", "ya": "Ya"})
    df["Catatan"] = df["Catatan"].astype(str).replace({"": "-"})
    df = df[df["Nama"] != ""].copy()
    return df

def load_jamaah():
    # Prioritas utama: Google Sheet Jamaah
    online = load_sheet_csv("Jamaah")
    if not online.empty:
        return rapikan_jamaah_df(online)

    # Fallback: CSV lokal lama
    init_jamaah()
    try:
        df = pd.read_csv(JAMAAH_FILE, dtype=str).fillna("-")
        for k in KOLOM_JAMAAH:
            if k not in df.columns:
                df[k] = "-"
        return rapikan_jamaah_df(df)
    except Exception:
        return pd.DataFrame(DATA_JAMAAH_AWAL, columns=KOLOM_JAMAAH)

def load_setting_wa():
    df = load_sheet_csv("Setting WA")
    if df.empty or "Key" not in df.columns or "Value" not in df.columns:
        return {}
    return dict(zip(df["Key"].astype(str), df["Value"].astype(str)))

def pengumuman_aktif_24jam(df):
    """Ambil pengumuman yang masih aktif maksimal 1x24 jam untuk dashboard."""
    if df is None or df.empty:
        return pd.DataFrame(columns=KOLOM_PENGUMUMAN)

    hasil = df.copy()
    for k in KOLOM_PENGUMUMAN:
        if k not in hasil.columns:
            hasil[k] = ""

    hasil["_waktu"] = pd.to_datetime(hasil["Tanggal"], errors="coerce")
    sekarang = waktu_wib()
    batas = sekarang - timedelta(hours=24)
    hasil = hasil[hasil["_waktu"].notna() & (hasil["_waktu"] >= batas)].copy()
    return hasil.drop(columns=["_waktu"], errors="ignore")


def is_aang_deden_row(row):
    nama = str(row.get("Nama", "")).lower()
    catatan = str(row.get("Catatan", "")).lower()
    aktif = str(row.get("Aktif", "")).lower()
    return "aang deden" in nama or (aktif == "khusus" and "pengisi" in catatan)


def filter_jamaah_aktif_umum(df):
    """Target umum: hanya Aktif=Ya, sehingga Aang Deden/Khusus tidak ikut semua pesan."""
    if df is None or df.empty:
        return pd.DataFrame(columns=KOLOM_JAMAAH)
    target = df[df["Aktif"].astype(str).str.lower().eq("ya")].copy()
    target = target[~target.apply(is_aang_deden_row, axis=1)].copy()
    return target


def tambah_khusus_jika_pengisi(target, jamaah_df, pengisi_text=""):
    """Tambahkan jamaah Khusus hanya jika nama beliau memang menjadi pengisi/pimpinan kegiatan."""
    if jamaah_df is None or jamaah_df.empty:
        return target
    if "aang deden" not in str(pengisi_text).lower():
        return target
    khusus = jamaah_df[jamaah_df.apply(is_aang_deden_row, axis=1)].copy()
    if khusus.empty:
        return target
    return pd.concat([target, khusus], ignore_index=True).drop_duplicates(subset=["NoWA"])

def save_jamaah(df):
    # Fallback lokal lama, tetap disimpan untuk cadangan.
    df.to_csv(JAMAAH_FILE, index=False)


def simpan_jamaah_google(nama, jk, nowa, aktif, catatan):
    """Simpan data jamaah langsung ke Google Sheet tab Jamaah."""
    try:
        sh, info = koneksi_google_sheet_write()
        if sh is None:
            return False, info

        ws = sh.worksheet("Jamaah")
        ws.append_row(
            [str(nama).strip(), str(jk).strip(), normalisasi_wa(nowa), str(aktif).strip(), str(catatan).strip() or "-"],
            value_input_option="USER_ENTERED"
        )
        return True, "Data jamaah berhasil disimpan ke Google Sheet."
    except Exception as e:
        return False, str(e)

def normalisasi_wa(nomor):
    nomor = str(nomor).replace("+", "").replace("-", "").replace(" ", "").strip()
    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    return nomor

def wa_nomor_link(nomor, text):
    return f"https://wa.me/{normalisasi_wa(nomor)}?text=" + urllib.parse.quote(text)

def pesan_senenan(pengisi):
    return f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

Besok seperti biasa akan dilaksanakan Pengajian Senenan di Madrasah Al-Falah pada pukul 07.30 WIB.

👳 Pengisi:
{pengisi}

📍 Tempat:
Madrasah Al-Falah

👥 Grup Jamaah AL-BARZANJI:
{GRUP_AL_BARZANJI}

🌐 Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Terima kasih kepada jamaah yang hadir tepat waktu.

Pesan ini dikirim otomatis melalui Al-Falah Digital."""

def pesan_malam_rabu(pengisi):
    return f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

Malam ini akan dilaksanakan Pengajian Malam Rabu di Madrasah Al-Falah pada pukul 19.30 WIB.

👳 Pengisi:
{pengisi}

📍 Tempat:
Madrasah Al-Falah

👥 Grup Jamaah AL-BARZANJI:
{GRUP_AL_BARZANJI}

🌐 Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Terima kasih kepada jamaah yang hadir tepat waktu.

Pesan ini dikirim otomatis melalui Al-Falah Digital."""

def pesan_syahriahan():
    return f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

Malam ini akan dilaksanakan Syahriahan Sholawat di Masjid Jami Al-Falah.

👳 Pimpinan:
Aang Deden Kasyful Anwar

📍 Tempat:
Masjid Jami Al-Falah

🌐 Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Terima kasih atas partisipasi seluruh jamaah dan masyarakat.

Pesan ini dikirim otomatis melalui Al-Falah Digital."""

def banner_base64():
    if os.path.exists(BANNER_FILE):
        with open(BANNER_FILE, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def tampilkan_banner_premium(tanggal_wib, hijriah_text):
    img64 = banner_base64()
    if img64:
        st.markdown(f"""
        <div style="
            position:relative;
            height:240px;
            border-radius:28px;
            border:3px solid #FFD700;
            background-image:linear-gradient(rgba(0,0,0,.20),rgba(0,0,0,.55)),url('data:image/png;base64,{img64}');
            background-size:cover;
            background-position:center;
            box-shadow:0 0 32px rgba(255,215,0,.85);
            overflow:hidden;
            margin-bottom:18px;
        ">
            <div style="position:absolute;left:0;right:0;bottom:0;padding:22px;text-align:center;background:linear-gradient(transparent,rgba(0,0,0,.72));">
                <div style="color:#FFD700;font-size:44px;font-weight:950;text-shadow:0 0 12px #FFD700,0 0 28px #00ff66;">🕌 MASJID JAMI AL-FALAH</div>
                <div style="color:white;font-size:20px;font-weight:850;">Smart Masjid Digital • Kas • Jadwal Pengajian • Pengumuman</div>
                <div style="display:inline-block;margin-top:10px;background:#020617;color:#00ff66;border:2px solid #FFD700;border-radius:14px;padding:9px 16px;font-weight:900;box-shadow:0 0 18px rgba(255,215,0,.75);">📅 {format_tanggal(tanggal_wib)} &nbsp; | &nbsp; 🌙 {hijriah_text}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#011c16,#064e3b,#022c22);padding:24px;border-radius:24px;text-align:center;border:2px solid #FFD700;box-shadow:0 0 28px rgba(255,215,0,.7);margin-bottom:18px;">
            <div style="color:#FFD700;font-size:42px;font-weight:950;text-shadow:0 0 14px #FFD700;">🕌 MASJID JAMI AL-FALAH</div>
            <div style="color:white;font-size:18px;font-weight:800;">Smart Masjid Digital • Kas • Jadwal Pengajian • Pengumuman</div>
            <div style="display:inline-block;margin-top:10px;background:#020617;color:#00ff66;border:2px solid #FFD700;border-radius:14px;padding:9px 16px;font-weight:900;">📅 {format_tanggal(tanggal_wib)} &nbsp; | &nbsp; 🌙 {hijriah_text}</div>
        </div>
        """, unsafe_allow_html=True)

def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)

def kirim_telegram(pesan):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        try:
            token = st.secrets["TELEGRAM_BOT_TOKEN"]
        except:
            token = None
    if not token:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": pesan}, timeout=10)
        return True
    except:
        return False


def ambil_secret(nama, default=""):
    try:
        return st.secrets[nama]
    except Exception:
        return os.getenv(nama, default)

def kirim_fonnte(nomor, pesan):
    token = ambil_secret("FONNTE_TOKEN", "") or ambil_secret("FONTE_TOKEN", "")
    if not token:
        return False, "FONNTE_TOKEN belum diisi di Streamlit Secrets"

    nomor = normalisasi_wa(nomor)
    try:
        res = requests.post(
            "https://api.fonnte.com/send",
            headers={"Authorization": token},
            data={
                "target": nomor,
                "message": pesan,
                "countryCode": "62",
            },
            timeout=30,
        )
        try:
            hasil = res.json()
        except Exception:
            hasil = {"raw": res.text}

        if res.status_code == 200:
            return True, str(hasil)
        return False, f"HTTP {res.status_code}: {hasil}"
    except Exception as e:
        return False, str(e)


def ambil_service_account_info():
    """Ambil data Service Account dari Streamlit Secrets.
    Mendukung 3 format:
    1) [gcp_service_account]
    2) GOOGLE_SERVICE_ACCOUNT berisi JSON string
    3) key service account ditaruh langsung di root Secrets
    """
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    try:
        if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
            raw = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
            if isinstance(raw, str):
                return json.loads(raw)
            return dict(raw)
    except Exception:
        pass

    # Format root-level seperti: type, project_id, private_key, client_email, dll.
    keys = [
        "type", "project_id", "private_key_id", "private_key",
        "client_email", "client_id", "auth_uri", "token_uri",
        "auth_provider_x509_cert_url", "client_x509_cert_url", "universe_domain"
    ]
    info = {}
    for k in keys:
        try:
            if k in st.secrets:
                info[k] = st.secrets[k]
        except Exception:
            pass

    if "private_key" in info:
        info["private_key"] = str(info["private_key"]).replace("\\n", "\n")

    if "client_email" in info and "private_key" in info:
        info.setdefault("type", "service_account")
        info.setdefault("token_uri", "https://oauth2.googleapis.com/token")
        return info

    return None


def koneksi_google_sheet_write():
    try:
        info = ambil_service_account_info()
        if not info:
            return None, "Service Account belum ditemukan di Streamlit Secrets"

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(SHEET_ID), "OK"
    except Exception as e:
        return None, str(e)


def simpan_log_wa(nama, nowa, jenis_pesan, status, keterangan):
    try:
        sh, info = koneksi_google_sheet_write()
        if sh is None:
            return False, info

        ws = sh.worksheet("Log WA")
        waktu = waktu_wib().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([
            waktu,
            str(nama),
            str(nowa),
            str(jenis_pesan),
            str(status),
            str(keterangan)[:500],
        ], value_input_option="USER_ENTERED")
        return True, "Log tersimpan"
    except Exception as e:
        return False, str(e)


def baca_log_wa():
    try:
        sh, info = koneksi_google_sheet_write()
        if sh is None:
            return pd.DataFrame(columns=["Tanggal", "Nama", "NoWA", "JenisPesan", "Status", "Keterangan"])
        ws = sh.worksheet("Log WA")
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame(columns=["Tanggal", "Nama", "NoWA", "JenisPesan", "Status", "Keterangan"])


def tanggal_berikutnya(target_weekday):
    hari_ini = date.today()
    selisih = (target_weekday - hari_ini.weekday()) % 7
    return hari_ini + timedelta(days=selisih)

def index_rotasi_rabu(tgl_rabu):
    start = date(2026, 6, 16)
    return ((tgl_rabu - start).days // 7) % 4

def index_rotasi_senin(tgl_senin):
    start = date(2026, 6, 15)
    return ((tgl_senin - start).days // 7) % 4

def format_tanggal(tgl):
    hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    return f"{hari[tgl.weekday()]}, {tgl.day} {bulan[tgl.month-1]} {tgl.year}"

@st.cache_data(ttl=3600)
def kalender_hijriah_online(tgl):
    try:
        tanggal_api = tgl.strftime("%d-%m-%Y")
        url = f"https://api.aladhan.com/v1/gToH/{tanggal_api}"
        r = requests.get(url, timeout=10).json()
        h = r["data"]["hijri"]

        nama_bulan_id = {
            "Muharram": "Muharram",
            "Safar": "Safar",
            "Rabīʿ al-awwal": "Rabiul Awal",
            "Rabīʿ al-thānī": "Rabiul Akhir",
            "Jumādá al-ūlá": "Jumadil Awal",
            "Jumādá al-ākhirah": "Jumadil Akhir",
            "Rajab": "Rajab",
            "Shaʿbān": "Sya'ban",
            "Ramaḍān": "Ramadhan",
            "Shawwāl": "Syawal",
            "Dhū al-Qaʿdah": "Dzulqa'dah",
            "Dhū al-Ḥijjah": "Dzulhijjah",
        }

        bulan_en = h["month"]["en"]
        bulan_id = nama_bulan_id.get(bulan_en, bulan_en)
        return f"{int(h['day'])} {bulan_id} {h['year']} H"
    except:
        return "1 Muharram 1448 H"

@st.cache_data(ttl=1800)
def jadwal_sholat_cianjur():
    try:
        url = "https://api.aladhan.com/v1/timingsByCity"
        params = {
            "city": "Cianjur",
            "country": "Indonesia",
            "method": 20
        }
        r = requests.get(url, params=params, timeout=10).json()
        t = r["data"]["timings"]
        return {
            "Subuh": t["Fajr"][:5],
            "Dzuhur": t["Dhuhr"][:5],
            "Ashar": t["Asr"][:5],
            "Maghrib": t["Maghrib"][:5],
            "Isya": t["Isha"][:5],
        }
    except:
        return {
            "Subuh": "04:35",
            "Dzuhur": "11:55",
            "Ashar": "15:15",
            "Maghrib": "17:50",
            "Isya": "19:00",
        }

def waktu_wib():
    return datetime.utcnow() + timedelta(hours=7)

def daftar_agenda_terdekat():
    sekarang = waktu_wib()
    agenda = []

    tgl_selasa = tanggal_berikutnya(1)
    mulai_selasa = datetime(tgl_selasa.year, tgl_selasa.month, tgl_selasa.day, 19, 30)
    selesai_selasa = datetime(tgl_selasa.year, tgl_selasa.month, tgl_selasa.day, 21, 30)

    if selesai_selasa < sekarang:
        mulai_selasa += timedelta(days=7)
        selesai_selasa += timedelta(days=7)

    agenda.append({
        "nama": "Pengajian Malam Rabu",
        "mulai": mulai_selasa,
        "selesai": selesai_selasa,
        "pengisi": pengajian_malam_rabu[index_rotasi_rabu(mulai_selasa.date())],
    })

    tgl_senin = tanggal_berikutnya(0)
    mulai_senin = datetime(tgl_senin.year, tgl_senin.month, tgl_senin.day, 7, 30)
    selesai_senin = datetime(tgl_senin.year, tgl_senin.month, tgl_senin.day, 9, 0)

    if selesai_senin < sekarang:
        mulai_senin += timedelta(days=7)
        selesai_senin += timedelta(days=7)

    agenda.append({
        "nama": "Pengajian Senenan",
        "mulai": mulai_senin,
        "selesai": selesai_senin,
        "pengisi": pengajian_senin[index_rotasi_senin(mulai_senin.date())],
    })

    return sorted(agenda, key=lambda x: x["mulai"])

def status_pengajian_terdekat():
    sekarang = waktu_wib()
    agenda = daftar_agenda_terdekat()

    for item in agenda:
        if item["mulai"] <= sekarang <= item["selesai"]:
            item["target"] = item["selesai"]
            return item, "berjalan"

    for item in agenda:
        if item["mulai"] > sekarang:
            item["target"] = item["mulai"]
            return item, "menunggu"

    agenda[0]["target"] = agenda[0]["mulai"]
    return agenda[0], "menunggu"





def tampilkan_running_text_mewah(teks, mode_status="SELAMAT DATANG"):
    safe_text = str(teks).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    components.html(f"""
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap');
    body {{ margin:0; padding:0; background:transparent; }}

    .lux-led-wrapper {{
        background:linear-gradient(135deg,#020617,#064e3b,#022c22);
        border:3px solid #FFD700;
        border-radius:24px;
        height:132px;
        overflow:hidden;
        position:relative;
        box-shadow:0 0 14px rgba(255,215,0,.55), inset 0 0 12px rgba(0,255,102,.10);
    }}

    .lux-led-text {{
        position:absolute;
        left:36px;
        right:36px;
        text-align:center;
        color:#eafff2;
        font-family:'Poppins', sans-serif;
        font-size:22px;
        font-weight:800;
        letter-spacing:.3px;
        line-height:1.55;
        text-shadow:0 0 3px rgba(0,255,102,.65);
        animation: naikMewah 28s linear infinite;
        white-space:normal;
    }}

    .lux-dot {{
        position:absolute;
        width:9px;
        height:9px;
        border-radius:50%;
        background:#FFD700;
        box-shadow:0 0 8px #FFD700;
        animation:kedipLampu 1.4s infinite;
    }}

    .dot1 {{ top:16px; left:16px; }}
    .dot2 {{ top:16px; right:16px; animation-delay:.25s; }}
    .dot3 {{ bottom:16px; left:16px; animation-delay:.5s; }}
    .dot4 {{ bottom:16px; right:16px; animation-delay:.75s; }}

    @keyframes naikMewah {{
        0% {{ top:112%; opacity:0; }}
        10% {{ opacity:1; }}
        38% {{ top:50%; transform:translateY(-50%); opacity:1; }}
        76% {{ top:50%; transform:translateY(-50%); opacity:1; }}
        100% {{ top:-115%; opacity:0; }}
    }}

    @keyframes kedipLampu {{
        0%,100% {{ opacity:1; transform:scale(1); }}
        50% {{ opacity:.45; transform:scale(.8); }}
    }}
    </style>
    </head>
    <body>
        <div class="lux-led-wrapper">
            <div class="lux-dot dot1"></div>
            <div class="lux-dot dot2"></div>
            <div class="lux-dot dot3"></div>
            <div class="lux-dot dot4"></div>
            <div class="lux-led-text">{safe_text}</div>
        </div>
    </body>
    </html>
    """, height=152)

def tampilkan_kartu_bank(judul, nilai, subjudul="", ikon="💳", tema="hijau"):
    warna = {
        "hijau": ("#064e3b", "#16a34a", "#bbf7d0"),
        "emas": ("#78350f", "#f59e0b", "#fef3c7"),
        "biru": ("#1e3a8a", "#2563eb", "#dbeafe"),
        "ungu": ("#581c87", "#9333ea", "#f3e8ff"),
        "merah": ("#7f1d1d", "#dc2626", "#fee2e2"),
    }
    a, b, c = warna.get(tema, warna["hijau"])
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,{a},{b});
        border-radius:24px;
        padding:24px;
        min-height:150px;
        color:white;
        box-shadow:0 12px 28px rgba(0,0,0,.18);
        border:2px solid rgba(255,215,0,.75);
        position:relative;
        overflow:hidden;
        margin-bottom:16px;
    ">
        <div style="position:absolute;right:-35px;top:-35px;width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,.12);"></div>
        <div style="font-size:30px;">{ikon}</div>
        <div style="font-size:16px;font-weight:800;margin-top:8px;color:{c};">{judul}</div>
        <div style="font-size:34px;font-weight:950;margin-top:8px;text-shadow:0 0 10px rgba(0,0,0,.25);">{nilai}</div>
        <div style="font-size:13px;margin-top:12px;opacity:.92;">{subjudul}</div>
        <div style="font-size:12px;margin-top:10px;letter-spacing:2px;opacity:.65;">AL-FALAH DIGITAL CARD</div>
    </div>
    """, unsafe_allow_html=True)


def detail_keuangan_box(kas_df, label_filter=None, judul="Detail Keuangan"):
    df = kas_df.copy()

    if label_filter:
        df = df[df["Kategori"].astype(str).str.contains(label_filter, case=False, na=False)].copy()

    if df.empty:
        st.info(f"Belum ada data untuk {judul}.")
        return

    masuk = df[df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    keluar = df[df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo_detail = masuk - keluar

    a, b, c = st.columns(3)
    a.metric("Pemasukan", rupiah(masuk))
    b.metric("Pengeluaran", rupiah(keluar))
    c.metric("Saldo Akhir", rupiah(saldo_detail))

    tampil = df.tail(20).copy()
    tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
    st.dataframe(tampil, use_container_width=True)


def angka_sheet(x):
    try:
        s = str(x).replace("Rp", "").replace(".", "").replace(",", "").replace(" ", "").strip()
        if s == "" or s.lower() == "nan":
            return 0
        return float(s)
    except Exception:
        return 0

def load_kas_terpisah(sheet_name):
    try:
        df = load_sheet_csv(sheet_name)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Tanggal", "Keterangan", "Masuk", "Keluar", "Petugas"])

        for col in ["Tanggal", "Keterangan", "Masuk", "Keluar", "Petugas"]:
            if col not in df.columns:
                df[col] = ""

        df = df[["Tanggal", "Keterangan", "Masuk", "Keluar", "Petugas"]].copy()
        df["Masuk"] = df["Masuk"].apply(angka_sheet)
        df["Keluar"] = df["Keluar"].apply(angka_sheet)
        return df
    except Exception:
        return pd.DataFrame(columns=["Tanggal", "Keterangan", "Masuk", "Keluar", "Petugas"])

def saldo_kas_terpisah(sheet_name):
    df = load_kas_terpisah(sheet_name)
    masuk = df["Masuk"].sum() if not df.empty else 0
    keluar = df["Keluar"].sum() if not df.empty else 0
    return masuk, keluar, masuk - keluar, df

def detail_keuangan_terpisah_box(df, judul="Detail Keuangan"):
    if df is None or df.empty:
        st.info(f"Belum ada data untuk {judul}.")
        return

    masuk = df["Masuk"].sum()
    keluar = df["Keluar"].sum()
    saldo_detail = masuk - keluar

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#020617,#064e3b);border:2px solid #FFD700;border-radius:22px;padding:18px;color:white;margin-bottom:12px;box-shadow:0 0 18px rgba(255,215,0,.45);">
        <div style="font-size:20px;font-weight:900;color:#FFD700;margin-bottom:10px;">{judul}</div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <div style="flex:1;min-width:150px;background:rgba(255,255,255,.08);padding:14px;border-radius:16px;">
                <div style="font-size:13px;color:#bbf7d0;font-weight:800;">Pemasukan</div>
                <div style="font-size:26px;font-weight:950;color:#00ff66;">{rupiah(masuk)}</div>
            </div>
            <div style="flex:1;min-width:150px;background:rgba(255,255,255,.08);padding:14px;border-radius:16px;">
                <div style="font-size:13px;color:#fecaca;font-weight:800;">Pengeluaran</div>
                <div style="font-size:26px;font-weight:950;color:#f87171;">{rupiah(keluar)}</div>
            </div>
            <div style="flex:1;min-width:150px;background:rgba(255,255,255,.08);padding:14px;border-radius:16px;">
                <div style="font-size:13px;color:#fef3c7;font-weight:800;">Saldo Akhir</div>
                <div style="font-size:26px;font-weight:950;color:#FFD700;">{rupiah(saldo_detail)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tampil = df.tail(20).copy()
    tampil["Masuk"] = tampil["Masuk"].apply(rupiah)
    tampil["Keluar"] = tampil["Keluar"].apply(rupiah)
    st.dataframe(tampil, use_container_width=True, hide_index=True)

def detail_keuangan_masjid_box(kas_df):
    if kas_df is None or kas_df.empty:
        st.info("Belum ada data Kas Masjid.")
        return

    df = kas_df.copy()
    masuk = df[df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    keluar = df[df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo_detail = masuk - keluar

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#020617,#065f46);border:2px solid #FFD700;border-radius:22px;padding:18px;color:white;margin-bottom:12px;box-shadow:0 0 18px rgba(255,215,0,.45);">
        <div style="font-size:20px;font-weight:900;color:#FFD700;margin-bottom:10px;">Detail Kas Masjid</div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <div style="flex:1;min-width:150px;background:rgba(255,255,255,.08);padding:14px;border-radius:16px;">
                <div style="font-size:13px;color:#bbf7d0;font-weight:800;">Pemasukan</div>
                <div style="font-size:26px;font-weight:950;color:#00ff66;">{rupiah(masuk)}</div>
            </div>
            <div style="flex:1;min-width:150px;background:rgba(255,255,255,.08);padding:14px;border-radius:16px;">
                <div style="font-size:13px;color:#fecaca;font-weight:800;">Pengeluaran</div>
                <div style="font-size:26px;font-weight:950;color:#f87171;">{rupiah(keluar)}</div>
            </div>
            <div style="flex:1;min-width:150px;background:rgba(255,255,255,.08);padding:14px;border-radius:16px;">
                <div style="font-size:13px;color:#fef3c7;font-weight:800;">Saldo Akhir</div>
                <div style="font-size:26px;font-weight:950;color:#FFD700;">{rupiah(saldo_detail)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pengeluaran_df = df[df["Jenis"] == "Pengeluaran"].copy()
    if not pengeluaran_df.empty:
        st.markdown("### 🧾 Keterangan Pengeluaran Kas Masjid")
        tampil_pengeluaran = pengeluaran_df[["Tanggal", "Kategori", "Keterangan", "Jumlah", "Petugas"]].tail(10).copy()
        tampil_pengeluaran["Jumlah"] = tampil_pengeluaran["Jumlah"].apply(rupiah)
        st.dataframe(tampil_pengeluaran, use_container_width=True, hide_index=True)

    st.markdown("### 📋 Riwayat Transaksi Terakhir")
    tampil = df.tail(20).copy()
    tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
    st.dataframe(tampil, use_container_width=True, hide_index=True)



def hikmah_harian():
    daftar = [
        "Barang siapa memakmurkan masjid, semoga Allah memakmurkan hatinya dengan iman.",
        "Shalat berjamaah adalah penguat ukhuwah dan persatuan umat.",
        "Sebaik-baik manusia adalah yang paling bermanfaat bagi sesama.",
        "Infak yang ikhlas akan menjadi cahaya dan keberkahan bagi pemiliknya.",
        "Mari makmurkan Masjid Jami Al-Falah dengan shalat, ilmu, dzikir, dan sedekah."
    ]
    try:
        idx = waktu_wib().toordinal() % len(daftar)
        return daftar[idx]
    except Exception:
        return daftar[0]

def buat_laporan_bulanan_text():
    sekarang = waktu_wib()
    awal_bulan_ini = datetime(sekarang.year, sekarang.month, 1)
    akhir_bulan_lalu = awal_bulan_ini - timedelta(days=1)
    periode = akhir_bulan_lalu.strftime("%m-%Y")

    df = kas_df.copy()
    df["Tanggal_dt"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    laporan = df[
        (df["Tanggal_dt"].dt.year == akhir_bulan_lalu.year) &
        (df["Tanggal_dt"].dt.month == akhir_bulan_lalu.month)
    ].copy()

    masuk = laporan[laporan["Jenis"] == "Pemasukan"]["Jumlah"].sum() if not laporan.empty else 0
    keluar = laporan[laporan["Jenis"] == "Pengeluaran"]["Jumlah"].sum() if not laporan.empty else 0

    total_masuk = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    total_keluar = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo_masjid = total_masuk - total_keluar

    try:
        _, _, saldo_madrasah, _ = saldo_kas_terpisah("Kas Madrasah")
    except Exception:
        saldo_madrasah = 0
    try:
        _, _, saldo_rajaban, _ = saldo_kas_terpisah("Kas Rajaban")
    except Exception:
        saldo_rajaban = 0

    return f"""📊 LAPORAN KEUANGAN BULANAN
MASJID JAMI AL-FALAH

السلام عليكم ورحمة الله وبركاته

Berikut kami sampaikan laporan keuangan Masjid Jami Al-Falah periode {periode} sebagai bentuk transparansi kepada seluruh jamaah.

💰 Kas Masjid
Pemasukan bulan lalu : {rupiah(masuk)}
Pengeluaran bulan lalu : {rupiah(keluar)}
Saldo akhir : {rupiah(saldo_masjid)}

🏫 Kas Madrasah
Saldo akhir : {rupiah(saldo_madrasah)}

🌙 Iuran Rajaban
Saldo akhir : {rupiah(saldo_rajaban)}

Rincian lengkap dapat dilihat pada aplikasi Al-Falah Digital.

Semoga Allah SWT menerima amal kebaikan para jamaah dan muhsinin.

جزاكم الله خيرا كثيرا

والسلام عليكم ورحمة الله وبركاته

Pesan ini dikirim otomatis oleh Sistem Informasi Masjid Jami Al-Falah."""

def boleh_kirim_ke_jamaah(row, pengisi_kegiatan=""):
    nama = str(row.get("Nama", "")).lower()
    if "aang deden" in nama and "aang deden" not in str(pengisi_kegiatan).lower():
        return False
    aktif = str(row.get("Aktif", "")).strip().lower()
    return aktif in ["ya", "khusus"]

def daftar_target_broadcast(jamaah_df, pengisi_kegiatan=""):
    if jamaah_df is None or jamaah_df.empty:
        return pd.DataFrame(columns=KOLOM_JAMAAH)
    target = jamaah_df[jamaah_df.apply(lambda r: boleh_kirim_ke_jamaah(r, pengisi_kegiatan), axis=1)].copy()
    target = target[target["NoWA"].astype(str).str.strip() != ""].copy()
    return target.drop_duplicates(subset=["NoWA"])

def kirim_broadcast_aman(target_df, pesan, jenis_pesan="Broadcast", delay_detik=25, batas_kirim=5):
    import time
    berhasil = 0
    gagal = 0
    hasil = []

    for _, row in target_df.head(int(batas_kirim)).iterrows():
        nama = str(row.get("Nama", "Jamaah"))
        nomor = str(row.get("NoWA", ""))
        ok, info = kirim_fonnte(nomor, pesan)
        status = "Berhasil" if ok else "Gagal"
        if ok:
            berhasil += 1
        else:
            gagal += 1
        simpan_log_wa(nama, nomor, jenis_pesan, status, info)
        hasil.append({"Nama": nama, "NoWA": nomor, "Status": status, "Keterangan": str(info)[:200]})
        time.sleep(int(delay_detik))

    return berhasil, gagal, pd.DataFrame(hasil)

def tampilkan_mode_tv_masjid():
    agenda_status, status_pengajian = status_pengajian_terdekat()
    target_js = agenda_status["target"].strftime("%Y-%m-%dT%H:%M:%S")
    status_text = "SEDANG BERLANGSUNG" if status_pengajian == "berjalan" else "AKAN DIMULAI"
    teks_hikmah = hikmah_harian()

    components.html(f"""
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@800;900&family=Poppins:wght@700;800;900&display=swap');
    body {{ margin:0; background:#020617; color:white; font-family:'Poppins',sans-serif; }}
    .tv {{
        min-height:760px;
        background:radial-gradient(circle at top left, rgba(255,215,0,.22), transparent 28%), radial-gradient(circle at bottom right, rgba(0,255,120,.18), transparent 35%), linear-gradient(135deg,#020617,#064e3b,#022c22);
        border:4px solid #FFD700; border-radius:30px; padding:34px; text-align:center; box-shadow:0 0 36px rgba(255,215,0,.7);
    }}
    .title {{ font-family:'Cinzel',serif; color:#FFD700; font-size:54px; font-weight:900; letter-spacing:2px; margin-bottom:8px; }}
    .arab {{ font-size:34px; color:#fef3c7; margin-bottom:14px; }}
    .clock {{ background:#020617; border:3px solid #FFD700; border-radius:22px; display:inline-block; padding:16px 32px; color:#eafff2; font-size:58px; font-weight:900; margin:20px 0; }}
    .status {{ font-size:28px; color:#FFD700; font-weight:900; margin-top:14px; }}
    .agenda {{ font-size:42px; color:#00ff88; font-weight:900; margin-top:8px; }}
    .detail {{ font-size:25px; margin-top:12px; color:#f8fafc; }}
    .count {{ font-size:50px; color:#00ff88; font-weight:900; margin-top:18px; }}
    .hikmah {{ margin-top:34px; padding:22px; border-radius:22px; background:rgba(255,255,255,.08); border:1px solid rgba(255,215,0,.65); font-size:25px; line-height:1.55; color:#fefce8; }}
    </style>
    </head>
    <body>
    <div class="tv">
        <div class="arab">السلام عليكم ورحمة الله وبركاته</div>
        <div class="title">MASJID JAMI AL-FALAH</div>
        <div style="font-size:22px;color:#d1fae5;">Kp. Caringin RT/RW 005/005 Desa Sukasari</div>
        <div class="clock" id="jam"></div>
        <div style="font-size:24px;color:#fef3c7;">{format_tanggal(tanggal_wib)} • {hijriah_text}</div>
        <div class="status">{status_text}</div>
        <div class="agenda">{agenda_status['nama']}</div>
        <div class="detail">👳 Pengisi: {agenda_status['pengisi']} • {agenda_status['mulai'].strftime('%H:%M')} WIB</div>
        <div class="count" id="countdown"></div>
        <div class="hikmah">📖 {teks_hikmah}</div>
    </div>
    <script>
    function updateClock(){{
        const now = new Date();
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const wib = new Date(utc + (7 * 60 * 60 * 1000));
        let h = String(wib.getHours()).padStart(2,'0');
        let m = String(wib.getMinutes()).padStart(2,'0');
        let s = String(wib.getSeconds()).padStart(2,'0');
        document.getElementById("jam").innerHTML = h + ":" + m + ":" + s + " WIB";
    }}
    const target = new Date("{target_js}+07:00").getTime();
    function updateCountdown(){{
        const now = new Date().getTime();
        let diff = target - now;
        if(diff < 0) diff = 0;
        const days = Math.floor(diff / (1000*60*60*24));
        const hours = Math.floor((diff % (1000*60*60*24)) / (1000*60*60));
        const minutes = Math.floor((diff % (1000*60*60)) / (1000*60));
        const seconds = Math.floor((diff % (1000*60)) / 1000);
        document.getElementById("countdown").innerHTML = days + " Hari  " + hours + " Jam  " + minutes + " Menit  " + seconds + " Detik";
    }}
    setInterval(updateClock, 1000);
    setInterval(updateCountdown, 1000);
    updateClock();
    updateCountdown();
    </script>
    </body>
    </html>
    """, height=820)


def status_badge_kegiatan(target_dt, mulai_dt=None, selesai_dt=None):
    now = waktu_wib()
    if mulai_dt and selesai_dt and mulai_dt <= now <= selesai_dt:
        return "🔴 SEDANG BERLANGSUNG", "#dc2626"
    selisih = target_dt - now
    if selisih.total_seconds() < 0:
        return "✅ SELESAI", "#16a34a"
    if selisih.days == 0:
        return "🟡 HARI INI", "#f59e0b"
    if selisih.days == 1:
        return "🟠 BESOK", "#ea580c"
    return "🟢 AKAN DATANG", "#16a34a"

def teks_countdown_singkat(target_dt):
    now = waktu_wib()
    diff = target_dt - now
    if diff.total_seconds() <= 0:
        return "Sedang berlangsung / sudah dimulai"
    hari = diff.days
    jam = diff.seconds // 3600
    menit = (diff.seconds % 3600) // 60
    if hari > 0:
        return f"{hari} hari {jam} jam lagi"
    if jam > 0:
        return f"{jam} jam {menit} menit lagi"
    return f"{menit} menit lagi"

def nomor_pengisi(nama_pengisi):
    try:
        data = load_jamaah()
        if data is None or data.empty:
            return ""
        nama_low = str(nama_pengisi).lower()
        for _, r in data.iterrows():
            nama_j = str(r.get("Nama", "")).lower()
            if nama_j and (nama_j in nama_low or nama_low in nama_j):
                return str(r.get("NoWA", "")).strip()
    except Exception:
        pass
    return ""

def kartu_jadwal_premium(judul, icon, tanggal, waktu, pengisi, catatan, tema="hijau", mulai_dt=None, selesai_dt=None):
    warna = {
        "hijau": ("#022c22", "#047857", "#34d399"),
        "emas": ("#451a03", "#b45309", "#fbbf24"),
        "biru": ("#0f172a", "#1d4ed8", "#60a5fa"),
    }
    a, b, c = warna.get(tema, warna["hijau"])
    target_dt = mulai_dt if mulai_dt else waktu_wib()
    badge, badge_color = status_badge_kegiatan(target_dt, mulai_dt, selesai_dt)
    countdown = teks_countdown_singkat(target_dt)
    nomor = nomor_pengisi(pengisi)
    wa_link = f"https://wa.me/{nomor}" if nomor else "#"

    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,{a},{b});
        border:2px solid #FFD700;
        border-radius:26px;
        padding:24px;
        color:white;
        box-shadow:0 12px 30px rgba(0,0,0,.18);
        position:relative;
        overflow:hidden;
        min-height:280px;
        margin-bottom:18px;
    ">
        <div style="position:absolute;right:-40px;top:-40px;width:150px;height:150px;border-radius:50%;background:rgba(255,255,255,.12);"></div>
        <div style="position:absolute;top:18px;right:18px;background:{badge_color};color:white;padding:7px 13px;border-radius:999px;font-size:13px;font-weight:900;">
            {badge}
        </div>
        <div style="font-size:42px;margin-bottom:10px;">{icon}</div>
        <div style="font-size:29px;font-weight:950;color:#fff;text-shadow:0 0 8px rgba(0,0,0,.35);margin-bottom:16px;">
            {judul}
        </div>
        <div style="background:rgba(255,255,255,.10);border-radius:18px;padding:15px;margin-bottom:12px;border:1px solid rgba(255,255,255,.18);">
            <div style="font-size:16px;line-height:1.75;">
                📅 <b>Tanggal:</b> {tanggal}<br>
                🕘 <b>Waktu:</b> {waktu}<br>
                👳 <b>Pengisi:</b> {pengisi}<br>
                ⏳ <b>Status:</b> {countdown}
            </div>
        </div>
        <div style="font-size:14px;color:#fef3c7;line-height:1.5;margin-bottom:16px;">
            {catatan}
        </div>
        <a href="{wa_link}" target="_blank" style="
            display:inline-block;
            text-decoration:none;
            background:#25D366;
            color:white;
            font-weight:900;
            padding:10px 16px;
            border-radius:14px;
        ">📲 Hubungi Pengisi</a>
    </div>
    """, unsafe_allow_html=True)

def tampilkan_jadwal_premium_v211():
    st.markdown("## 📌 Jadwal Pengajian Minggu Ini")

    tgl_rabu = tanggal_berikutnya(1)
    pengisi_rabu = pengajian_malam_rabu[index_rotasi_rabu(tgl_rabu)]
    mulai_rabu = datetime.combine(tgl_rabu.date(), datetime.strptime("19:30", "%H:%M").time())
    selesai_rabu = datetime.combine(tgl_rabu.date(), datetime.strptime("21:30", "%H:%M").time())

    tgl_senin = tanggal_berikutnya(0)
    pengisi_senin = pengajian_senin[index_rotasi_senin(tgl_senin)]
    mulai_senin = datetime.combine(tgl_senin.date(), datetime.strptime("07:30", "%H:%M").time())
    selesai_senin = datetime.combine(tgl_senin.date(), datetime.strptime("09:00", "%H:%M").time())

    c1, c2 = st.columns(2)
    with c1:
        kartu_jadwal_premium(
            "Pengajian Malam Rabu",
            "📖",
            format_tanggal(tgl_rabu),
            "19:30 - 21:30 WIB",
            pengisi_rabu,
            "Catatan: Jika ustadz berhalangan, akan diganti oleh ustadz lain.",
            "hijau",
            mulai_dt=mulai_rabu,
            selesai_dt=selesai_rabu
        )
    with c2:
        kartu_jadwal_premium(
            "Pengajian Senenan",
            "🌸",
            format_tanggal(tgl_senin),
            "07:30 - 09:00 WIB",
            pengisi_senin,
            "Pengajian ibu-ibu Senenan. Jika ustadz berhalangan, akan diganti oleh ustadz lain.",
            "emas",
            mulai_dt=mulai_senin,
            selesai_dt=selesai_senin
        )

    hari_kamis = tanggal_berikutnya(3)
    mulai_syahriahan = datetime.combine(hari_kamis.date(), datetime.strptime("20:00", "%H:%M").time())
    selesai_syahriahan = datetime.combine(hari_kamis.date(), datetime.strptime("21:30", "%H:%M").time())

    kartu_jadwal_premium(
        "Syahriahan Sholawat",
        "🌙",
        "Malam Jumat awal bulan Hijriah",
        "Ba'da Isya / 20:00 - 21:30 WIB",
        "Aang Deden Kasyful Anwar",
        "Agenda bulanan pembacaan sholawat, dzikir, dan doa bersama masyarakat Masjid Jami Al-Falah.",
        "biru",
        mulai_dt=mulai_syahriahan,
        selesai_dt=selesai_syahriahan
    )


def save_kas_terpisah(sheet_name, df):
    """Simpan dataframe ke tab khusus: Kas Madrasah / Kas Rajaban."""
    sh, info = koneksi_google_sheet_write()
    if sh is None:
        raise Exception(f"Gagal koneksi Google Sheet: {info}")

    try:
        ws = sh.worksheet(sheet_name)
    except Exception:
        ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=5)

    df = df.copy()
    for col in ["Tanggal", "Keterangan", "Masuk", "Keluar", "Petugas"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["Tanggal", "Keterangan", "Masuk", "Keluar", "Petugas"]]
    ws.clear()
    ws.append_row(["Tanggal", "Keterangan", "Masuk", "Keluar", "Petugas"])
    if not df.empty:
        ws.append_rows(df.astype(str).values.tolist())

def simpan_input_kas_terarah(tanggal, jenis, kategori, keterangan, jumlah, petugas):
    """
    Routing kas:
    - Kas Madrasah -> tab Kas Madrasah
    - Iuran Rajaban -> tab Kas Rajaban
    - Kategori lain -> kas masjid utama
    """
    global kas_df

    kategori_text = str(kategori).strip().lower()

    if kategori_text == "kas madrasah":
        df_khusus = load_kas_terpisah("Kas Madrasah")
        data = pd.DataFrame([{
            "Tanggal": str(tanggal),
            "Keterangan": keterangan,
            "Masuk": jumlah if jenis == "Pemasukan" else 0,
            "Keluar": jumlah if jenis == "Pengeluaran" else 0,
            "Petugas": petugas
        }])
        df_khusus = pd.concat([df_khusus, data], ignore_index=True)
        save_kas_terpisah("Kas Madrasah", df_khusus)
        return "Kas Madrasah"

    elif kategori_text == "iuran rajaban":
        df_khusus = load_kas_terpisah("Kas Rajaban")
        data = pd.DataFrame([{
            "Tanggal": str(tanggal),
            "Keterangan": keterangan,
            "Masuk": jumlah if jenis == "Pemasukan" else 0,
            "Keluar": jumlah if jenis == "Pengeluaran" else 0,
            "Petugas": petugas
        }])
        df_khusus = pd.concat([df_khusus, data], ignore_index=True)
        save_kas_terpisah("Kas Rajaban", df_khusus)
        return "Kas Rajaban"

    else:
        data = pd.DataFrame([{
            "Tanggal": str(tanggal),
            "Jenis": jenis,
            "Kategori": kategori,
            "Keterangan": keterangan,
            "Jumlah": jumlah,
            "Petugas": petugas
        }])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)
        return "Kas Masjid"

kas_df = load_kas()
pengumuman_df = load_pengumuman()
pengumuman_aktif_df = pengumuman_aktif_24jam(pengumuman_df)

# Setting dari Google Sheet jika tersedia
setting_wa_online = load_setting_wa()
LINK_APP = setting_wa_online.get("LinkApp", LINK_APP)
GRUP_AL_BARZANJI = setting_wa_online.get("GroupBarzaji", GRUP_AL_BARZANJI)

wib = waktu_wib()
tanggal_wib = wib.date()
hijriah_text = kalender_hijriah_online(tanggal_wib)
sholat = jadwal_sholat_cianjur()

# =========================
# ENDPOINT OTOMATIS V21 UNTUK GITHUB ACTIONS
# ?auto=laporan_bulanan&run=1
# ?auto=senenan&run=1
# ?auto=malam_rabu&run=1
# ?auto=syahriahan&run=1
# =========================
try:
    auto = st.query_params.get("auto", "")
except Exception:
    auto = ""

if auto:
    jamaah_auto = load_jamaah()

    if auto == "laporan_bulanan":
        pesan_auto = buat_laporan_bulanan_text()
        pengisi_auto = "Laporan Keuangan"
        jenis_auto = "Laporan Keuangan Bulanan"
    elif auto == "senenan":
        tgl_senin_auto = tanggal_berikutnya(0)
        pengisi_auto = pengajian_senin[index_rotasi_senin(tgl_senin_auto)]
        pesan_auto = pesan_senenan(pengisi_auto)
        jenis_auto = "Pengajian Senenan"
    elif auto == "malam_rabu":
        tgl_rabu_auto = tanggal_berikutnya(1)
        pengisi_auto = pengajian_malam_rabu[index_rotasi_rabu(tgl_rabu_auto)]
        pesan_auto = pesan_malam_rabu(pengisi_auto)
        jenis_auto = "Pengajian Malam Rabu"
    elif auto == "syahriahan":
        pengisi_auto = "Aang Deden Kasyful Anwar"
        pesan_auto = pesan_syahriahan()
        jenis_auto = "Syahriahan Sholawat"
    else:
        st.error("Auto endpoint tidak dikenal.")
        st.stop()

    target_auto = daftar_target_broadcast(jamaah_auto, pengisi_auto)
    st.title("🤖 Auto Broadcast V21")
    st.write(f"Jenis: {jenis_auto}")
    st.write(f"Target: {len(target_auto)} jamaah")
    st.warning("Endpoint otomatis memakai batas aman 5 nomor per run.")

    if st.query_params.get("run", "") == "1":
        berhasil, gagal, hasil_df = kirim_broadcast_aman(
            target_auto,
            pesan_auto,
            jenis_pesan=jenis_auto,
            delay_detik=25,
            batas_kirim=5
        )
        st.success(f"Auto run selesai. Berhasil: {berhasil} | Gagal: {gagal}")
        st.dataframe(hasil_df, use_container_width=True, hide_index=True)
        kirim_telegram(f"🕌 AL-FALAH DIGITAL\n\nAuto {jenis_auto} selesai.\nBerhasil: {berhasil}\nGagal: {gagal}")
    else:
        st.info("Tambahkan &run=1 untuk menjalankan auto broadcast.")
    st.stop()




# =========================================================
# V21.3 - WA OTOMATIS KEGIATAN & LAPORAN KEUANGAN
# =========================================================
def laporan_keuangan_text():
    try:
        pemasukan = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
        pengeluaran = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
        saldo = pemasukan - pengeluaran
        total_kotak_amal = kas_df[kas_df["Kategori"] == "Kotak Amal"]["Jumlah"].sum()
        total_madrasah = kas_df[kas_df["Kategori"].astype(str).str.contains("Madrasah", case=False, na=False)]["Jumlah"].sum()
        total_rajaban = kas_df[kas_df["Kategori"].astype(str).str.contains("Rajaban", case=False, na=False)]["Jumlah"].sum()
    except Exception:
        pemasukan = pengeluaran = saldo = total_kotak_amal = total_madrasah = total_rajaban = 0

    return f"""📊 LAPORAN KEUANGAN MASJID JAMI AL-FALAH

Tanggal: {format_tanggal(tanggal_wib)}

💰 Total Pemasukan: {rupiah(pemasukan)}
⬇️ Total Pengeluaran: {rupiah(pengeluaran)}
✅ Saldo Kas: {rupiah(saldo)}
📦 Total Kotak Amal: {rupiah(total_kotak_amal)}
🏫 Kas/Iuran Madrasah: {rupiah(total_madrasah)}
🌙 Iuran Rajaban: {rupiah(total_rajaban)}

🕌 Masjid Jami Al-Falah
Kp. Caringin RT/RW 005/005
Desa Sukasari, Karangtengah, Cianjur

Pesan ini dikirim otomatis melalui Al-Falah Digital."""


def target_otomatis(jenis_auto, jamaah_df):
    if jamaah_df is None or jamaah_df.empty:
        return pd.DataFrame(columns=KOLOM_JAMAAH), "Target kosong"

    if jenis_auto == "senenan":
        target = jamaah_df[(jamaah_df["JenisKelamin"] == "Perempuan") & (jamaah_df["Aktif"].astype(str).str.lower().eq("ya"))].copy()
        return target, "Jamaah perempuan aktif"

    if jenis_auto == "rabu":
        target = jamaah_df[(jamaah_df["JenisKelamin"] == "Laki-laki") & (jamaah_df["Aktif"].astype(str).str.lower().eq("ya"))].copy()
        tgl_selasa = tanggal_berikutnya(1)
        pengisi = pengajian_malam_rabu[index_rotasi_rabu(tgl_selasa)]
        target = tambah_khusus_jika_pengisi(target, jamaah_df, pengisi)
        return target, "Jamaah laki-laki aktif"

    if jenis_auto == "syahriahan":
        target = filter_jamaah_aktif_umum(jamaah_df)
        target = tambah_khusus_jika_pengisi(target, jamaah_df, "Aang Deden")
        return target, "Semua jamaah aktif"

    if jenis_auto == "laporan":
        nomor = ambil_secret("FONTE_DEVICE_ID", "") or ambil_secret("FONNTE_DEVICE_ID", "") or NOMOR_MASJID
        target = pd.DataFrame([["Admin/Masjid", "-", normalisasi_wa(nomor), "Ya", "Laporan Keuangan"]], columns=KOLOM_JAMAAH)
        return target, "Nomor masjid/admin"

    return pd.DataFrame(columns=KOLOM_JAMAAH), "Jenis otomatis tidak dikenal"


def pesan_otomatis(jenis_auto):
    if jenis_auto == "senenan":
        tgl_senin = tanggal_berikutnya(0)
        pengisi = pengajian_senin[index_rotasi_senin(tgl_senin)]
        return "Pengajian Senenan Otomatis", pesan_senenan(pengisi)

    if jenis_auto == "rabu":
        tgl_selasa = tanggal_berikutnya(1)
        pengisi = pengajian_malam_rabu[index_rotasi_rabu(tgl_selasa)]
        return "Pengajian Malam Rabu Otomatis", pesan_malam_rabu(pengisi)

    if jenis_auto == "syahriahan":
        return "Syahriahan Sholawat Otomatis", pesan_syahriahan()

    if jenis_auto == "laporan":
        return "Laporan Keuangan Otomatis", laporan_keuangan_text()

    return "Otomatis", ""


def sudah_terkirim_hari_ini(jenis_pesan):
    try:
        log_df = baca_log_wa()
        if log_df.empty:
            return False
        hari_ini = waktu_wib().strftime("%Y-%m-%d")
        tanggal_col = log_df.get("Tanggal", pd.Series(dtype=str)).astype(str)
        jenis_col = log_df.get("JenisPesan", pd.Series(dtype=str)).astype(str)
        status_col = log_df.get("Status", pd.Series(dtype=str)).astype(str)
        cek = log_df[
            tanggal_col.str.startswith(hari_ini)
            & jenis_col.eq(jenis_pesan)
            & status_col.eq("Terkirim")
        ]
        return not cek.empty
    except Exception:
        return False


def kirim_otomatis_v20(jenis_auto, paksa=False):
    jamaah_df = load_jamaah()
    jenis_pesan, pesan = pesan_otomatis(jenis_auto)

    if not pesan.strip():
        return {"ok": False, "info": "Pesan kosong", "sukses": 0, "gagal": 0}

    if (not paksa) and sudah_terkirim_hari_ini(jenis_pesan):
        return {"ok": False, "info": f"{jenis_pesan} sudah pernah terkirim hari ini", "sukses": 0, "gagal": 0}

    target, target_label = target_otomatis(jenis_auto, jamaah_df)
    if target.empty:
        return {"ok": False, "info": "Target kosong", "sukses": 0, "gagal": 0}

    target = target.copy()
    target["NoWA"] = target["NoWA"].astype(str).apply(normalisasi_wa)
    target = target[target["NoWA"] != ""].drop_duplicates(subset=["NoWA"])

    sukses = 0
    gagal = 0
    detail = []

    for _, row in target.iterrows():
        nama = str(row.get("Nama", "Tanpa Nama")).strip() or "Tanpa Nama"
        nomor = normalisasi_wa(row.get("NoWA", ""))
        ok, info = kirim_fonnte(nomor, pesan)
        status = "Terkirim" if ok else "Gagal"
        if ok:
            sukses += 1
        else:
            gagal += 1
        simpan_log_wa(nama, nomor, jenis_pesan, status, str(info)[:180])
        detail.append({"Nama": nama, "NoWA": nomor, "Status": status, "Keterangan": str(info)[:180]})

    ringkasan = f"""🕌 AL-FALAH DIGITAL V20

WA otomatis selesai.
Jenis: {jenis_pesan}
Target: {target_label}
Jumlah Target: {len(target)}
✅ Berhasil: {sukses}
❌ Gagal: {gagal}
Waktu: {waktu_wib().strftime('%d-%m-%Y %H:%M:%S')} WIB"""
    kirim_telegram(ringkasan)
    return {"ok": True, "info": ringkasan, "sukses": sukses, "gagal": gagal, "detail": detail, "pesan": pesan, "target_label": target_label}


# Endpoint sederhana untuk GitHub Actions / cron:
# ?auto=senenan&key=ISI_AUTO_KEY
# ?auto=rabu&key=ISI_AUTO_KEY
# ?auto=syahriahan&key=ISI_AUTO_KEY
# ?auto=laporan&key=ISI_AUTO_KEY
try:
    qp = st.query_params
    auto_param = qp.get("auto", "")
    key_param = qp.get("key", "")
    auto_key = ambil_secret("AUTO_KEY", "")
    if auto_param and auto_key and key_param == auto_key:
        hasil_auto = kirim_otomatis_v20(auto_param, paksa=False)
        st.json(hasil_auto)
        st.stop()
except Exception:
    pass

st.sidebar.title("🕌 APP AL-FALAH V21.3")

mode = st.sidebar.radio("Mode Aplikasi", ["👥 Jamaah", "🔐 Admin"])

if mode == "🔐 Admin":
    menu = st.sidebar.radio(
        "Menu Admin",
        ["🏠 Dashboard", "💰 Input Kas", "📦 Input Kotak Amal", "📊 Laporan Kas", "👥 Data Jamaah", "📲 WA Jamaah", "🤖 WA Otomatis V20", "👥 Pengurus DKM", "📅 Jadwal Pengajian", "📢 Pengumuman", "📲 Share WhatsApp"]
    )
else:
    menu = st.sidebar.radio(
        "Menu Jamaah",
        ["🏠 Dashboard", "📺 Mode TV Masjid", "👥 Pengurus DKM", "📅 Jadwal Pengajian", "📢 Pengumuman", "📲 Share WhatsApp"]
    )

if menu == "🏠 Dashboard":

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}

h1, h2, h3 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: .3px;
}

[data-testid="stMetricValue"] {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 900 !important;
    color: #064e3b !important;
    text-shadow: 0 0 8px rgba(255,215,0,.35);
}

[data-testid="stMetricLabel"] {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 800 !important;
    color: #3b3b3b !important;
}

.led-text {
    font-family: 'Poppins', sans-serif !important;
}
    @keyframes glowPulse {
        0% { text-shadow:0 0 6px #FFD700,0 0 12px #FFD700; }
        50% { text-shadow:0 0 15px #FFD700,0 0 35px #FFD700,0 0 65px #00ff99; }
        100% { text-shadow:0 0 6px #FFD700,0 0 12px #FFD700; }
    }

    @keyframes lampBlink {
        0%,100% { opacity:1; box-shadow:0 0 20px #FFD700; }
        50% { opacity:.35; box-shadow:0 0 4px #FFD700; }
    }

    @keyframes borderGlow {
        0% { box-shadow:0 0 18px rgba(255,215,0,.45); }
        50% { box-shadow:0 0 40px rgba(255,215,0,.95), 0 0 70px rgba(0,255,120,.25); }
        100% { box-shadow:0 0 18px rgba(255,215,0,.45); }
    }

    .premium-hero {
        background:
        radial-gradient(circle at top left, rgba(255,215,0,.22), transparent 30%),
        radial-gradient(circle at top right, rgba(0,255,120,.18), transparent 35%),
        linear-gradient(135deg,#011c16,#064e3b,#022c22);
        padding:38px;
        border-radius:30px;
        text-align:center;
        border:2px solid #FFD700;
        margin-bottom:24px;
        animation:borderGlow 3s infinite;
    }

    .premium-title {
        color:#FFD700;
        font-size:56px;
        font-weight:950;
        animation:glowPulse 2.4s infinite;
        margin-bottom:8px;
    }

    .premium-subtitle {
        color:#fef9c3;
        font-size:24px;
        font-weight:800;
    }

    .premium-address {
        color:#ecfdf5;
        font-size:17px;
        margin-top:10px;
    }

    .lamp {
        display:inline-block;
        width:14px;
        height:14px;
        margin:0 7px;
        border-radius:50%;
        background:#FFD700;
        animation:lampBlink 1.3s infinite;
    }

    .premium-chip {
        background:#020617;
        color:#00ff66;
        display:inline-block;
        padding:13px 20px;
        border-radius:16px;
        border:2px solid #FFD700;
        margin-top:18px;
        font-size:19px;
        font-weight:900;
        box-shadow:0 0 18px rgba(255,215,0,.7);
    }

    .led-box {
        background:#020617;
        border:3px solid #FFD700;
        border-radius:18px;
        padding:13px;
        margin-bottom:22px;
        box-shadow:0 0 22px rgba(255,215,0,.75), inset 0 0 20px rgba(0,255,102,.18);
    }

    .led-text {
        color:#00ff66;
        font-size:23px;
        font-weight:950;
        letter-spacing:1px;
        text-shadow:0 0 6px #00ff66,0 0 14px #00ff66,0 0 28px #00ff66;
    }

    .prayer-card {
        background:linear-gradient(135deg,#022c22,#064e3b);
        color:white;
        border:2px solid #FFD700;
        border-radius:18px;
        padding:18px;
        text-align:center;
        box-shadow:0 0 18px rgba(255,215,0,.35);
        margin-bottom:12px;
    }

    .prayer-time {
        color:#00ff66;
        font-size:28px;
        font-weight:950;
        text-shadow:0 0 10px #00ff66;
    }

    .wa-button {
        display:block;
        background:linear-gradient(135deg,#16a34a,#22c55e);
        color:white !important;
        padding:16px;
        border-radius:18px;
        text-align:center;
        font-size:22px;
        font-weight:900;
        text-decoration:none;
        box-shadow:0 0 18px rgba(34,197,94,.45);
        margin-top:10px;
    }
    </style>
    """, unsafe_allow_html=True)

    tampilkan_banner_premium(tanggal_wib, hijriah_text)

    components.html("""
    <div style="
        background:#020617;
        border:3px solid #FFD700;
        color:#00ff66;
        padding:14px;
        border-radius:18px;
        text-align:center;
        font-size:34px;
        font-weight:950;
        box-shadow:0 0 25px rgba(255,215,0,.8), inset 0 0 22px rgba(0,255,102,.18);
        margin-bottom:18px;
        font-family:Arial;
    ">
        🕒 <span id="jam"></span> WIB
    </div>

    <script>
    function updateClock(){
        const now = new Date();
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const wib = new Date(utc + (7 * 60 * 60 * 1000));
        let h = String(wib.getHours()).padStart(2,'0');
        let m = String(wib.getMinutes()).padStart(2,'0');
        let s = String(wib.getSeconds()).padStart(2,'0');
        document.getElementById("jam").innerHTML = h + ":" + m + ":" + s;
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
    """, height=95)

    agenda_status, status_pengajian = status_pengajian_terdekat()
    target_js = agenda_status["target"].strftime("%Y-%m-%dT%H:%M:%S")

    if status_pengajian == "berjalan":
        judul_countdown = "🟢 Pengajian Sedang Berjalan"
        teks_target = "Berakhir dalam:"
        waktu_tampil = agenda_status["selesai"]
    else:
        judul_countdown = "⏳ Pengajian Terdekat"
        teks_target = "Dimulai dalam:"
        waktu_tampil = agenda_status["mulai"]

    st.markdown("## ⏳ Status Pengajian Terdekat")
    components.html(f"""
    <div style="
        background:linear-gradient(135deg,#020617,#064e3b);
        border:3px solid #FFD700;
        border-radius:20px;
        padding:22px;
        text-align:center;
        color:white;
        box-shadow:0 0 22px rgba(255,215,0,.65);
        font-family:Arial;
    ">
        <div style="font-size:24px;font-weight:bold;color:#FFD700;">{judul_countdown}</div>
        <div style="font-size:23px;font-weight:bold;color:#00ff66;margin-top:8px;">{agenda_status['nama']}</div>
        <div style="font-size:18px;margin-top:6px;">{format_tanggal(waktu_tampil.date())} - {waktu_tampil.strftime('%H:%M')} WIB</div>
        <div style="font-size:16px;margin-top:5px;">👳 Pengisi: {agenda_status['pengisi']}</div>
        <div style="font-size:18px;margin-top:12px;color:#fef3c7;">{teks_target}</div>
        <div id="countdown" style="font-size:36px;font-weight:900;color:#00ff66;margin-top:6px;text-shadow:0 0 12px #00ff66;"></div>
    </div>
    <script>
    const target = new Date("{target_js}+07:00").getTime();
    function updateCountdown(){{
        const now = new Date().getTime();
        let diff = target - now;
        if(diff < 0){{
            location.reload();
            return;
        }}
        const days = Math.floor(diff / (1000*60*60*24));
        const hours = Math.floor((diff % (1000*60*60*24)) / (1000*60*60));
        const minutes = Math.floor((diff % (1000*60*60)) / (1000*60));
        const seconds = Math.floor((diff % (1000*60)) / 1000);
        document.getElementById("countdown").innerHTML =
            days + " Hari  " + hours + " Jam  " + minutes + " Menit  " + seconds + " Detik";
    }}
    setInterval(updateCountdown, 1000);
    updateCountdown();
    </script>
    """, height=300)

    st.divider()

    pemasukan = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran
    total_kotak_amal = kas_df[kas_df["Kategori"] == "Kotak Amal"]["Jumlah"].sum()
    madrasah_masuk, madrasah_keluar, kas_madrasah, df_kas_madrasah = saldo_kas_terpisah("Kas Madrasah")
    rajaban_masuk, rajaban_keluar, iuran_rajaban, df_kas_rajaban = saldo_kas_terpisah("Kas Rajaban")
    jumlah_buka_kotak = len(kas_df[kas_df["Kategori"] == "Kotak Amal"])

    st.markdown("## 💳 Kartu Saldo Akhir")
    c1, c2, c3 = st.columns(3)
    with c1:
        tampilkan_kartu_bank("Saldo Akhir Kas Masjid", rupiah(saldo), "Klik detail di bawah kartu", "💰", "hijau")
        with st.expander("📋 Lihat detail Kas Masjid"):
            detail_keuangan_masjid_box(kas_df)

    with c2:
        tampilkan_kartu_bank("Saldo Akhir Kas Madrasah", rupiah(kas_madrasah), "Klik detail di bawah kartu", "🏫", "biru")
        with st.expander("📋 Lihat detail Kas Madrasah"):
            detail_keuangan_terpisah_box(df_kas_madrasah, "Detail Kas Madrasah")

    with c3:
        tampilkan_kartu_bank("Saldo Akhir Iuran Rajaban", rupiah(iuran_rajaban), "Klik detail di bawah kartu", "🌙", "emas")
        with st.expander("📋 Lihat detail Iuran Rajaban"):
            detail_keuangan_terpisah_box(df_kas_rajaban, "Detail Iuran Rajaban")



    teks_led_mewah = (
        "Selamat datang di Sistem Informasi Masjid Jami Al-Falah • "
        "Pengajian Malam Rabu pukul 19:30 WIB • "
        "Pengajian Senenan pukul 07:30 WIB • "
        "Syahriahan Sholawat malam Jumat awal bulan Hijriah • "
        "Kas Masjid, Kas Madrasah, dan Iuran Rajaban dikelola secara transparan"
    )

    if not pengumuman_aktif_df.empty:
        terakhir = pengumuman_aktif_df.tail(1).iloc[0]
        teks_led_mewah = f"PENGUMUMAN MASJID • {terakhir['Judul']} • {terakhir['Isi']} • Pesan ini dikirim otomatis melalui Al-Falah Digital"

    tampilkan_running_text_mewah(teks_led_mewah)


    st.divider()

    tgl_rabu = tanggal_berikutnya(1)
    ustadz_rabu = pengajian_malam_rabu[index_rotasi_rabu(tgl_rabu)]
    tgl_senin = tanggal_berikutnya(0)
    ustadz_senin = pengajian_senin[index_rotasi_senin(tgl_senin)]

    st.markdown("## 📌 Jadwal Pengajian Minggu Ini")
    a, b = st.columns(2)

    with a:
        st.markdown(f"""
        <div style="background:#f0fdf4;border:1px solid #22c55e;padding:24px;border-radius:22px;box-shadow:0 6px 18px rgba(0,0,0,.10);">
            <h3>📖 Pengajian Malam Rabu</h3>
            <p><b>📅 Tanggal:</b> {format_tanggal(tgl_rabu)}</p>
            <p><b>🕢 Waktu:</b> 19:30 - 21:30 WIB</p>
            <p><b>👳 Pengisi:</b> {ustadz_rabu}</p>
            <p style="font-size:14px;color:#374151;">Catatan: Jika ustadz tidak berhalangan. Jika berhalangan, akan diganti oleh ustadz lain.</p>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown(f"""
        <div style="background:#fffbeb;border:1px solid #f59e0b;padding:24px;border-radius:22px;box-shadow:0 6px 18px rgba(0,0,0,.10);">
            <h3>🌸 Pengajian Senenan</h3>
            <p><b>📅 Tanggal:</b> {format_tanggal(tgl_senin)}</p>
            <p><b>🕢 Waktu:</b> 07:30 - 09:00 WIB</p>
            <p><b>👳 Pengisi:</b> {ustadz_senin}</p>
            <p style="font-size:14px;color:#374151;">Catatan: Jika ustadz tidak berhalangan. Jika berhalangan, akan diganti oleh ustadz lain.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#eff6ff;border:1px solid #3b82f6;padding:22px;border-radius:22px;margin-top:18px;box-shadow:0 6px 18px rgba(0,0,0,.10);">
        <h3>🌙 Syahriahan Sholawat</h3>
        <p><b>Waktu:</b> Malam Jumat awal bulan Hijriah, pukul 20:00 - 21:30 WIB</p>
        <p><b>Pengisi:</b> Aang Deden Kasyful Anwar</p>
        <p style="font-size:14px;color:#374151;">Catatan: Jika tidak berhalangan. Jika berhalangan, akan diganti oleh ustadz lain.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📞 Hubungi Pengurus DKM")
    teks_wa_admin = "Assalamu'alaikum, saya ingin menghubungi pengurus DKM Masjid Jami Al-Falah."
    st.markdown(f"<a class='wa-button' href='{wa_link(teks_wa_admin)}' target='_blank'>📲 Hubungi DKM via WhatsApp</a>", unsafe_allow_html=True)

    st.divider()

    st.subheader("📋 Transaksi Kas Terbaru")
    if kas_df.empty:
        st.info("Belum ada data kas.")
    else:
        tampil = kas_df.tail(7).copy()
        tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
        st.dataframe(tampil, use_container_width=True)

    st.divider()

    st.subheader("📅 Agenda Kegiatan Masjid")
    st.dataframe(pd.DataFrame(agenda_tetap, columns=["Kegiatan", "Hari", "Waktu"]), use_container_width=True)

    st.divider()

    st.subheader("👥 Pengurus Inti DKM")
    p1, p2, p3, p4 = st.columns(4)
    p1.info("Ketua DKM\n\nAang Deden Kasyful Anwar")
    p2.info("Wakil Ketua\n\nIden Tazuni")
    p3.info("Sekretaris\n\nUstadz Ihin")
    p4.info("Bendahara\n\nAceng Abdul Roup")

    st.divider()

    st.subheader("📢 Pengumuman Terbaru")
    if pengumuman_aktif_df.empty:
        st.info("Belum ada pengumuman aktif. Pengumuman otomatis hilang dari dashboard setelah 1x24 jam.")
    else:
        st.caption("Pengumuman di dashboard hanya tampil maksimal 1x24 jam sejak dibuat.")
        st.dataframe(pengumuman_aktif_df.tail(5), use_container_width=True)

    st.divider()

    st.markdown("## 🕌 Jadwal Sholat Hari Ini - Cianjur")
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        st.markdown(f"<div class='prayer-card'><h3>Subuh</h3><div class='prayer-time'>{sholat['Subuh']}</div></div>", unsafe_allow_html=True)
    with s2:
        st.markdown(f"<div class='prayer-card'><h3>Dzuhur</h3><div class='prayer-time'>{sholat['Dzuhur']}</div></div>", unsafe_allow_html=True)
    with s3:
        st.markdown(f"<div class='prayer-card'><h3>Ashar</h3><div class='prayer-time'>{sholat['Ashar']}</div></div>", unsafe_allow_html=True)
    with s4:
        st.markdown(f"<div class='prayer-card'><h3>Maghrib</h3><div class='prayer-time'>{sholat['Maghrib']}</div></div>", unsafe_allow_html=True)
    with s5:
        st.markdown(f"<div class='prayer-card'><h3>Isya</h3><div class='prayer-time'>{sholat['Isya']}</div></div>", unsafe_allow_html=True)


elif menu == "📺 Mode TV Masjid":
    st.subheader("📺 Mode TV Masjid Jami Al-Falah")
    st.info("Mode ini cocok dibuka di TV masjid: jam besar, kalender Hijriah, status kegiatan live, countdown, dan hikmah harian.")
    tampilkan_mode_tv_masjid()

elif menu == "🤖 Broadcast Aman V21":
    st.subheader("🤖 Broadcast Aman V21")
    st.warning("Gunakan setelah akun WhatsApp masjid sudah pulih. Mode aman mengirim bertahap agar tidak dianggap spam.")

    jamaah_df = load_jamaah()

    jenis_broadcast = st.selectbox(
        "Jenis Pesan",
        ["Pengajian Senenan", "Pengajian Malam Rabu", "Syahriahan Sholawat", "Laporan Keuangan Bulanan"]
    )

    pengisi_kegiatan = ""
    if jenis_broadcast == "Pengajian Senenan":
        tgl_senin = tanggal_berikutnya(0)
        pengisi_kegiatan = pengajian_senin[index_rotasi_senin(tgl_senin)]
        pesan_broadcast = pesan_senenan(pengisi_kegiatan)
    elif jenis_broadcast == "Pengajian Malam Rabu":
        tgl_selasa = tanggal_berikutnya(1)
        pengisi_kegiatan = pengajian_malam_rabu[index_rotasi_rabu(tgl_selasa)]
        pesan_broadcast = pesan_malam_rabu(pengisi_kegiatan)
    elif jenis_broadcast == "Syahriahan Sholawat":
        pengisi_kegiatan = "Aang Deden Kasyful Anwar"
        pesan_broadcast = pesan_syahriahan()
    else:
        pengisi_kegiatan = "Laporan Keuangan"
        pesan_broadcast = buat_laporan_bulanan_text()

    target_df = daftar_target_broadcast(jamaah_df, pengisi_kegiatan)

    st.info(f"Target penerima: {len(target_df)} jamaah aktif. Aang Deden otomatis dilewati jika bukan pengisi/pimpinan kegiatan.")
    st.text_area("Preview Pesan", value=pesan_broadcast, height=330)

    c1, c2 = st.columns(2)
    delay_detik = c1.number_input("Delay per nomor / detik", min_value=5, max_value=120, value=25)
    batas_kirim = c2.number_input("Batas kirim sekali jalan", min_value=1, max_value=100, value=5)

    st.dataframe(target_df[["Nama", "NoWA", "Aktif", "Catatan"]], use_container_width=True, hide_index=True)

    if st.button("🚀 Kirim Broadcast Aman Sekarang"):
        berhasil, gagal, hasil_df = kirim_broadcast_aman(
            target_df,
            pesan_broadcast,
            jenis_pesan=jenis_broadcast,
            delay_detik=delay_detik,
            batas_kirim=batas_kirim
        )
        st.success(f"Selesai. Berhasil: {berhasil} | Gagal: {gagal}")
        st.dataframe(hasil_df, use_container_width=True, hide_index=True)
        kirim_telegram(f"🕌 AL-FALAH DIGITAL\n\nBroadcast {jenis_broadcast} selesai.\nBerhasil: {berhasil}\nGagal: {gagal}\n\nPesan ini dikirim otomatis melalui Al-Falah Digital.")


elif menu == "💰 Input Kas":
    st.subheader("💰 Input Kas Admin")
    with st.form("form_kas"):
        c1, c2, c3 = st.columns(3)
        tanggal = c1.date_input("Tanggal", date.today())
        jenis = c2.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = c3.selectbox("Kategori", ["Infaq Jumat", "Kotak Amal", "Kas Madrasah", "Iuran Rajaban", "Donatur", "Pembangunan", "Listrik", "Kebersihan", "Lainnya"])
        keterangan = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah", min_value=0, step=1000)
        petugas = st.text_input("Petugas", value="Aceng Abdul Roup")
        simpan = st.form_submit_button("💾 Simpan Kas")
    if simpan:
                tujuan_simpan = simpan_input_kas_terarah(
                    tanggal=tanggal,
                    jenis=jenis,
                    kategori=kategori,
                    keterangan=keterangan,
                    jumlah=jumlah,
                    petugas=petugas
                )

                kirim_telegram(
                    f"🕌 APP MASJID JAMI AL-FALAH\n\n"
                    f"Data Kas Baru\n"
                    f"Jenis: {jenis}\n"
                    f"Kategori: {kategori}\n"
                    f"Disimpan ke: {tujuan_simpan}\n"
                    f"Tanggal: {tanggal}\n"
                    f"Jumlah: {rupiah(jumlah)}\n"
                    f"Petugas: {petugas}\n"
                    f"Keterangan: {keterangan}"
                )

                st.success(f"Data kas berhasil disimpan ke {tujuan_simpan}.")

elif menu == "📦 Input Kotak Amal":
    st.subheader("📦 Input Kotak Amal Admin")
    with st.form("form_kotak"):
        tanggal = st.date_input("Tanggal Buka Kotak Amal", date.today())
        jumlah = st.number_input("Jumlah Kotak Amal", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan", value="Kotak amal masjid")
        petugas = st.text_input("Petugas Penghitung", value="Aceng Abdul Roup")
        simpan = st.form_submit_button("💾 Simpan Kotak Amal")
    if simpan:
        data = pd.DataFrame([{"Tanggal": str(tanggal), "Jenis": "Pemasukan", "Kategori": "Kotak Amal", "Keterangan": keterangan, "Jumlah": jumlah, "Petugas": petugas}])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)
        kirim_telegram(f"🕌 APP MASJID JAMI AL-FALAH\n\nPemasukan Kotak Amal\nTanggal: {tanggal}\nJumlah: {rupiah(jumlah)}\nPetugas: {petugas}\nKeterangan: {keterangan}")
        st.success("Kotak amal berhasil disimpan.")

elif menu == "📊 Laporan Kas":
    st.subheader("📊 Laporan Kas Masjid")
    if kas_df.empty:
        st.info("Belum ada data kas.")
    else:
        kas_df["Tanggal"] = pd.to_datetime(kas_df["Tanggal"], errors="coerce")
        daftar_bulan = sorted(kas_df["Tanggal"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)
        bulan = st.selectbox("Pilih Bulan", daftar_bulan)
        laporan = kas_df[kas_df["Tanggal"].dt.strftime("%Y-%m") == bulan]
        pemasukan_bulan = laporan[laporan["Jenis"] == "Pemasukan"]["Jumlah"].sum()
        pengeluaran_bulan = laporan[laporan["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
        saldo_bulan = pemasukan_bulan - pengeluaran_bulan
        c1, c2, c3 = st.columns(3)
        c1.metric("Pemasukan Bulan Ini", rupiah(pemasukan_bulan))
        c2.metric("Pengeluaran Bulan Ini", rupiah(pengeluaran_bulan))
        c3.metric("Saldo Bulan Ini", rupiah(saldo_bulan))
        tampil = laporan.copy()
        tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
        st.dataframe(tampil, use_container_width=True)
        csv = laporan.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Laporan CSV", csv, f"laporan_kas_{bulan}.csv", "text/csv")


elif menu == "👥 Data Jamaah":
    st.subheader("👥 Data Jamaah AL-FALAH")
    jamaah_df = load_jamaah()

    j1, j2, j3, j4 = st.columns(4)
    j1.metric("Total Data", len(jamaah_df))
    j2.metric("Laki-laki", len(jamaah_df[jamaah_df["JenisKelamin"] == "Laki-laki"]))
    j3.metric("Perempuan", len(jamaah_df[jamaah_df["JenisKelamin"] == "Perempuan"]))
    j4.metric("Khusus", len(jamaah_df[jamaah_df["Aktif"] == "Khusus"]))

    st.warning("Nomor WhatsApp jamaah hanya tampil di mode Admin. Jangan sebarkan data ini ke halaman publik.")
    st.dataframe(jamaah_df, use_container_width=True)

    st.divider()
    st.markdown("### ➕ Tambah Jamaah")
    with st.form("form_tambah_jamaah_v13"):
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Jamaah")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        nowa = st.text_input("Nomor WhatsApp", placeholder="contoh: 0858xxxx atau 62858xxxx")
        aktif = st.selectbox("Status", ["Ya", "Khusus", "Tidak Aktif"])
        catatan = st.text_input("Catatan", value="-")
        simpan_jamaah = st.form_submit_button("💾 Simpan Jamaah")

    if simpan_jamaah:
        if not nama.strip() or not nowa.strip():
            st.error("Nama dan nomor WhatsApp wajib diisi.")
        else:
            ok, info = simpan_jamaah_google(nama.strip(), jk, nowa.strip(), aktif, catatan.strip())
            if ok:
                st.success(info)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Gagal menyimpan jamaah ke Google Sheet: {info}")

elif menu == "📲 WA Jamaah":
    st.subheader("📲 Share WhatsApp Jamaah")
    jamaah_df = load_jamaah()

    jenis_info = st.selectbox("Pilih Pengumuman", ["Pengajian Senenan", "Pengajian Malam Rabu", "Syahriahan Sholawat"])

    if jenis_info == "Pengajian Senenan":
        tgl_senin = tanggal_berikutnya(0)
        pengisi_default = pengajian_senin[index_rotasi_senin(tgl_senin)]
        pengisi = st.selectbox("Pengisi", ["Aang Deden", "Ustadz Ihin", "Ustadz Nanang"], index=["Aang Deden", "Ustadz Ihin", "Ustadz Nanang"].index(pengisi_default) if pengisi_default in ["Aang Deden", "Ustadz Ihin", "Ustadz Nanang"] else 0)
        pesan = pesan_senenan(pengisi)
        target = jamaah_df[(jamaah_df["JenisKelamin"] == "Perempuan") & (jamaah_df["Aktif"] == "Ya")].copy()
        target_label = "Jamaah perempuan"

    elif jenis_info == "Pengajian Malam Rabu":
        tgl_selasa = tanggal_berikutnya(1)
        pengisi_default = pengajian_malam_rabu[index_rotasi_rabu(tgl_selasa)]
        daftar_pengisi = ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden"]
        pengisi = st.selectbox("Pengisi", daftar_pengisi, index=daftar_pengisi.index(pengisi_default) if pengisi_default in daftar_pengisi else 0)
        pesan = pesan_malam_rabu(pengisi)
        target = jamaah_df[(jamaah_df["JenisKelamin"] == "Laki-laki") & (jamaah_df["Aktif"] == "Ya")].copy()
        if pengisi == "Aang Deden":
            khusus = jamaah_df[jamaah_df["Nama"].str.lower().str.contains("aang deden", na=False)].copy()
            target = pd.concat([target, khusus], ignore_index=True).drop_duplicates(subset=["NoWA"])
        target_label = "Jamaah laki-laki"

    else:
        pesan = pesan_syahriahan()
        target = jamaah_df[jamaah_df["Aktif"].isin(["Ya", "Khusus"])].copy()
        target_label = "Semua jamaah aktif"

    st.info(f"Target: {target_label} | Jumlah: {len(target)} penerima")
    st.text_area("Isi pesan siap kirim", value=pesan, height=270)

    ringkasan = f"""🕌 AL-FALAH DIGITAL V20

Pengumuman disiapkan:
{jenis_info}

Target: {target_label}
Jumlah penerima: {len(target)}

Pesan sudah tersedia di menu WA Jamaah."""
    if st.button("🔔 Kirim Ringkasan ke Telegram Admin"):
        if kirim_telegram(ringkasan):
            st.success("Ringkasan terkirim ke Telegram admin.")
        else:
            st.warning("Telegram belum terkirim. Cek TELEGRAM_BOT_TOKEN di Secrets.")

    st.markdown("### 🚀 Kirim WA Otomatis Fonnte")
    st.warning("Pastikan pesan sudah benar. Setelah tombol diklik, pesan akan langsung dikirim ke seluruh target melalui Fonnte.")
    konfirmasi = st.checkbox("Saya sudah cek pesan dan siap mengirim ke semua target")

    if st.button("🚀 Kirim WhatsApp Otomatis ke Semua Target", disabled=not konfirmasi, use_container_width=True):
        if target.empty:
            st.error("Target kosong. Tidak ada pesan yang dikirim.")
        else:
            progress = st.progress(0)
            sukses = 0
            gagal = 0
            log_hasil = []

            for i, (_, row) in enumerate(target.iterrows(), start=1):
                nama_jamaah = row["Nama"]
                nomor_jamaah = row["NoWA"]

                ok, info = kirim_fonnte(nomor_jamaah, pesan)
                status = "Terkirim" if ok else "Gagal"

                if ok:
                    sukses += 1
                else:
                    gagal += 1

                ket = str(info)[:180]
                log_ok, log_info = simpan_log_wa(nama_jamaah, nomor_jamaah, jenis_info, status, ket)

                log_hasil.append({
                    "Nama": nama_jamaah,
                    "NoWA": nomor_jamaah,
                    "Status": status,
                    "Keterangan": ket,
                    "Log WA": "Tersimpan" if log_ok else f"Gagal: {log_info}"
                })

                progress.progress(i / len(target))

            st.success(f"Selesai. Berhasil: {sukses} | Gagal: {gagal}")
            st.dataframe(pd.DataFrame(log_hasil), use_container_width=True)
            kirim_telegram(f"🕌 AL-FALAH DIGITAL V20\n\nWA Otomatis selesai.\nJenis: {jenis_info}\nTarget: {target_label}\nBerhasil: {sukses}\nGagal: {gagal}")

    st.markdown("### Daftar Target")
    st.dataframe(target[["Nama", "JenisKelamin", "NoWA", "Aktif"]], use_container_width=True)

    st.markdown("### Riwayat Log WA")
    log_df = baca_log_wa()
    if log_df.empty:
        st.info("Log WA masih kosong atau belum bisa dibaca.")
    else:
        st.dataframe(log_df.tail(30), use_container_width=True)

    st.markdown("### Tombol Manual Cadangan")
    st.caption("Jika gateway sedang bermasalah, tombol manual ini masih bisa dipakai satu per satu.")
    for _, row in target.iterrows():
        st.link_button(f"📱 Manual ke {row['Nama']}", wa_nomor_link(row["NoWA"], pesan), use_container_width=True)

    st.markdown("### Grup AL-BARZANJI")
    st.markdown(f"[👥 Buka Grup AL-BARZANJI]({GRUP_AL_BARZANJI})")


elif menu == "🤖 WA Otomatis V20":
    st.subheader("🤖 WA Otomatis V20 - Kegiatan & Laporan Keuangan")
    st.success("Modul ini untuk mengirim pesan otomatis kegiatan masjid dan laporan keuangan melalui Fonnte.")

    jenis_auto = st.selectbox(
        "Pilih jenis otomatis",
        [
            "senenan",
            "rabu",
            "syahriahan",
            "laporan",
        ],
        format_func=lambda x: {
            "senenan": "Pengajian Senenan",
            "rabu": "Pengajian Malam Rabu",
            "syahriahan": "Syahriahan Sholawat",
            "laporan": "Laporan Keuangan",
        }.get(x, x)
    )

    jenis_pesan, pesan_preview = pesan_otomatis(jenis_auto)
    target_preview, target_label = target_otomatis(jenis_auto, load_jamaah())

    c1, c2, c3 = st.columns(3)
    c1.metric("Jenis Pesan", jenis_pesan)
    c2.metric("Target", target_label)
    c3.metric("Jumlah", len(target_preview))

    st.text_area("Preview pesan otomatis", value=pesan_preview, height=320)

    with st.expander("Lihat target penerima", expanded=False):
        if target_preview.empty:
            st.warning("Target masih kosong.")
        else:
            st.dataframe(target_preview[["Nama", "JenisKelamin", "NoWA", "Aktif", "Catatan"]], use_container_width=True)

    st.markdown("### 🔗 Link Cron GitHub Actions")
    st.caption("Buka link ini dari GitHub Actions sesuai jadwal. AUTO_KEY harus diisi di Streamlit Secrets.")
    app_url = LINK_APP.rstrip("/")
    st.code(f"{app_url}/?auto={jenis_auto}&key=ISI_AUTO_KEY")

    st.markdown("### 🚀 Tes Kirim Sekarang")
    paksa = st.checkbox("Paksa kirim walaupun hari ini sudah pernah terkirim")
    siap = st.checkbox("Saya sudah cek pesan dan target, siap kirim")

    if st.button("🚀 Kirim Otomatis Sekarang", disabled=not siap, use_container_width=True):
        hasil = kirim_otomatis_v20(jenis_auto, paksa=paksa)
        if hasil.get("ok"):
            st.success(f"Selesai. Berhasil: {hasil.get('sukses')} | Gagal: {hasil.get('gagal')}")
            st.dataframe(pd.DataFrame(hasil.get("detail", [])), use_container_width=True)
        else:
            st.warning(hasil.get("info", "Tidak terkirim"))

    st.markdown("### 📋 Log WA Terbaru")
    log_df = baca_log_wa()
    if log_df.empty:
        st.info("Log WA kosong atau belum bisa dibaca.")
    else:
        st.dataframe(log_df.tail(50), use_container_width=True)

elif menu == "👥 Pengurus DKM":
    st.subheader("👥 Struktur Pengurus DKM")
    for jabatan, daftar_nama in pengurus.items():
        with st.expander(jabatan, expanded=jabatan in ["Ketua DKM", "Wakil Ketua", "Sekretaris", "Bendahara"]):
            for nama in daftar_nama:
                st.write(f"- {nama}")

elif menu == "📅 Jadwal Pengajian":
    st.subheader("📅 Jadwal Pengajian Lengkap")
    df_jadwal = pd.DataFrame([
        ["Pengajian Malam Rabu", "Malam Rabu", "19:30 - 21:30 WIB", "Ihin → Nanang → Jujun → Aang Deden"],
        ["Pengajian Senenan", "Senin", "07:30 - 09:00 WIB", "Nanang → Aang Deden → Ihin → Ihin"],
        ["Syahriahan Sholawat", "Malam Jumat awal bulan Hijriah", "20:00 - 21:30 WIB", "Aang Deden Kasyful Anwar"]
    ], columns=["Kegiatan", "Hari", "Waktu", "Rotasi/Pengisi"])
    st.dataframe(df_jadwal, use_container_width=True)

elif menu == "📢 Pengumuman":
    st.subheader("📢 Buat Pengumuman")
    with st.form("form_pengumuman"):
        judul = st.text_input("Judul Pengumuman")
        isi = st.text_area("Isi Pengumuman")
        simpan = st.form_submit_button("💾 Simpan Pengumuman")
    st.caption("Pengumuman yang dibuat akan tampil di dashboard maksimal 1x24 jam, lalu hilang otomatis dari dashboard.")
    if simpan:
        if not judul.strip() or not isi.strip():
            st.error("Judul dan isi pengumuman wajib diisi.")
        else:
            data = pd.DataFrame([{"Tanggal": waktu_wib().strftime("%Y-%m-%d %H:%M:%S"), "Judul": judul.strip(), "Isi": isi.strip()}])
            pengumuman_df = pd.concat([pengumuman_df, data], ignore_index=True)
            save_pengumuman(pengumuman_df)
            st.success("Pengumuman berhasil disimpan dan akan aktif 1x24 jam di dashboard.")
            st.cache_data.clear()
            st.rerun()

    if not pengumuman_df.empty:
        tampil_peng = pengumuman_df.copy()
        tampil_peng["Waktu"] = pd.to_datetime(tampil_peng["Tanggal"], errors="coerce")
        tampil_peng["Status Dashboard"] = tampil_peng["Waktu"].apply(lambda x: "Aktif" if pd.notna(x) and x >= waktu_wib() - timedelta(hours=24) else "Kadaluarsa")
        st.dataframe(tampil_peng.drop(columns=["Waktu"], errors="ignore"), use_container_width=True)

elif menu == "📲 Share WhatsApp":
    st.subheader("📲 V17 Smart Broadcast WhatsApp")

    if mode != "🔐 Admin":
        st.info("Menu ini untuk membagikan informasi masjid secara manual.")
        teks = st.text_area("Teks yang akan dibagikan", value=f"""Assalamu'alaikum Warahmatullahi Wabarakatuh

Pengumuman Masjid Jami Al-Falah
Kp. Caringin

Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Grup Jamaah AL-BARZANJI:
{GRUP_AL_BARZANJI}

Jazakumullahu khairan.""", height=220)
        st.markdown(f"[📤 Bagikan ke WhatsApp]({wa_link(teks)})")
        st.code(teks)
    else:
        st.caption("Kirim pengumuman otomatis via Fonnte, simpan Log WA, dan kirim ringkasan ke Telegram Admin.")

        jamaah_df = load_jamaah()
        log_df = baca_log_wa()

        jenis_broadcast = st.selectbox(
            "Jenis Pesan",
            ["Pengumuman Terakhir", "Pesan Custom", "Pengajian Senenan", "Pengajian Malam Rabu", "Syahriahan Sholawat"]
        )

        judul_pesan = "Pengumuman Masjid Jami Al-Falah"
        isi_default = ""

        if jenis_broadcast == "Pengumuman Terakhir":
            if pengumuman_aktif_df.empty:
                st.warning("Belum ada pengumuman aktif. Buat dulu di menu 📢 Pengumuman atau gunakan Pesan Custom.")
                isi_default = ""
            else:
                terakhir = pengumuman_aktif_df.tail(1).iloc[0]
                judul_pesan = str(terakhir.get("Judul", "Pengumuman Masjid Jami Al-Falah"))
                isi_peng = str(terakhir.get("Isi", ""))
                isi_default = f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

{judul_pesan}

{isi_peng}

🌐 Aplikasi AL-FALAH Digital:
{LINK_APP}

Jazakumullahu khairan.

🕌 DKM Masjid Jami AL-FALAH"""

        elif jenis_broadcast == "Pesan Custom":
            judul_pesan = st.text_input("Judul Pesan", value="Pengumuman Masjid Jami AL-FALAH")
            isi_default = f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

{judul_pesan}

Silakan isi pengumuman di sini.

🌐 Aplikasi AL-FALAH Digital:
{LINK_APP}

Jazakumullahu khairan.

🕌 DKM Masjid Jami AL-FALAH"""

        elif jenis_broadcast == "Pengajian Senenan":
            tgl_senin = tanggal_berikutnya(0)
            pengisi_default = pengajian_senin[index_rotasi_senin(tgl_senin)]
            daftar_pengisi = ["Aang Deden", "Ustadz Ihin", "Ustadz Nanang"]
            pengisi = st.selectbox("Pengisi", daftar_pengisi, index=daftar_pengisi.index(pengisi_default) if pengisi_default in daftar_pengisi else 0)
            judul_pesan = "Pengajian Senenan"
            isi_default = pesan_senenan(pengisi)

        elif jenis_broadcast == "Pengajian Malam Rabu":
            tgl_selasa = tanggal_berikutnya(1)
            pengisi_default = pengajian_malam_rabu[index_rotasi_rabu(tgl_selasa)]
            daftar_pengisi = ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden"]
            pengisi = st.selectbox("Pengisi", daftar_pengisi, index=daftar_pengisi.index(pengisi_default) if pengisi_default in daftar_pengisi else 0)
            judul_pesan = "Pengajian Malam Rabu"
            isi_default = pesan_malam_rabu(pengisi)

        else:
            judul_pesan = "Syahriahan Sholawat"
            isi_default = pesan_syahriahan()

        st.markdown("### ✍️ Preview dan Edit Pesan")
        pesan_final = st.text_area("Pesan yang akan dikirim", value=isi_default, height=320)

        st.markdown("### 🎯 Target Penerima")
        target_mode = st.radio(
            "Pilih Target",
            ["Tes ke nomor admin saja", "Semua jamaah aktif", "Pengurus", "Perempuan aktif", "Laki-laki aktif", "Nomor tertentu"],
            horizontal=False
        )

        if target_mode == "Tes ke nomor admin saja":
            nomor_test = ambil_secret("FONNTE_DEVICE_ID", "6281395440454")
            nomor_test = st.text_input("Nomor Test", value=nomor_test)
            target = pd.DataFrame([["Admin/Test", "-", normalisasi_wa(nomor_test), "Ya", "Test"]], columns=KOLOM_JAMAAH)
            target_label = "Tes ke nomor admin saja"

        elif target_mode == "Semua jamaah aktif":
            target = filter_jamaah_aktif_umum(jamaah_df)
            target_label = "Semua jamaah aktif (tanpa data khusus)"

        elif target_mode == "Pengurus":
            target = jamaah_df[jamaah_df["Catatan"].astype(str).str.lower().str.contains("pengurus", na=False)].copy()
            target_label = "Pengurus"

        elif target_mode == "Perempuan aktif":
            target = jamaah_df[(jamaah_df["JenisKelamin"] == "Perempuan") & (jamaah_df["Aktif"].astype(str).str.lower().eq("ya"))].copy()
            target_label = "Jamaah perempuan aktif"

        elif target_mode == "Laki-laki aktif":
            target = jamaah_df[(jamaah_df["JenisKelamin"] == "Laki-laki") & (jamaah_df["Aktif"].astype(str).str.lower().eq("ya"))].copy()
            target_label = "Jamaah laki-laki aktif"

        else:
            nama_manual = st.text_input("Nama Penerima", value="Test Manual")
            nomor_manual = st.text_input("Nomor WhatsApp", value="6281395440454")
            target = pd.DataFrame([[nama_manual, "-", normalisasi_wa(nomor_manual), "Ya", "Manual"]], columns=KOLOM_JAMAAH)
            target_label = "Nomor tertentu"

        # Jamaah berstatus Khusus seperti Aang Deden tidak ikut semua pesan.
        # Beliau hanya ditambahkan jika memang menjadi pengisi/pimpinan kegiatan.
        if jenis_broadcast in ["Pengajian Malam Rabu", "Pengajian Senenan"] and "pengisi" in locals():
            target = tambah_khusus_jika_pengisi(target, jamaah_df, pengisi)
        elif jenis_broadcast == "Syahriahan Sholawat":
            target = tambah_khusus_jika_pengisi(target, jamaah_df, "Aang Deden")

        target = target.copy()
        if not target.empty:
            target["NoWA"] = target["NoWA"].astype(str).apply(normalisasi_wa)
            target = target[target["NoWA"] != ""].drop_duplicates(subset=["NoWA"])

        c1, c2, c3 = st.columns(3)
        c1.metric("Target", target_label)
        c2.metric("Jumlah Penerima", len(target))
        c3.metric("Log WA", len(log_df) if not log_df.empty else 0)

        with st.expander("👀 Lihat daftar target", expanded=True):
            if target.empty:
                st.warning("Target kosong.")
            else:
                st.dataframe(target[["Nama", "JenisKelamin", "NoWA", "Aktif", "Catatan"]], use_container_width=True)

        st.markdown("### 🚀 Kirim Otomatis")
        st.warning("Pastikan pesan dan target sudah benar. Setelah tombol diklik, pesan akan langsung dikirim via Fonnte.")
        konfirmasi = st.checkbox("Saya sudah cek pesan dan target, siap mengirim")

        if st.button("🚀 Kirim WhatsApp Otomatis", disabled=not konfirmasi, use_container_width=True):
            if target.empty:
                st.error("Target kosong. Tidak ada pesan dikirim.")
            elif not pesan_final.strip():
                st.error("Pesan kosong. Isi pesan terlebih dahulu.")
            else:
                progress = st.progress(0)
                sukses = 0
                gagal = 0
                log_hasil = []

                for i, (_, row) in enumerate(target.iterrows(), start=1):
                    nama_jamaah = str(row.get("Nama", "")).strip() or "Tanpa Nama"
                    nomor_jamaah = normalisasi_wa(row.get("NoWA", ""))

                    ok, info = kirim_fonnte(nomor_jamaah, pesan_final)
                    status = "Terkirim" if ok else "Gagal"

                    if ok:
                        sukses += 1
                    else:
                        gagal += 1

                    ket = str(info)[:180]
                    log_ok, log_info = simpan_log_wa(nama_jamaah, nomor_jamaah, jenis_broadcast, status, ket)

                    log_hasil.append({
                        "Nama": nama_jamaah,
                        "NoWA": nomor_jamaah,
                        "Status": status,
                        "Keterangan": ket,
                        "Log WA": "Tersimpan" if log_ok else f"Gagal: {log_info}"
                    })
                    progress.progress(i / len(target))

                st.success(f"Selesai. Berhasil: {sukses} | Gagal: {gagal}")
                st.dataframe(pd.DataFrame(log_hasil), use_container_width=True)

                ringkasan = f"""🕌 AL-FALAH DIGITAL V20

WA Broadcast selesai.
Jenis: {jenis_broadcast}
Target: {target_label}
Jumlah Target: {len(target)}
✅ Berhasil: {sukses}
❌ Gagal: {gagal}
Waktu: {waktu_wib().strftime('%d-%m-%Y %H:%M:%S')} WIB"""
                kirim_telegram(ringkasan)

        st.markdown("### 📋 Riwayat Log WA Terbaru")
        log_df = baca_log_wa()
        if log_df.empty:
            st.info("Log WA masih kosong atau belum bisa dibaca.")
        else:
            st.dataframe(log_df.tail(50), use_container_width=True)

        st.markdown("### 🧯 Tombol Manual Cadangan")
        st.caption("Jika Fonnte sedang bermasalah, tombol manual ini masih bisa dipakai.")
        st.markdown(f"[📤 Bagikan Manual ke WhatsApp]({wa_link(pesan_final)})")
        st.code(pesan_final)
