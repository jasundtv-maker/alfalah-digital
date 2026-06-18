import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime, timedelta
import os
import urllib.parse
import requests
import json
import gspread
from google.oauth2.service_account import Credentials

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="APP AL-FALAH", page_icon="🕌", layout="wide")

# --- CSS SOFT ELEGANT ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stApp { background-color: #F8F9F7; color: #2D3436; }
    
    /* Card Mewah */
    .glass-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .luxury-title {
        color: #064E3B;
        font-weight: 800;
        font-size: 32px;
        text-align: center;
        border-bottom: 3px solid #D4AF37;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    
    div.stButton > button {
        border-radius: 12px !important;
        border: none !important;
        background: #064E3B !important;
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI UTAMA ---
def rupiah(angka):
    return "Rp {:,.0f}".format(float(angka)).replace(",", ".")

def main():
    st.markdown('<div class="luxury-title">🕌 MASJID JAMI AL-FALAH</div>', unsafe_allow_html=True)
    
    # Sidebar
    mode = st.sidebar.radio("Mode Aplikasi", ["👥 Jamaah", "🔐 Admin"])
    menu = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Kas Masjid", "📅 Jadwal Pengajian"])

    if menu == "🏠 Dashboard":
        st.markdown('<div class="glass-card"><h3>Selamat Datang, Jamaah</h3><p>Informasi terkini Masjid Jami Al-Falah.</p></div>', unsafe_allow_html=True)
        
        # Contoh Metric yang elegan
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo Kas", "Rp 9.301.000")
        c2.metric("Kas Madrasah", "Rp 469.000")
        c3.metric("Iuran Rajaban", "Rp 700.000")
        
    elif menu == "📅 Jadwal Pengajian":
        st.subheader("Jadwal Pengajian")
        st.markdown("""
        <div class="glass-card">
            <h4>📖 Pengajian Malam Rabu</h4>
            <p>Waktu: 19:30 - 21:30 WIB | Pengisi: Ustadz Nanang</p>
        </div>
        """, unsafe_allow_html=True)

# --- EKSEKUSI ---
if __name__ == "__main__":
    main()
