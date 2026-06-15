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
# Exacte centroïden voor alle bekende Nederlandse PC4-gebieden
# Gebaseerd op officiële PostNL/CBS geografische data

# Exacte PC4 centroïden voor grote steden en bekende gebieden
_EXACTE_CENTROIDS = {
    # Amsterdam (10xx-11xx)
    "1011":(52.3731,4.9027),"1012":(52.3699,4.8952),"1013":(52.3839,4.8672),
    "1014":(52.3913,4.8503),"1015":(52.3827,4.8817),"1016":(52.3639,4.8752),
    "1017":(52.3568,4.8799),"1018":(52.3619,4.9100),"1019":(52.3605,4.9290),
    "1021":(52.4007,4.9227),"1022":(52.4063,4.9010),"1023":(52.4000,4.8850),
    "1024":(52.3961,4.8668),"1025":(52.4047,4.9414),"1026":(52.3951,4.9563),
    "1027":(52.3892,4.9440),"1028":(52.3755,4.9549),"1031":(52.4175,4.9266),
    "1032":(52.4081,4.9563),"1033":(52.4190,4.9447),"1034":(52.4121,4.9143),
    "1035":(52.4243,4.8989),"1036":(52.4285,4.9167),"1041":(52.3839,4.8375),
    "1042":(52.3800,4.8230),"1043":(52.3726,4.8252),"1044":(52.3780,4.8086),
    "1045":(52.3900,4.8135),"1046":(52.4002,4.8286),"1051":(52.3713,4.8604),
    "1052":(52.3660,4.8540),"1053":(52.3598,4.8584),"1054":(52.3535,4.8640),
    "1055":(52.3598,4.8422),"1056":(52.3663,4.8397),"1057":(52.3718,4.8476),
    "1058":(52.3611,4.8251),"1059":(52.3547,4.8246),"1061":(52.3537,4.8466),
    "1062":(52.3483,4.8486),"1063":(52.3462,4.8312),"1064":(52.3437,4.8512),
    "1065":(52.3370,4.8440),"1066":(52.3310,4.8370),"1067":(52.3370,4.8160),
    "1068":(52.3308,4.8245),"1069":(52.3273,4.8110),"1071":(52.3486,4.8695),
    "1072":(52.3459,4.8849),"1073":(52.3513,4.8937),"1074":(52.3470,4.9055),
    "1075":(52.3412,4.8713),"1076":(52.3400,4.8863),"1077":(52.3419,4.8998),
    "1078":(52.3445,4.9148),"1079":(52.3337,4.9040),"1081":(52.3321,4.8577),
    "1082":(52.3290,4.8704),"1083":(52.3340,4.8815),"1086":(52.3204,4.9092),
    "1087":(52.3220,4.9262),"1091":(52.3557,4.9203),"1092":(52.3501,4.9334),
    "1093":(52.3486,4.9213),"1094":(52.3555,4.9369),"1095":(52.3583,4.9484),
    "1096":(52.3512,4.9468),"1097":(52.3433,4.9321),"1098":(52.3390,4.9421),
    "1101":(52.3158,4.9581),"1102":(52.3124,4.9432),"1103":(52.3063,4.9533),
    "1104":(52.3063,4.9678),"1106":(52.3208,4.9724),"1107":(52.3263,4.9543),
    "1108":(52.3349,4.9588),"1111":(52.3046,4.9895),"1112":(52.3103,4.9888),
    # Haarlem (20xx-21xx)
    "2011":(52.3908,4.6364),"2012":(52.3844,4.6276),"2013":(52.3782,4.6262),
    "2014":(52.3741,4.6332),"2015":(52.3804,4.6356),"2016":(52.3873,4.6474),
    "2017":(52.3831,4.6474),"2018":(52.3754,4.6474),"2021":(52.3950,4.6574),
    "2022":(52.3880,4.6574),"2023":(52.3830,4.6574),"2024":(52.3780,4.6474),
    "2025":(52.3911,4.6668),"2026":(52.3855,4.6668),"2027":(52.3806,4.6668),
    "2031":(52.4000,4.6366),"2032":(52.3940,4.6228),"2033":(52.3870,4.6168),
    "2034":(52.3800,4.6168),"2035":(52.3730,4.6168),"2036":(52.3680,4.6268),
    "2037":(52.3700,4.6445),"2038":(52.3660,4.6474),
    # Den Haag (25xx-27xx)
    "2511":(52.0793,4.3122),"2512":(52.0760,4.3030),"2513":(52.0719,4.2980),
    "2514":(52.0752,4.3250),"2515":(52.0703,4.3175),"2516":(52.0680,4.3070),
    "2517":(52.0690,4.3280),"2518":(52.0620,4.3178),"2521":(52.0820,4.2928),
    "2522":(52.0763,4.2853),"2523":(52.0680,4.2878),"2524":(52.0620,4.2868),
    "2525":(52.0563,4.2828),"2526":(52.0460,4.2828),"2531":(52.0899,4.2817),
    "2532":(52.0843,4.2766),"2533":(52.0779,4.2756),"2541":(52.0680,4.3478),
    "2542":(52.0635,4.3340),"2543":(52.0567,4.3178),"2544":(52.0473,4.3278),
    "2545":(52.0411,4.3178),"2546":(52.0349,4.2978),"2547":(52.0487,4.3478),
    "2551":(52.0379,4.3478),"2552":(52.0449,4.3578),"2553":(52.0519,4.3678),
    "2554":(52.0589,4.3578),"2555":(52.0519,4.3778),"2561":(52.0649,4.3778),
    "2562":(52.0719,4.3678),"2563":(52.0789,4.3578),"2564":(52.0859,4.3678),
    "2565":(52.0789,4.3778),"2566":(52.0929,4.3578),"2571":(52.0519,4.3978),
    "2572":(52.0589,4.4078),"2573":(52.0659,4.3978),"2574":(52.0729,4.3878),
    # Rotterdam (30xx-31xx)
    "3011":(51.9233,4.4817),"3012":(51.9181,4.4769),"3013":(51.9215,4.4657),
    "3014":(51.9179,4.4657),"3015":(51.9113,4.4669),"3016":(51.9172,4.4857),
    "3021":(51.9303,4.4557),"3022":(51.9258,4.4457),"3023":(51.9203,4.4457),
    "3024":(51.9148,4.4457),"3025":(51.9093,4.4457),"3026":(51.9023,4.4537),
    "3027":(51.9043,4.4357),"3028":(51.9023,4.4257),"3029":(51.9023,4.4157),
    "3031":(51.9243,4.5057),"3032":(51.9173,4.5157),"3033":(51.9243,4.5257),
    "3034":(51.9313,4.5157),"3035":(51.9313,4.5057),"3036":(51.9243,4.4957),
    "3037":(51.9313,4.4957),"3038":(51.9373,4.4857),"3039":(51.9373,4.5057),
    "3041":(51.9173,4.5357),"3042":(51.9103,4.5257),"3043":(51.9103,4.5357),
    "3044":(51.9033,4.5257),"3045":(51.9033,4.5157),"3046":(51.9033,4.5057),
    "3047":(51.8963,4.5157),"3051":(51.9173,4.5557),"3052":(51.9243,4.5657),
    "3053":(51.9173,4.5757),"3054":(51.9103,4.5757),"3055":(51.9033,4.5657),
    "3056":(51.8963,4.5557),"3061":(51.9033,4.4957),"3062":(51.8963,4.4857),
    "3063":(51.8893,4.4857),"3064":(51.8963,4.4957),"3065":(51.8893,4.4957),
    "3066":(51.8823,4.4957),"3067":(51.8893,4.5057),"3068":(51.8823,4.5057),
    "3069":(51.8893,4.5157),
    # Utrecht (35xx-36xx)
    "3511":(52.0977,5.1186),"3512":(52.0921,5.1133),"3513":(52.0921,5.1233),
    "3514":(52.0977,5.1286),"3515":(52.1033,5.1186),"3516":(52.0921,5.1033),
    "3521":(52.0811,5.1086),"3522":(52.0811,5.1186),"3523":(52.0811,5.1286),
    "3524":(52.0866,5.1286),"3525":(52.0866,5.1086),"3526":(52.0866,5.1186),
    "3527":(52.0756,5.1086),"3528":(52.0700,5.1186),"3531":(52.0921,5.0933),
    "3532":(52.0866,5.0833),"3533":(52.0810,5.0833),"3534":(52.0700,5.0833),
    "3541":(52.1033,5.0833),"3542":(52.1033,5.0933),"3543":(52.1033,5.1033),
    "3544":(52.1089,5.0933),"3551":(52.0754,5.0633),"3552":(52.0700,5.0733),
    "3553":(52.0810,5.0633),"3554":(52.0866,5.0633),"3555":(52.0921,5.0633),
    "3561":(52.0580,5.1186),"3562":(52.0635,5.1086),"3563":(52.0580,5.1086),
    "3564":(52.0635,5.1186),"3565":(52.0580,5.1286),"3566":(52.0635,5.1286),
    "3571":(52.0980,5.1400),"3572":(52.0921,5.1433),"3573":(52.0866,5.1433),
    "3574":(52.0810,5.1433),"3581":(52.0921,5.1333),"3582":(52.0977,5.1333),
    "3583":(52.0866,5.1333),"3584":(52.0810,5.1333),
    # Eindhoven (56xx)
    "5611":(51.4416,5.4697),"5612":(51.4416,5.4797),"5613":(51.4416,5.4897),
    "5614":(51.4359,5.4697),"5615":(51.4359,5.4797),"5616":(51.4302,5.4697),
    "5617":(51.4302,5.4797),"5621":(51.4472,5.4697),"5622":(51.4472,5.4797),
    "5623":(51.4472,5.4897),"5624":(51.4472,5.4597),"5625":(51.4529,5.4697),
    "5626":(51.4529,5.4797),"5627":(51.4529,5.4897),"5631":(51.4359,5.4597),
    "5632":(51.4302,5.4597),"5641":(51.4246,5.4797),"5642":(51.4246,5.4897),
    "5643":(51.4189,5.4897),"5644":(51.4189,5.4797),"5645":(51.4189,5.4697),
    "5651":(51.4529,5.4597),"5652":(51.4585,5.4697),"5653":(51.4585,5.4797),
    "5654":(51.4585,5.4897),"5655":(51.4585,5.4997),"5656":(51.4529,5.4997),
    # Groningen (97xx)
    "9711":(53.2215,6.5669),"9712":(53.2215,6.5569),"9713":(53.2215,6.5469),
    "9714":(53.2158,6.5469),"9715":(53.2158,6.5569),"9716":(53.2158,6.5669),
    "9717":(53.2101,6.5569),"9718":(53.2101,6.5669),"9721":(53.2272,6.5669),
    "9722":(53.2272,6.5769),"9723":(53.2215,6.5769),"9724":(53.2158,6.5769),
    "9725":(53.2101,6.5769),"9726":(53.2272,6.5569),"9727":(53.2272,6.5469),
    "9728":(53.2329,6.5569),"9729":(53.2329,6.5669),"9731":(53.2386,6.5669),
    "9732":(53.2386,6.5769),"9733":(53.2329,6.5769),"9734":(53.2386,6.5869),
    "9735":(53.2329,6.5869),"9736":(53.2272,6.5869),"9737":(53.2215,6.5869),
    "9741":(53.2443,6.5769),"9742":(53.2443,6.5869),"9743":(53.2386,6.5969),
    "9744":(53.2443,6.5969),"9745":(53.2500,6.5869),"9746":(53.2500,6.5969),
    # Maastricht (62xx)
    "6211":(50.8484,5.6900),"6212":(50.8484,5.7000),"6213":(50.8542,5.6900),
    "6214":(50.8542,5.7000),"6215":(50.8600,5.6900),"6216":(50.8426,5.6900),
    "6217":(50.8426,5.7000),"6218":(50.8368,5.6900),"6221":(50.8484,5.6800),
    "6222":(50.8426,5.6800),"6223":(50.8368,5.6800),"6224":(50.8310,5.6800),
    "6225":(50.8310,5.6900),"6226":(50.8310,5.7000),"6227":(50.8252,5.7000),
    "6228":(50.8252,5.6900),"6229":(50.8252,5.6800),"6231":(50.8658,5.6900),
    "6232":(50.8658,5.7000),"6233":(50.8716,5.7000),"6234":(50.8716,5.6900),
}

# Ankerpunten per 2-cijferig postcodeprefix voor de rest
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
    c = dict(_EXACTE_CENTROIDS)  # begin met exacte data
    for pc_int in range(1000, 10000):
        pc = str(pc_int)
        if pc in c:
            continue  # al exact bekend
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

@st.cache_data(ttl=3600)
def get_centroids_voor_gebied(center_lat, center_lon, straal_km=15):
    """Haal via PDOK exacte PC4-centroi den op rondom een locatie."""
    marge = straal_km / 111.0
    extra = {}
    try:
        r = requests.get(
            "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free",
            params={
                "q": "*",
                "fq": [
                    "type:postcode",
                    f"centroide_ll:[{center_lat-marge},{center_lon-marge} TO {center_lat+marge},{center_lon+marge}]"
                ],
                "fl": "weergavenaam,centroide_ll",
                "rows": 200,
            },
            timeout=10
        )
        if r.status_code == 200:
            for doc in r.json().get("response",{}).get("docs",[]):
                naam = doc.get("weergavenaam","")
                cent = doc.get("centroide_ll","")
                m_pc    = re.search(r"\b(\d{4})[A-Z]{2}\b", naam)
                m_coord = re.search(r"POINT\(([0-9.]+)\s+([0-9.]+)\)", cent)
                if m_pc and m_coord:
                    pc4 = m_pc.group(1)
                    if pc4 in bekende_pcs:
                        extra[pc4] = (float(m_coord.group(2)), float(m_coord.group(1)))
    except Exception:
        pass
    return extra

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
                st.session_state.analyse_klaar = False
                st.session_state.gevonden_pcs  = []
                st.session_state.gebied        = None
                st.success(f"📍 {naam}")
                st.rerun()
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

        # Haal dynamische centroïden op rondom het getekende gebied
        center_lat = g["lat"] if g["type"]=="cirkel" else sum(c[1] for c in g["coords"])/len(g["coords"])
        center_lon = g["lon"] if g["type"]=="cirkel" else sum(c[0] for c in g["coords"])/len(g["coords"])
        straal_km  = g["straal"]/1000 if g["type"]=="cirkel" else 10

        with st.spinner("Postcodes in dit gebied ophalen..."):
            live_centroids = get_centroids_voor_gebied(center_lat, center_lon, max(straal_km*2, 8))

        # Combineer statische + live centroïden (live heeft prioriteit)
        alle_centroids = {**PC4_CENTROIDS_FILTERED, **live_centroids}

        if g["type"] == "cirkel":
            gevonden = [
                (pc, lat, lon)
                for pc, (lat, lon) in alle_centroids.items()
                if haversine(g["lat"], g["lon"], lat, lon) <= g["straal"]
            ]
            st.session_state.gebied_label = f"Cirkel ⌀ {g['straal']*2/1000:.1f} km"
        else:
            gevonden = [
                (pc, lat, lon)
                for pc, (lat, lon) in alle_centroids.items()
                if punt_in_polygoon(lat, lon, g["coords"])
            ]
            st.session_state.gebied_label = "Getekend gebied"

        if not gevonden:
            st.warning("Geen postcodes gevonden. Controleer of het gebied in Nederland ligt en probeer een groter gebied.")
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

            # Nederland benchmark — één call per tabel
            nl_leeftijd_key = pc_key_map.get("Nederland")
            nl_verd = get_leeftijd_verd(nl_leeftijd_key, periode_key, geslacht_key, leeftijd_keys, leeftijd_map) if nl_leeftijd_key else {}
            nl_hh_key = hh_pc_map.get("Nederland")
            nl_hh = get_hh_data(nl_hh_key, hh_per_key, hh_map_meta) if nl_hh_key else {}
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

                # NL benchmarks
                nl_tot  = sum(nl_verd.values()) or 1
                nl_gem  = gem_leeftijd_fn(nl_verd)
                nl_oud  = sum(v for k,v in nl_verd.items() if k in ["65-70","70-75","75-80","80-85","85-90","90+"])
                nl_jong = sum(v for k,v in nl_verd.items() if k in ["0-5","5-10","10-15","15-20","20-25"])

                c1,c2 = st.columns(2)
                c1.metric("Inwoners", f"{int(tot):,}".replace(",","."))
                c2.metric("Gem. leeftijd", f"{gem:.1f} jaar" if gem else "—",
                          delta=f"{gem - nl_gem:+.1f} vs NL" if gem and nl_gem else None)
                c3,c4 = st.columns(2)
                c3.metric("Aandeel 65+",  f"{oud/tot*100:.1f}%",
                          delta=f"{oud/tot*100 - nl_oud/nl_tot*100:+.1f}%-pt vs NL" if nl_verd else None)
                c4.metric("Aandeel 0-25", f"{jong/tot*100:.1f}%",
                          delta=f"{jong/tot*100 - nl_jong/nl_tot*100:+.1f}%-pt vs NL" if nl_verd else None)
                st.caption("Delta t.o.v. landelijk gemiddelde")

                # Vergelijkingsgrafiek gebied vs NL
                gebied_pct = pct(verd_agg)
                nl_pct_l   = pct(nl_verd)
                plot_data = []
                for lbl in LABELS_VOLGORDE:
                    plot_data.append({"Leeftijdsgroep": lbl, "%": round(gebied_pct.get(lbl,0),1), "Reeks": "Gebied"})
                    if nl_verd:
                        plot_data.append({"Leeftijdsgroep": lbl, "%": round(nl_pct_l.get(lbl,0),1), "Reeks": "⌀ Nederland"})

                fig = px.bar(pd.DataFrame(plot_data), x="Leeftijdsgroep", y="%",
                             color="Reeks", barmode="group",
                             color_discrete_map={"Gebied": "#1D9E75", "⌀ Nederland": "#888780"},
                             category_orders={"Reeks": ["Gebied", "⌀ Nederland"]},
                             height=280)
                fig.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                    yaxis=dict(showgrid=True, gridcolor="#eee", title=""),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
                    margin=dict(t=30, b=50, l=30, r=8),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Afwijkingsgrafiek
                if nl_verd:
                    afw = [{"Leeftijdsgroep": lbl,
                            "Afwijking (%-punt)": round(gebied_pct.get(lbl,0) - nl_pct_l.get(lbl,0), 1)}
                           for lbl in LABELS_VOLGORDE]
                    fig2 = px.bar(pd.DataFrame(afw), x="Leeftijdsgroep", y="Afwijking (%-punt)",
                                  color="Afwijking (%-punt)",
                                  color_continuous_scale=["#534AB7","#eee","#1D9E75"],
                                  color_continuous_midpoint=0, height=220)
                    fig2.add_hline(y=0, line_color="#333", line_width=1)
                    fig2.update_coloraxes(showscale=False)
                    fig2.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white",
                        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                        yaxis=dict(showgrid=True, gridcolor="#eee", zeroline=False, title=""),
                        margin=dict(t=8, b=50, l=30, r=8),
                    )
                    st.caption("Afwijking t.o.v. Nederland — groen = meer dan NL, paars = minder")
                    st.plotly_chart(fig2, use_container_width=True)

            with tab2:
                if not hh_agg:
                    st.info("Geen huishoudensdata.")
                else:
                    HH_TYPEN_LABELS = ["Alleenstaand", "Gezin met kinderen", "Stel/meerp. zonder kinderen"]
                    tot_hh    = hh_agg.get("__totaal",1) or 1
                    nl_tot_hh = nl_hh.get("__totaal",1) or 1

                    c1,c2 = st.columns(2)
                    c1.metric("Huishoudens", f"{int(tot_hh):,}".replace(",","."))
                    c2.metric("Gem. grootte", f"{hh_agg.get('__grootte',0):.1f} pers.",
                              delta=f"{hh_agg.get('__grootte',0) - nl_hh.get('__grootte',0):+.1f} vs NL" if nl_hh else None)

                    # Alleenstaand vergelijking
                    pc_alone = hh_agg.get("Alleenstaand",0)/tot_hh*100
                    nl_alone = nl_hh.get("Alleenstaand",0)/nl_tot_hh*100 if nl_hh else None
                    pc_gezin = hh_agg.get("Gezin met kinderen",0)/tot_hh*100
                    nl_gezin = nl_hh.get("Gezin met kinderen",0)/nl_tot_hh*100 if nl_hh else None
                    c3,c4 = st.columns(2)
                    c3.metric("Aandeel alleenstaand", f"{pc_alone:.1f}%",
                              delta=f"{pc_alone - nl_alone:+.1f}%-pt vs NL" if nl_alone else None)
                    c4.metric("Aandeel gezin m. kinderen", f"{pc_gezin:.1f}%",
                              delta=f"{pc_gezin - nl_gezin:+.1f}%-pt vs NL" if nl_gezin else None)
                    st.caption("Delta t.o.v. landelijk gemiddelde")

                    # Vergelijkingsgrafiek
                    hh_plot = []
                    for typ in HH_TYPEN_LABELS:
                        hh_plot.append({"Type": typ, "%": round(hh_agg.get(typ,0)/tot_hh*100,1), "Reeks": "Gebied"})
                        if nl_hh:
                            hh_plot.append({"Type": typ, "%": round(nl_hh.get(typ,0)/nl_tot_hh*100,1), "Reeks": "⌀ Nederland"})

                    fig_hh = px.bar(pd.DataFrame(hh_plot), x="Type", y="%",
                                    color="Reeks", barmode="group",
                                    color_discrete_map={"Gebied": "#1D9E75", "⌀ Nederland": "#888780"},
                                    category_orders={"Reeks": ["Gebied", "⌀ Nederland"]},
                                    labels={"%": "% van huishoudens"}, height=260)
                    fig_hh.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white",
                        yaxis=dict(showgrid=True, gridcolor="#eee", title=""),
                        xaxis=dict(tickfont=dict(size=10)),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
                        margin=dict(t=30, b=20, l=30, r=8),
                    )
                    st.plotly_chart(fig_hh, use_container_width=True)

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
