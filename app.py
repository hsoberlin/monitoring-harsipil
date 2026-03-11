import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from datetime import datetime
import json

# 1. Konfigurasi Halaman & Tema Mobile-App
st.set_page_config(page_title="Portfolio Pemeliharaan Sipil", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; background-color: #f8fafc !important; color: #0f172a !important; }
    
    /* Styling Dropdown Multi-Project */
    .project-selector-container { background-color: #1e3a8a; padding: 15px; border-radius: 12px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .project-selector-title { color: #ffffff; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 16px !important; color: #0f172a !important; cursor: pointer !important; }
    
    .app-header { background-color: #ffffff !important; padding: 15px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px; text-align: center; border: 1px solid #e2e8f0; }
    .app-title { color: #0f172a !important; font-size: 16px; font-weight: 700; margin-bottom: 4px; letter-spacing: -0.5px; line-height: 1.3; }
    .app-subtitle { color: #475569 !important; font-size: 11px; font-weight: 600; }
    
    .metric-container { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 15px; }
    .metric-card { flex: 1; background-color: #ffffff !important; padding: 12px 5px; border-radius: 10px; border: 1px solid #cbd5e1; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .metric-card.normal { border-top: 4px solid #3b82f6; }
    .metric-card.alert { border-top: 4px solid #ef4444; }
    .metric-label { font-size: 9px; color: #475569 !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-val { font-size: 18px; font-weight: 800; color: #0f172a !important; margin-top: 4px; }
    
    .streamlit-expanderHeader { background-color: #ffffff !important; color: #1e3a8a !important; font-size: 14px !important; font-weight: 700 !important; border-radius: 8px; border: 1px solid #e2e8f0; }
    div[data-testid="stExpanderDetails"] { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #e2e8f0; border-top: none; padding: 10px; border-radius: 0 0 8px 8px; }
    
    .stTable { font-size: 12px !important; background-color: #ffffff !important; }
    th { background-color: #e2e8f0 !important; color: #0f172a !important; font-weight: 700 !important; border-bottom: 2px solid #cbd5e1 !important; }
    td { background-color: #ffffff !important; color: #0f172a !important; border-bottom: 1px solid #e2e8f0 !important; padding: 8px !important; }
    
    header { display: none !important; } #MainMenu { display: none !important; } footer { display: none !important; }
    
    /* Signature Area Vertikal (Tanpa Singkatan) */
    .sign-container { 
        display: block; 
        text-align: center; 
        font-size: 10px; 
        color: #475569 !important; 
        margin-top: 25px; 
        padding-top: 15px; 
        border-top: 1px solid #cbd5e1; 
    }
    .sign-box { margin-bottom: 25px; font-weight: 700; line-height: 1.4; }
    </style>
""", unsafe_allow_html=True)

try:
    kredensial = json.loads(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(kredensial)
    
    # DAFTAR PROJECT (Silakan tambahkan file baru di sini)
    DAFTAR_PROJECT = {
        "Pekerjaan Saluran Ubrug Tahap Dua": "Master Data Project - Sipil Pemeliharaan PLN IP UBP SGL",
        "Proyek Jembatan Cikuya": "File Spreadsheet Cikuya",
        "Proyek Bendungan": "File Spreadsheet Bendungan"
    }

    # UI Dropdown Pemilihan Project
    st.markdown("<div class='project-selector-container'><div class='project-selector-title'>DAFTAR PROYEK PEMELIHARAAN SIPIL</div>", unsafe_allow_html=True)
    selected_project = st.selectbox("", list(DAFTAR_PROJECT.keys()), label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    try:
        sh = gc.open(DAFTAR_PROJECT[selected_project])
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"File '{DAFTAR_PROJECT[selected_project]}' tidak ditemukan. Pastikan nama file di Google Sheets sesuai dan sudah dibagikan (share) ke email Service Account.")
        st.stop()

    def get_df(name):
        return pd.DataFrame(sh.worksheet(name).get_all_records())

    # Load Data
    df_master = get_df("DATA_MASTER_PROYEK")
    df_progress = get_df("PROGRESS_GLOBAL")
    df_realisasi = get_df("REALISASI_PEKERJAAN")
    df_qc = get_df("QUALITY_CONTROL_DAN_TEMUAN")
    df_rencana = get_df("RENCANA_MINGGU_DEPAN")
    df_admin = get_df("STATUS_APPROVAL_ADMINISTRASI")

    if not df_master.empty:
        m = df_master.iloc[0]
        st.markdown(f"""
        <div class="app-header">
            <div class="app-title">{m['Nama_Pekerjaan']}</div>
            <div class="app-subtitle">
                Nomor Kontrak: {m['No_Kontrak']} <br> Target Selesai: {m['Target_Selesai']} | Update: {datetime.now().strftime('%d %B %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not df_progress.empty:
        p = df_progress.iloc[-1]
        dev_val = float(str(p['Deviasi_Persen']).replace('%',''))
        alert_class = "alert" if dev_val < 0 else "normal"
        color_val = "#ef4444" if dev_val < 0 else "#10b981"
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card normal"><div class="metric-label">Rencana</div><div class="metric-val">{p['Rencana_Persen']}%</div></div>
            <div class="metric-card normal"><div class="metric-label">Aktual</div><div class="metric-val">{p['Aktual_Persen']}%</div></div>
            <div class="metric-card {alert_class}"><div class="metric-label">Deviasi</div><div class="metric-val" style="color: {color_val};">{p['Deviasi_Persen']}%</div></div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_progress['Minggu_Ke'], y=df_progress['Rencana_Persen'], name='Rencana', line=dict(color='#3b82f6', width=3), mode='lines+markers', marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=df_progress['Minggu_Ke'], y=df_progress['Aktual_Persen'], name='Aktual', line=dict(color='#ef4444', width=3), mode='lines+markers', marker=dict(size=8)))
        
        fig.update_layout(
            height=220, margin=dict(l=10, r=10, t=5, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11, color='#0f172a')),
            xaxis=dict(tickfont=dict(size=10, color='#0f172a')), yaxis=dict(tickfont=dict(size=10, color='#0f172a'))
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    with st.expander("1. REALISASI PEKERJAAN", expanded=True):
        if not df_realisasi.empty: st.table(df_realisasi)
    with st.expander("2. QUALITY CONTROL DAN TEMUAN"):
        if not df_qc.empty: st.table(df_qc)
    with st.expander("3. RENCANA KERJA MINGGU DEPAN"):
        if not df_rencana.empty: st.table(df_rencana)
    with st.expander("4. STATUS ADMINISTRASI DAN PENAGIHAN"):
        if not df_admin.empty: st.table(df_admin)

    # AREA TANDA TANGAN TANPA SINGKATAN
    st.markdown("""
        <div class="sign-container">
            <div class="sign-box">PT Solusi Paripurna Indonesia<br><br><br>(____________________)</div>
            <div class="sign-box">PT PLN (Persero) Pusat Manajemen Proyek<br><br><br>(____________________)</div>
            <div class="sign-box">PT PLN Indonesia Power Unit Bisnis Pembangkitan Saguling<br><br><br>(____________________)</div>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Sistem Gagal Memuat Data. Detail Error: {e}")
