from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="FVE 3D Smart Home",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PRÉMIOVÝ DARK MODE ---
st.markdown("""
<style>
.stApp { background: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 100%); }
.stMarkdown, .stText, h1, h2, h3, h4, h5, h6, span, label, p { color: #f8fafc !important; }
div[data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.65); backdrop-filter: blur(12px);
    border: 1px solid rgba(148, 163, 184, 0.18); padding: 18px 20px; border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45); transition: transform 0.2s ease, border-color 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px); border-color: rgba(56, 189, 248, 0.45);
}
div[data-testid="stMetricValue"] div { color: #38bdf8 !important; font-weight: 800 !important; text-shadow: 0 0 10px rgba(56, 189, 248, 0.3); }
div[data-testid="stMetricDelta"] div { font-weight: 600 !important; }
.power-card {
    padding: 14px 20px; border-radius: 14px; margin-bottom: 12px; font-size: 15px; font-weight: 600; display: flex;
    justify-content: space-between; align-items: center; background: rgba(30, 41, 59, 0.65); backdrop-filter: blur(8px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.4); border: 1px solid rgba(148,163,184,0.15); transition: transform 0.2s ease;
}
.power-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.6); }
.c-fve { border-left: 5px solid #fbbf24; }
.c-dum { border-left: 5px solid #ef4444; }
.c-sit-out { border-left: 5px solid #10b981; }
.c-sit-in { border-left: 5px solid #f59e0b; }
.c-bat { border-left: 5px solid #38bdf8; }
.val { font-size: 19px; font-weight: 900; }
.legend-box { background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(148,163,184,0.15); padding: 20px; border-radius: 14px; margin-top: 15px; }
.leg-row { display: flex; align-items: center; margin-bottom: 15px; }
.leg-dot { width: 18px; height: 18px; border-radius: 50%; margin-right: 15px; border: 2px solid white; box-shadow: 0 0 8px rgba(255,255,255,0.4); flex-shrink: 0; }
.dot-green { background-color: #10b981; box-shadow: 0 0 10px #10b981; }
.dot-orange { background-color: #f59e0b; box-shadow: 0 0 10px #f59e0b; }
.dot-off { background-color: transparent; border: 2px dashed #64748b; box-shadow: none; }
.leg-text { font-size: 15px; line-height: 1.2; } .leg-sub { font-size: 12px; color: #94a3b8; }
.stRadio > div { background: rgba(15,23,42,0.8); padding: 10px; border-radius: 10px; border: 1px solid #334155; }
.fin-card {
    background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 14px; padding: 16px 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.fin-title { font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.fin-value { font-size: 24px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --- BOČNÍ PANEL (HLAVNÍ NAVIGACE) ---
st.sidebar.header("🧭 Navigace")
rezim_aplikace = st.sidebar.radio(
    "Vyberte režim:",
    ["🏡 3D Simulace", "📖 Uživatelská příručka"]
)

if rezim_aplikace == "📖 Uživatelská příručka":
    st.title("📖 Uživatelská příručka: 3D Digitální Dvojče FVE")
    st.markdown("""
    Tato aplikace slouží jako interaktivní dispečink a simulátor chytré domácnosti vybavené fotovoltaickou elektrárnou (FVE) a bateriovým úložištěm. Umožňuje detailně analyzovat toky energií, chování jednotlivých spotřebičů, ekonomiku provozu a interakci s distribuční sítí.

    ---

    ### 1. Levý ovládací panel (Nastavení, filtry a ceník)
    Levý postranní panel je hlavním řídícím centrem aplikace. Zde nastavujete, jaký scénář a jaké detaily chcete analyzovat.

    *   **⚙️ Nastavení Simulace (Vyberte období):** Umožňuje přepínat mezi šesti předpřipravenými scénáři z Excelu (Leden, Červenec, Říjen – vždy rozděleno na pracovní den a víkend). Po změně období se celá aplikace automaticky přepočítá.
    *   **👁️ 3D Pohled:** Přepínač pro hlavní 3D mapu. 
        *   *Interiér a spotřebiče:* Odkryje střechu a zobrazí rozložení místností, baterii a spotřebiče.
        *   *Střecha a Jihovýchodní FVE:* Skryje interiér a zobrazí solární panely. Pokud panely vyrábí, zezelenají.
    *   **🎛️ Zobrazení spotřebičů (Filtr):** Zde můžete zapínat a vypínat jednotlivé spotřebiče (např. světla, televizi, pračku). Filtr okamžitě skryje ikonu ve 3D modelu i v grafech. Pomocí rychlých tlačítek **✅ Vybrat vše** a **🔍 Jen hledaný** můžete bleskově vyfiltrovat jediný spotřebič.
    *   **🔌 Spotřebiče (Cesta časem):** Speciální vyhledávač. Pokud vyberete spotřebič, aplikace najde všechny okamžiky, kdy byl zapnutý. Kliknutím na časové tlačítko se posuvník času rovnou přesune.
    *   **💰 Ekonomické parametry:** Nastavení nákupní ceny elektřiny ze sítě (Kč/kWh) a výkupní ceny přetoků (Kč/kWh) pro výpočet denní finanční úspory.

    ---

    ### 2. Hlavní souhrnné metriky a Měřítko (kW vs kWh)
    Šestice číselných ukazatelů na samém vrchu obrazovky poskytuje rychlý denní souhrn za celých 24 hodin vybraného scénáře (včetně procentuální **Soběstačnosti domu** a špičkových výkonů). Tyto souhrnné hodnoty jsou uváděny v **objemu energie (kWh)**.
    
    *Moderní energetické dispečinky (a tedy i tato aplikace ve 3D modelu, kartách budíků a denních grafech) však ukazují **okamžitý výkon (kW)**.*
    Z toho důvodu aplikace provádí matematický přepočet: Hodnotu energie získanou z 15minutového úseku v Excelu násobí čtyřmi (`x 4`), čímž získá reálný okamžitý fyzikální výkon, jaký zrovna protékal kabely. Všechny tečky ve 3D modelu reprezentují aktuální zatížení.

    ---

    ### 3. Analytické grafy a Bilance dne
    Aplikace obsahuje sadu interaktivních grafů. Ve všech denních grafech se navíc zobrazuje **svislá ryska (`⏱️ Zvolený čas`)**, která přesně odpovídá pozici vašeho Stroje času.

    **1. Základní toky (Zdroj vs Spotřeba + Stav baterie SOC %)**
    Ukazuje celkový příkon domu (červená křivka) v porovnání s výrobou solárních panelů (žlutá plocha) a odběrem ze sítě (modrá přerušovaná čára). Zelená tečkovaná křivka na pravé ose Y ukazuje průběh nabití baterie (0–100 %).

    **2. Energetická stopa spotřebičů**
    Skládaný sloupcový graf. Rozpad červené křivky z prvního grafu na drobné. Tento graf dynamicky zoomuje osu Y. Pokud vypnete velké žrouty a necháte jen notebook a mobil, graf automaticky změní měřítko.

    **3. Interakce s distribuční sítí**
    Zrcadlový plošný graf. Červená plocha nahoře znamená nákup (dům síť zatěžuje). Zelená plocha do mínusu představuje přetoky (prodej přebytků).

    **4. Struktura krytí spotřeby a Využití FVE (Prstencové grafy + Finanční bilance)**
    Dva souhrnné grafy ukazující, kolik % spotřeby domu pokrylo přímo slunce, kolik baterie a kolik síť, a kam přesně odtekla vyrobená solární energie, doplněné o finanční vyhodnocení dne v Kč.

    ---

    ### 4. Žebříček žroutů a Celoroční srovnání
    Tabulka na konci aplikace sčítá celodenní spotřebu jednotlivých spotřebičů v **kWh**, ukazuje jejich procentuální podíl na chodu domácnosti, špičkový příkon v **kW**, celkovou dobu provozu v **hodinách** a odhadované náklady. Pod tabulkou lze rozbalit souhrnné porovnání všech 6 sezónních scénářů.

    ---

    ### 🎮 5. Jak ovládat 3D model (Nástrojový panel)
    Když najedete myší do pravého horního rohu 3D modelu, objeví se skrytý nástrojový panel (tzv. Modebar). Ten obsahuje velmi užitečné nástroje pro ovládání pohledu na váš digitální dům.

    *   📷 **Download plot as a png (Vyfotit scénu):** První ikonka fotoaparátu okamžitě uloží aktuální 3D pohled na váš dům jako kvalitní obrázek do vašeho počítače.
    *   🔎 **Zoom (Lupa):** Zapne režim přibližování. Když stisknete levé tlačítko myši a táhnete nahoru, přibližujete se k domu (můžete "vjet" až do místností). Táhnutím dolů se od domu oddalujete. Rychleji to však jde pouhým točením kolečka na myši.
    *   ✥ **Pan (Posun / Ruka):** Zapne režim rovnoběžného posunu. Umožňuje vám "chytit" celou 3D scénu a přesunout ji doleva, doprava, nahoru nebo dolů, aniž byste měnili natočení (sklon) kamery. 
    *   🔄 **Orbital rotation (Orbitální rotace - Výchozí):** Toto je základní a nejdůležitější režim! Umožňuje vám kliknout kamkoliv do obrázku a plynule dům otáčet, naklánět a prohlížet si ho ze všech stran. 
    *   ⏏️ **Turntable rotation (Otočný stůl):** Zamkne jednu osu rotace. Na rozdíl od orbitální rotace, kde můžete model převrátit "vzhůru nohama", vás tento režim nutí točit modelem pouze dokola, jako by stál na stole. Zabraňuje tomu, abyste se ve 3D prostoru dezorientovali.
    *   🏠 **Reset camera to default (Návrat domů):** Nejdůležitější pojistka. Pokud dům omylem posunete mimo obrazovku, přiblížíte tak moc, že nevíte kde jste, nebo jej nechtěně překlopíte vzhůru nohama, **klikněte na tuto ikonu domečku**. Okamžitě vám celou scénu a kameru zresetuje do původního krásného výchozího stavu.

    **Další klávesové a myší zkratky:**
    *   **Kolečko myši:** Slouží pro plynulé a nekonečné přibližování a oddalování.
    *   **Kliknutí pravým tlačítkem + tažení:** Rychle přepne z rotace do režimu "Pan" (Posun prostoru) – skvělé pro vystředění domu.
    """)
    st.stop()

# -----------------------------------------------------------------------------------------
# --- ZDE ZAČÍNÁ KLASICKÁ 3D SIMULACE ---
# -----------------------------------------------------------------------------------------

st.title("🏡 3D Digitální Dvojče: FVE Domácnost")

if 'slider_cas' not in st.session_state:
    st.session_state.slider_cas = "12:00"

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
        df_d = df_d.rename(columns={
            'Plynový kotel + ohřev vody + topení': 'Elektrický kotel + ohřev vody + topení'
        })
        
    soc_col_name = next((col for col in ['Soc', 'Soc %', 'Soc  %'] if col in df_b.columns), None)
            
    times = [t.strftime("%H:%M") if hasattr(t, 'strftime') else str(t)[:5] for t in df_b['Čas']]
    df_b['Čas_zobrazeni'] = times
    df_d['Čas_zobrazeni'] = times
    cols_to_numeric = [
        'Spotřeba', 'Přímá vlastní spotřeba z FVE', 'Výroba FVE',
        'Odběr z DS', 'Přetok do DS', 'Spotřeba z baterie', 'Stav baterie',
        'Nabíjení (Netto)', 'Nabíjení (Brutto)', 'Vybíjení (Netto)', 'Vybíjení (Brutto)', 'Vlastní spotřeba'
    ]
    if soc_col_name:
        cols_to_numeric.append(soc_col_name)
    for col in cols_to_numeric:
        if col in df_b.columns:
            df_b[col] = pd.to_numeric(df_b[col], errors='coerce').fillna(0)
    return df_b, df_d, soc_col_name

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Nastavení Simulace")
obdobi = st.sidebar.selectbox(
    "Vyberte období:",
    [
        "Leden (pracovní den)", "Leden (víkend)",
        "Červenec (pracovní den)", "Červenec (víkend)",
        "Říjen (pracovní den)", "Říjen (víkend)"
    ]
)

sheet_map = {
    "Leden (pracovní den)": ("Leden", "Leden data"),
    "Leden (víkend)": ("Leden vík", "Leden vík data"),
    "Červenec (pracovní den)": ("Červenec", "Červenec data"),
    "Červenec (víkend)": ("Červenec vík", "Červenec vík data"),
    "Říjen (pracovní den)": ("Říjen", "Říjen data"),
    "Říjen (víkend)": ("Říjen vík", "Říjen vík data"),
}
sheet_bal, sheet_data = sheet_map[obdobi]

df_bal, df_app, soc_col_name = load_data(EXCEL_PATH, sheet_bal, sheet_data)

st.sidebar.markdown("---")
vrstva_zobrazeni = st.sidebar.radio(
    "👁️ 3D Pohled:",
    ("Interiér a spotřebiče", "Střecha a Jihovýchodní FVE")
)

ignore_cols = ['Datum', 'Čas', 'Spotřeba domácnosti', 'Čas_zobrazeni']
appliance_cols = [c for c in df_app.columns if c not in ignore_cols and not c.startswith('Unnamed')]
df_app_unique = df_app.loc[:, ~df_app.columns.duplicated()]

active_appliances = []
for c in appliance_cols:
    if c in df_app_unique.columns:
        if pd.to_numeric(df_app_unique[c], errors='coerce').fillna(0).sum() > 0: 
            active_appliances.append(c)

if "filter_spotrebice" not in st.session_state:
    st.session_state.filter_spotrebice = active_appliances.copy()
else:
    st.session_state.filter_spotrebice = [
        a for a in st.session_state.filter_spotrebice if a in active_appliances
    ]
    if not st.session_state.filter_spotrebice:
        st.session_state.filter_spotrebice = active_appliances.copy()

st.sidebar.markdown("---")
st.sidebar.header("🔌 Spotřebiče")
hledany_spotrebic = st.sidebar.selectbox(
    "Vyhledat a skočit na čas zapnutí:",
    ["(Nevybráno)"] + active_appliances
)

if hledany_spotrebic != "(Nevybráno)":
    s_data = pd.to_numeric(df_app_unique[hledany_spotrebic], errors='coerce').fillna(0)
    aktivni_casy = s_data[s_data > 0]
    
    if not aktivni_casy.empty:
        st.sidebar.markdown(f"*Nalezeno {len(aktivni_casy)} úseků, kdy je {hledany_spotrebic} zapnutý:*")
        def skocit_v_case(novy_cas):
            st.session_state.slider_cas = novy_cas
        for idx_btn, val in aktivni_casy.items():
            cas_skoku = df_bal.loc[idx_btn, 'Čas_zobrazeni']
            st.sidebar.button(
                f"⏱️ {cas_skoku} ({val*4:.3f} kW)", 
                key=f"btn_skok_{hledany_spotrebic}_{cas_skoku}",
                on_click=skocit_v_case, 
                args=(cas_skoku,)
            )
    else:
        st.sidebar.info("Tento spotřebič se ve vybraný den nezapíná.")

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Zobrazení spotřebičů")

def vybrat_vsechny_spotrebice():
    st.session_state.filter_spotrebice = active_appliances.copy()

def vybrat_jen_hledany():
    if hledany_spotrebic != "(Nevybráno)":
        st.session_state.filter_spotrebice = [hledany_spotrebic]

b_col1, b_col2 = st.sidebar.columns(2)
b_col1.button("✅ Vybrat vše", on_click=vybrat_vsechny_spotrebice, use_container_width=True)
b_col2.button("🔍 Jen hledaný", on_click=vybrat_jen_hledany, use_container_width=True)

vybrane_spotrebice = st.sidebar.multiselect(
    "Vyberte, co chcete vidět v modelu a grafech:", 
    options=active_appliances, 
    key="filter_spotrebice"
)

st.sidebar.markdown("---")
st.sidebar.header("💰 Ekonomické parametry")
cena_nakup = st.sidebar.number_input(
    "Cena nákupu ze sítě (Kč/kWh):", min_value=1.0, max_value=20.0, value=6.50, step=0.10
)
cena_vykup = st.sidebar.number_input(
    "Výkupní cena přetoků (Kč/kWh):", min_value=0.0, max_value=10.0, value=1.50, step=0.10
)

# --- VÝPOČTY PRO HLAVNÍ METRIKY ---
celkova_fve = df_bal['Výroba FVE'].sum()
max_fve_kw = (df_bal['Výroba FVE'] * 4).max()
celkova_spotreba = df_bal['Spotřeba'].sum()
max_spotreba_kw = (df_bal['Spotřeba'] * 4).max()
celkovy_odber_ds = df_bal['Odběr z DS'].sum()
celkovy_pretok_ds = df_bal['Přetok do DS'].sum()
prima_fve = df_bal['Přímá vlastní spotřeba z FVE'].sum()
spotreba_z_bat = df_bal['Spotřeba z baterie'].sum()

sobestacnost_pct = (1.0 - (celkovy_odber_ds / celkova_spotreba)) * 100 if celkova_spotreba > 0 else 0.0
vyuziti_fve_pct = ((celkova_fve - celkovy_pretok_ds) / celkova_fve) * 100 if celkova_fve > 0 else 0.0
konec_bat_kwh = df_bal['Stav baterie'].iloc[-1]
start_bat_kwh = df_bal['Stav baterie'].iloc[0]
delta_bat_kwh = konec_bat_kwh - start_bat_kwh

# --- HLAVNÍ METRIKY (6 KARET S KONTEXTEM) ---
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("☀️ Výroba FVE", f"{celkova_fve:.1f} kWh", f"Špička: {max_fve_kw:.2f} kW")
c2.metric("🏠 Spotřeba domu", f"{celkova_spotreba:.1f} kWh", f"Max: {max_spotreba_kw:.2f} kW", delta_color="off")
c3.metric("🛡️ Soběstačnost", f"{sobestacnost_pct:.1f} %", f"Využití FVE: {vyuziti_fve_pct:.0f} %")
c4.metric(
    "🔌 Odběr ze sítě",
    f"{celkovy_odber_ds:.1f} kWh",
    f"{(celkovy_odber_ds/celkova_spotreba*100 if celkova_spotreba else 0):.1f} % spotřeby",
    delta_color="inverse"
)
c5.metric(
    "⚡ Přetoky do sítě",
    f"{celkovy_pretok_ds:.1f} kWh",
    f"{(celkovy_pretok_ds/celkova_fve*100 if celkova_fve else 0):.1f} % výroby"
)
c6.metric("🔋 Baterie (konec)", f"{konec_bat_kwh:.1f} kWh", f"{delta_bat_kwh:+.1f} kWh za den")
st.markdown("---")

# --- STROJ ČASU S RYCHLÝMI TLAČÍTKY ---
casy_list = df_bal['Čas_zobrazeni'].tolist()

def posun_casu(krok):
    akt_idx = casy_list.index(st.session_state.slider_cas) if st.session_state.slider_cas in casy_list else 48
    novy_idx = max(0, min(len(casy_list) - 1, akt_idx + krok))
    st.session_state.slider_cas = casy_list[novy_idx]

def nastav_cas(konkretni_cas):
    if konkretni_cas in casy_list:
        st.session_state.slider_cas = konkretni_cas

st.markdown("### ⏱️ Stroj Času (Interaktivní 3D Dvojče)")
tc1, tc2, tc3, tc4, tc5 = st.columns(5)
tc1.button("⏪ -15 min", on_click=posun_casu, args=(-1,), use_container_width=True)
tc2.button("🌅 Ranní špička (06:45)", on_click=nastav_cas, args=("06:45",), use_container_width=True)
tc3.button("☀️ Poledne (12:00)", on_click=nastav_cas, args=("12:00",), use_container_width=True)
tc4.button("🌆 Večerní špička (18:00)", on_click=nastav_cas, args=("18:00",), use_container_width=True)
tc5.button("⏩ +15 min", on_click=posun_casu, args=(1,), use_container_width=True)

zvoleny_cas = st.select_slider(
    "Posunem sledujte změny v domě v čase:",
    options=casy_list,
    key="slider_cas"
)
idx = df_bal[df_bal['Čas_zobrazeni'] == zvoleny_cas].index[0]
radek_bal = df_bal.iloc[idx]
radek_app = df_app.iloc[idx]

bere_ze_site = radek_bal['Odběr z DS'] > 0
aktivni_barva = "#f59e0b" if bere_ze_site else "#10b981" 
aktualni_fve_kw = radek_bal['Výroba FVE'] * 4
aktualni_baterie_kwh = radek_bal['Stav baterie']
soc = (
    radek_bal[soc_col_name] * 100
    if soc_col_name and radek_bal[soc_col_name] <= 1.0
    else (aktualni_baterie_kwh / 20.0) * 100
)

nabijeni_kw = radek_bal.get('Nabíjení (Netto)', 0) * 4
vybijeni_kw = radek_bal.get('Vybíjení (Netto)', 0) * 4

try:
    hodina = int(str(zvoleny_cas).split(':')[0])
except ValueError:
    hodina = 12

col_leg, col_mapa, col_budiky = st.columns([0.75, 2.3, 0.95])

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
    
    fig_3d.add_trace(go.Mesh3d(
        x=[-5, 25, 25, -5], y=[-5, -5, 20, 20], z=[-0.1, -0.1, -0.1, -0.1],
        color='#064e3b', opacity=0.4, hoverinfo='skip', showscale=False
    ))
    
    kompas_opac = 1.0 if vrstva_zobrazeni != "Interiér a spotřebiče" else 0.0
    fig_3d.add_trace(go.Scatter3d(
        x=[-2, 22], y=[7.5, 7.5], z=[-0.05, -0.05], mode='lines',
        line=dict(color=f'rgba(255,255,255,{kompas_opac})', width=2),
        hoverinfo='skip', showlegend=False
    ))
    fig_3d.add_trace(go.Scatter3d(
        x=[10, 10], y=[-2, 17], z=[-0.05, -0.05], mode='lines',
        line=dict(color=f'rgba(255,255,255,{kompas_opac})', width=2),
        hoverinfo='skip', showlegend=False
    ))
    fig_3d.add_trace(go.Scatter3d(
        x=[10, 10, 23, -3], y=[-3, 18, 7.5, 7.5], z=[0, 0, 0, 0], mode='text',
        text=['<b>JIH (S)</b>', '<b>SEVER (N)</b>', '<b>VÝCHOD (E)</b>', '<b>ZÁPAD (W)</b>'],
        textfont=dict(color=f'rgba(56,189,248,{kompas_opac})', size=14, family="Arial Black"),
        hoverinfo='skip', showlegend=False
    ))

    Z_WALL = 1.8

    if vrstva_zobrazeni == "Interiér a spotřebiče":
        rooms = [
            {"name": "Obývací pokoj", "x0": 0, "y0": 10, "x1": 8, "y1": 15},
            {"name": "Kuchyně",       "x0": 8, "y0": 10, "x1": 15, "y1": 15},
            {"name": "Koupelna 2",    "x0": 15,"y0": 10, "x1": 20, "y1": 15},
            {"name": "Pokoj 1",       "x0": 0, "y0": 5, "x1": 6, "y1": 10},
            {"name": "Chodba",        "x0": 6, "y0": 5, "x1": 15, "y1": 10},
            {"name": "Pokoj 2",       "x0": 15,"y0": 5, "x1": 20, "y1": 10},
            {"name": "Koupelna 1",    "x0": 0, "y0": 0, "x1": 5, "y1": 5},
            {"name": "Tech. místnost","x0": 5, "y0": 0, "x1": 10, "y1": 5},
            {"name": "Pokoj 3",       "x0": 10,"y0": 0, "x1": 20, "y1": 5},
        ]
        for r in rooms:
            fig_3d.add_trace(go.Mesh3d(
                x=[r["x0"], r["x1"], r["x1"], r["x0"]],
                y=[r["y0"], r["y0"], r["y1"], r["y1"]],
                z=[0, 0, 0, 0], color='#334155', opacity=0.8, hoverinfo='skip'
            ))
            xl = [r["x0"], r["x1"], r["x1"], r["x0"], r["x0"], r["x0"], r["x1"], r["x1"], r["x1"], r["x1"], r["x1"], r["x0"], r["x0"], r["x0"]]
            yl = [r["y0"], r["y0"], r["y1"], r["y1"], r["y0"], r["y0"], r["y0"], r["y0"], r["y1"], r["y1"], r["y1"], r["y1"], r["y1"], r["y0"]]
            zl = [0, 0, 0, 0, 0, Z_WALL, Z_WALL, 0, 0, Z_WALL, Z_WALL, Z_WALL, 0, Z_WALL]
            fig_3d.add_trace(go.Scatter3d(
                x=xl, y=yl, z=zl, mode='lines',
                line=dict(color='#94a3b8', width=2), showlegend=False, hoverinfo='skip'
            ))
            fig_3d.add_trace(go.Scatter3d(
                x=[(r["x0"]+r["x1"])/2], y=[(r["y0"]+r["y1"])/2], z=[0.1],
                mode='text', text=[r["name"]],
                textfont=dict(color="#94a3b8", size=10), showlegend=False, hoverinfo='skip'
            ))

        b_x, b_y = 9.0, 3.5
        b_w, b_h = 0.8, 0.8
        max_bat_height = 1.4
        current_bat_height = max(0.1, (soc / 100) * max_bat_height)
        bat_color = "#ef4444" if soc <= 5.5 else ("#f59e0b" if soc <= 10.5 else "#10b981")
        
        b_xs = [b_x, b_x+b_w, b_x+b_w, b_x, b_x, b_x+b_w, b_x+b_w, b_x]
        b_ys = [b_y, b_y, b_y+b_h, b_y+b_h, b_y, b_y, b_y+b_h, b_y+b_h]
        b_zs = [0, 0, 0, 0, max_bat_height, max_bat_height, max_bat_height, max_bat_height]
        fig_3d.add_trace(go.Mesh3d(
            x=b_xs, y=b_ys, z=b_zs, color='#94a3b8', opacity=0.1, alphahull=0, hoverinfo='skip'
        ))
        
        fill_zs = [0, 0, 0, 0, current_bat_height, current_bat_height, current_bat_height, current_bat_height]
        fig_3d.add_trace(go.Mesh3d(
            x=b_xs, y=b_ys, z=fill_zs, color=bat_color, opacity=0.9, alphahull=0,
            hovertemplate=f"<b>Fyzická Baterie</b><br>Nabití: {soc:.1f}%<extra></extra>"
        ))
        fig_3d.add_trace(go.Scatter3d(
            x=[b_x, b_x+b_w, b_x+b_w, b_x, b_x, b_x, b_x+b_w, b_x+b_w, b_x+b_w, b_x+b_w, b_x, b_x],
            y=[b_y, b_y, b_y+b_h, b_y+b_h, b_y, b_y, b_y, b_y, b_y+b_h, b_y+b_h, b_y+b_h, b_y+b_h],
            z=[0, 0, 0, 0, 0, max_bat_height, max_bat_height, 0, 0, max_bat_height, max_bat_height, 0],
            mode='lines', line=dict(color='#ffffff', width=2), hoverinfo='skip', showlegend=False
        ))
        fig_3d.add_trace(go.Scatter3d(
            x=[b_x + b_w/2], y=[b_y + b_h/2], z=[max_bat_height + 0.3],
            mode='text', text=[f"<b>{soc:.0f}%</b>"],
            textfont=dict(color=bat_color, size=15, family="Arial Black"),
            hoverinfo='skip', showlegend=False
        ))

        kotel_col = 'Elektrický kotel + ohřev vody + topení'
        appliances_map = {
            'Televize': {'label': 'TV', 'pos': (2.5, 12.5)},
            'Elektrické žaluzie': {'label': 'Žaluzie', 'pos': (5.5, 12.5)},
            'Myčka': {'label': 'Myčka', 'pos': (9.5, 13.5)},
            'Elektrický sporák': {'label': 'Sporák', 'pos': (11.5, 13.5)},
            'Mikrovlnka': {'label': 'Mikrovlnka', 'pos': (13.5, 13.5)},
            'Kávovar': {'label': 'Kávovar', 'pos': (9.5, 11)},
            'Elektrická trouba': {'label': 'Trouba', 'pos': (11.5, 11)},
            'Topinkovač': {'label': 'Topinkovač', 'pos': (13.5, 11)},
            'Tablet': {'label': 'Tablet', 'pos': (2, 7.5)},
            'Počítače': {'label': 'PC', 'pos': (4, 7.5)}, 
            'Vysavač': {'label': 'Vysavač', 'pos': (10.5, 7.5)},
            'Notebook': {'label': 'Notebook', 'pos': (17.5, 7.5)}, 
            'Radio': {'label': 'Rádio', 'pos': (2.5, 2.5)},
            'Pračka': {'label': 'Pračka', 'pos': (6.5, 2.5)}, 
            'Sušička': {'label': 'Sušička', 'pos': (8.5, 2.5)}, 
            'Elektrický kotel': {'label': 'Kotel', 'pos': (7.5, 1.0), 'source_col': kotel_col}, 
            'Mobilní telefon': {'label': 'Mobil', 'pos': (15, 2.5)}
        }
        for r in rooms:
            appliances_map[f'Světlo ({r["name"]})'] = {
                'label': 'Světlo', 'pos': (r["x0"] + 1, r["y1"] - 1),
                'source_col': 'Osvětlení', 'is_shared': True, 'display_name': 'Světlo'
            }
            if r["name"] != "Chodba":
                appliances_map[f'Topení ({r["name"]})'] = {
                    'label': 'Topení', 'pos': (r["x1"] - 1, r["y0"] + 1),
                    'source_col': kotel_col, 'is_shared': True, 'display_name': 'Elektrické topení'
                }

        x_app, y_app, z_app, texts_app, colors_app, sizes_app, hover_app, borders_app = [], [], [], [], [], [], [], []

        for app_name, info in appliances_map.items():
            source = info.get('source_col', app_name)
            
            if source not in vybrane_spotrebice:
                continue
                
            display_name = info.get('display_name', app_name)
            val = 0
            if source in df_app.columns:
                hodnota = radek_app[source]
                if isinstance(hodnota, pd.Series):
                    val = pd.to_numeric(hodnota, errors='coerce').fillna(0).sum()
                else:
                    val = pd.to_numeric(hodnota, errors='coerce')
                    val = 0 if pd.isna(val) else val
                if info.get('is_shared'):
                    val = val / 9.0

            x_app.append(info['pos'][0])
            y_app.append(info['pos'][1])
            z_app.append(0.5)
            
            if val > 0.001:  
                colors_app.append(aktivni_barva)
                borders_app.append('white')
                sizes_app.append(20 + min((val * 25), 40))
                texts_app.append(f"<b>{info['label']}</b>")
                hover_app.append(f"<b>{display_name}</b><br>ZAPNUTO: {val*4:.3f} kW")
            else:
                colors_app.append('rgba(0,0,0,0)')
                borders_app.append('rgba(0,0,0,0)')
                sizes_app.append(1) 
                texts_app.append('')
                hover_app.append(f"<b>{display_name}</b> (Vypnuto)")

        fig_3d.add_trace(go.Scatter3d(
            x=x_app, y=y_app, z=z_app, mode='markers+text',
            marker=dict(size=sizes_app, color=colors_app, line=dict(color=borders_app, width=2)),
            text=texts_app, textposition="top center",
            textfont=dict(size=14, color="#ffffff", family="Arial Black"),
            hoverinfo="text", hovertext=hover_app, showlegend=False
        ))
        
        camera_eye = dict(x=-0.55, y=-1.35, z=1.1)
        
    else:
        fig_3d.add_trace(go.Mesh3d(
            x=[-0.5, 20.5, 20.5, -0.5], y=[-0.5, -0.5, 7.5, 7.5],
            z=[Z_WALL, Z_WALL, Z_WALL+2.0, Z_WALL+2.0],
            color='#334155', opacity=0.9, hoverinfo='skip', showscale=False
        ))
        fig_3d.add_trace(go.Mesh3d(
            x=[-0.5, 20.5, 20.5, -0.5], y=[7.5, 7.5, 15.5, 15.5],
            z=[Z_WALL+2.0, Z_WALL+2.0, Z_WALL, Z_WALL],
            color='#1e293b', opacity=0.9, hoverinfo='skip', showscale=False
        ))
        fig_3d.add_trace(go.Scatter3d(
            x=[-0.5, 20.5, 20.5, -0.5, -0.5, -0.5, 20.5, 20.5, -0.5],
            y=[-0.5, -0.5, 15.5, 15.5, -0.5, 7.5, 7.5, 15.5, 7.5],
            z=[Z_WALL, Z_WALL, Z_WALL, Z_WALL, Z_WALL, Z_WALL+2.0, Z_WALL+2.0, Z_WALL, Z_WALL+2.0],
            mode='lines', line=dict(color='#0ea5e9', width=4), showlegend=False, hoverinfo='skip'
        ))

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
                z_bottom = Z_WALL + (py * (2.0 / 7.5)) + z_gap
                z_top = Z_WALL + ((py + h) * (2.0 / 7.5)) + z_gap
                cx = [px, px+w, px+w, px]
                cy = [py, py, py+h, py+h]
                cz = [z_bottom, z_bottom, z_top, z_top]
                all_corners_x.extend(cx + [cx[0], None])
                all_corners_y.extend(cy + [cy[0], None])
                all_corners_z.extend(cz + [cz[0], None])
                mesh_x.extend(cx)
                mesh_y.extend(cy)
                mesh_z.extend(cz)
                mesh_i.extend([mesh_idx, mesh_idx])
                mesh_j.extend([mesh_idx+1, mesh_idx+2])
                mesh_k.extend([mesh_idx+2, mesh_idx+3])
                mesh_idx += 4

        fig_3d.add_trace(go.Scatter3d(
            x=all_corners_x, y=all_corners_y, z=all_corners_z,
            mode='lines', line=dict(color=panel_line, width=5), hoverinfo='skip', showlegend=False
        ))
        fig_3d.add_trace(go.Mesh3d(
            x=mesh_x, y=mesh_y, z=mesh_z, color=panel_color, opacity=0.95,
            i=mesh_i, j=mesh_j, k=mesh_k,
            hovertemplate=f"<b>Fyzický FVE Panel</b><br>Celkový výkon pole: {aktualni_fve_kw:.2f} kW<extra></extra>",
            showscale=False
        ))
        
        panel_text = f"FVE VYRÁBÍ<br>☀️ {aktualni_fve_kw:.2f} kW" if je_aktivni else ""
        fig_3d.add_trace(go.Scatter3d(
            x=[10], y=[3.5], z=[Z_WALL + 3.0], mode='text', text=[panel_text],
            textfont=dict(color="#10b981", size=18, family="Arial Black"),
            hoverinfo="skip", showlegend=False
        ))
        
        camera_eye = dict(x=0.1, y=-1.35, z=0.9)

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
        textfont=dict(color=bublina_barva, size=16, family="Arial Black"),
        hoverinfo='skip', showlegend=False
    ))

    # --- 100% ZACHOVANÉ PROPORCE 3D MODELU A ZÁMEK KAMERY ---
    fig_3d.update_layout(
        showlegend=False,
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, 22]), 
            yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-2, 17]), 
            zaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 9]),
            camera=dict(up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=-0.2), eye=camera_eye),
            uirevision=vrstva_zobrazeni
        ),
        margin=dict(l=0, r=0, t=0, b=80), 
        paper_bgcolor="rgba(0,0,0,0)", 
        height=700,
        uirevision=vrstva_zobrazeni
    )
    st.plotly_chart(fig_3d, use_container_width=True, key="mapa_3d")

with col_budiky:
    st.markdown(f"""
    <div class="power-card c-fve"><span>☀️ FVE vyrábí</span> <span class="val" style="color: #fbbf24;">{aktualni_fve_kw:.2f} kW</span></div>
    <div class="power-card c-dum"><span>🏠 Dům bere</span> <span class="val" style="color: #ef4444;">{radek_bal['Spotřeba'] * 4:.2f} kW</span></div>
    """, unsafe_allow_html=True)
    
    if radek_bal['Odběr z DS'] > 0:
        st.markdown(
            f'<div class="power-card c-sit-in"><span>🌐 Nákup ze sítě</span> <span class="val" style="color: #f59e0b;">{radek_bal["Odběr z DS"] * 4:.2f} kW</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="power-card c-sit-out"><span>💰 Do sítě</span> <span class="val" style="color: #34d399;">{radek_bal["Přetok do DS"] * 4:.2f} kW</span></div>',
            unsafe_allow_html=True
        )

    if nabijeni_kw > 0.01:
        st.markdown(
            f'<div class="power-card c-bat"><span>⚡ Baterie (Nabíjení)</span> <span class="val" style="color: #38bdf8;">+{nabijeni_kw:.2f} kW</span></div>',
            unsafe_allow_html=True
        )
    elif vybijeni_kw > 0.01:
        st.markdown(
            f'<div class="power-card c-bat"><span>🔋 Baterie (Vybíjení)</span> <span class="val" style="color: #a855f7;">-{vybijeni_kw:.2f} kW</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="power-card c-bat"><span>💤 Baterie (V klidu)</span> <span class="val" style="color: #94a3b8;">0.00 kW</span></div>',
            unsafe_allow_html=True
        )
    
    barva = "#ef4444" if soc <= 5.5 else ("#f59e0b" if soc <= 10.5 else "#10b981")
    fig_bat = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soc,
        number={'suffix': " %", 'font': {'size': 35, 'color': barva}},
        title={'text': f"🔋 Baterie ({radek_bal['Stav baterie']:.1f} kWh)", 'font': {'size': 18, 'color': '#f8fafc'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': "#94a3b8"}},
            'bar': {'color': barva},
            'bgcolor': "rgba(15,23,42,0.8)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 5], 'color': "#7f1d1d"},
                {'range': [5, 10], 'color': "#78350f"},
                {'range': [10, 100], 'color': "#064e3b"}
            ]
        }
    ))
    fig_bat.update_layout(height=280, margin=dict(l=40, r=40, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bat, use_container_width=True)


# --- PRVNÍ GRAF: ZÁKLADNÍ TOKY + KŘIVKA NABITÍ BATERIE (SOC %) ---
st.markdown("---")
st.markdown("### 📈 Denní průběh energií, spotřeby (kW) a nabití baterie (%)")

soc_series = (
    df_bal[soc_col_name] * 100
    if soc_col_name and df_bal[soc_col_name].max() <= 1.05
    else (df_bal['Stav baterie'] / 20.0) * 100
)

fig_toky = go.Figure()
fig_toky.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'],
    y=df_bal['Výroba FVE'] * 4,
    mode='lines',
    name='Výroba FVE (kW)',
    line=dict(color='#fbbf24', width=3),
    fill='tozeroy',
    hovertemplate='%{y:.3f} kW<extra></extra>'
))
fig_toky.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'],
    y=df_bal['Spotřeba'] * 4,
    mode='lines',
    name='Příkon domu (kW)',
    line=dict(color='#ef4444', width=3),
    hovertemplate='%{y:.3f} kW<extra></extra>'
))
fig_toky.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'],
    y=df_bal['Odběr z DS'] * 4,
    mode='lines',
    name='Odběr ze sítě (kW)',
    line=dict(color='#38bdf8', width=2, dash='dash'),
    hovertemplate='%{y:.3f} kW<extra></extra>'
))
fig_toky.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'],
    y=soc_series,
    mode='lines',
    name='Stav baterie SOC (%)',
    yaxis='y2',
    line=dict(color='#10b981', width=2.5, dash='dot'),
    hovertemplate='%{y:.1f} %<extra></extra>'
))

fig_toky.add_shape(
    type="line",
    x0=zvoleny_cas, x1=zvoleny_cas,
    y0=0, y1=1,
    xref="x", yref="paper",
    line=dict(color="rgba(255, 255, 255, 0.75)", width=2, dash="solid")
)
fig_toky.add_annotation(
    x=zvoleny_cas, y=1.0,
    xref="x", yref="paper",
    text=f"⏱️ {zvoleny_cas}",
    showarrow=False,
    xanchor="left", yanchor="top",
    font=dict(color="#f8fafc", size=12),
    bgcolor="rgba(15, 23, 42, 0.85)"
)

max_y_toky = max(
    (df_bal['Výroba FVE'] * 4).max(),
    (df_bal['Spotřeba'] * 4).max(),
    (df_bal['Odběr z DS'] * 4).max()
) * 1.1 + 1

fig_toky.update_layout(
    title=dict(
        text="Základní toky výkonu (levá osa v kW) vs. Nabití baterie SOC (pravá osa v %)",
        font=dict(size=16, color="#e2e8f0")
    ),
    xaxis_title="",
    yaxis_title="Výkon (kW)",
    hovermode="x unified",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
    font=dict(color="#f8fafc", size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", type='category'), 
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, max_y_toky]),
    yaxis2=dict(
        title="Baterie SOC (%)",
        overlaying="y",
        side="right",
        range=[0, 105],
        showgrid=False,
        tickfont=dict(color="#10b981")
    ),
    margin=dict(t=45, b=10)
)
st.plotly_chart(fig_toky, use_container_width=True)


# --- DRUHÝ GRAF: SPOTŘEBIČE ---
fig_spotrebice = go.Figure()
distinct_colors = [
    '#38bdf8', '#a3e635', '#f87171', '#c084fc', '#fbbf24', '#2dd4bf',
    '#fb7185', '#818cf8', '#fcd34d', '#34d399', '#f472b6', '#60a5fa'
]

for idx_c, app_name in enumerate(vybrane_spotrebice):
    vykon_kw = pd.to_numeric(df_app_unique[app_name], errors='coerce').fillna(0) * 4
    fig_spotrebice.add_trace(go.Bar(
        x=df_bal['Čas_zobrazeni'],
        y=vykon_kw,
        name=app_name,
        marker_color=distinct_colors[idx_c % len(distinct_colors)],
        marker_line_color='rgba(255,255,255,0.3)',
        marker_line_width=1,
        hovertemplate='<b>%{y:.3f} kW</b><extra></extra>'
    ))

fig_spotrebice.add_shape(
    type="line",
    x0=zvoleny_cas, x1=zvoleny_cas,
    y0=0, y1=1,
    xref="x", yref="paper",
    line=dict(color="rgba(255, 255, 255, 0.75)", width=2, dash="solid")
)

if vybrane_spotrebice:
    df_vybrane = df_app_unique[vybrane_spotrebice].apply(pd.to_numeric, errors='coerce').fillna(0)
    max_y_spotrebice = max(df_vybrane.sum(axis=1).max() * 4 * 1.1 + 0.05, 0.2)
else:
    max_y_spotrebice = 1.0

fig_spotrebice.update_layout(
    title=dict(
        text="Energetická stopa spotřebičů (Z čeho se skládá celková spotřeba domu)",
        font=dict(size=16, color="#e2e8f0")
    ),
    barmode='stack',
    xaxis_title="Čas",
    yaxis_title="Příkon (kW)",
    hovermode="x unified", 
    height=600,
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, font=dict(size=13)),
    font=dict(color="#f8fafc", size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", type='category'), 
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, max_y_spotrebice]), 
    margin=dict(t=50, r=150)
)
st.plotly_chart(fig_spotrebice, use_container_width=True)


# --- TŘETÍ GRAF: INTERAKCE SE SÍTÍ ---
st.markdown("---")
st.markdown("### ⚡ Interakce s distribuční sítí (Nákup vs Prodej)")

fig_sit = go.Figure()

fig_sit.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'],
    y=df_bal['Odběr z DS'] * 4, 
    mode='lines',
    name='Nákup ze sítě', 
    line=dict(color='#ef4444', width=2),
    fill='tozeroy', 
    hovertemplate='<b>Nákup:</b> %{y:.3f} kW<extra></extra>'
))

fig_sit.add_trace(go.Scatter(
    x=df_bal['Čas_zobrazeni'],
    y=-df_bal['Přetok do DS'] * 4, 
    mode='lines',
    name='Prodej do sítě (Přetoky)', 
    line=dict(color='#10b981', width=2),
    fill='tozeroy', 
    customdata=df_bal['Přetok do DS'] * 4, 
    hovertemplate='<b>Prodej:</b> %{customdata:.3f} kW<extra></extra>'
))

fig_sit.add_shape(
    type="line",
    x0=zvoleny_cas, x1=zvoleny_cas,
    y0=0, y1=1,
    xref="x", yref="paper",
    line=dict(color="rgba(255, 255, 255, 0.75)", width=2, dash="solid")
)

max_y_sit = max((df_bal['Odběr z DS'] * 4).max() * 1.1 + 0.5, 2.0)
min_y_sit = min(-(df_bal['Přetok do DS'] * 4).max() * 1.1 - 0.5, -2.0)

fig_sit.update_layout(
    title=dict(
        text="Zrcadlová bilance: Kdy síť zatěžujeme a kdy ji naopak krmíme",
        font=dict(size=16, color="#e2e8f0")
    ),
    xaxis_title="Čas",
    yaxis_title="Výkon (kW)",
    hovermode="x unified",
    height=350,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
    font=dict(color="#f8fafc", size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", type='category'), 
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zeroline=True,
        zerolinecolor="rgba(255,255,255,0.4)",
        zerolinewidth=2,
        range=[min_y_sit, max_y_sit]
    ), 
    margin=dict(t=50, b=10)
)
st.plotly_chart(fig_sit, use_container_width=True)


# --- NOVÁ SEKCE: ENERGETICKÁ A FINANČNÍ BILANCE DNE ---
st.markdown("---")
st.markdown("### 🍩 Celodenní energetická a finanční bilance")

col_d1, col_d2, col_fin = st.columns([1.2, 1.2, 1.0])

with col_d1:
    fig_kryti = go.Figure(go.Pie(
        labels=['Přímá FVE do domu', 'Vytaženo z baterie', 'Nákup ze sítě (DS)'],
        values=[prima_fve, spotreba_z_bat, celkovy_odber_ds],
        hole=0.58,
        marker=dict(colors=['#fbbf24', '#10b981', '#ef4444'], line=dict(color='#0f172a', width=2)),
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>%{value:.2f} kWh (%{percent})<extra></extra>'
    ))
    fig_kryti.update_layout(
        title=dict(text="Z čeho byl živen dům?", font=dict(size=15, color="#e2e8f0"), x=0.5),
        annotations=[dict(
            text=f"<b>{celkova_spotreba:.1f}</b><br>kWh",
            x=0.5, y=0.5, font_size=16, showarrow=False, font_color="#f8fafc"
        )],
        height=300, margin=dict(t=40, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"),
        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_kryti, use_container_width=True)

with col_d2:
    nabijeni_brutto = (
        df_bal['Nabíjení (Brutto)'].sum()
        if 'Nabíjení (Brutto)' in df_bal.columns
        else max(0.0, celkova_fve - prima_fve - celkovy_pretok_ds)
    )
    fig_vyuziti = go.Figure(go.Pie(
        labels=['Spotřebováno přímo', 'Uloženo do baterie', 'Prodáno do sítě (Přetok)'],
        values=[prima_fve, nabijeni_brutto, celkovy_pretok_ds],
        hole=0.58,
        marker=dict(colors=['#fbbf24', '#38bdf8', '#34d399'], line=dict(color='#0f172a', width=2)),
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>%{value:.2f} kWh (%{percent})<extra></extra>'
    ))
    fig_vyuziti.update_layout(
        title=dict(text="Kam šla vyrobená FVE?", font=dict(size=15, color="#e2e8f0"), x=0.5),
        annotations=[dict(
            text=f"<b>{celkova_fve:.1f}</b><br>kWh",
            x=0.5, y=0.5, font_size=16, showarrow=False, font_color="#f8fafc"
        )],
        height=300, margin=dict(t=40, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"),
        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_vyuziti, use_container_width=True)

with col_fin:
    naklady_bez_fve = celkova_spotreba * cena_nakup
    naklady_s_fve = (celkovy_odber_ds * cena_nakup) - (celkovy_pretok_ds * cena_vykup)
    uspora_kc = naklady_bez_fve - naklady_s_fve

    st.markdown(f"""
    <div class="fin-card" style="margin-bottom: 12px;">
        <div class="fin-title">Náklady na den BEZ FVE</div>
        <div class="fin-value" style="color: #ef4444;">{naklady_bez_fve:.0f} Kč</div>
    </div>
    <div class="fin-card" style="margin-bottom: 12px;">
        <div class="fin-title">Skutečný náklad S FVE (po odečtení přetoků)</div>
        <div class="fin-value" style="color: #38bdf8;">{naklady_s_fve:.0f} Kč</div>
    </div>
    <div class="fin-card" style="border-color: rgba(16, 185, 129, 0.5);">
        <div class="fin-title">✨ Čistá denní úspora díky FVE</div>
        <div class="fin-value" style="color: #10b981;">+{uspora_kc:.0f} Kč</div>
    </div>
    """, unsafe_allow_html=True)


# --- ŽEBŘÍČEK ŽROUTŮ ENERGIE (ROZŠÍŘENÁ ANALYTICKÁ TABULKA) ---
st.markdown("---")
st.markdown("### 🥇 Žebříček žroutů (Detailní analýza spotřebičů)")

rows_zrouti = []
celkova_vybrana_kwh = sum(
    pd.to_numeric(df_app_unique[c], errors='coerce').fillna(0).sum()
    for c in vybrane_spotrebice
)

for c in vybrane_spotrebice:
    s_col = pd.to_numeric(df_app_unique[c], errors='coerce').fillna(0)
    suma_kwh = s_col.sum()
    if suma_kwh > 0:
        spicka_kw = (s_col * 4).max()
        doba_hod = (s_col > 0).sum() * 0.25
        podil_pct = (suma_kwh / celkova_vybrana_kwh * 100) if celkova_vybrana_kwh > 0 else 0
        odhad_kc = suma_kwh * cena_nakup
        bar_len = int(round(podil_pct / 5))
        viz_pruh = "█" * bar_len + "░" * (20 - bar_len)
        rows_zrouti.append({
            "Spotřebič": c,
            "Spotřeba (kWh)": f"{suma_kwh:.3f}",
            "Podíl (%)": f"{podil_pct:.1f} %",
            "Vizualizace podílu": viz_pruh,
            "Špičkový příkon (kW)": f"{spicka_kw:.3f}",
            "Doba běhu (hod)": f"{doba_hod:.2f} h",
            "Hodnota energie (Kč)": f"{odhad_kc:.1f} Kč",
            "_sort": suma_kwh
        })

if rows_zrouti:
    df_zrouti = pd.DataFrame(rows_zrouti).sort_values(by="_sort", ascending=False).drop(columns=["_sort"])
    st.markdown(df_zrouti.to_html(index=False, classes='table table-striped', justify='left'), unsafe_allow_html=True)
    st.markdown("""<style>.table { width: 100%; color: #f8fafc; border-collapse: collapse; font-size: 15px; } .table th, .table td { padding: 11px 14px; border-bottom: 1px solid #334155; } .table th { background-color: rgba(15,23,42,0.85); color: #38bdf8 !important; } .table-striped tbody tr:nth-of-type(odd) { background-color: rgba(30,41,59,0.35); }</style>""", unsafe_allow_html=True)


# --- SROVNÁNÍ VŠECH 6 SCÉNÁŘŮ V EXCELU ---
st.markdown("---")
with st.expander("🌍 Celoroční porovnání všech 6 scénářů (Leden vs. Červenec vs. Říjen)"):
    @st.cache_data
    def load_all_scenarios(file_path, _sheet_map):
        prehled = []
        for nazev, (sb, sd) in _sheet_map.items():
            dfb, _, _ = load_data(file_path, sb, sd)
            fve_s = dfb['Výroba FVE'].sum()
            spot_s = dfb['Spotřeba'].sum()
            odb_s = dfb['Odběr z DS'].sum()
            pret_s = dfb['Přetok do DS'].sum()
            sob_s = (1.0 - odb_s / spot_s) * 100 if spot_s > 0 else 0
            prehled.append({
                "Období": nazev,
                "Výroba FVE (kWh)": round(fve_s, 2),
                "Spotřeba domu (kWh)": round(spot_s, 2),
                "Odběr ze sítě (kWh)": round(odb_s, 2),
                "Přetoky do sítě (kWh)": round(pret_s, 2),
                "Soběstačnost (%)": round(sob_s, 1)
            })
        return pd.DataFrame(prehled)

    df_all = load_all_scenarios(EXCEL_PATH, sheet_map)
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=df_all["Období"], y=df_all["Výroba FVE (kWh)"],
        name="Výroba FVE (kWh)", marker_color="#fbbf24"
    ))
    fig_comp.add_trace(go.Bar(
        x=df_all["Období"], y=df_all["Spotřeba domu (kWh)"],
        name="Spotřeba domu (kWh)", marker_color="#ef4444"
    ))
    fig_comp.add_trace(go.Bar(
        x=df_all["Období"], y=df_all["Odběr ze sítě (kWh)"],
        name="Odběr ze sítě (kWh)", marker_color="#38bdf8"
    ))
    fig_comp.add_trace(go.Bar(
        x=df_all["Období"], y=df_all["Přetoky do sítě (kWh)"],
        name="Přetoky do sítě (kWh)", marker_color="#10b981"
    ))
    fig_comp.update_layout(
        barmode="group", height=360,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"), margin=dict(t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_comp, use_container_width=True)
    st.dataframe(df_all, use_container_width=True, hide_index=True)