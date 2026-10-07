from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

BASE_DIR = Path(__file__).parent
excel_candidates = [
    BASE_DIR / "projekt-FVE-domacnost4_3.xlsx", 
    BASE_DIR / "projekt-FVE-domacnost4_2.xlsx", 
    BASE_DIR / "projekt-FVE-domacnost4.xlsx"
]
EXCEL_PATH = next((p for p in excel_candidates if p.exists()), None)
if EXCEL_PATH is None:
    st.error("Excelový soubor nebyl nalezen.")
    st.stop()

st.sidebar.header("⚙️ Nastavení Simulace")
obdobi = st.sidebar.selectbox("Vyberte období:", ["Leden (pracovní den)", "Leden (víkend)", "Červenec (pracovní den)", "Červenec (víkend)", "Říjen (pracovní den)", "Říjen (víkend)"])

st.sidebar.markdown("---")
vrstva_zobrazeni = st.sidebar.radio("👁️ 3D Pohled:", ("Interiér a spotřebiče", "Střecha a Jihovýchodní FVE"))

sheet_map = {
    "Leden (pracovní den)": ("Leden", "Leden data"), "Leden (víkend)": ("Leden vík", "Leden vík data"),
    "Červenec (pracovní den)": ("Červenec", "Červenec data"), "Červenec (víkend)": ("Červenec vík", "Červenec vík data"),
    "Říjen (pracovní den)": ("Říjen", "Říjen data"), "Říjen (víkend)": ("Říjen vík", "Říjen vík data"),
}
sheet_bal, sheet_data = sheet_map[obdobi]

@st.cache_data
def load_data(file_path, sheet_b, sheet_d):
    df_b = pd.read_excel(file_path, sheet_name=sheet_b, skiprows=[1]).iloc[:96].copy()
    df_d = pd.read_excel(file_path, sheet_name=sheet_d).iloc[:96].copy()
    df_b.columns = [str(c).strip() for c in df_b.columns]
    df_d.columns = [str(c).strip() for c in df_d.columns]
    soc_col_name = next((col for col in ['Soc', 'Soc %', 'Soc  %'] if col in df_b.columns), None)
    times = [t.strftime("%H:%M") if hasattr(t, 'strftime') else str(t)[:5] for t in df_b['Čas']]
    df_b['Čas_zobrazeni'] = times; df_d['Čas_zobrazeni'] = times
    cols_to_numeric = ['Spotřeba', 'Přímá vlastní spotřeba z FVE', 'Výroba FVE', 'Odběr z DS', 'Přetok do DS', 'Spotřeba z baterie', 'Stav baterie']
    if soc_col_name: cols_to_numeric.append(soc_col_name)
    for col in cols_to_numeric:
        if col in df_b.columns: df_b[col] = pd.to_numeric(df_b[col], errors='coerce').fillna(0)
    return df_b, df_d, soc_col_name

df_bal, df_app, soc_col_name = load_data(EXCEL_PATH, sheet_bal, sheet_data)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("☀ Výroba FVE", f"{df_bal['Výroba FVE'].sum():.1f} kWh")
c2.metric("🏠 Spotřeba domu", f"{df_bal['Spotřeba'].sum():.1f} kWh")
c3.metric("🔌 Odběr ze sítě", f"{df_bal['Odběr z DS'].sum():.1f} kWh")
c4.metric("⚡ Přetoky do sítě", f"{df_bal['Přetok do DS'].sum():.1f} kWh")
c5.metric("🔋 Baterie (na konci)", f"{df_bal['Stav baterie'].iloc[-1]:.1f} kWh")
st.markdown("---")

st.markdown("### ⏱️ Stroj Času (Interaktivní 3D Dvojče)")
zvoleny_cas = st.select_slider("Posunem sledujte změny v domě v čase:", options=df_bal['Čas_zobrazeni'].tolist(), value="12:00")
idx = df_bal[df_bal['Čas_zobrazeni'] == zvoleny_cas].index[0]
radek_bal = df_bal.iloc[idx]
radek_app = df_app.iloc[idx]

bere_ze_site = radek_bal['Odběr z DS'] > 0
aktivni_barva = "#f59e0b" if bere_ze_site else "#10b981" 
aktualni_fve_kw = radek_bal['Výroba FVE'] * 4

col_leg, col_mapa, col_budiky = st.columns([0.7, 2.3, 1.0])

with col_leg:
    st.markdown("<h4 style='margin-bottom: 0px;'>Barevná legenda</h4>", unsafe_allow_html=True)
    if vrstva_zobrazeni == "Interiér a spotřebiče":
        st.markdown("""
        <div class="legend-box">
            <div class="leg-row"><div class="leg-dot dot-green"></div><div class="leg-text"><b>FVE / Baterie</b><br><span class="leg-sub">Dům je zcela soběstačný</span></div></div>
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
    
    # TRÁVNÍK (Pozemek)
    fig_3d.add_trace(go.Mesh3d(
        x=[-5, 25, 25, -5], y=[-5, -5, 20, 20], z=[-0.1, -0.1, -0.1, -0.1],
        color='#064e3b', opacity=0.4, hoverinfo='skip', showscale=False 
    ))
    
    # KOMPAS NA ZEMI
    fig_3d.add_trace(go.Scatter3d(x=[-2, 22], y=[7.5, 7.5], z=[-0.05, -0.05], mode='lines', line=dict(color='white', width=2), hoverinfo='skip'))
    fig_3d.add_trace(go.Scatter3d(x=[10, 10], y=[-2, 17], z=[-0.05, -0.05], mode='lines', line=dict(color='white', width=2), hoverinfo='skip'))
    fig_3d.add_trace(go.Scatter3d(
        x=[10, 10, 23, -3], y=[-3, 18, 7.5, 7.5], z=[0, 0, 0, 0],
        mode='text', text=['<b>JIH (S)</b>', '<b>SEVER (N)</b>', '<b>VÝCHOD (E)</b>', '<b>ZÁPAD (W)</b>'],
        textfont=dict(color="#38bdf8", size=14, family="Arial Black"), hoverinfo='skip'
    ))

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

        appliances_map = {
            'Televize': {'label': 'TV', 'pos': (2.5, 12.5)}, 'Elektrické žaluzie': {'label': 'Žaluzie', 'pos': (5.5, 12.5)},
            'Myčka': {'label': 'Myčka', 'pos': (9.5, 13.5)}, 'Elektrický sporák': {'label': 'Sporák', 'pos': (11.5, 13.5)},
            'Mikrovlnka': {'label': 'Mikrovlnka', 'pos': (13.5, 13.5)}, 'Kávovar': {'label': 'Kávovar', 'pos': (9.5, 11)},
            'Elektrická trouba': {'label': 'Trouba', 'pos': (11.5, 11)}, 'Topinkovač': {'label': 'Topinkovač', 'pos': (13.5, 11)},
            'Tablet': {'label': 'Tablet', 'pos': (2, 7.5)}, 'Počítače': {'label': 'PC', 'pos': (4, 7.5)}, 
            'Vysavač': {'label': 'Vysavač', 'pos': (10.5, 7.5)}, 'Notebook': {'label': 'Notebook', 'pos': (17.5, 7.5)}, 
            'Radio': {'label': 'Rádio', 'pos': (2.5, 2.5)}, 'Pračka': {'label': 'Pračka', 'pos': (6.5, 2.5)}, 
            'Sušička': {'label': 'Sušička', 'pos': (8.5, 2.5)}, 'Plynový kotel + ohřev vody + topení': {'label': 'Kotel', 'pos': (7.5, 1.0)}, 
            'Mobilní telefon': {'label': 'Mobil', 'pos': (15, 2.5)}
        }
        for r in rooms:
            appliances_map[f'Světlo ({r["name"]})'] = {'label': 'Světlo', 'pos': (r["x0"] + 1, r["y1"] - 1), 'source_col': 'Osvětlení', 'is_shared': True}
            if r["name"] != "Chodba":
                appliances_map[f'Topení ({r["name"]})'] = {'label': 'Topení', 'pos': (r["x1"] - 1, r["y0"] + 1), 'source_col': 'Plynový kotel + ohřev vody + topení', 'is_shared': True}

        x_app, y_app, z_app, texts_app, colors_app, sizes_app, hover_app, borders_app = [], [], [], [], [], [], [], []

        for app_name, info in appliances_map.items():
            source = info.get('source_col', app_name)
            val = 0
            if source in df_app.columns:
                hodnota = radek_app[source]
                if isinstance(hodnota, pd.Series): val = pd.to_numeric(hodnota, errors='coerce').fillna(0).sum()
                else: val = pd.to_numeric(hodnota, errors='coerce'); val = 0 if pd.isna(val) else val
                if info.get('is_shared'): val = val / 9.0

            x_app.append(info['pos'][0]); y_app.append(info['pos'][1]); z_app.append(0.5)
            
            if val > 0.001:  
                colors_app.append(aktivni_barva); borders_app.append('white'); sizes_app.append(20 + min((val * 25), 40))
                texts_app.append(f"<b>{info['label']}</b>"); hover_app.append(f"<b>{app_name}</b><br>ZAPNUTO: {val*4:.3f} kW")
            else:
                colors_app.append('rgba(0,0,0,0)'); borders_app.append('rgba(0,0,0,0)'); sizes_app.append(1) 
                texts_app.append(''); hover_app.append(f"<b>{app_name}</b> (Vypnuto)")

        fig_3d.add_trace(go.Scatter3d(
            x=x_app, y=y_app, z=z_app, mode='markers+text',
            marker=dict(size=sizes_app, color=colors_app, line=dict(color=borders_app, width=2)),
            text=texts_app, textposition="top center", textfont=dict(size=14, color="#ffffff", family="Arial Black"),
            hoverinfo="text", hovertext=hover_app, showlegend=False
        ))
        camera_eye = dict(x=-0.8, y=-1.8, z=1.5)
        
    else:
        # --- ZOBRAZENÍ 2: STŘECHA A ZAROVNANÉ PANELY ---
        
        # VIDITELNĚJŠÍ STŘECHA S OSTRÝMI HRANAMI
        # Jižní svah (S) - světlejší modro-šedá
        fig_3d.add_trace(go.Mesh3d(
            x=[-0.5, 20.5, 20.5, -0.5], y=[-0.5, -0.5, 7.5, 7.5], z=[Z_WALL, Z_WALL, Z_WALL+2.0, Z_WALL+2.0],
            color='#334155', opacity=0.9, hoverinfo='skip', showscale=False
        ))
        # Severní svah (N) - lehce tmavší
        fig_3d.add_trace(go.Mesh3d(
            x=[-0.5, 20.5, 20.5, -0.5], y=[7.5, 7.5, 15.5, 15.5], z=[Z_WALL+2.0, Z_WALL+2.0, Z_WALL, Z_WALL],
            color='#1e293b', opacity=0.9, hoverinfo='skip', showscale=False
        ))
        # Výrazný obrys střechy pro perfektní čitelnost
        fig_3d.add_trace(go.Scatter3d(
            x=[-0.5, 20.5, 20.5, -0.5, -0.5, -0.5, 20.5, 20.5, -0.5], 
            y=[-0.5, -0.5, 15.5, 15.5, -0.5, 7.5, 7.5, 15.5, 7.5], 
            z=[Z_WALL, Z_WALL, Z_WALL, Z_WALL, Z_WALL, Z_WALL+2.0, Z_WALL+2.0, Z_WALL, Z_WALL+2.0],
            mode='lines', line=dict(color='#0ea5e9', width=4), showlegend=False, hoverinfo='skip'
        ))

        je_aktivni = aktualni_fve_kw > 0.05
        panel_color = '#10b981' if je_aktivni else '#0f172a' 
        panel_line = '#34d399' if je_aktivni else '#1e293b'
        
        # DOKONALÉ ZAROVNÁNÍ PANELŮ (Grid)
        # 5 sloupců a 2 řady s přesnými mezerami
        # Šířka střechy je od 0 do 20. Sloupce dáme rovnoměrně:
        panel_xs = [2.0, 5.5, 9.0, 12.5, 16.0] 
        # Délka svahu je od 0 do 7.5. Řady dáme hezky nad sebe:
        panel_ys = [1.0, 4.0]     
        
        # Geometrie jednoho panelu
        w = 3.0   # Šířka jednoho panelu (x)
        h = 2.5   # Délka jednoho panelu po svahu (y)
        z_gap = 0.03 # Panely leží téměř přilepené ke střeše
        
        for px in panel_xs:
            for py in panel_ys:
                # Výpočet sklonu (Z) přesně podle úhlu střechy
                z_bottom = Z_WALL + (py * (2.0 / 7.5)) + z_gap
                z_top = Z_WALL + ((py + h) * (2.0 / 7.5)) + z_gap
                
                corners_x = [px, px+w, px+w, px]
                corners_y = [py, py, py+h, py+h]
                corners_z = [z_bottom, z_bottom, z_top, z_top]
                
                # Rám panelu
                fig_3d.add_trace(go.Scatter3d(
                    x=corners_x + [corners_x[0]], y=corners_y + [corners_y[0]], z=corners_z + [corners_z[0]],
                    mode='lines', line=dict(color=panel_line, width=5), hoverinfo='skip', showlegend=False
                ))
                
                # Skleněná výplň panelu
                fig_3d.add_trace(go.Mesh3d(
                    x=corners_x, y=corners_y, z=corners_z,
                    color=panel_color, opacity=0.95,
                    i=[0, 0], j=[1, 2], k=[2, 3],
                    hovertemplate=f"<b>Fyzický FVE Panel</b><br>Celkový výkon pole: {aktualni_fve_kw:.2f} kW<extra></extra>",
                    showscale=False
                ))
        
        if je_aktivni:
            fig_3d.add_trace(go.Scatter3d(
                x=[10], y=[3.5], z=[Z_WALL + 3.0], mode='text',
                text=[f"FVE VYRÁBÍ<br>☀ {aktualni_fve_kw:.2f} kW"],
                textfont=dict(color="#10b981", size=18, family="Arial Black"), hoverinfo="skip", showlegend=False
            ))

        camera_eye = dict(x=0.2, y=-1.8, z=1.2)

    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, 22]),
            yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, 17]),
            zaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-0.5, 6]),
            camera=dict(up=dict(x=0,y=0,z=1), center=dict(x=0,y=0,z=-0.2), eye=camera_eye)
        ),
        margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", height=500
    )
    st.plotly_chart(fig_3d, use_container_width=True)

with col_budiky:
    dum_kw = radek_bal['Spotřeba'] * 4
    sit_odb = radek_bal['Odběr z DS'] * 4
    sit_pre = radek_bal['Přetok do DS'] * 4
    
    st.markdown(f"""
    <div class="power-card c-fve"><span>☀️ FVE vyrábí</span> <span class="val" style="color: #fbbf24;">{aktualni_fve_kw:.2f} kW</span></div>
    <div class="power-card c-dum"><span>🏠 Dům bere</span> <span class="val" style="color: #ef4444;">{dum_kw:.2f} kW</span></div>
    """, unsafe_allow_html=True)
    
    if sit_odb > 0: st.markdown(f"""<div class="power-card c-sit-in"><span>🌐 Nákup ze sítě</span> <span class="val" style="color: #f59e0b;">{sit_odb:.2f} kW</span></div>""", unsafe_allow_html=True)
    else: st.markdown(f"""<div class="power-card c-sit-out"><span>💰 Do sítě</span> <span class="val" style="color: #34d399;">{sit_pre:.2f} kW</span></div>""", unsafe_allow_html=True)
    
    aktualni_baterie_kwh = radek_bal['Stav baterie']
    if soc_col_name: raw_soc = radek_bal[soc_col_name]; aktualni_soc_procenta = raw_soc * 100 if raw_soc <= 1.0 else raw_soc
    else: aktualni_soc_procenta = (aktualni_baterie_kwh / 20.0) * 100
    
    barva_baterie = "#ef4444" if aktualni_soc_procenta <= 10.5 else "#10b981"

    fig_bat = go.Figure(go.Indicator(
        mode="gauge+number", value=aktualni_soc_procenta,
        number={'suffix': " %", 'font': {'size': 35, 'color': barva_baterie}},
        title={'text': f"🔋 SoC Baterie ({aktualni_baterie_kwh:.1f} kWh)", 'font': {'size': 18, 'color':'#f8fafc'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': "#94a3b8"}},
            'bar': {'color': barva_baterie}, 'bgcolor': "rgba(15,23,42,0.8)", 'borderwidth': 0,
            'steps': [{'range': [0, 10], 'color': "#7f1d1d"}, {'range': [10, 100], 'color': "#064e3b"}],
        }
    ))
    fig_bat.update_layout(height=280, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bat, use_container_width=True)

st.markdown("---")

st.markdown("### 📈 Denní průběh energií a spotřeby v kW")

ignore_cols = ['Datum', 'Čas', 'Spotřeba domácnosti', 'Čas_zobrazeni']
appliance_cols = [c for c in df_app.columns if c not in ignore_cols]
df_app_unique = df_app.loc[:, ~df_app.columns.duplicated()]

active_appliances = []
for c in appliance_cols:
    if c in df_app_unique.columns:
        if pd.to_numeric(df_app_unique[c], errors='coerce').fillna(0).sum() > 0: active_appliances.append(c)

fig_toky = go.Figure()
fig_toky.add_trace(go.Scatter(x=df_bal['Čas_zobrazeni'], y=df_bal['Výroba FVE']*4, mode='lines', name='Výroba FVE', line=dict(color='#fbbf24', width=3), fill='tozeroy', hovertemplate='%{y:.2f} kW<extra></extra>'))
fig_toky.add_trace(go.Scatter(x=df_bal['Čas_zobrazeni'], y=df_bal['Spotřeba']*4, mode='lines', name='Příkon domu', line=dict(color='#ef4444', width=3), hovertemplate='%{y:.2f} kW<extra></extra>'))
fig_toky.add_trace(go.Scatter(x=df_bal['Čas_zobrazeni'], y=df_bal['Odběr z DS']*4, mode='lines', name='Odběr ze sítě', line=dict(color='#38bdf8', width=2, dash='dash'), hovertemplate='%{y:.2f} kW<extra></extra>'))

fig_toky.update_layout(
    title=dict(text="Základní toky (Zdroj vs Spotřeba)", font=dict(size=16, color="#e2e8f0")),
    xaxis_title="", yaxis_title="Výkon (kW)", hovermode="x unified", height=380,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
    font=dict(color="#f8fafc", size=13), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, max(df_bal['Spotřeba']*4)*1.1 + 1]),
    margin=dict(t=40, b=10)
)
st.plotly_chart(fig_toky, use_container_width=True)

fig_spotrebice = go.Figure()
distinct_colors = ['#38bdf8', '#a3e635', '#f87171', '#c084fc', '#fbbf24', '#2dd4bf', '#fb7185', '#818cf8', '#fcd34d', '#34d399', '#f472b6', '#60a5fa']

for idx, app_name in enumerate(active_appliances):
    vykon_kw = pd.to_numeric(df_app_unique[app_name], errors='coerce').fillna(0) * 4
    fig_spotrebice.add_trace(go.Bar(
        x=df_bal['Čas_zobrazeni'], y=vykon_kw, name=app_name,
        marker_color=distinct_colors[idx % len(distinct_colors)],
        marker_line_color='rgba(255,255,255,0.3)', marker_line_width=1,
        hovertemplate='<b>%{y:.2f} kW</b><extra></extra>' 
    ))

fig_spotrebice.update_layout(
    title=dict(text="Energetická stopa spotřebičů (Z čeho se skládá celková spotřeba domu)", font=dict(size=16, color="#e2e8f0")),
    barmode='stack', xaxis_title="Čas", yaxis_title="Příkon (kW)", hovermode="x unified", height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(size=14)),
    font=dict(color="#f8fafc", size=13), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", type='category'), yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, max(df_bal['Spotřeba']*4)*1.1 + 1]),
    margin=dict(t=50)
)
st.plotly_chart(fig_spotrebice, use_container_width=True)

st.markdown("---")
st.markdown("### 🥇 Žebříček žroutů (Celková denní spotřeba)")
sums = {c: pd.to_numeric(df_app_unique[c], errors='coerce').fillna(0).sum() for c in active_appliances}
top_zrouti = [(name, val) for name, val in sorted(sums.items(), key=lambda x: x[1], reverse=True) if val > 0]

if top_zrouti:
    df_zrouti = pd.DataFrame(top_zrouti, columns=["Spotřebič", "Suma (kWh)"])
    df_zrouti["Suma (kWh)"] = df_zrouti["Suma (kWh)"].apply(lambda x: f"{x:.3f}")
    st.markdown(df_zrouti.to_html(index=False, classes='table table-striped', justify='left'), unsafe_allow_html=True)
    st.markdown("""<style>.table { width: 100%; color: #f8fafc; border-collapse: collapse; font-size: 16px; } .table th, .table td { padding: 10px; border-bottom: 1px solid #334155; } .table th { background-color: rgba(15,23,42,0.8); } .table-striped tbody tr:nth-of-type(odd) { background-color: rgba(30,41,59,0.3); }</style>""", unsafe_allow_html=True)