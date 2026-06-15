import re
import math
import streamlit as st
import requests
import pandas as pd
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Catchment Area Analyse", page_icon="🎯", layout="wide")
st.title("🎯 Catchment Area Analyse")
st.caption("Teken een cirkel of polygoon • Alle postcodes binnen het gebied worden geanalyseerd")

BASE    = "https://opendata.cbs.nl/ODataApi/OData/83502NED"
HH_BASE = "https://opendata.cbs.nl/ODataApi/OData/83505NED"
HK_BASE = "https://opendata.cbs.nl/ODataApi/OData/85640NED"

# ── Statische PC4 centroïden ───────────────────────────────────────────────────
# Ankerpunten per 2-cijferig postcodeprefix (lat, lon)
_ANCHORS = {
    10:(52.37,4.90), 11:(52.37,4.89), 12:(52.38,4.87), 13:(52.37,5.22),
    14:(52.37,4.84), 15:(52.44,4.83), 16:(52.46,4.79), 17:(52.50,4.80),
    18:(52.50,4.73), 19:(52.47,4.66), 20:(52.38,4.64), 21:(52.39,4.64),
    22:(52.25,4.53), 23:(52.17,4.47), 24:(52.17,4.42), 25:(52.07,4.32),
    26:(52.07,4.28), 27:(52.07,4.38), 28:(52.07,4.40), 29:(51.97,4.28),
    30:(51.92,4.48), 31:(51.90,4.46), 32:(51.92,4.40), 33:(51.88,4.54),
    34:(51.87,4.68), 35:(51.85,4.35), 36:(51.87,4.60), 37:(51.88,4.76),
    38:(51.82,4.65), 39:(51.82,4.43), 40:(51.91,5.00), 41:(51.87,4.93),
    42:(51.89,4.58), 43:(51.65,3.90), 44:(51.50,3.85), 45:(51.53,4.47),
    46:(51.57,4.55), 47:(51.60,4.62), 48:(51.57,4.48), 49:(51.52,4.46),
    50:(51.57,5.08), 51:(51.57,5.09), 52:(51.43,5.48), 53:(51.45,5.50),
    54:(51.52,5.17), 55:(51.42,5.48), 56:(51.50,5.62), 57:(51.70,5.30),
    58:(51.73,5.32), 59:(51.43,6.10), 60:(51.85,5.87), 61:(51.85,5.88),
    62:(50.85,5.68), 63:(51.20,5.98), 64:(51.52,5.98), 65:(51.85,5.88),
    66:(51.97,5.93), 67:(51.97,5.92), 68:(51.97,6.00), 69:(52.00,6.20),
    70:(52.00,6.20), 71:(52.17,6.15), 72:(52.22,6.18), 73:(52.22,6.90),
    74:(52.22,6.22), 75:(52.22,6.90), 76:(52.52,6.10), 77:(52.52,6.11),
    78:(52.50,6.10), 79:(52.50,6.48), 80:(52.52,6.10), 81:(52.50,6.09),
    82:(52.52,5.47), 83:(52.30,5.55), 84:(52.17,5.40), 85:(52.07,5.12),
    86:(52.08,5.12), 87:(52.20,5.45), 88:(52.22,5.50), 89:(52.10,5.12),
    90:(53.22,6.57), 91:(53.22,6.57), 92:(52.75,6.92), 93:(52.85,6.35),
    94:(52.87,6.55), 95:(53.10,6.88), 96:(53.32,6.30), 97:(53.20,5.75),
    98:(53.20,5.72), 99:(52.93,5.85),
}

def _build_centroids():
    c = {}
    for pc_int in range(1000, 10000):
        pc = str(pc_int)
        prefix = int(pc[:2])
        if prefix in _ANCHORS:
            base_lat, base_lon = _ANCHORS[prefix]
            suffix = int(pc[2:])
            c[pc] = (
                round(base_lat + (suffix // 10 - 5) * 0.003, 4),
                round(base_lon + (suffix %  10 - 5) * 0.004, 4),
            )
    return c

PC4_CENTROIDS = _build_centroids()

# ── CBS labels ─────────────────────────────────────────────────────────────────
LABEL_MAP = {
    "0 tot 5 jaar":"0-5","5 tot 10 jaar":"5-10","10 tot 15 jaar":"10-15",
    "15 tot 20 jaar":"15-20","20 tot 25 jaar":"20-25","25 tot 30 jaar":"25-30",
    "30 tot 35 jaar":"30-35","35 tot 40 jaar":"35-40","40 tot 45 jaar":"40-45",
    "45 tot 50 jaar":"45-50","50 tot 55 jaar":"50-55","55 tot 60 jaar":"55-60",
    "60 tot 65 jaar":"60-65","65 tot 70 jaar":"65-70","70 tot 75 jaar":"70-75",
    "75 tot 80 jaar":"75-80","80 tot 85 jaar":"80-85","85 tot 90 jaar":"85-90",
    "90 jaar of ouder":"90+",
}
GEWENSTE        = list(LABEL_MAP.keys())
LABELS_VOLGORDE = list(LABEL_MAP.values())
GEWICHTEN = {
    "0-5":2.5,"5-10":7.5,"10-15":12.5,"15-20":17.5,"20-25":22.5,
    "25-30":27.5,"30-35":32.5,"35-40":37.5,"40-45":42.5,"45-50":47.5,
    "50-55":52.5,"55-60":57.5,"60-65":62.5,"65-70":67.5,"70-75":72.5,
    "75-80":77.5,"80-85":82.5,"85-90":87.5,"90+":92.5,
}
HK_GEWENST = {
    "Totaal":"Totaal","Nederland":"Nederland",
    "Europa (exclusief Nederland)":"Europa (excl. NL)",
    "Afrika":"Afrika","Amerika":"Amerika","Azië":"Azië",
    "Turkije":"Turkije","Marokko":"Marokko","Suriname":"Suriname",
}
HK_CAT   = ["Nederland","Europa (excl. NL)","Turkije","Marokko","Suriname","Afrika","Amerika","Azië"]
HH_TYPEN = {
    "Eenpersoonshuishouden":"Alleenstaand",
    "Meerpersoonshuishouden met kinderen":"Gezin met kinderen",
    "Meerpersoonshuishouden zonder kinderen":"Stel/meerp. zonder kinderen",
}

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("gebied", None), ("gevonden_pcs", []),
    ("kaart_center", [52.15, 5.30]), ("kaart_zoom", 8),
    ("gebied_label", ""), ("analyse_klaar", False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── CBS helpers ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch(url):
    rows, nxt = [], url
    while nxt:
        r = requests.get(nxt, timeout=30)
        r.raise_for_status()
        d = r.json()
        rows.extend(d.get("value", []))
        nxt = d.get("odata.nextLink")
    return rows

@st.cache_data(ttl=3600)
def get_leeftijd_meta():
    perioden      = fetch(f"{BASE}/Perioden?$format=json")
    periode_key   = perioden[-1]["Key"]
    periode_title = perioden[-1]["Title"].strip()
    leeftijden    = fetch(f"{BASE}/Leeftijd?$format=json")
    leeftijd_map  = {l["Key"].strip(): l["Title"].strip() for l in leeftijden}
    leeftijd_keys = [k for k,v in leeftijd_map.items() if v in GEWENSTE]
    geslachten    = fetch(f"{BASE}/Geslacht?$format=json")
    geslacht_key  = next(g["Key"] for g in geslachten if "Totaal" in g["Title"])
    alle_pc       = fetch(f"{BASE}/Postcode?$format=json")
    pc_key_map    = {item["Title"].strip(): item["Key"] for item in alle_pc}
    return periode_key, periode_title, leeftijd_map, leeftijd_keys, geslacht_key, pc_key_map

@st.cache_data(ttl=3600)
def get_leeftijd_verd(pc_key, periode_key, geslacht_key, leeftijd_keys, leeftijd_map):
    out = {}
    for lkey in leeftijd_keys:
        obs = fetch(
            f"{BASE}/TypedDataSet?$format=json"
            f"&$filter=Perioden eq '{periode_key}' and Geslacht eq '{geslacht_key}'"
            f" and Postcode eq '{pc_key}' and Leeftijd eq '{lkey}'"
            f"&$select=Leeftijd,Bevolking_1"
        )
        for row in obs:
            label = LABEL_MAP.get(leeftijd_map.get(row.get("Leeftijd","").strip(),""))
            if label:
                out[label] = out.get(label,0) + (row.get("Bevolking_1") or 0)
    return out

@st.cache_data(ttl=3600)
def get_hh_meta():
    perioden = fetch(f"{HH_BASE}/Perioden?$format=json")
    per_key  = perioden[-1]["Key"]
    hh_typen = fetch(f"{HH_BASE}/Huishoudenssamenstelling?$format=json")
    hh_map   = {h["Key"].strip(): h["Title"].strip() for h in hh_typen}
    alle_pc  = fetch(f"{HH_BASE}/Postcode?$format=json")
    pc_map   = {item["Title"].strip(): item["Key"] for item in alle_pc}
    return per_key, hh_map, pc_map

@st.cache_data(ttl=3600)
def get_hh_data(pc_key, periode_key, hh_map):
    obs = fetch(
        f"{HH_BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq '{periode_key}' and Postcode eq '{pc_key}'"
        f"&$select=Huishoudenssamenstelling,ParticuliereHuishoudens_1,GemiddeldeHuishoudensgrootte_2"
    )
    d = {}
    for row in obs:
        titel = hh_map.get(row.get("Huishoudenssamenstelling","").strip(),"")
        if titel in HH_TYPEN:
            d[HH_TYPEN[titel]] = row.get("ParticuliereHuishoudens_1") or 0
        if titel == "Totaal particuliere huishoudens":
            d["__totaal"]  = row.get("ParticuliereHuishoudens_1") or 0
            d["__grootte"] = row.get("GemiddeldeHuishoudensgrootte_2") or 0
    return d

@st.cache_data(ttl=3600)
def get_hk_meta():
    perioden   = fetch(f"{HK_BASE}/Perioden?$format=json")
    per_key    = perioden[-1]["Key"]
    hk_landen  = fetch(f"{HK_BASE}/Herkomstland?$format=json")
    hk_map     = {h["Key"].strip(): h["Title"].strip() for h in hk_landen}
    gb_landen  = fetch(f"{HK_BASE}/Geboorteland?$format=json")
    gb_totaal  = next((g["Key"] for g in gb_landen if "Totaal" in g["Title"]), None)
    geslachten = fetch(f"{HK_BASE}/Geslacht?$format=json")
    gsl_key    = next(g["Key"] for g in geslachten if "Totaal" in g["Title"])
    alle_pc    = fetch(f"{HK_BASE}/Postcode?$format=json")
    pc_map     = {item["Title"].strip(): item["Key"] for item in alle_pc}
    return per_key, hk_map, gb_totaal, gsl_key, pc_map

@st.cache_data(ttl=3600)
def get_hk_data(pc_key, periode_key, gb_totaal, gsl_key, hk_map):
    obs = fetch(
        f"{HK_BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq '{periode_key}' and Geboorteland eq '{gb_totaal}'"
        f" and Geslacht eq '{gsl_key}' and Postcode eq '{pc_key}'"
        f"&$select=Herkomstland,Bevolking_1"
    )
    result = {}
    for row in obs:
        titel = hk_map.get(row.get("Herkomstland","").strip(),"")
        if titel in HK_GEWENST:
            result[HK_GEWENST[titel]] = row.get("Bevolking_1") or 0
    return result

# ── PDOK geocode (voor zoekfunctie) ───────────────────────────────────────────
@st.cache_data(ttl=3600)
def geocode(zoekterm):
    try:
        r = requests.get(
            "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free",
            params={"q": zoekterm, "rows": 1, "fl": "centroide_ll,weergavenaam"},
            timeout=6
        )
        if r.status_code == 200:
            docs = r.json().get("response",{}).get("docs",[])
            if docs:
                centroide = docs[0].get("centroide_ll","")
                naam = docs[0].get("weergavenaam","")
                m = re.search(r'POINT\(([0-9.]+)\s+([0-9.]+)\)', centroide)
                if m:
                    return float(m.group(2)), float(m.group(1)), naam
    except Exception:
        pass
    return None, None, None

# ── Geometrie helpers ──────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((phi2-phi1)/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(math.radians(lon2-lon1)/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def punt_in_polygoon(lat, lon, polygon_coords):
    x, y, inside, j = lon, lat, False, len(polygon_coords)-1
    for i in range(len(polygon_coords)):
        xi, yi = polygon_coords[i]
        xj, yj = polygon_coords[j]
        if ((yi>y) != (yj>y)) and (x < (xj-xi)*(y-yi)/(yj-yi+1e-10)+xi):
            inside = not inside
        j = i
    return inside

def meter_naar_graad_lat(m): return m / 111320
def meter_naar_graad_lon(m, lat): return m / (111320 * math.cos(math.radians(lat)))

# ── Rekenhulpen ────────────────────────────────────────────────────────────────
def combineer(verds):
    out = {}
    for v in verds:
        for k,a in v.items(): out[k] = out.get(k,0)+a
    return out

def pct(verd):
    tot = sum(verd.values())
    return {k: v/tot*100 for k,v in verd.items()} if tot else {}

def gem_leeftijd_fn(verd):
    tot = sum(verd.values())
    return sum(GEWICHTEN[k]*v for k,v in verd.items())/tot if tot else None

# ── Data laden ─────────────────────────────────────────────────────────────────
with st.spinner("Metadata laden..."):
    periode_key, periode_title, leeftijd_map, leeftijd_keys, geslacht_key, pc_key_map = get_leeftijd_meta()
    hh_per_key, hh_map_meta, hh_pc_map = get_hh_meta()
    hk_per_key, hk_map_meta, gb_totaal, gsl_key, hk_pc_map = get_hk_meta()

# Filter PC4_CENTROIDS op alleen bekende CBS-postcodes
bekende_pcs = set(pc_key_map.keys())
PC4_CENTROIDS_FILTERED = {pc: v for pc, v in PC4_CENTROIDS.items() if pc in bekende_pcs}

# ── Zijbalk ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📍 Locatie zoeken")
    zoek_input = st.text_input("Adres, postcode of plaatsnaam",
                               placeholder="bijv. Kalverstraat Amsterdam")

    if st.button("🔍 Zoek & zoom in", use_container_width=True):
        if zoek_input:
            lat, lon, naam = geocode(zoek_input)
            if lat:
                st.session_state.kaart_center = [lat, lon]
                st.session_state.kaart_zoom   = 14
                st.success(f"📍 {naam}")
            else:
                st.error("Locatie niet gevonden.")

    st.divider()
    st.header("✏️ Tekentools")
    st.markdown("""
**Op de kaart (linksboven):**
- ⬛ **Polygoon** — klik punten, dubbelklik sluiten
- 🔴 **Cirkel** — klik middelpunt, sleep voor straal
- 🗑️ **Prullenbak** — wis het gebied

Klik daarna op **▶ Analyseer** hieronder.
    """)

    analyseer_btn = st.button("▶ Analyseer gebied", type="primary",
                              use_container_width=True)

    st.divider()
    max_pcs = st.slider("Max. postcodes", 5, 40, 15,
                        help="Meer = vollediger maar trager")
    st.caption(f"Peiljaar: {periode_title}")
    st.caption(f"{len(PC4_CENTROIDS_FILTERED):,} postcodes beschikbaar")

# ── Kaart ──────────────────────────────────────────────────────────────────────
col_kaart, col_result = st.columns([3, 2], gap="medium")

with col_kaart:
    m = folium.Map(
        location=st.session_state.kaart_center,
        zoom_start=st.session_state.kaart_zoom,
        tiles="CartoDB positron",
    )

    Draw(
        draw_options={
            "polyline": False, "rectangle": False,
            "marker": False, "circlemarker": False,
            "polygon": {"allowIntersection": False, "showArea": True, "metric": True},
            "circle": {"showRadius": True, "metric": True, "feet": False},
        },
        edit_options={"edit": True, "remove": True},
        position="topleft",
    ).add_to(m)

    # Toon eerder getekend gebied
    if st.session_state.gebied:
        g = st.session_state.gebied
        if g["type"] == "cirkel":
            folium.Circle(
                location=[g["lat"], g["lon"]], radius=g["straal"],
                color="#1D9E75", weight=2, fill=True, fill_opacity=0.12,
            ).add_to(m)
            folium.Marker(
                location=[g["lat"], g["lon"]],
                icon=folium.DivIcon(
                    html=(f'<div style="background:white;padding:3px 8px;border-radius:4px;'
                          f'border:1.5px solid #1D9E75;font-size:12px;font-weight:600;'
                          f'color:#1D9E75;white-space:nowrap;box-shadow:0 1px 3px rgba(0,0,0,.2)">'
                          f'⭕ {g["straal"]:.0f} m</div>'),
                    icon_size=(110, 26), icon_anchor=(55, 13),
                )
            ).add_to(m)
        elif g["type"] == "polygoon":
            folium.Polygon(
                locations=[[c[1],c[0]] for c in g["coords"]],
                color="#1D9E75", weight=2, fill=True, fill_opacity=0.12,
            ).add_to(m)

    # Gevonden postcodes
    for pc, lat_c, lon_c in st.session_state.gevonden_pcs:
        folium.CircleMarker(
            location=[lat_c, lon_c], radius=6,
            color="#1D9E75", fill=True, fill_color="#1D9E75",
            fill_opacity=0.8, tooltip=f"📮 {pc}",
        ).add_to(m)

    kaart_output = st_folium(
        m, width="100%", height=580,
        returned_objects=["all_drawings"],
        key="tekenkaart",
    )

    # Verwerk getekende vormen
    drawings = (kaart_output or {}).get("all_drawings") or []
    if drawings:
        laatste = drawings[-1]
        geom  = laatste.get("geometry", {})
        gtype = geom.get("type","")
        props = laatste.get("properties", {})

        if gtype == "Point" and props.get("radius"):
            lon_c, lat_c = geom["coordinates"]
            nieuw = {"type":"cirkel","lat":lat_c,"lon":lon_c,"straal":float(props["radius"])}
        elif gtype == "Polygon":
            nieuw = {"type":"polygoon","coords":geom["coordinates"][0]}
        else:
            nieuw = None

        if nieuw:
            st.session_state.gebied = nieuw
            st.session_state.analyse_klaar = False

# ── Analyse ────────────────────────────────────────────────────────────────────
if analyseer_btn:
    if not st.session_state.gebied:
        st.warning("Teken eerst een gebied op de kaart.")
    else:
        g = st.session_state.gebied

        if g["type"] == "cirkel":
            gevonden = [
                (pc, lat, lon)
                for pc, (lat, lon) in PC4_CENTROIDS_FILTERED.items()
                if haversine(g["lat"], g["lon"], lat, lon) <= g["straal"]
            ]
            st.session_state.gebied_label = f"Cirkel ⌀ {g['straal']*2/1000:.1f} km"
        else:
            gevonden = [
                (pc, lat, lon)
                for pc, (lat, lon) in PC4_CENTROIDS_FILTERED.items()
                if punt_in_polygoon(lat, lon, g["coords"])
            ]
            st.session_state.gebied_label = "Getekend gebied"

        if not gevonden:
            st.warning("Geen postcodes gevonden in dit gebied. Zoom verder in en teken een kleiner gebied.")
        else:
            st.session_state.gevonden_pcs  = sorted(gevonden, key=lambda x: x[0])
            st.session_state.analyse_klaar = True
            st.rerun()

# ── Resultaten ─────────────────────────────────────────────────────────────────
with col_result:
    if not st.session_state.analyse_klaar or not st.session_state.gevonden_pcs:
        st.markdown("""
### 👈 Aan de slag

1. **Zoek** een locatie links (bijv. een straat of postcode)
2. **Zoom in** op je gewenste gebied
3. **Teken** een cirkel 🔴 of polygoon ⬛
4. Klik **▶ Analyseer gebied**

---
**Tip voor retailers:** Teken een cirkel van 1–2 km rondom een (potentiële) winkellocatie voor een catchment area analyse.
        """)
    else:
        pcs_data = st.session_state.gevonden_pcs
        label    = st.session_state.gebied_label
        pcs_list = [p[0] for p in pcs_data]

        st.subheader(f"📊 {label}")
        st.caption(f"{len(pcs_list)} postcodes: {', '.join(pcs_list[:8])}{'…' if len(pcs_list)>8 else ''}")

        pcs_te_laden = pcs_list[:max_pcs]
        if len(pcs_list) > max_pcs:
            st.info(f"Analyse op {max_pcs} van de {len(pcs_list)} postcodes.")

        with st.spinner(f"CBS data ophalen voor {len(pcs_te_laden)} postcodes..."):
            verdelingen, hh_res, hk_res = {}, {}, {}
            prog = st.progress(0)
            for i, pc in enumerate(pcs_te_laden):
                prog.progress((i+1)/len(pcs_te_laden), text=f"Postcode {pc}...")
                key = pc_key_map.get(pc)
                if key:
                    v = get_leeftijd_verd(key, periode_key, geslacht_key, leeftijd_keys, leeftijd_map)
                    if v: verdelingen[pc] = v
                hh_key = hh_pc_map.get(pc)
                if hh_key:
                    d = get_hh_data(hh_key, hh_per_key, hh_map_meta)
                    if d: hh_res[pc] = d
                hk_key = hk_pc_map.get(pc)
                if hk_key:
                    d = get_hk_data(hk_key, hk_per_key, gb_totaal, gsl_key, hk_map_meta)
                    if d: hk_res[pc] = d
            prog.empty()

        if not verdelingen:
            st.warning("Geen CBS data gevonden voor dit gebied.")
        else:
            verd_agg = combineer(list(verdelingen.values()))
            hh_agg   = combineer(list(hh_res.values()))
            hk_agg   = combineer(list(hk_res.values()))

            tab1, tab2, tab3 = st.tabs(["👥 Leeftijd", "🏠 Huishoudens", "🌍 Herkomst"])

            with tab1:
                tot  = sum(verd_agg.values())
                gem  = gem_leeftijd_fn(verd_agg)
                oud  = sum(v for k,v in verd_agg.items() if k in ["65-70","70-75","75-80","80-85","85-90","90+"])
                jong = sum(v for k,v in verd_agg.items() if k in ["0-5","5-10","10-15","15-20","20-25"])
                c1,c2 = st.columns(2)
                c1.metric("Inwoners",      f"{int(tot):,}".replace(",","."))
                c2.metric("Gem. leeftijd", f"{gem:.1f} jaar" if gem else "—")
                c3,c4 = st.columns(2)
                c3.metric("Aandeel 65+",  f"{oud/tot*100:.1f}%")
                c4.metric("Aandeel 0-25", f"{jong/tot*100:.1f}%")
                df = pd.DataFrame([
                    {"Leeftijdsgroep": lbl, "%": round(pct(verd_agg).get(lbl,0),1)}
                    for lbl in LABELS_VOLGORDE
                ])
                fig = px.bar(df, x="Leeftijdsgroep", y="%",
                             color_discrete_sequence=["#1D9E75"], height=250)
                fig.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                    yaxis=dict(showgrid=True, gridcolor="#eee", title=""),
                    margin=dict(t=8, b=50, l=30, r=8), showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                if not hh_agg:
                    st.info("Geen huishoudensdata.")
                else:
                    tot_hh = hh_agg.get("__totaal",1) or 1
                    c1,c2 = st.columns(2)
                    c1.metric("Huishoudens",  f"{int(tot_hh):,}".replace(",","."))
                    c2.metric("Gem. grootte", f"{hh_agg.get('__grootte',0):.1f} pers.")
                    pie = {k:v for k,v in hh_agg.items() if not k.startswith("__") and v>0}
                    if pie:
                        fig_p = px.pie(names=list(pie.keys()), values=list(pie.values()),
                                       color_discrete_sequence=["#1D9E75","#185FA5","#BA7517"],
                                       hole=0.45, height=250)
                        fig_p.update_layout(margin=dict(t=8,b=8,l=8,r=8),
                                            legend=dict(font=dict(size=10)))
                        st.plotly_chart(fig_p, use_container_width=True)
                        tot_pie = sum(pie.values())
                        for k,v in pie.items():
                            st.write(f"**{k}:** {v/tot_pie*100:.1f}%")

            with tab3:
                if not hk_agg:
                    st.info("Geen herkomstdata.")
                else:
                    tot_hk = hk_agg.get("Totaal",1) or 1
                    pct_nl = hk_agg.get("Nederland",0)/tot_hk*100
                    c1,c2 = st.columns(2)
                    c1.metric("Herkomst NL",       f"{pct_nl:.1f}%")
                    c2.metric("Herkomst buiten NL", f"{100-pct_nl:.1f}%")
                    hk_df = pd.DataFrame([
                        {"Herkomst": cat, "%": round(hk_agg.get(cat,0)/tot_hk*100,1)}
                        for cat in HK_CAT if hk_agg.get(cat,0)>0
                    ])
                    if not hk_df.empty:
                        fig_h = px.bar(hk_df, x="%", y="Herkomst", orientation="h",
                                       color_discrete_sequence=["#534AB7"], height=260)
                        fig_h.update_layout(
                            plot_bgcolor="white", paper_bgcolor="white",
                            xaxis=dict(showgrid=True, gridcolor="#eee"),
                            yaxis=dict(autorange="reversed"),
                            margin=dict(t=8, b=30, l=8, r=8), showlegend=False,
                        )
                        st.plotly_chart(fig_h, use_container_width=True)

st.divider()
st.caption("Data: CBS StatLine (CC BY 4.0) | Geodata: PDOK | App gebouwd met Streamlit")
