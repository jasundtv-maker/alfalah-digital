import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import os
import urllib.parse
import requests
import base64
import json
import html
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="APP MASJID JAMI AL-FALAH V19", page_icon="🕌", layout="wide")

KAS_FILE = "kas_masjid.csv"
PENGUMUMAN_FILE = "pengumuman.csv"
BANNER_FILE = "banner.png"
JAMAAH_FILE = "jamaah.csv"
CHAT_ID = "8951538688"
LINK_APP = "https://kas-masjid-alfalah.streamlit.app"
GRUP_AL_BARZAJI = "https://chat.whatsapp.com/JWobEDYP9MXEfDYHt8zlLR"
SHEET_ID = "18Af7MohqKRIOlU9XuGCCmXeSaPfqOv8_DWrGH65Zqtc"

KOLOM_KAS = ["Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Petugas"]
KOLOM_PENGUMUMAN = ["Tanggal", "Judul", "Isi", "MasaAktifJam"]
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
            df = pd.read_csv(PENGUMAN_FILE)
        except NameError:
            df = pd.read_csv(PENGUMUMAN_FILE)
        except Exception:
            return pd.DataFrame(columns=KOLOM_PENGUMUMAN)

        for k in KOLOM_PENGUMUMAN:
            if k not in df.columns:
                df[k] = 24 if k == "MasaAktifJam" else ""

        df["MasaAktifJam"] = pd.to_numeric(df["MasaAktifJam"], errors="coerce").fillna(24).astype(int)
        return df[KOLOM_PENGUMUMAN]

    return pd.DataFrame(columns=KOLOM_PENGUMUMAN)

def save_pengumuman(df):
    df.to_csv(PENGUMUMAN_FILE, index=False)

def filter_pengumuman_aktif(df):
    """Tampilkan pengumuman yang belum kadaluarsa.
    Default masa aktif 24 jam. MasaAktifJam = 0 berarti permanen.
    """
    if df.empty:
        return df.copy()

    hasil = df.copy()
    hasil["TanggalParse"] = pd.to_datetime(hasil["Tanggal"], errors="coerce")
    hasil["MasaAktifJam"] = pd.to_numeric(hasil.get("MasaAktifJam", 24), errors="coerce").fillna(24).astype(int)

    sekarang = waktu_wib()
    permanen = hasil["MasaAktifJam"] <= 0
    belum_expired = hasil["TanggalParse"] + pd.to_timedelta(hasil["MasaAktifJam"], unit="h") >= sekarang

    hasil = hasil[permanen | belum_expired].drop(columns=["TanggalParse"], errors="ignore")
    return hasil[KOLOM_PENGUMUMAN]

def bersihkan_html(teks):
    return html.escape(str(teks)).replace("\n", "<br>")

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

👥 Grup Jamaah AL-BARZAJI:
{GRUP_AL_BARZAJI}

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

👥 Grup Jamaah AL-BARZAJI:
{GRUP_AL_BARZAJI}

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

👥 Grup Jamaah AL-BARZAJI:
{GRUP_AL_BARZAJI}

🌐 Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Terima kasih atas partisipasi seluruh jamaah.

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




def target_jamaah_wa_umum():
    """Target laporan transparansi: semua jamaah aktif Ya. Data Khusus tidak ikut broadcast umum."""
    df = load_jamaah()
    if df.empty:
        return df
    df = df.copy()
    df["Aktif"] = df["Aktif"].astype(str).str.strip()
    df["Nama"] = df["Nama"].astype(str).str.strip()
    return df[(df["Aktif"].str.lower() == "ya") & (~df["Nama"].str.lower().str.contains("aang deden", na=False))].copy()


def buat_teks_laporan_kas_bulanan(df, bulan=None, judul="LAPORAN KAS MASJID"):
    """Membuat teks laporan kas singkat untuk WhatsApp."""
    if df.empty:
        return "Belum ada data kas."

    temp = df.copy()
    temp["Tanggal"] = pd.to_datetime(temp["Tanggal"], errors="coerce")
    temp["Jumlah"] = pd.to_numeric(temp["Jumlah"], errors="coerce").fillna(0)

    if bulan:
        temp = temp[temp["Tanggal"].dt.strftime("%Y-%m") == bulan]

    if temp.empty:
        return f"{judul}\n\nBelum ada transaksi untuk periode ini."

    pemasukan = temp[temp["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = temp[temp["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran

    rincian_kategori = temp.groupby(["Jenis", "Kategori"], dropna=False)["Jumlah"].sum().reset_index()
    baris = []
    for _, r in rincian_kategori.iterrows():
        baris.append(f"- {r['Jenis']} | {r['Kategori']}: {rupiah(r['Jumlah'])}")

    periode = bulan if bulan else "Semua Periode"
    teks = f"""🕌 {judul}\nMasjid Jami AL-FALAH Kp. Caringin\n\nPeriode: {periode}\n\n⬆️ Total Pemasukan: {rupiah(pemasukan)}\n⬇️ Total Pengeluaran: {rupiah(pengeluaran)}\n💰 Saldo Periode: {rupiah(saldo)}\n\nRincian:\n""" + "\n".join(baris[:20])

    teks += f"""\n\n🌐 Laporan lengkap bisa dilihat di aplikasi:\n{LINK_APP}\n\nJazakumullahu khairan.\n🕌 DKM Masjid Jami AL-FALAH"""
    return teks


def kirim_broadcast_wa_ke_jamaah(pesan, jenis_pesan="Laporan Transparansi"):
    """Kirim WA ke jamaah aktif dan simpan Log WA."""
    target = target_jamaah_wa_umum()
    if target.empty:
        st.warning("Target jamaah aktif kosong.")
        return 0, 0, []

    progress = st.progress(0)
    sukses = 0
    gagal = 0
    log_hasil = []

    for i, (_, row) in enumerate(target.iterrows(), start=1):
        nama = row.get("Nama", "")
        nowa = row.get("NoWA", "")
        ok, info = kirim_fonnte(nowa, pesan)
        status = "Terkirim" if ok else "Gagal"
        if ok:
            sukses += 1
        else:
            gagal += 1
        simpan_log_wa(nama, nowa, jenis_pesan, status, str(info)[:300])
        log_hasil.append({"Nama": nama, "NoWA": nowa, "Status": status, "Keterangan": str(info)[:160]})
        progress.progress(i / len(target))

    ringkasan = f"🕌 AL-FALAH DIGITAL V18.1\n\n{jenis_pesan} selesai dikirim.\nTarget: {len(target)}\n✅ Berhasil: {sukses}\n❌ Gagal: {gagal}"
    kirim_telegram(ringkasan)
    return sukses, gagal, log_hasil

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

kas_df = load_kas()
pengumuman_df = load_pengumuman()
pengumuman_aktif_df = filter_pengumuman_aktif(pengumuman_df)

# Setting dari Google Sheet jika tersedia
setting_wa_online = load_setting_wa()
LINK_APP = setting_wa_online.get("LinkApp", LINK_APP)
GRUP_AL_BARZAJI = setting_wa_online.get("GroupBarzaji", GRUP_AL_BARZAJI)

wib = waktu_wib()
tanggal_wib = wib.date()
hijriah_text = kalender_hijriah_online(tanggal_wib)
sholat = jadwal_sholat_cianjur()

st.sidebar.title("🕌 APP AL-FALAH V19")

mode = st.sidebar.radio("Mode Aplikasi", ["👥 Jamaah", "🔐 Admin"])

if mode == "🔐 Admin":
    menu = st.sidebar.radio(
        "Menu Admin",
        ["🏠 Dashboard", "💰 Input Kas", "📦 Input Kotak Amal", "🏫 Kas Madrasah & PHBI", "📊 Laporan Kas", "👥 Data Jamaah", "📲 WA Jamaah", "👥 Pengurus DKM", "📅 Jadwal Pengajian", "📢 Pengumuman", "📲 Share WhatsApp"]
    )
else:
    menu = st.sidebar.radio(
        "Menu Jamaah",
        ["🏠 Dashboard", "👥 Pengurus DKM", "📅 Jadwal Pengajian", "📢 Pengumuman", "📲 Share WhatsApp"]
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

    running_text = "📢 Selamat datang di APP MASJID JAMI AL-FALAH\nJadwal pengajian, kas masjid, pengurus, dan pengumuman dapat dilihat langsung di dashboard ini."
    if not pengumuman_aktif_df.empty:
        terakhir = pengumuman_aktif_df.tail(1).iloc[0]
        running_text = f"📢 PENGUMUMAN TERBARU\n\n{terakhir['Judul']}\n\n{terakhir['Isi']}"

    running_html = bersihkan_html(running_text)
    components.html(f"""
    <div style="
        height:190px;
        background:#020617;
        border:3px solid #FFD700;
        border-radius:18px;
        padding:0 18px;
        margin-bottom:22px;
        overflow:hidden;
        box-shadow:0 0 22px rgba(255,215,0,.75), inset 0 0 20px rgba(0,255,102,.18);
        position:relative;
        font-family:Arial, sans-serif;
    ">
        <div style="
            position:absolute;
            left:0;
            right:0;
            top:0;
            padding:10px 16px;
            text-align:center;
            color:#FFD700;
            font-size:20px;
            font-weight:900;
            background:linear-gradient(180deg,#020617 60%,rgba(2,6,23,.75));
            z-index:2;
            text-shadow:0 0 10px #FFD700;
        ">📢 INFO MASJID AL-FALAH</div>

        <div class="vertical-text">
            {running_html}
        </div>
    </div>

    <style>
    .vertical-text {{
        position:absolute;
        width:100%;
        left:0;
        padding:0 22px;
        box-sizing:border-box;
        color:#00ff66;
        font-size:24px;
        font-weight:900;
        line-height:1.55;
        text-align:center;
        text-shadow:0 0 6px #00ff66,0 0 16px #00ff66;
        animation: naikPelan 45s linear infinite;
        white-space:normal;
    }}
    @keyframes naikPelan {{
        0% {{ transform: translateY(175px); }}
        100% {{ transform: translateY(-115%); }}
    }}
    </style>
    """, height=215)

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
    jumlah_buka_kotak = len(kas_df[kas_df["Kategori"] == "Kotak Amal"])

    khusus_madrasah = kas_df[kas_df["Kategori"].isin(["Kotak Amal Senenan", "Kas Madrasah"])].copy()
    masuk_madrasah = khusus_madrasah[khusus_madrasah["Jenis"] == "Pemasukan"]["Jumlah"].sum() if not khusus_madrasah.empty else 0
    keluar_madrasah = khusus_madrasah[khusus_madrasah["Jenis"] == "Pengeluaran"]["Jumlah"].sum() if not khusus_madrasah.empty else 0
    saldo_madrasah = masuk_madrasah - keluar_madrasah

    khusus_rajaban = kas_df[kas_df["Kategori"] == "Iuran PHBI Rajaban"].copy()
    masuk_rajaban = khusus_rajaban[khusus_rajaban["Jenis"] == "Pemasukan"]["Jumlah"].sum() if not khusus_rajaban.empty else 0
    keluar_rajaban = khusus_rajaban[khusus_rajaban["Jenis"] == "Pengeluaran"]["Jumlah"].sum() if not khusus_rajaban.empty else 0
    saldo_rajaban = masuk_rajaban - keluar_rajaban

    st.markdown("## 📊 Ringkasan Laporan")
    st.caption("Saldo akhir tampil ringkas. Klik tombol laporan lengkap di bawah setiap kartu untuk melihat rincian.")

    st.markdown("""
    <style>
    .finance-card-premium {
        min-height: 215px;
        border-radius: 26px;
        padding: 24px;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 18px 45px rgba(2, 6, 23, .22);
        border: 1px solid rgba(255,255,255,.34);
        margin-bottom: 12px;
    }
    .finance-card-premium::before {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: -60px;
        top: -60px;
        background: rgba(255,255,255,.16);
        border-radius: 50%;
    }
    .finance-card-title {
        font-size: 20px;
        font-weight: 950;
        letter-spacing: .3px;
        position: relative;
        z-index: 2;
    }
    .finance-card-label {
        margin-top: 18px;
        font-size: 13px;
        font-weight: 800;
        opacity: .88;
        position: relative;
        z-index: 2;
    }
    .finance-card-value {
        margin-top: 4px;
        font-size: 34px;
        line-height: 1.1;
        font-weight: 950;
        text-shadow: 0 4px 18px rgba(0,0,0,.35);
        position: relative;
        z-index: 2;
    }
    .finance-card-button {
        margin-top: 24px;
        display: inline-block;
        padding: 12px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,.18);
        border: 1px solid rgba(255,255,255,.55);
        font-weight: 950;
        font-size: 13px;
        box-shadow: inset 0 0 18px rgba(255,255,255,.13);
        position: relative;
        z-index: 2;
    }
    .finance-note-premium {
        background: linear-gradient(135deg,#020617,#064e3b);
        color: #fef3c7;
        border: 2px solid #facc15;
        border-radius: 18px;
        padding: 14px 18px;
        font-weight: 850;
        box-shadow: 0 0 18px rgba(250,204,21,.3);
        margin: 8px 0 16px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    def kartu_laporan_premium(judul, saldo_akhir, warna1, warna2, ikon):
        st.markdown(f"""
        <div class="finance-card-premium" style="background:linear-gradient(135deg,{warna1},{warna2});">
            <div class="finance-card-title">{ikon} {judul}</div>
            <div class="finance-card-label">Saldo akhir saat ini</div>
            <div class="finance-card-value">{rupiah(saldo_akhir)}</div>
            <div class="finance-card-button">📋 Klik Laporan Lengkap →</div>
        </div>
        """, unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)
    with k1:
        kartu_laporan_premium("Laporan Kas Masjid", saldo, "#052e16", "#16a34a", "💰")
    with k2:
        kartu_laporan_premium("Laporan Kas Madrasah", saldo_madrasah, "#1e1b4b", "#06b6d4", "🏫")
    with k3:
        kartu_laporan_premium("Laporan Iuran Rajaban", saldo_rajaban, "#7c2d12", "#f97316", "🎉")

    st.markdown("<div class='finance-note-premium'>🟢 Transparansi Keuangan Aktif • Klik salah satu laporan lengkap di bawah ini untuk melihat rincian tanpa perlu scroll jauh.</div>", unsafe_allow_html=True)

    st.markdown("## 🧭 Pusat Informasi Keuangan Masjid")
    st.caption("Rincian laporan ditempatkan tepat di bawah ringkasan agar jamaah mudah melihat laporan lengkap.")

    with st.expander("💰 📋 Klik Laporan Lengkap Kas Masjid", expanded=False):
        st.metric("Saldo Kas Masjid", rupiah(saldo))
        st.metric("Total Pemasukan", rupiah(pemasukan))
        st.metric("Total Pengeluaran", rupiah(pengeluaran))
        tampil = kas_df.tail(20).copy()
        if not tampil.empty:
            tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
            st.dataframe(tampil, use_container_width=True)
        else:
            st.info("Belum ada data kas masjid.")

    with st.expander("🏫 📋 Klik Laporan Lengkap Kas Madrasah", expanded=False):
        khusus = kas_df[kas_df["Kategori"].isin(["Kotak Amal Senenan", "Kas Madrasah"])].copy()
        st.metric("Saldo Kas Madrasah", rupiah(saldo_madrasah))
        st.metric("Total Pemasukan Madrasah", rupiah(masuk_madrasah))
        st.metric("Total Pengeluaran Madrasah", rupiah(keluar_madrasah))
        if not khusus.empty:
            khusus_tampil = khusus.tail(20).copy()
            khusus_tampil["Jumlah"] = khusus_tampil["Jumlah"].apply(rupiah)
            st.dataframe(khusus_tampil, use_container_width=True)
        else:
            st.info("Belum ada data kas madrasah.")

    with st.expander("🎉 📋 Klik Laporan Lengkap Iuran Rajaban", expanded=False):
        rajaban = kas_df[kas_df["Kategori"] == "Iuran PHBI Rajaban"].copy()
        st.metric("Saldo Dana Rajaban", rupiah(saldo_rajaban))
        st.metric("Total Iuran Masuk", rupiah(masuk_rajaban))
        st.metric("Total Pengeluaran", rupiah(keluar_rajaban))
        if not rajaban.empty:
            rajaban_tampil = rajaban.tail(20).copy()
            rajaban_tampil["Jumlah"] = rajaban_tampil["Jumlah"].apply(rupiah)
            st.dataframe(rajaban_tampil, use_container_width=True)
        else:
            st.info("Belum ada data iuran Rajaban.")

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

    st.markdown("## 🧭 Pusat Informasi Masjid")
    st.caption("Informasi umum masjid. Untuk laporan keuangan lengkap, lihat bagian Pusat Informasi Keuangan di atas.")

    card4, card5, card6 = st.columns(3)
    with card4:
        with st.expander("📢 Pengumuman Aktif", expanded=False):
            if pengumuman_aktif_df.empty:
                st.info("Belum ada pengumuman aktif.")
            else:
                st.dataframe(pengumuman_aktif_df.tail(5), use_container_width=True)

    with card5:
        with st.expander("📅 Agenda Kegiatan", expanded=False):
            st.dataframe(pd.DataFrame(agenda_tetap, columns=["Kegiatan", "Hari", "Waktu"]), use_container_width=True)

    with card6:
        with st.expander("👥 Pengurus Inti DKM", expanded=False):
            st.info("Ketua DKM\n\nAang Deden Kasyful Anwar")
            st.info("Wakil Ketua\n\nIden Tazuni")
            st.info("Sekretaris\n\nUstadz Ihin")
            st.info("Bendahara\n\nAceng Abdul Roup")

    with st.expander("📞 Hubungi Pengurus DKM", expanded=False):
        teks_wa_admin = "Assalamu'alaikum, saya ingin menghubungi pengurus DKM Masjid Jami Al-Falah."
        st.markdown(f"<a class='wa-button' href='{wa_link(teks_wa_admin)}' target='_blank'>📲 Hubungi DKM via WhatsApp</a>", unsafe_allow_html=True)

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

elif menu == "💰 Input Kas":
    st.subheader("💰 Input Kas Admin")
    with st.form("form_kas"):
        c1, c2, c3 = st.columns(3)
        tanggal = c1.date_input("Tanggal", date.today())
        jenis = c2.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = c3.selectbox("Kategori", ["Infaq Jumat", "Kotak Amal", "Kotak Amal Senenan", "Iuran PHBI Rajaban", "Kas Madrasah", "Donatur", "Pembangunan", "Listrik", "Kebersihan", "Lainnya"])
        keterangan = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah", min_value=0, step=1000)
        petugas = st.text_input("Petugas", value="Aceng Abdul Roup")
        simpan = st.form_submit_button("💾 Simpan Kas")
    if simpan:
        data = pd.DataFrame([{"Tanggal": str(tanggal), "Jenis": jenis, "Kategori": kategori, "Keterangan": keterangan, "Jumlah": jumlah, "Petugas": petugas}])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)
        kirim_telegram(f"🕌 APP MASJID JAMI AL-FALAH\n\nData Kas Baru\nJenis: {jenis}\nKategori: {kategori}\nTanggal: {tanggal}\nJumlah: {rupiah(jumlah)}\nPetugas: {petugas}\nKeterangan: {keterangan}")
        st.success("Data kas berhasil disimpan.")

elif menu == "📦 Input Kotak Amal":
    st.subheader("📦 Input Kotak Amal Admin")
    st.caption("Bisa untuk kotak amal masjid biasa atau kotak amal Senenan madrasah.")

    with st.form("form_kotak_v18_1"):
        c1, c2 = st.columns(2)
        tanggal = c1.date_input("Tanggal Buka Kotak Amal", date.today())
        kategori_kotak = c2.selectbox("Jenis Kotak Amal", ["Kotak Amal", "Kotak Amal Senenan"])
        jumlah = st.number_input("Jumlah Kotak Amal", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan", value="Kotak amal masjid" if kategori_kotak == "Kotak Amal" else "Kotak amal Senenan madrasah")
        petugas = st.text_input("Petugas Penghitung", value="Aceng Abdul Roup")
        kirim_wa = st.checkbox("Setelah disimpan, kirim laporan singkat ke WA jamaah", value=False)
        simpan = st.form_submit_button("💾 Simpan Kotak Amal")

    if simpan:
        data = pd.DataFrame([{"Tanggal": str(tanggal), "Jenis": "Pemasukan", "Kategori": kategori_kotak, "Keterangan": keterangan, "Jumlah": jumlah, "Petugas": petugas}])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)
        pesan_admin = f"🕌 APP MASJID JAMI AL-FALAH\n\nPemasukan {kategori_kotak}\nTanggal: {tanggal}\nJumlah: {rupiah(jumlah)}\nPetugas: {petugas}\nKeterangan: {keterangan}"
        kirim_telegram(pesan_admin)
        st.success(f"{kategori_kotak} berhasil disimpan.")

        if kirim_wa:
            pesan_wa = f"""🕌 LAPORAN TRANSPARANSI {kategori_kotak.upper()}
Masjid Jami AL-FALAH Kp. Caringin

Tanggal: {format_tanggal(tanggal)}
Jumlah: {rupiah(jumlah)}
Petugas: {petugas}
Keterangan: {keterangan}

🌐 Laporan lengkap bisa dilihat di aplikasi:
{LINK_APP}

Jazakumullahu khairan.
🕌 DKM Masjid Jami AL-FALAH"""
            sukses, gagal, log_hasil = kirim_broadcast_wa_ke_jamaah(pesan_wa, f"Laporan {kategori_kotak}")
            st.info(f"Laporan WA selesai. Berhasil: {sukses} | Gagal: {gagal}")
            st.dataframe(pd.DataFrame(log_hasil), use_container_width=True)

elif menu == "🏫 Kas Madrasah & PHBI":
    st.subheader("🏫 Kas Madrasah & PHBI")
    st.caption("Input khusus pemasukan kotak amal Senenan madrasah dan iuran PHBI Rajaban.")

    with st.form("form_kas_madrasah_phbi_v18_1"):
        c1, c2 = st.columns(2)
        tanggal = c1.date_input("Tanggal", date.today(), key="tgl_madrasah_phbi")
        kategori = c2.selectbox("Kategori", ["Kotak Amal Senenan", "Iuran PHBI Rajaban", "Kas Madrasah"])
        jumlah = st.number_input("Jumlah", min_value=0, step=1000, key="jumlah_madrasah_phbi")
        keterangan = st.text_input("Keterangan", value="Setoran " + kategori)
        petugas = st.text_input("Petugas", value="Aceng Abdul Roup", key="petugas_madrasah_phbi")
        kirim_wa = st.checkbox("Kirim laporan pemasukan ini ke WA jamaah", value=False, key="wa_madrasah_phbi")
        simpan = st.form_submit_button("💾 Simpan Pemasukan")

    if simpan:
        data = pd.DataFrame([{"Tanggal": str(tanggal), "Jenis": "Pemasukan", "Kategori": kategori, "Keterangan": keterangan, "Jumlah": jumlah, "Petugas": petugas}])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)
        kirim_telegram(f"🕌 APP MASJID JAMI AL-FALAH\n\nPemasukan {kategori}\nTanggal: {tanggal}\nJumlah: {rupiah(jumlah)}\nPetugas: {petugas}\nKeterangan: {keterangan}")
        st.success(f"Pemasukan {kategori} berhasil disimpan.")

        if kirim_wa:
            pesan_wa = f"""🕌 LAPORAN TRANSPARANSI {kategori.upper()}
Masjid Jami AL-FALAH Kp. Caringin

Tanggal: {format_tanggal(tanggal)}
Jumlah: {rupiah(jumlah)}
Petugas: {petugas}
Keterangan: {keterangan}

🌐 Laporan lengkap bisa dilihat di aplikasi:
{LINK_APP}

Jazakumullahu khairan.
🕌 DKM Masjid Jami AL-FALAH"""
            sukses, gagal, log_hasil = kirim_broadcast_wa_ke_jamaah(pesan_wa, f"Laporan {kategori}")
            st.info(f"Laporan WA selesai. Berhasil: {sukses} | Gagal: {gagal}")
            st.dataframe(pd.DataFrame(log_hasil), use_container_width=True)

    st.divider()
    st.markdown("### 📊 Ringkasan Kas Madrasah & PHBI")
    khusus = kas_df[kas_df["Kategori"].isin(["Kotak Amal Senenan", "Kas Madrasah"])].copy()
    if khusus.empty:
        st.info("Belum ada data.")
    else:
        khusus["Tanggal"] = pd.to_datetime(khusus["Tanggal"], errors="coerce")
        bulan_list = sorted(khusus["Tanggal"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)
        bulan_pilih = st.selectbox("Pilih Bulan Laporan", bulan_list)
        laporan = khusus[khusus["Tanggal"].dt.strftime("%Y-%m") == bulan_pilih].copy()
        total = laporan["Jumlah"].sum()
        st.metric("Total Pemasukan Bulan Ini", rupiah(total))
        tampil = laporan.copy()
        tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
        st.dataframe(tampil, use_container_width=True)

        teks_laporan = buat_teks_laporan_kas_bulanan(khusus, bulan_pilih, "LAPORAN KAS MADRASAH & PHBI")
        with st.expander("👁️ Preview Laporan WA Bulanan"):
            st.code(teks_laporan)
        if st.button("📤 Kirim Laporan Bulanan Kas Madrasah & PHBI ke WA Jamaah", use_container_width=True):
            sukses, gagal, log_hasil = kirim_broadcast_wa_ke_jamaah(teks_laporan, "Laporan Bulanan Kas Madrasah & PHBI")
            st.success(f"Laporan bulanan terkirim. Berhasil: {sukses} | Gagal: {gagal}")
            st.dataframe(pd.DataFrame(log_hasil), use_container_width=True)

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

        st.divider()
        st.markdown("### 📤 Kirim Laporan Kas Bulanan ke WA Jamaah")
        teks_laporan_kas = buat_teks_laporan_kas_bulanan(kas_df, bulan, "LAPORAN KAS MASJID")
        with st.expander("👁️ Preview Pesan WA"):
            st.code(teks_laporan_kas)
        if st.button("📤 Kirim Laporan Kas Bulanan ke WA Jamaah", use_container_width=True):
            sukses, gagal, log_hasil = kirim_broadcast_wa_ke_jamaah(teks_laporan_kas, "Laporan Bulanan Kas Masjid")
            st.success(f"Laporan WA terkirim. Berhasil: {sukses} | Gagal: {gagal}")
            st.dataframe(pd.DataFrame(log_hasil), use_container_width=True)


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

    ringkasan = f"""🕌 AL-FALAH DIGITAL V18

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
            kirim_telegram(f"🕌 AL-FALAH DIGITAL V18\n\nWA Otomatis selesai.\nJenis: {jenis_info}\nTarget: {target_label}\nBerhasil: {sukses}\nGagal: {gagal}")

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

    st.markdown("### Grup AL-BARZAJI")
    st.markdown(f"[👥 Buka Grup AL-BARZAJI]({GRUP_AL_BARZAJI})")

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
    st.caption("V18: pengumuman otomatis hilang dari dashboard setelah masa aktif habis. Arsip tetap tersimpan.")

    with st.form("form_pengumuman"):
        judul = st.text_input("Judul Pengumuman")
        isi = st.text_area("Isi Pengumuman")
        masa_label = st.selectbox(
            "Masa Tampil di Dashboard",
            ["1 Hari / 24 Jam", "3 Hari", "7 Hari", "30 Hari", "Permanen"],
            index=0
        )
        simpan = st.form_submit_button("💾 Simpan Pengumuman")

    if simpan:
        if not judul.strip() or not isi.strip():
            st.error("Judul dan isi pengumuman wajib diisi.")
        else:
            masa_map = {
                "1 Hari / 24 Jam": 24,
                "3 Hari": 72,
                "7 Hari": 168,
                "30 Hari": 720,
                "Permanen": 0,
            }
            data = pd.DataFrame([{
                "Tanggal": waktu_wib().strftime("%Y-%m-%d %H:%M:%S"),
                "Judul": judul.strip(),
                "Isi": isi.strip(),
                "MasaAktifJam": masa_map.get(masa_label, 24),
            }])
            pengumuman_df = pd.concat([pengumuman_df, data], ignore_index=True)
            save_pengumuman(pengumuman_df)
            st.success("Pengumuman berhasil disimpan. Jika masa aktif habis, pengumuman otomatis hilang dari dashboard.")
            st.cache_data.clear()

    pengumuman_aktif_df = filter_pengumuman_aktif(pengumuman_df)

    st.markdown("### ✅ Pengumuman Aktif di Dashboard")
    if pengumuman_aktif_df.empty:
        st.info("Belum ada pengumuman aktif.")
    else:
        st.dataframe(pengumuman_aktif_df.tail(10), use_container_width=True)

    st.markdown("### 🗂️ Arsip Semua Pengumuman")
    if pengumuman_df.empty:
        st.info("Belum ada arsip pengumuman.")
    else:
        st.dataframe(pengumuman_df.tail(50), use_container_width=True)

elif menu == "📲 Share WhatsApp":
    st.subheader("📲 V18 Smart Broadcast WhatsApp")

    if mode != "🔐 Admin":
        st.info("Menu ini untuk membagikan informasi masjid secara manual.")
        teks = st.text_area("Teks yang akan dibagikan", value=f"""Assalamu'alaikum Warahmatullahi Wabarakatuh

Pengumuman Masjid Jami Al-Falah
Kp. Caringin

Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Grup Jamaah AL-BARZAJI:
{GRUP_AL_BARZAJI}

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
            pengumuman_aktif_df = filter_pengumuman_aktif(pengumuman_df)
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
            target = jamaah_df[jamaah_df["Aktif"].astype(str).str.lower().isin(["ya", "khusus"])].copy()
            target_label = "Semua jamaah aktif"

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

                ringkasan = f"""🕌 AL-FALAH DIGITAL V18

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
