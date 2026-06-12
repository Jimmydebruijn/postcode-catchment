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
st.caption("Teken een cirkel of polygoon op de kaart • Alle postcodes binnen het gebied worden geanalyseerd")

BASE    = "https://opendata.cbs.nl/ODataApi/OData/83502NED"
HH_BASE = "https://opendata.cbs.nl/ODataApi/OData/83505NED"
HK_BASE = "https://opendata.cbs.nl/ODataApi/OData/85640NED"

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
HK_CAT = ["Nederland","Europa (excl. NL)","Turkije","Marokko","Suriname","Afrika","Amerika","Azië"]
HH_TYPEN = {
    "Eenpersoonshuishouden":"Alleenstaand",
    "Meerpersoonshuishouden met kinderen":"Gezin met kinderen",
    "Meerpersoonshuishouden zonder kinderen":"Stel/meerp. zonder kinderen",
}

# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [
    ("getekend_gebied", None),
    ("gevonden_pcs", []),
    ("kaart_center", [52.15, 5.3]),
    ("kaart_zoom", 7),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── CBS fetch ──────────────────────────────────────────────────────────────────
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

# ── Postcodecentroïden via PDOK ────────────────────────────────────────────────
@st.cache_data(ttl=86400)
def get_pc4_centroids():
    """Haal centroïden van alle 4-cijferige postcodes op via PDOK WFS."""
    try:
        url = (
            "https://service.pdok.nl/cbs/gebiedsindelingen/2024/wfs/v1_0"
            "?service=WFS&version=2.0.0&request=GetFeature"
            "&typeName=postcode4_gegeneraliseerd&outputFormat=json"
            "&propertyName=postcode4,geom"
        )
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            features = r.json().get("features", [])
            centroids = {}
            for f in features:
                pc = f["properties"].get("postcode4","").strip()
                geom = f.get("geometry",{})
                if geom.get("type") == "Point":
                    lon, lat = geom["coordinates"]
                    centroids[pc] = (lat, lon)
                elif geom.get("type") in ("Polygon","MultiPolygon"):
                    # Bereken centroïde van bbox
                    coords = geom["coordinates"]
                    all_coords = []
                    def extract(c):
                        if isinstance(c[0], list):
                            for s in c: extract(s)
                        else:
                            all_coords.append(c)
                    extract(coords)
                    if all_coords:
                        lons = [c[0] for c in all_coords]
                        lats = [c[1] for c in all_coords]
                        centroids[pc] = (sum(lats)/len(lats), sum(lons)/len(lons))
            return centroids
    except Exception:
        pass
    return {}

# ── Geometrie helpers ──────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    """Afstand in meters tussen twee GPS-coördinaten."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def punt_in_polygoon(lat, lon, polygon_coords):
    """Ray casting algoritme: ligt punt (lat,lon) in polygoon?
    polygon_coords: lijst van [lon, lat] paren (GeoJSON volgorde)."""
    x, y = lon, lat
    n = len(polygon_coords)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon_coords[i]
        xj, yj = polygon_coords[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
            inside = not inside
        j = i
    return inside

def postcodes_in_cirkel(centroiden, center_lat, center_lon, straal_m):
    return [
        pc for pc, (lat, lon) in centroiden.items()
        if haversine(center_lat, center_lon, lat, lon) <= straal_m
    ]

def postcodes_in_polygoon(centroiden, polygon_coords):
    return [
        pc for pc, (lat, lon) in centroiden.items()
        if punt_in_polygoon(lat, lon, polygon_coords)
    ]

# ── PDOK geocode ───────────────────────────────────────────────────────────────
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

with st.spinner("Postcode centroïden laden (eenmalig)..."):
    pc4_centroids = get_pc4_centroids()

# ── Zijbalk ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📍 Zoeken")
    zoek_input = st.text_input("Adres, postcode of plaatsnaam",
                               placeholder="bijv. Leidsestraat Amsterdam")

    if st.button("🔍 Zoeken", use_container_width=True) and zoek_input:
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
    **Gebruik de knoppen op de kaart:**
    - ⬜ **Polygoon** — vrije vorm tekenen
    - ⭕ **Cirkel** — klik en sleep voor straal
    - 🗑️ **Verwijder** — gebied wissen

    Teken één gebied → de postcodes binnen dat gebied worden automatisch geanalyseerd.
    """)

    st.divider()
    st.header("⚙️ Instellingen")
    max_pcs = st.slider("Max. postcodes te analyseren", 5, 50, 20,
                        help="Meer postcodes = vollediger maar trager")

    st.divider()
    st.caption(f"Peiljaar: {periode_title}")
    if pc4_centroids:
        st.caption(f"{len(pc4_centroids):,} postcodes geladen")

# ── Kaart ──────────────────────────────────────────────────────────────────────
col_kaart, col_result = st.columns([3, 2], gap="medium")

with col_kaart:
    m = folium.Map(
        location=st.session_state.kaart_center,
        zoom_start=st.session_state.kaart_zoom,
        tiles="CartoDB positron",
    )

    # Teken-plugin
    draw = Draw(
        draw_options={
            "polyline":  False,
            "rectangle": False,
            "marker":    False,
            "circlemarker": False,
            "polygon":   {"allowIntersection": False, "showArea": True},
            "circle":    {"showRadius": True, "metric": True},
        },
        edit_options={"edit": True, "remove": True},
        position="topleft",
    )
    draw.add_to(m)

    # Toon eerder getekend gebied opnieuw
    if st.session_state.getekend_gebied:
        gebied = st.session_state.getekend_gebied
        if gebied["type"] == "cirkel":
            folium.Circle(
                location=[gebied["lat"], gebied["lon"]],
                radius=gebied["straal"],
                color="#1D9E75", fill=True, fill_opacity=0.15,
            ).add_to(m)
        elif gebied["type"] == "polygoon":
            # GeoJSON coords zijn [lon,lat], Folium wil [lat,lon]
            coords_latlon = [[c[1],c[0]] for c in gebied["coords"]]
            folium.Polygon(
                locations=coords_latlon,
                color="#1D9E75", fill=True, fill_opacity=0.15,
            ).add_to(m)

    # Toon gevonden postcodes als punten
    if st.session_state.gevonden_pcs and pc4_centroids:
        for pc in st.session_state.gevonden_pcs:
            if pc in pc4_centroids:
                lat, lon = pc4_centroids[pc]
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color="#1D9E75",
                    fill=True,
                    fill_opacity=0.7,
                    tooltip=pc,
                ).add_to(m)

    kaart_output = st_folium(
        m,
        width="100%",
        height=580,
        returned_objects=["all_drawings", "last_active_drawing"],
        key="tekenkaart",
    )

    # Verwerk getekend gebied
    drawings = kaart_output.get("all_drawings") or []
    if drawings:
        laatste = drawings[-1]
        geom = laatste.get("geometry", {})
        gtype = geom.get("type","")

        if gtype == "Point" and laatste.get("properties",{}).get("radius"):
            # Cirkel
            straal = laatste["properties"]["radius"]
            lon, lat = geom["coordinates"]
            nieuw = {"type": "cirkel", "lat": lat, "lon": lon, "straal": straal}
        elif gtype == "Polygon":
            coords = geom["coordinates"][0]
            nieuw = {"type": "polygoon", "coords": coords}
        else:
            nieuw = None

        if nieuw and nieuw != st.session_state.getekend_gebied:
            st.session_state.getekend_gebied = nieuw

            # Bepaal welke postcodes in het gebied vallen
            if not pc4_centroids:
                st.warning("Postcode centroïden niet beschikbaar.")
            else:
                if nieuw["type"] == "cirkel":
                    gevonden = postcodes_in_cirkel(
                        pc4_centroids, nieuw["lat"], nieuw["lon"], nieuw["straal"]
                    )
                    straal_km = nieuw["straal"] / 1000
                    st.session_state.gebied_label = f"Cirkel {straal_km:.1f}km"
                else:
                    gevonden = postcodes_in_polygoon(pc4_centroids, nieuw["coords"])
                    st.session_state.gebied_label = "Getekend gebied"

                st.session_state.gevonden_pcs = sorted(gevonden)
                st.rerun()

# ── Resultaten ─────────────────────────────────────────────────────────────────
with col_result:
    if not st.session_state.gevonden_pcs:
        st.markdown("""
        ### 👈 Teken een gebied

        1. Gebruik **⬜ Polygoon** of **⭕ Cirkel** in de kaartbalk links
        2. Teken je gewenste catchment area
        3. De demografische analyse verschijnt hier automatisch

        **Tip:** Zoek eerst een locatie in de zijbalk, zoom dan in en teken een gebied.
        """)
    else:
        pcs = st.session_state.gevonden_pcs
        label = st.session_state.get("gebied_label","Getekend gebied")

        st.subheader(f"📊 {label}")
        st.caption(f"{len(pcs)} postcodes gevonden: {', '.join(pcs[:8])}{'…' if len(pcs)>8 else ''}")

        # Begrens voor snelheid
        pcs_te_laden = pcs[:max_pcs]
        if len(pcs) > max_pcs:
            st.info(f"Analyse op basis van {max_pcs} van de {len(pcs)} postcodes (zie instelling links).")

        with st.spinner(f"Data ophalen voor {len(pcs_te_laden)} postcodes..."):
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
                             color_discrete_sequence=["#1D9E75"], height=260)
                fig.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                    yaxis=dict(showgrid=True, gridcolor="#eee", title=""),
                    margin=dict(t=8, b=50, l=30, r=8),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                if not hh_agg:
                    st.info("Geen huishoudensdata.")
                else:
                    tot_hh = hh_agg.get("__totaal",1) or 1
                    c1,c2 = st.columns(2)
                    c1.metric("Huishoudens", f"{int(tot_hh):,}".replace(",","."))
                    c2.metric("Gem. grootte", f"{hh_agg.get('__grootte',0):.1f} pers.")

                    pie = {k:v for k,v in hh_agg.items() if not k.startswith("__") and v>0}
                    if pie:
                        fig_p = px.bar(
                            x=list(pie.values()),
                            y=list(pie.keys()),
                            orientation="h",
                            color_discrete_sequence=["#1D9E75","#185FA5","#BA7517"],
                            height=200,
                        )
                        fig_p.update_layout(
                            plot_bgcolor="white", paper_bgcolor="white",
                            xaxis=dict(showgrid=True, gridcolor="#eee", title="Huishoudens"),
                            yaxis=dict(title=""),
                            margin=dict(t=8, b=30, l=8, r=8),
                            showlegend=False,
                        )
                        st.plotly_chart(fig_p, use_container_width=True)

                    # % verdeling
                    pie_pct = {k: round(v/tot_hh*100,1) for k,v in pie.items()}
                    for k,v in pie_pct.items():
                        st.write(f"**{k}:** {v}%")

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
                            margin=dict(t=8, b=30, l=8, r=8),
                            showlegend=False,
                        )
                        st.plotly_chart(fig_h, use_container_width=True)

st.divider()
st.caption("Data: CBS StatLine (CC BY 4.0) | Geodata: PDOK Locatieserver | App gebouwd met Streamlit")
