from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="FVE 3D Smart Home", layout="wide", initial_sidebar_state="collapsed")

# --- PRÉMIOVÝ DARK MODE ---
st.markdown("""
<style>
.stApp { background: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 100%); }
.stMarkdown, .stText, h1, h2, h3, h4, h5, h6, span, label, p { color: #f8fafc !important; }
div[data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px);
    border: 1px solid rgba(148, 163, 184, 0.15); padding: 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}
div[data-testid="stMetricValue"] div { color: #38bdf8 !important; font-weight: 800 !important; text-shadow: 0 0 10px rgba(56, 189, 248, 0.3); }
.power-card {
    padding: 16px 22px; border-radius: 14px; margin-bottom: 15px; font-size: 16px; font-weight: 600; display: flex;
    justify-content: space-between; align-items: center; background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(8px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.4); border: 1px solid rgba(148,163,184,0.15); transition: transform 0.2s ease;
}
.power-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.6); }
.c-fve { border-left: 5px solid #fbbf24; } .c-dum { border-left: 5px solid #ef4444; }
.c-sit-out { border-left: 5px solid #10b981; } .c-sit-in { border-left: 5px solid #f59e0b; }
.val { font-size: 20px; font-weight: 900; }
.legend-box { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148,163,184,0.15); padding: 20px; border-radius: 14px; margin-top: 15px; }
.leg-row { display: flex; align-items: center; margin-bottom: 15px; }
.leg-dot { width: 18px; height: 18px; border-radius: 50%; margin-right: 15px; border: 2px solid white; box-shadow: 0 0 8px rgba(255,255,255,0.4); }
.dot-green { background-color: #10b981; box-shadow: 0 0 10px #10b981; }
.dot-orange { background-color: #f59e0b; box-shadow: 0 0 10px #f59e0b; }
.dot-off { background-color: transparent; border: 2px dashed #64748b; box-shadow: none; }
.leg-text { font-size: 15px; line-height: 1.2; } .leg-sub { font-size: 12px; color: #94a3b8; }
.stRadio > div { background: rgba(15,23,42,0.8); padding: 10px; border-radius: 10px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

st.title("🏡 3D Digitální Dvojče: FVE Domácnost")

# --- INICIALIZACE ČASU PRO AUTOMATICKÉ PŘETÁČENÍ ---
if 'slider_cas' not in st.session_state:
    st.session_state.slider_cas = "12:00"

# --- NAČÍTÁNÍ DAT ---
BASE_DIR = Path(__file__).parent
excel_candidates = [
    BASE_DIR / "projekt-FVE-domacnost4_3.xlsx", 
    BASE_DIR / "projekt-FVE-domacnost4_2.xlsx", 
    BASE_DIR / "projekt-FVE-domacnost4.xlsx"
]
EXCEL_PATH = next((p for p in excel_candidates if p.exists()), None)
if EXCEL_PATH is None:
    st.error("Excelový soubor nebyl nalezen. Ujistěte se, že je uložen ve stejné složce jako app.py.")
    st.stop()

@st.cache_data
def load_data(file_path, sheet_b, sheet_d):
    df_b = pd.read_excel(file_path, sheet_name=sheet_b, skiprows=[1]).iloc[:96].copy()
    df_d = pd.read_excel(file_path, sheet_name=sheet_d).iloc[:96].copy()
    df_b.columns = [str(c).strip() for c in df_b.columns]
    df_d.columns = [str(c).strip() for c in df_d.columns]
    
    if 'Plynový kotel + ohřev vody + topení' in df_d.columns:
        df_d = df_d.rename(columns={'Plynový kotel + ohřev vody + topení': 'Elektrický kotel + ohřev vody + topení'})
        
    soc_col_name = next((col for col in ['Soc', 'Soc %', 'Soc  %'] if col in df_b.columns), None)
            
    times = [t.strftime("%H:%M") if hasattr(t, 'strftime') else str(t)[:5] for t in df_b['Čas']]
    df_b['Čas_zobrazeni'] = times; df_d['Čas_zobrazeni'] = times
    cols_to_numeric = ['Spotřeba', 'Přímá vlastní spotřeba z FVE', 'Výroba FVE', 'Odběr z DS', 'Přetok do DS', 'Spotřeba z baterie', 'Stav baterie']
    if soc_col_name: cols_to_numeric.append(soc_col_name)
    for col in cols_to_numeric:
        if col in df_b.columns: df_b[col] = pd.to_numeric(df_b[col], errors='coerce').fillna(0)
    return df_b, df_d, soc_col_name

# --- BOČNÍ PANEL (NASTAVENÍ) ---
st.sidebar.header("⚙️ Nastavení Simulace")
obdobi = st.sidebar.selectbox("Vyberte období:", ["Leden (pracovní den)", "Leden (víkend)", "Červenec (pracovní den)", "Červenec (víkend)", "Říjen (pracovní den)", "Říjen (víkend)"])

sheet_map = {
    "Leden (pracovní den)": ("Leden", "Leden data"), "Leden (víkend)": ("Leden vík", "Leden vík data"),
    "Červenec (pracovní den)": ("Červenec", "Červenec data"), "Červenec (víkend)": ("Červenec vík", "Červenec vík data"),
    "Říjen (pracovní den)": ("Říjen", "Říjen data"), "Říjen (víkend)": ("Říjen vík", "Říjen vík data"),
}
sheet_bal, sheet_data = sheet_map[obdobi]

df_bal, df_app, soc_col_name = load_data(EXCEL_PATH, sheet_bal, sheet_data)

st.sidebar.markdown("---")
vrstva_zobrazeni = st.sidebar.radio("👁️ 3D Pohled:", ("Interiér a spotřebiče", "Střecha a Jihovýchodní FVE"))

# --- PŘÍPRAVA SEZNAMU SPOTŘEBIČŮ PRO FILTR ---
ignore_cols = ['Datum', 'Čas', 'Spotřeba domácnosti', 'Čas_zobrazeni']
appliance_cols = [c for c in df_app.columns if c not in ignore_cols and not c.startswith('Unnamed')]
df_app_unique = df_app.loc[:, ~df_app.columns.duplicated()]

active_appliances = []
for c in appliance_cols:
    if c in df_app_unique.columns:
        if pd.to_numeric(df_app_unique[c], errors='coerce').fillna(0).sum() > 0: 
            active_appliances.append(c)

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Zobrazení spotřebičů")
vybrane_spotrebice = st.sidebar.multiselect(
    "Vyberte, co chcete vidět v modelu a grafech:", 
    options=active_appliances, 
    default=active_appliances
)

# --- VYHLEDÁVAČ A SKOK V ČASE NA KONKRÉTNÍ SPOTŘEBIČ ---
st.sidebar.markdown("---")
st.sidebar.header("🔌 Spotřebiče")
hledany_spotrebic = st.sidebar.selectbox("Vyhledat a skočit na čas zapnutí:", ["(Nevybráno)"] + active_appliances)

if hledany_spotrebic != "(Nevybráno)":
    s_data = pd.to_numeric(df_app_unique[hledany_spotrebic], errors='coerce').fillna(0)
    aktivni_casy = s_data[s_data > 0]
    
    if not aktivni_casy.empty:
        st.sidebar.markdown(f"*Nalezeno {len(aktivni_casy)} úseků, kdy je {hledany_spotrebic} zapnutý:*")
        
        def skocit_v_case(novy_cas):
            st.session_state.slider_cas = novy_cas
            
        # Projdeme všechny aktivní časy a pro každý vytvoříme tlačítko
        for idx, val in aktivni_casy.items():
            cas_skoku = df_bal.loc[idx, 'Čas_zobrazeni']
            st.sidebar.button(
                f"⏱️ {cas_skoku} ({val*4:.3f} kW)", 
                key=f"btn_skok_{hledany_spotrebic}_{cas_skoku}",
                on_click=skocit_v_case, 
                args=(cas_skoku,)
            )
    else:
        st.sidebar.info("Tento spotřebič se ve vybraný den nezapíná.")

# --- HLAVNÍ METRIKY ---
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("☀ Výroba FVE", f"{df_bal['Výroba FVE'].sum():.1f} kWh")
c2.metric("🏠 Spotřeba domu", f"{df_bal['Spotřeba'].sum():.1f} kWh")
c3.metric("🔌 Odběr ze sítě", f"{df_bal['Odběr z DS'].sum():.1f} kWh")
c4.metric("⚡ Přetoky do sítě", f"{df_bal['Přetok do DS'].sum():.1f} kWh")
c5.metric("🔋 Baterie (na konci)", f"{df_bal['Stav baterie'].iloc[-1]:.1f} kWh")
st.markdown("---")

st.markdown("### ⏱️ Stroj Času (Interaktivní 3D Dvojče)")
# PROPOJENÍ POSUVNÍKU SE SESSION_STATE
zvoleny_cas = st.select_slider("Posunem sledujte změny v domě v čase:", options=df_bal['Čas_zobrazeni'].tolist(), key="slider_cas")
idx = df_bal[df_bal['Čas_zobrazeni'] == zvoleny_cas].index[0]
radek_bal = df_bal.iloc[idx]
radek_app = df_app.iloc[idx]

bere_ze_site = radek_bal['Odběr z DS'] > 0
aktivni_barva = "#f59e0b" if bere_ze_site else "#10b981" 
aktualni_fve_kw = radek_bal['Výroba FVE'] * 4
aktualni_baterie_kwh = radek_bal['Stav baterie']
soc = radek_bal[soc_col_name] * 100 if soc_col_name and radek_bal[soc_col_name] <= 1.0 else (aktualni_baterie_kwh / 20.0) * 100

try:
    hodina = int(str(zvoleny_cas).split(':')[0])
except ValueError:
    hodina = 12

col_leg, col_mapa, col_budiky = st.columns([0.7, 2.3, 1.0])

with col_leg:
    st.markdown("<h4 style='margin-bottom: 0px;'>Barevná legenda</h4>", unsafe_allow_html=True)
    if vrstva_zobrazeni == "Interiér a spotřebiče":
        st.markdown("""
        <div class="legend-box">
            <div class="leg-row"><div class="leg-dot dot-green"></div><div class="leg-text"><b>FVE / Baterie</b><br><span class="leg-sub">Dům je soběstačný</span></div></div>
            <div class="leg-row"><div class="leg-dot dot-orange"></div><div class="leg-text"><b>Ze sítě (DS)</b><br><span class="leg-sub">Dům nakupuje elektřinu</span></div></div>
            <div class="leg-row" style="margin-bottom:0;"><div class="leg-dot dot-off"></div><div class="leg-text"><b>Vypnuto</b><br><span class="leg-sub">Bez odběru</span></div></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="legend-box">
            <div class="leg-row"><div class="leg-dot dot-green"></div><div class="leg-text"><b>Panely vyrábí</b><br><span class="leg-sub">Aktivní solární produkce</span></div></div>
            <div class="leg-row" style="margin-bottom:0;"><div class="leg-dot dot-off" style="border-color:#1e3a5f;"></div><div class="leg-text"><b>Nesvítí (Noc)</b><br><span class="leg-sub">Výroba 0 kW</span></div></div>
        </div>
        """, unsafe_allow_html=True)

with col_mapa:
    fig_3d = go.Figure()
    
    fig_3d.add_trace(go.Mesh3d(x=[-5, 25, 25, -5], y=[-5, -5, 20, 20], z=[-0.1, -0.1, -0.1, -0.1], color='#064e3b', opacity=0.4, hoverinfo='skip', showscale=False))
    
    kompas_opac = 1.0 if vrstva_zobrazeni != "Interiér a spotřebiče" else 0.0
    fig_3d.add_trace(go.Scatter3d(x=[-2, 22], y=[7.5, 7.5], z=[-0.05, -0.05], mode='lines', line=dict(color=f'rgba(255,255,255,{kompas_opac})', width=2), hoverinfo='skip'))
    fig_3d.add_trace(go.Scatter3d(x=[10, 10], y=[-2, 17], z=[-0.05, -0.05], mode='lines', line=dict(color=f'rgba(255,255,255,{kompas_opac})', width=2), hoverinfo='skip'))
    fig_3d.add_trace(go.Scatter3d(x=[10, 10, 23, -3], y=[-3, 18, 7.5, 7.5], z=[0, 0, 0, 0], mode='text', text=['<b>JIH (S)</b>', '<b>SEVER (N)</b>', '<b>VÝCHOD (E)</b>', '<b>ZÁPAD (W)</b>'], textfont=dict(color=f'rgba(56,189,248,{kompas_opac})', size=14, family="Arial Black"), hoverinfo='skip'))

    Z_WALL = 1.8

    if vrstva_zobrazeni == "Interiér a spotřebiče":
        rooms = [
            {"name": "Obývací pokoj", "x0": 0, "y0": 10, "x1": 8, "y1": 15}, {"name": "Kuchyně",       "x0": 8, "y0": 10, "x1": 15, "y1": 15},
            {"name": "Koupelna 2",    "x0": 15,"y0": 10, "x1": 20, "y1": 15}, {"name": "Pokoj 1",       "x0": 0, "y0": 5, "x1": 6, "y1": 10},
            {"name": "Chodba",        "x0": 6, "y0": 5, "x1": 15, "y1": 10}, {"name": "Pokoj 2",       "x0": 15,"y0": 5, "x1": 20, "y1": 10},
            {"name": "Koupelna 1",    "x0": 0, "y0": 0, "x1": 5, "y1": 5}, {"name": "Tech. místnost","x0": 5, "y0": 0, "x1": 10, "y1": 5},
            {"name": "Pokoj 3",       "x0": 10,"y0": 0, "x1": 20, "y1": 5},
        ]
        for r in rooms:
            fig_3d.add_trace(go.Mesh3d(x=[r["x0"], r["x1"], r["x1"], r["x0"]], y=[r["y0"], r["y0"], r["y1"], r["y1"]], z=[0, 0, 0, 0], color='#334155', opacity=0.8, hoverinfo='skip'))
            xl = [r["x0"], r["x1"], r["x1"], r["x0"], r["x0"], r["x0"], r["x1"], r["x1"], r["x1"], r["x1"], r["x1"], r["x0"], r["x0"], r["x0"]]
            yl = [r["y0"], r["y0"], r["y1"], r["y1"], r["y0"], r["y0"], r["y0"], r["y0"], r["y1"], r["y1"], r["y1"], r["y1"], r["y1"], r["y0"]]
            zl = [0, 0, 0, 0, 0, Z_WALL, Z_WALL, 0, 0, Z_WALL, Z_WALL, Z_WALL, 0, Z_WALL]
            fig_3d.add_trace(go.Scatter3d(x=xl, y=yl, z=zl, mode='lines', line=dict(color='#94a3b8', width=2), showlegend=False, hoverinfo='skip'))
            fig_3d.add_trace(go.Scatter3d(x=[(r["x0"]+r["x1"])/2], y=[(r["y0"]+r["y1"])/2], z=[0.1], mode='text', text=[r["name"]], textfont=dict(color="#94a3b8", size=10), showlegend=False, hoverinfo='skip'))

        b_x, b_y = 9.0, 3.5
        b_w, b_h = 0.8, 0.8
        max_bat_height = 1.4
        current_bat_height = max(0.1, (soc / 100) * max_bat_height)
        bat_color = "#ef4444" if soc <= 5.5 else ("#f59e0b" if soc <= 10.5 else "#10b981")
        
        b_xs = [b_x, b_x+b_w, b_x+b_w, b_x, b_x, b_x+b_w, b_x+b_w, b_x]
        b_ys = [b_y, b_y, b_y+b_h, b_y+b_h, b_y, b_y, b_y+b_h, b_y+b_h]
        b_zs = [0, 0, 0, 0, max_bat_height, max_bat_height, max_bat_height, max_bat_height]
        fig_3d.add_trace(go.Mesh3d(x=b_xs, y=b_ys, z=b_zs, color='#94a3b8', opacity=0.1, alphahull=0, hoverinfo='skip'))
        
        fill_zs = [0, 0, 0, 0, current_bat_height, current_bat_height, current_bat_height, current_bat_height]
        fig_3d.add_trace(go.Mesh3d(x=b_xs, y=b_ys, z=fill_zs, color=bat_color, opacity=0.9, alphahull=0, hovertemplate=f"<b>Fyzická Baterie</b><br>Nabití: {soc:.1f}%<extra></extra>"))
        fig_3d.add_trace(go.Scatter3d(x=[b_x, b_x+b_w, b_x+b_w, b_x, b_x, b_x, b_x+b_w, b_x+b_w, b_x+b_w, b_x+b_w, b_x, b_x], y=[b_y, b_y, b_y+b_h, b_y+b_h, b_y, b_y, b_y, b_y, b_y+b_h, b_y+b_h, b_y+b_h, b_y+b_h], z=[0, 0, 0, 0, 0, max_bat_height, max_bat_height, 0, 0, max_bat_height, max_bat_height, 0], mode='lines', line=dict(color='#ffffff', width=2), hoverinfo='skip'))
        fig_3d.add_trace(go.Scatter3d(x=[b_x + b_w/2], y=[b_y + b_h/2], z=[max_bat_height + 0.3], mode='text', text=[f"<b>{soc:.0f}%</b>"], textfont=dict(color=bat_color, size=15, family="Arial Black"), hoverinfo='skip'))

        kotel_col = 'Elektrický kotel + ohřev vody + topení'
        appliances_map = {
            'Televize': {'label': 'TV', 'pos': (2.5, 12.5)}, 'Elektrické žaluzie': {'label': 'Žaluzie', 'pos': (5.5, 12.5)},
            'Myčka': {'label': 'Myčka', 'pos': (9.5, 13.5)}, 'Elektrický sporák': {'label': 'Sporák', 'pos': (11.5, 13.5)},
            'Mikrovlnka': {'label': 'Mikrovlnka', 'pos': (13.5, 13.5)}, 'Kávovar': {'label': 'Kávovar', 'pos': (9.5, 11)},
            'Elektrická trouba': {'label': 'Trouba', 'pos': (11.5, 11)}, 'Topinkovač': {'label': 'Topinkovač', 'pos': (13.5, 11)},
            'Tablet': {'label': 'Tablet', 'pos': (2, 7.5)}, 'Počítače': {'label': 'PC', 'pos': (4, 7.5)}, 
            'Vysavač': {'label': 'Vysavač', 'pos': (10.5, 7.5)}, 'Notebook': {'label': 'Notebook', 'pos': (17.5, 7.5)}, 
            'Radio': {'label': 'Rádio', 'pos': (2.5, 2.5)}, 'Pračka': {'label': 'Pračka', 'pos': (6.5, 2.5)}, 
            'Sušička': {'label': 'Sušička', 'pos': (8.5, 2.5)}, 
            'Elektrický kotel': {'label': 'Kotel', 'pos': (7.5, 1.0), 'source_col': kotel_col}, 
            'Mobilní telefon': {'label': 'Mobil', 'pos': (15, 2.5)}
        }
        for r in rooms:
            appliances_map[f'Světlo ({r["name"]})'] = {'label': 'Světlo', 'pos': (r["x0"] + 1, r["y1"] - 1), 'source_col': 'Osvětlení', 'is_shared': True, 'display_name': 'Světlo'}
            if r["name"] != "Chodba":
                appliances_map[f'Topení ({r["name"]})'] = {'label': 'Topení', 'pos': (r["x1"] - 1, r["y0"] + 1), 'source_col': kotel_col, 'is_shared': True, 'display_name': 'Elektrické topení'}

        x_app, y_app, z_app, texts_app, colors_app, sizes_app, hover_app, borders_app = [], [], [], [], [], [], [], []

        for app_name, info in appliances_map.items():
            source = info.get('source_col', app_name)
            
            # Pokud uživatel vypnul spotřebič v bočním panelu, nezobrazí se v 3D
            if source not in vybrane_spotrebice:
                continue
                
            display_name = info.get('display_name', app_name)
            val = 0
            if source in df_app.columns:
                hodnota = radek_app[source]
                if isinstance(hodnota, pd.Series): val = pd.to_numeric(hodnota, errors='coerce').fillna(0).sum()
                else: val = pd.to_numeric(hodnota, errors='coerce'); val = 0 if pd.isna(val) else val
                if info.get('is_shared'): val = val / 9.0

            x_app.append(info['pos'][0]); y_app.append(info['pos'][1]); z_app.append(0.5)
            
            if val > 0.001:  
                colors_app.append(aktivni_barva); borders_app.append('white'); sizes_app.append(20 + min((val * 25), 40))
                texts_app.append(f"<b>{info['label']}</b>")
                hover_app.append(f"<b>{display_name}</b><br>ZAPNUTO: {val*4:.3f} kW")
            else:
                colors_app.append('rgba(0,0,0,0)'); borders_app.append('rgba(0,0,0,0)'); sizes_app.append(1) 
                texts_app.append('')
                hover_app.append(f"<b>{display_name}</b> (Vypnuto)")

        fig_3d.add_trace(go.Scatter3d(
            x=x_app, y=y_app, z=z_app, mode='markers+text',
            marker=dict(size=sizes_app, color=colors_app, line=dict(color=borders_app, width=2)),
            text=texts_app, textposition="top center", textfont=dict(size=14, color="#ffffff", family="Arial Black"),
            hoverinfo="text", hovertext=hover_app, showlegend=False
        ))
        
        camera_eye = dict(x=-0.8, y=-1.8, z=1.5)
        
    else:
        fig_3d.add_trace(go.Mesh3d(x=[-0.5, 20.5, 20.5, -0.5], y=[-0.5, -0.5, 7.5, 7.5], z=[Z_WALL, Z_WALL, Z_WALL+2.0, Z_WALL+2.0], color='#334155', opacity=0.9, hoverinfo='skip', showscale=False))
        fig_3d.add_trace(go.Mesh3d(x=[-0.5, 20.5, 20.5, -0.5], y=[7.5, 7.5, 15.5, 15.5], z=[Z_WALL+2.0, Z_WALL+2.0, Z_WALL, Z_WALL], color='#1e293b', opacity=0.9, hoverinfo='skip', showscale=False))
        fig_3d.add_trace(go.Scatter3d(x=[-0.5, 20.5, 20.5, -0.5, -0.5, -0.5, 20.5, 20.5, -0.5], y=[-0.5, -0.5, 15.5, 15.5, -0.5, 7.5, 7.5, 15.5, 7.5], z=[Z_WALL, Z_WALL, Z_WALL, Z_WALL, Z_WALL, Z_WALL+2.0, Z_WALL+2.0, Z_WALL, Z_WALL+2.0], mode='lines', line=dict(color='#0ea5e9', width=4), showlegend=False, hoverinfo='skip'))

        je_aktivni = aktualni_fve_kw > 0.05
        panel_color = '#10b981' if je_aktivni else '#0f172a' 
        panel_line = '#34d399' if je_aktivni else '#1e293b'
        panel_xs = [2.0, 5.5, 9.0, 12.5, 16.0] 
        panel_ys = [1.0, 4.0]     
        w, h, z_gap = 3.0, 2.5, 0.03
        
        all_corners_x, all_corners_y, all_corners_z = [], [], []
        mesh_x, mesh_y, mesh_z, mesh_i, mesh_j, mesh_k = [], [], [], [], [], []
        mesh_idx = 0
        
        for px in panel_xs:
            for py in panel_ys:
                z_bottom = Z_WALL + (py * (2.0 / 7.5)) + z_gap; z_top = Z_WALL + ((py + h) * (2.0 / 7.5)) + z_gap
                cx = [px, px+w, px+w, px]; cy = [py, py, py+h, py+h]; cz = [z_bottom, z_bottom, z_top, z_top]
                all_corners_x.extend(cx + [cx[0], None]); all_corners_y.extend(cy + [cy[0], None]); all_corners_z.extend(cz + [cz[0], None])
                mesh_x.extend(cx); mesh_y.extend(cy); mesh_z.extend(cz)
                mesh_i.extend([mesh_idx, mesh_idx]); mesh_j.extend([mesh_idx+1, mesh_idx+2]); mesh_k.extend([mesh_idx+2, mesh_idx+3])
                mesh_idx += 4

        fig_3d.add_trace(go.Scatter3d(x=all_corners_x, y=all_corners_y, z=all_corners_z, mode='lines', line=dict(color=panel_line, width=5), hoverinfo='skip', showlegend=False))
        fig_3d.add_trace(go.Mesh3d(x=mesh_x, y=mesh_y, z=mesh_z, color=panel_color, opacity=0.95, i=mesh_i, j=mesh_j, k=mesh_k, hovertemplate=f"<b>Fyzický FVE Panel</b><br>Celkový výkon pole: {aktualni_fve_kw:.2f} kW<extra></extra>", showscale=False))
        
        panel_text = f"FVE VYRÁBÍ<br>☀️ {aktualni_fve_kw:.2f} kW" if je_aktivni else ""
        fig_3d.add_trace(go.Scatter3d(x=[10], y=[3.5], z=[Z_WALL + 3.0], mode='text', text=[panel_text], textfont=dict(color="#10b981", size=18, family="Arial Black"), hoverinfo="skip", showlegend=False))
        
        camera_eye = dict(x=0.2, y=-1.8, z=1.2)

    bublina_text = ""
    bublina_barva = "#ffffff"
    
    if soc >= 90 and radek_bal['Přetok do DS'] > 0:
        bublina_text = "FVE JEDE NAPLNO.<br>Dům je soběstačný a přebytky se prodávají."
        bublina_barva = "#34d399"
    elif soc <= 10.5 and soc > 5.5 and not bere_ze_site:
        bublina_text = "POZOR: Baterie klesla na 10 %.<br>Dům jede z rezervy střídače."
        bublina_barva = "#f59e0b"
    elif soc <= 5.5:
        bublina_text = "KRITICKÝ STAV BATERIE (5 %).<br>Systém odpojen, čeká se na slunce."
        bublina_barva = "#ef4444"
    elif bere_ze_site and aktualni_fve_kw == 0 and radek_bal['Spotřeba'] * 4 > 2.0:
        typ_spicky = "RANNÍ" if hodina < 12 else "VEČERNÍ"
        bublina_text = f"{typ_spicky} ŠPIČKA!<br>Dům nakupuje drahou elektřinu ze sítě."
        bublina_barva = "#ef4444"
    elif aktualni_fve_kw > 2.0 and not bere_ze_site and soc < 90:
        bublina_text = "FVE JEDE NAPLNO.<br>Dům je soběstačný a baterie se nabíjí."
        bublina_barva = "#fbbf24"
        
    fig_3d.add_trace(go.Scatter3d(
        x=[10], y=[7.5], z=[Z_WALL + 5.5], mode='text',
        text=[f"<b>{bublina_text}</b>"] if bublina_text else [""], 
        textposition="middle center",
        textfont=dict(color=bublina_barva, size=16, family="Arial Black"), hoverinfo='skip', showlegend=False
    ))

    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, 22]), 
            yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, 17]), 
            zaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 9]), 
            camera=dict(up=dict(x=0,y=0,z=1), center=dict(x=0,y=0,z=-0.2), eye=camera_eye)
        ),
        margin=dict(l=0, r=0, t=0, b=0), 
        paper_bgcolor="rgba(0,0,0,0)", 
        height=500,
        uirevision=True  
    )
    st.plotly_chart(fig_3d, use_container_width=True)

with col_budiky:
    st.markdown(f"""
    <div class="power-card c-fve"><span>☀️ FVE vyrábí</span> <span class="val" style="color: #fbbf24;">{aktualni_fve_kw:.2f} kW</span></div>
    <div class="power-card c-dum"><span>🏠 Dům bere</span> <span class="val" style="color: #ef4444;">{radek_bal['Spotřeba'] * 4:.2f} kW</span></div>
    """, unsafe_allow_html=True)
    
    if radek_bal['Odběr z DS'] > 0: st.markdown(f"""<div class="power-card c-sit-in"><span>🌐 Nákup ze sítě</span> <span class="val" style="color: #f59e0b;">{radek_bal['Odběr z DS'] * 4:.2f} kW</span></div>""", unsafe_allow_html=True)
    else: st.markdown(f"""<div class="power-card c-sit-out"><span>💰 Do sítě</span> <span class="val" style="color: #34d399;">{radek_bal['Přetok do DS'] * 4:.2f} kW</span></div>""", unsafe_allow_html=True)
    
    barva = "#ef4444" if soc <= 5.5 else ("#f59e0b" if soc <= 10.5 else "#10b981")
    fig_bat = go.Figure(go.Indicator(
        mode="gauge+number", value=soc, number={'suffix': " %", 'font': {'size': 35, 'color': barva}},
        title={'text': f"🔋 Baterie ({radek_bal['Stav baterie']:.1f} kWh)", 'font': {'size': 18, 'color':'#f8fafc'}},
        gauge={'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': "#94a3b8"}}, 'bar': {'color': barva}, 'bgcolor': "rgba(15,23,42,0.8)", 'borderwidth': 0, 'steps': [{'range': [0, 5], 'color': "#7f1d1d"}, {'range': [5, 10], 'color': "#78350f"}, {'range': [10, 100], 'color': "#064e3b"}]}
    ))
    fig_bat.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bat, use_container_width=True)


# --- PRVNÍ GRAF: ZÁKLADNÍ TOKY ---
st.markdown("---")
st.markdown("### 📈 Denní průběh energií a spotřeby v kW")

fig_toky = go.Figure()
fig_toky.add_trace(go.Scatter(x=df_bal['Čas_zobrazeni'], y=df_bal['Výroba FVE']*4, mode='lines', name='Výroba FVE', line=dict(color='#fbbf24', width=3), fill='tozeroy', hovertemplate='%{y:.3f} kW<extra></extra>'))
fig_toky.add_trace(go.Scatter(x=df_bal['Čas_zobrazeni'], y=df_bal['Spotřeba']*4, mode='lines', name='Příkon domu', line=dict(color='#ef4444', width=3), hovertemplate='%{y:.3f} kW<extra></extra>'))
fig_toky.add_trace(go.Scatter(x=df_bal['Čas_zobrazeni'], y=df_bal['Odběr z DS']*4, mode='lines', name='Odběr ze sítě', line=dict(color='#38bdf8', width=2, dash='dash'), hovertemplate='%{y:.3f} kW<extra></extra>'))

max_y_toky = max((df_bal['Výroba FVE']*4).max(), (df_bal['Spotřeba']*4).max(), (df_bal['Odběr z DS']*4).max()) * 1.1 + 1

fig_toky.update_layout(
    title=dict(text="Základní toky (Zdroj vs Spotřeba)", font=dict(size=16, color="#e2e8f0")),
    xaxis_title="", yaxis_title="Výkon (kW)", hovermode="x unified", height=380,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
    font=dict(color="#f8fafc", size=13), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), 
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, max_y_toky]), 
    margin=dict(t=40, b=10)
)
st.plotly_chart(fig_toky, use_container_width=True)


# --- DRUHÝ GRAF: SPOTŘEBIČE ---
fig_spotrebice = go.Figure()
distinct_colors = ['#38bdf8', '#a3e635', '#f87171', '#c084fc', '#fbbf24', '#2dd4bf', '#fb7185', '#818cf8', '#fcd34d', '#34d399', '#f472b6', '#60a5fa']

# Kreslíme pouze ty, které uživatel nevypnul
for idx, app_name in enumerate(vybrane_spotrebice):
    vykon_kw = pd.to_numeric(df_app_unique[app_name], errors='coerce').fillna(0) * 4
    fig_spotrebice.add_trace(go.Bar(x=df_bal['Čas_zobrazeni'], y=vykon_kw, name=app_name, marker_color=distinct_colors[idx % len(distinct_colors)], marker_line_color='rgba(255,255,255,0.3)', marker_line_width=1, hovertemplate='<b>%{y:.3f} kW</b><extra></extra>'))

# DYNAMICKÝ ZOOM OSY Y: 
if vybrane_spotrebice:
    df_vybrane = df_app_unique[vybrane_spotrebice].apply(pd.to_numeric, errors='coerce').fillna(0)
    # Najde největší vrchol vybraných spotřebičů
    max_y_spotrebice = max(df_vybrane.sum(axis=1).max() * 4 * 1.1 + 0.05, 0.2)
else:
    max_y_spotrebice = 1.0

fig_spotrebice.update_layout(
    title=dict(text="Energetická stopa spotřebičů (Z čeho se skládá celková spotřeba domu)", font=dict(size=16, color="#e2e8f0")),
    barmode='stack', xaxis_title="Čas", yaxis_title="Příkon (kW)", hovermode="x unified", 
    height=600,
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, font=dict(size=13)),
    font=dict(color="#f8fafc", size=13), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", type='category'), 
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, max_y_spotrebice]), 
    margin=dict(t=50, r=150)
)
st.plotly_chart(fig_spotrebice, use_container_width=True)


# --- TŘETÍ GRAF: INTERAKCE SE SÍTÍ (PŘETOKY VS ODBĚR) ---
st.markdown("---")
st.markdown("### ⚡ Interakce s distribuční sítí (Nákup vs Prodej)")

fig_sit = go.Figure()

fig_sit.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'], y=df_bal['Odběr z DS']*4, 
    mode='lines', name='Nákup ze sítě', 
    line=dict(color='#ef4444', width=2), fill='tozeroy', 
    hovertemplate='<b>Nákup:</b> %{y:.3f} kW<extra></extra>'
))

fig_sit.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'], y=-df_bal['Přetok do DS']*4, 
    mode='lines', name='Prodej do sítě (Přetoky)', 
    line=dict(color='#10b981', width=2), fill='tozeroy', 
    customdata=df_bal['Přetok do DS']*4, 
    hovertemplate='<b>Prodej:</b> %{customdata:.3f} kW<extra></extra>'
))

max_y_sit = max((df_bal['Odběr z DS']*4).max() * 1.1 + 0.5, 2.0)
min_y_sit = min(-(df_bal['Přetok do DS']*4).max() * 1.1 - 0.5, -2.0)

fig_sit.update_layout(
    title=dict(text="Zrcadlová bilance: Kdy síť zatěžujeme a kdy ji naopak krmíme", font=dict(size=16, color="#e2e8f0")),
    xaxis_title="Čas", yaxis_title="Výkon (kW)", hovermode="x unified", height=350,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
    font=dict(color="#f8fafc", size=13), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", type='category'), 
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zeroline=True, zerolinecolor="rgba(255,255,255,0.4)", zerolinewidth=2, range=[min_y_sit, max_y_sit]), 
    margin=dict(t=50, b=10)
)
st.plotly_chart(fig_sit, use_container_width=True)


# --- ŽEBŘÍČEK ŽROUTŮ ENERGIE ---
st.markdown("---")
st.markdown("### 🥇 Žebříček žroutů (Celková denní spotřeba)")
sums = {c: pd.to_numeric(df_app_unique[c], errors='coerce').fillna(0).sum() for c in vybrane_spotrebice}
top_zrouti = [(name, val) for name, val in sorted(sums.items(), key=lambda x: x[1], reverse=True) if val > 0]

if top_zrouti:
    df_zrouti = pd.DataFrame(top_zrouti, columns=["Spotřebič", "Suma (kWh)"])
    df_zrouti["Suma (kWh)"] = df_zrouti["Suma (kWh)"].apply(lambda x: f"{x:.3f}")
    st.markdown(df_zrouti.to_html(index=False, classes='table table-striped', justify='left'), unsafe_allow_html=True)
    st.markdown("""<style>.table { width: 100%; color: #f8fafc; border-collapse: collapse; font-size: 16px; } .table th, .table td { padding: 10px; border-bottom: 1px solid #334155; } .table th { background-color: rgba(15,23,42,0.8); } .table-striped tbody tr:nth-of-type(odd) { background-color: rgba(30,41,59,0.3); }</style>""", unsafe_allow_html=True)