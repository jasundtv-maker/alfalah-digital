import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import os
import urllib.parse
import requests

st.set_page_config(page_title="APP MASJID JAMI AL-FALAH V13 PREMIUM", page_icon="🕌", layout="wide")

# =========================
# KONFIGURASI FILE
# =========================
KAS_FILE = "kas_masjid.csv"
PENGUMUMAN_FILE = "pengumuman.csv"
JAMAAH_FILE = "jamaah.csv"
BANNER_FILE = "banner.png"
CHAT_ID = "8951538688"
LINK_APP = "https://kas-masjid-alfalah.streamlit.app"
GRUP_AL_BARZAJI = "https://chat.whatsapp.com/JWobEDYP9MXEfDYHt8zlLR"

KOLOM_KAS = ["Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Petugas"]
KOLOM_PENGUMUMAN = ["Tanggal", "Judul", "Isi"]
KOLOM_JAMAAH = ["Nama", "JenisKelamin", "NoWA", "Aktif", "Catatan"]

# =========================
# DATA DKM
# =========================
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
    "Keamanan": ["Ace Pu’ad", "Nyanyang (Gonyol)", "M. Emon"],
}

# Rotasi jadwal
pengajian_malam_rabu = ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden"]
pengajian_senenan = ["Ustadz Nanang", "Aang Deden", "Ustadz Ihin", "Ustadz Ihin"]

agenda_tetap = [
    ["Pengajian Malam Rabu", "Selasa malam Rabu", "19:30 - 21:30 WIB", "Madrasah Al-Falah"],
    ["Pengajian Senenan", "Senin pagi", "07:30 - 09:00 WIB", "Madrasah Al-Falah"],
    ["Syahriahan Sholawat", "Malam Jumat awal bulan Hijriah", "20:00 - 21:30 WIB", "Masjid Jami Al-Falah"],
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

# =========================
# FUNGSI UMUM
# =========================
def rupiah(angka):
    try:
        return "Rp {:,.0f}".format(float(angka)).replace(",", ".")
    except Exception:
        return "Rp 0"


def normalisasi_wa(nomor):
    nomor = str(nomor).replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    return nomor


def link_wa_nomor(nomor, text):
    nomor = normalisasi_wa(nomor)
    return f"https://wa.me/{nomor}?text={urllib.parse.quote(text)}"


def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)


def kirim_telegram(pesan):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        try:
            token = st.secrets["TELEGRAM_BOT_TOKEN"]
        except Exception:
            token = None
    if not token:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}, timeout=10)
        return True
    except Exception:
        return False

# =========================
# LOAD / SAVE DATA
# =========================
def load_kas():
    if os.path.exists(KAS_FILE):
        try:
            df = pd.read_csv(KAS_FILE)
            # Dukung file lama huruf kecil dari V12
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
            return pd.DataFrame(columns=KOLOM_KAS)
    return pd.DataFrame(columns=KOLOM_KAS)


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
        except Exception:
            return pd.DataFrame(columns=KOLOM_PENGUMUMAN)
    return pd.DataFrame(columns=KOLOM_PENGUMUMAN)


def save_pengumuman(df):
    df.to_csv(PENGUMUMAN_FILE, index=False)


def init_jamaah():
    if not os.path.exists(JAMAAH_FILE):
        pd.DataFrame(DATA_JAMAAH_AWAL, columns=KOLOM_JAMAAH).to_csv(JAMAAH_FILE, index=False)


def load_jamaah():
    init_jamaah()
    try:
        df = pd.read_csv(JAMAAH_FILE, dtype=str).fillna("-")
        for k in KOLOM_JAMAAH:
            if k not in df.columns:
                df[k] = "-"
        df["NoWA"] = df["NoWA"].apply(normalisasi_wa)
        return df[KOLOM_JAMAAH]
    except Exception:
        return pd.DataFrame(DATA_JAMAAH_AWAL, columns=KOLOM_JAMAAH)


def save_jamaah(df):
    df.to_csv(JAMAAH_FILE, index=False)

# =========================
# JADWAL & WAKTU
# =========================
def tanggal_berikutnya(target_weekday):
    hari_ini = date.today()
    selisih = (target_weekday - hari_ini.weekday()) % 7
    return hari_ini + timedelta(days=selisih)


def index_rotasi_rabu(tgl_selasa):
    start = date(2026, 6, 16)  # Selasa malam Rabu pertama: Ustadz Ihin
    return ((tgl_selasa - start).days // 7) % 4


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
    except Exception:
        return "Kalender Hijriah tidak terbaca"


@st.cache_data(ttl=1800)
def jadwal_sholat_cianjur():
    try:
        url = "https://api.aladhan.com/v1/timingsByCity"
        params = {"city": "Cianjur", "country": "Indonesia", "method": 20}
        r = requests.get(url, params=params, timeout=10).json()
        t = r["data"]["timings"]
        return {
            "Subuh": t["Fajr"][:5],
            "Dzuhur": t["Dhuhr"][:5],
            "Ashar": t["Asr"][:5],
            "Maghrib": t["Maghrib"][:5],
            "Isya": t["Isha"][:5],
        }
    except Exception:
        return {"Subuh": "04:35", "Dzuhur": "11:55", "Ashar": "15:15", "Maghrib": "17:50", "Isya": "19:00"}


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
        "pengisi": pengajian_senenan[index_rotasi_senin(mulai_senin.date())],
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

# =========================
# PESAN WHATSAPP
# =========================
def buat_pesan_senenan(pengisi):
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


def buat_pesan_malam_rabu(pengisi):
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


def buat_pesan_syahriahan():
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

# =========================
# LOAD DATA
# =========================
kas_df = load_kas()
pengumuman_df = load_pengumuman()
jamaah_df = load_jamaah()

wib = waktu_wib()
tanggal_wib = wib.date()
hijriah_text = kalender_hijriah_online(tanggal_wib)
sholat = jadwal_sholat_cianjur()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🕌 APP AL-FALAH V13")
mode = st.sidebar.radio("Mode Aplikasi", ["👥 Jamaah", "🔐 Admin"])

if mode == "🔐 Admin":
    menu = st.sidebar.radio(
        "Menu Admin",
        ["🏠 Dashboard", "💰 Input Kas", "📦 Input Kotak Amal", "📊 Laporan Kas", "👥 Data Jamaah", "👥 Pengurus DKM", "📅 Jadwal Pengajian", "📢 Pengumuman", "📲 Share WhatsApp"]
    )
else:
    menu = st.sidebar.radio(
        "Menu Jamaah",
        ["🏠 Dashboard", "👥 Pengurus DKM", "📅 Jadwal Pengajian", "📢 Pengumuman", "📲 Share WhatsApp"]
    )

# =========================
# DASHBOARD
# =========================
if menu == "🏠 Dashboard":

    if os.path.exists(BANNER_FILE):
        st.image(BANNER_FILE, use_container_width=True)

    st.markdown("""
    <style>
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
        background:radial-gradient(circle at top left, rgba(255,215,0,.22), transparent 30%),
        radial-gradient(circle at top right, rgba(0,255,120,.18), transparent 35%),
        linear-gradient(135deg,#011c16,#064e3b,#022c22);
        padding:22px;
        border-radius:26px;
        text-align:center;
        border:2px solid #FFD700;
        margin-bottom:20px;
        animation:borderGlow 3s infinite;
    }
    .premium-title {
        color:#FFD700;
        font-size:42px;
        font-weight:950;
        animation:glowPulse 2.4s infinite;
        margin-bottom:6px;
    }
    .premium-subtitle {
        color:#fef9c3;
        font-size:20px;
        font-weight:800;
    }
    .lamp {
        display:inline-block;
        width:12px;
        height:12px;
        margin:0 7px;
        border-radius:50%;
        background:#FFD700;
        animation:lampBlink 1.3s infinite;
    }
    .premium-chip {
        background:#020617;
        color:#00ff66;
        display:inline-block;
        padding:11px 18px;
        border-radius:16px;
        border:2px solid #FFD700;
        margin-top:16px;
        font-size:17px;
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

    st.markdown(f"""
    <div class="premium-hero">
        <div>
            <span class="lamp"></span><span class="lamp"></span><span class="lamp"></span>
            <span class="lamp"></span><span class="lamp"></span><span class="lamp"></span>
        </div>
        <div class="premium-title">🕌 MASJID JAMI AL-FALAH</div>
        <div class="premium-subtitle">Smart Masjid Digital • Kas • Jadwal Pengajian • Pengumuman</div>
        <div class="premium-chip">📅 {format_tanggal(tanggal_wib)} &nbsp; | &nbsp; 🌙 {hijriah_text}</div>
    </div>
    """, unsafe_allow_html=True)

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

    running_text = "📢 Selamat datang di APP MASJID JAMI AL-FALAH | Jadwal pengajian, kas masjid, pengurus dan pengumuman dapat dilihat langsung di dashboard ini."
    if not pengumuman_df.empty:
        terakhir = pengumuman_df.tail(1).iloc[0]
        running_text = f"📢 Pengumuman Terbaru: {terakhir['Judul']} - {terakhir['Isi']}"

    st.markdown(f"""
    <div class="led-box">
        <marquee scrollamount="7" class="led-text">{running_text}</marquee>
    </div>
    """, unsafe_allow_html=True)

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
        document.getElementById("countdown").innerHTML = days + " Hari  " + hours + " Jam  " + minutes + " Menit  " + seconds + " Detik";
    }}
    setInterval(updateCountdown, 1000);
    updateCountdown();
    </script>
    """, height=215)

    st.divider()

    pemasukan = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran
    total_kotak_amal = kas_df[kas_df["Kategori"] == "Kotak Amal"]["Jumlah"].sum()
    jumlah_buka_kotak = len(kas_df[kas_df["Kategori"] == "Kotak Amal"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Saldo Kas", rupiah(saldo))
    c2.metric("⬆️ Total Pemasukan", rupiah(pemasukan))
    c3.metric("⬇️ Total Pengeluaran", rupiah(pengeluaran))
    c4.metric("📦 Total Kotak Amal", rupiah(total_kotak_amal))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📦 Buka Kotak Amal", f"{jumlah_buka_kotak} kali")
    c6.metric("👥 Pengurus", sum(len(v) for v in pengurus.values()))
    c7.metric("📢 Pengumuman", len(pengumuman_df))
    c8.metric("👥 Jamaah", len(jamaah_df))

    st.divider()

    tgl_rabu = tanggal_berikutnya(1)
    ustadz_rabu = pengajian_malam_rabu[index_rotasi_rabu(tgl_rabu)]
    tgl_senin = tanggal_berikutnya(0)
    ustadz_senin = pengajian_senenan[index_rotasi_senin(tgl_senin)]

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
    st.dataframe(pd.DataFrame(agenda_tetap, columns=["Kegiatan", "Hari", "Waktu", "Tempat"]), use_container_width=True)

    st.divider()
    st.subheader("👥 Pengurus Inti DKM")
    p1, p2, p3, p4 = st.columns(4)
    p1.info("Ketua DKM\n\nAang Deden Kasyful Anwar")
    p2.info("Wakil Ketua\n\nIden Tazuni")
    p3.info("Sekretaris\n\nUstadz Ihin")
    p4.info("Bendahara\n\nAceng Abdul Roup")

    st.divider()
    st.subheader("📢 Pengumuman Terbaru")
    if pengumuman_df.empty:
        st.info("Belum ada pengumuman.")
    else:
        st.dataframe(pengumuman_df.tail(5), use_container_width=True)

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

# =========================
# INPUT KAS
# =========================
elif menu == "💰 Input Kas":
    st.subheader("💰 Input Kas Admin")
    with st.form("form_kas"):
        c1, c2, c3 = st.columns(3)
        tanggal = c1.date_input("Tanggal", date.today())
        jenis = c2.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = c3.selectbox("Kategori", ["Infaq Jumat", "Kotak Amal", "Donatur", "Pembangunan", "Listrik", "Kebersihan", "Perlengkapan", "Lainnya"])
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

# =========================
# LAPORAN KAS
# =========================
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

# =========================
# DATA JAMAAH
# =========================
elif menu == "👥 Data Jamaah":
    st.subheader("👥 Data Jamaah")
    df = load_jamaah()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Jamaah", len(df))
    c2.metric("Laki-laki", len(df[df["JenisKelamin"] == "Laki-laki"]))
    c3.metric("Perempuan", len(df[df["JenisKelamin"] == "Perempuan"]))
    c4.metric("Khusus", len(df[df["Aktif"] == "Khusus"]))

    st.dataframe(df, use_container_width=True)

    st.divider()
    st.markdown("### ➕ Tambah Jamaah")
    with st.form("form_tambah_jamaah"):
        nama = st.text_input("Nama Jamaah")
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        nowa = st.text_input("Nomor WhatsApp", placeholder="Contoh: 0857xxxx atau 62857xxxx")
        aktif = st.selectbox("Status", ["Ya", "Tidak", "Khusus"])
        catatan = st.text_input("Catatan", value="-")
        simpan_jamaah = st.form_submit_button("💾 Simpan Jamaah")

    if simpan_jamaah:
        if nama.strip() == "" or nowa.strip() == "":
            st.warning("Nama dan nomor WhatsApp wajib diisi.")
        else:
            baru = pd.DataFrame([{"Nama": nama, "JenisKelamin": jk, "NoWA": normalisasi_wa(nowa), "Aktif": aktif, "Catatan": catatan}])
            df = pd.concat([df, baru], ignore_index=True)
            save_jamaah(df)
            st.success("Data jamaah berhasil ditambahkan.")
            st.rerun()

# =========================
# PENGURUS
# =========================
elif menu == "👥 Pengurus DKM":
    st.subheader("👥 Struktur Pengurus DKM")
    for jabatan, daftar_nama in pengurus.items():
        with st.expander(jabatan, expanded=jabatan in ["Ketua DKM", "Wakil Ketua", "Sekretaris", "Bendahara"]):
            for nama in daftar_nama:
                st.write(f"- {nama}")

# =========================
# JADWAL
# =========================
elif menu == "📅 Jadwal Pengajian":
    st.subheader("📅 Jadwal Pengajian Lengkap")
    df_jadwal = pd.DataFrame([
        ["Pengajian Malam Rabu", "Selasa malam Rabu", "19:30 - 21:30 WIB", "Ihin → Nanang → Jujun → Aang Deden", "Madrasah Al-Falah"],
        ["Pengajian Senenan", "Senin pagi", "07:30 - 09:00 WIB", "Nanang → Aang Deden → Ihin → Ihin", "Madrasah Al-Falah"],
        ["Syahriahan Sholawat", "Malam Jumat awal bulan Hijriah", "20:00 - 21:30 WIB", "Aang Deden Kasyful Anwar", "Masjid Jami Al-Falah"],
    ], columns=["Kegiatan", "Hari", "Waktu", "Rotasi/Pengisi", "Tempat"])
    st.dataframe(df_jadwal, use_container_width=True)

# =========================
# PENGUMUMAN
# =========================
elif menu == "📢 Pengumuman":
    st.subheader("📢 Buat Pengumuman")
    with st.form("form_pengumuman"):
        judul = st.text_input("Judul Pengumuman")
        isi = st.text_area("Isi Pengumuman")
        simpan = st.form_submit_button("💾 Simpan Pengumuman")
    if simpan:
        data = pd.DataFrame([{"Tanggal": str(date.today()), "Judul": judul, "Isi": isi}])
        pengumuman_df = pd.concat([pengumuman_df, data], ignore_index=True)
        save_pengumuman(pengumuman_df)
        st.success("Pengumuman berhasil disimpan.")
    if not pengumuman_df.empty:
        st.dataframe(pengumuman_df, use_container_width=True)

# =========================
# SHARE WHATSAPP
# =========================
elif menu == "📲 Share WhatsApp":
    st.subheader("📲 Share WhatsApp Jamaah")
    df = load_jamaah()

    jenis_share = st.selectbox("Pilih Jenis Pengumuman", ["Pengajian Senenan", "Pengajian Malam Rabu", "Syahriahan Sholawat", "Pengumuman Bebas"])

    if jenis_share == "Pengajian Senenan":
        pengisi = st.selectbox("Pengisi", ["Aang Deden Kasyful Anwar", "Ustadz Ihin", "Ustadz Nanang"])
        teks = buat_pesan_senenan(pengisi)
        target = df[(df["JenisKelamin"] == "Perempuan") & (df["Aktif"] == "Ya")]

    elif jenis_share == "Pengajian Malam Rabu":
        pengisi = st.selectbox("Pengisi", ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden Kasyful Anwar"])
        teks = buat_pesan_malam_rabu(pengisi)
        target = df[(df["JenisKelamin"] == "Laki-laki") & (df["Aktif"] == "Ya")]
        if pengisi == "Aang Deden Kasyful Anwar":
            khusus = df[df["Nama"].str.lower().str.contains("aang deden", na=False)]
            target = pd.concat([target, khusus]).drop_duplicates(subset=["NoWA"])

    elif jenis_share == "Syahriahan Sholawat":
        teks = buat_pesan_syahriahan()
        target = df[df["Aktif"].isin(["Ya", "Khusus"])]

    else:
        teks = st.text_area("Teks Pengumuman Bebas", value="""Assalamu'alaikum Warahmatullahi Wabarakatuh.

Pengumuman Masjid Jami Al-Falah.

Silakan lihat informasi terbaru melalui:
https://kas-masjid-alfalah.streamlit.app

Pesan ini dikirim melalui Al-Falah Digital.""", height=220)
        target_opsi = st.selectbox("Target", ["Semua", "Laki-laki", "Perempuan"])
        if target_opsi == "Laki-laki":
            target = df[(df["JenisKelamin"] == "Laki-laki") & (df["Aktif"] == "Ya")]
        elif target_opsi == "Perempuan":
            target = df[(df["JenisKelamin"] == "Perempuan") & (df["Aktif"] == "Ya")]
        else:
            target = df[df["Aktif"].isin(["Ya", "Khusus"])]

    st.markdown("### 📝 Isi Pesan")
    teks = st.text_area("Pesan siap kirim", value=teks, height=300)

    st.markdown(f"### 🎯 Target Penerima: {len(target)} Jamaah")
    st.dataframe(target[["Nama", "JenisKelamin", "NoWA", "Aktif"]], use_container_width=True)

    if st.button("🔔 Kirim Ringkasan ke Telegram Admin"):
        pesan_admin = f"""🕌 <b>RINGKASAN SHARE WHATSAPP AL-FALAH</b>

Jenis: {jenis_share}
Jumlah Target: {len(target)} jamaah
Waktu: {waktu_wib().strftime('%d-%m-%Y %H:%M')} WIB

Pesan sudah disiapkan di aplikasi Al-Falah Digital."""
        if kirim_telegram(pesan_admin):
            st.success("Ringkasan berhasil dikirim ke Telegram admin.")
        else:
            st.warning("Telegram belum terkirim. Cek TELEGRAM_BOT_TOKEN di Secrets.")

    st.warning("Untuk keamanan WhatsApp, pengiriman masih dibuka satu per satu. Ini mengurangi risiko nomor dianggap spam.")

    for _, row in target.iterrows():
        st.link_button(
            f"📱 Kirim ke {row['Nama']}",
            link_wa_nomor(row["NoWA"], teks),
            use_container_width=True,
        )

st.divider()
st.caption("Al-Falah Digital V13 Premium | Masjid Jami Al-Falah | Transparansi, Amanah, dan Kemakmuran Masjid")
