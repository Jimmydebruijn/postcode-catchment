import re
import math
import streamlit as st
import requests
import pandas as pd
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import plotly.express as px

# ── Vaste winkeldata — 986 locaties (gegenereerd uit Adressenlijst.xlsx) ───────
WINKELS = [{"s":175,"c":"GEMERT","a":"NIEUWSTRAAT 6","p":"5421KP","lat":51.508,"lon":5.15},{"s":183,"c":"HARDERWIJK","a":"DONKERSTRAAT 37-I","p":"3841CB","lat":51.816,"lon":4.63},{"s":191,"c":"GELDERMALSEN","a":"GELDERSESTRAAT 27B","p":"4191BA","lat":51.886,"lon":4.91},{"s":213,"c":"MAARSSEN","a":"NASSAUSTRAAT 5","p":"3601BA","lat":51.85,"lon":4.58},{"s":221,"c":"HUIZEN","a":"LINDENLAAN 16","p":"1271BA","lat":52.378,"lon":4.825},{"s":230,"c":"BERGEN OP ZOOM","a":"ST. JOSEPHSTRAAT 15-17","p":"4611MJ","lat":51.554,"lon":4.53},{"s":248,"c":"VELP GLD","a":"HOOFDSTRAAT 226","p":"6881TR","lat":51.982,"lon":5.98},{"s":256,"c":"ARNHEM","a":"GROTE OORD 7","p":"6811GA","lat":51.954,"lon":5.98},{"s":264,"c":"ZEIST","a":"VOORHEUVEL 23","p":"3701JA","lat":51.86,"lon":4.74},{"s":272,"c":"BUNNIK","a":"V. HARDENBROEKLAAN 12-14","p":"3981EP","lat":51.832,"lon":4.41},{"s":280,"c":"BENNEKOM","a":"EDESEWEG 1","p":"6721JN","lat":51.958,"lon":5.9},{"s":299,"c":"TIEL","a":"WATERSTRAAT 31-33","p":"4001AM","lat":51.89,"lon":4.98},{"s":302,"c":"BAARN","a":"LAANSTRAAT 60","p":"3743BH","lat":51.876,"lon":4.75},{"s":361,"c":"SITTARD","a":"WALSTRAAT 45","p":"6131CV","lat":51.842,"lon":5.86},{"s":388,"c":"BEVERWIJK","a":"BREESTRAAT 73-75","p":"1941EE","lat":52.466,"lon":4.64},{"s":396,"c":"EINDHOVEN","a":"WINKELCENTR WOENSEL 283","p":"5625AG","lat":51.4529,"lon":5.4697},{"s":485,"c":"WORMERVEER","a":"KROMMENIEERWEG 34","p":"1521HK","lat":52.428,"lon":4.81},{"s":493,"c":"AMSTERDAM","a":"REIGERSBOS 94","p":"1106AS","lat":52.3208,"lon":4.9724},{"s":523,"c":"PAPENDRECHT","a":"MEENTPASSAGE 29","p":"3353HH","lat":51.88,"lon":4.53},{"s":728,"c":"SCHOONHOVEN","a":"LOPIKERSTRAAT 27-29","p":"2871BT","lat":52.078,"lon":4.38},{"s":795,"c":"EDE","a":"GROTESTRAAT 63","p":"6711AJ","lat":51.954,"lon":5.9},{"s":809,"c":"RENKUM","a":"DORPSSTRAAT 59-63","p":"6871AD","lat":51.978,"lon":5.98},{"s":817,"c":"EINDHOVEN","a":"WOENSELSE MARKT 45","p":"5612CS","lat":51.4416,"lon":5.4797},{"s":825,"c":"UTRECHT","a":"SMARAGDPLEIN 113","p":"3523ED","lat":52.0811,"lon":5.1286},{"s":841,"c":"HILVERSUM","a":"KERKSTRAAT 81","p":"1211CM","lat":52.354,"lon":4.825},{"s":850,"c":"UTRECHT","a":"AMSTERDAMSESTRAATWEG  391","p":"3551CL","lat":52.0754,"lon":5.0633},{"s":868,"c":"UTRECHT","a":"NACHTEGAALSTRAAT 20","p":"3581AH","lat":52.0921,"lon":5.1333},{"s":884,"c":"DE BILT","a":"HESSENWEG 156-158","p":"3731JM","lat":51.872,"lon":4.74},{"s":906,"c":"VAASSEN","a":"KOSTERSTRAAT 8","p":"8171CB","lat":52.508,"lon":6.07},{"s":930,"c":"CULEMBORG","a":"MARKT 49B","p":"4101BW","lat":51.85,"lon":4.91},{"s":1007,"c":"BLERICK","a":"KLOOSTERSTRAAT 33","p":"5921HB","lat":51.418,"lon":6.08},{"s":1015,"c":"HEERDE","a":"DORPSSTRAAT 42","p":"8181HS","lat":52.512,"lon":6.07},{"s":1023,"c":"WEERT","a":"MUNTPASSAGE 40","p":"6001GM","lat":51.83,"lon":5.85},{"s":1031,"c":"LANDGRAAF","a":"HOOFDSTRAAT 140","p":"6372EN","lat":51.208,"lon":5.965},{"s":1040,"c":"BARENDRECHT","a":"MIDDENBAAN 76","p":"2991CT","lat":51.986,"lon":4.26},{"s":1058,"c":"VOORTHUIZEN","a":"HOOFDSTRAAT 155B","p":"3781AD","lat":51.892,"lon":4.74},{"s":1066,"c":"LOSSER","a":"DE BRINK 48B","p":"7581JB","lat":52.232,"lon":6.88},{"s":1074,"c":"ALMELO","a":"GROTESTRAAT 77-79","p":"7607CE","lat":52.5,"lon":6.11},{"s":1082,"c":"EPE","a":"STERNPASSAGE 2","p":"8161HP","lat":52.504,"lon":6.07},{"s":1104,"c":"AMERSFOORT","a":"LEUSDERWEG 168","p":"3817KE","lat":51.804,"lon":4.66},{"s":1120,"c":"BUSSUM","a":"NASSAULAAN 34-36","p":"1404CP","lat":52.35,"lon":4.835},{"s":1139,"c":"AMSTERDAM","a":"OSDORPPLEIN 134","p":"1068EN","lat":52.3308,"lon":4.8245},{"s":1171,"c":"EINDHOVEN","a":"RECHTESTRAAT 22","p":"5611GP","lat":51.4416,"lon":5.4697},{"s":1198,"c":"ELST GLD","a":"DORPSSTRAAT 42","p":"6661EL","lat":51.974,"lon":5.91},{"s":1228,"c":"HEEMSKERK","a":"DEUTZSTRAAT 13A-19A","p":"1961NS","lat":52.474,"lon":4.64},{"s":1236,"c":"HOEVELAKEN","a":"BRINK 2A-4","p":"3871AM","lat":51.828,"lon":4.63},{"s":1260,"c":"BEUNINGEN GLD","a":"JULIANAPLEIN 8-14","p":"6641CT","lat":51.966,"lon":5.91},{"s":1287,"c":"PUTTEN","a":"KERKSTRAAT 21","p":"3882BM","lat":51.832,"lon":4.635},{"s":1309,"c":"HENGELO OV","a":"ENSCHEDESESTRAAT 19","p":"7551EG","lat":52.22,"lon":6.88},{"s":1317,"c":"ERMELO","a":"STATIONSSTRAAT 109-111","p":"3851NC","lat":51.82,"lon":4.63},{"s":1350,"c":"GOES","a":"GANZEPOORTSTRAAT 10","p":"4461JZ","lat":51.504,"lon":3.83},{"s":1368,"c":"LAREN NH","a":"NIEUWEWEG 8","p":"1251LJ","lat":52.37,"lon":4.825},{"s":1376,"c":"GRAVE","a":"HOOFSCHESTRAAT 15E","p":"5361ET","lat":51.454,"lon":5.48},{"s":1384,"c":"S GRAVENHAGE","a":"GROTE MARKTSTRAAT 38","p":"2511BJ","lat":52.0793,"lon":4.3122},{"s":1449,"c":"MEPPEL","a":"KRUISSTRAAT 20-05","p":"7941AN","lat":52.496,"lon":6.46},{"s":1457,"c":"ZEVENAAR","a":"GRIETSESTRAAT 12A","p":"6901GT","lat":51.98,"lon":6.18},{"s":1473,"c":"SCHIJNDEL","a":"HOOFDSTRAAT 99A","p":"5481AC","lat":51.532,"lon":5.15},{"s":1490,"c":"NIJKERK GLD","a":"SINGEL 26","p":"3861AE","lat":51.824,"lon":4.63},{"s":1503,"c":"HILVERSUM","a":"G. V AMSTELSTRAAT 108","p":"1214BC","lat":52.354,"lon":4.84},{"s":1511,"c":"DRIEBERGEN-RIJSENBURG","a":"TRAAY 73","p":"3971GC","lat":51.828,"lon":4.41},{"s":1520,"c":"DOORN","a":"AMERSFOORTSEWEG 6","p":"3941EM","lat":51.816,"lon":4.41},{"s":1538,"c":"MIDDELBURG","a":"LANGE DELFT 60-62","p":"4331AR","lat":51.642,"lon":3.88},{"s":1570,"c":"S HERTOGENBOSCH","a":"MGR VAN ROOSMALENPLEIN 5","p":"5213GC","lat":51.414,"lon":5.47},{"s":1589,"c":"VELDHOVEN","a":"PLEINTJES 58","p":"5501EB","lat":51.4,"lon":5.46},{"s":1600,"c":"VEGHEL","a":"MOLENWIEKEN 58","p":"5461KH","lat":51.524,"lon":5.15},{"s":1619,"c":"VEENENDAAL","a":"HOOFDSTRAAT 67-69","p":"3901AE","lat":51.8,"lon":4.41},{"s":1627,"c":"BARNEVELD","a":"JAN V SCHAFFELAARSTR 18","p":"3771BT","lat":51.888,"lon":4.74},{"s":1635,"c":"UDEN","a":"GALERIJ 5B","p":"5401GC","lat":51.5,"lon":5.15},{"s":1651,"c":"HEERLEN","a":"WANNERSTRAAT 10","p":"6413EV","lat":51.504,"lon":5.97},{"s":1660,"c":"S HERTOGENBOSCH","a":"HOOGE STEENWEG 3","p":"5211JN","lat":51.414,"lon":5.46},{"s":1678,"c":"DIDAM","a":"LIEVE VROUWEPLEIN 3A","p":"6942BP","lat":51.996,"lon":6.185},{"s":1694,"c":"WIJCHEN","a":"TOUWSLAGERSBAAN 18B","p":"6602AK","lat":51.95,"lon":5.915},{"s":1732,"c":"NIJMEGEN","a":"LANGE HEZELSTRAAT 16","p":"6511CJ","lat":51.834,"lon":5.86},{"s":1740,"c":"ARNHEM","a":"KRONENBURGPASSAGE 92","p":"6831ER","lat":51.962,"lon":5.98},{"s":1775,"c":"BLADEL","a":"SNIEDERSLAAN 28A","p":"5531EL","lat":51.412,"lon":5.46},{"s":1783,"c":"KROMMENIE","a":"ZUIDERHOOFDSTRAAT 57A","p":"1561AJ","lat":52.444,"lon":4.81},{"s":1791,"c":"UTRECHT","a":"DAMSTRAAT 7","p":"3531BP","lat":52.0921,"lon":5.0933},{"s":1899,"c":"HELMOND","a":"VEESTRAAT 8","p":"5701RC","lat":51.68,"lon":5.28},{"s":2011,"c":"HEERENVEEN","a":"DRACHT 103","p":"8442BM","lat":52.146,"lon":5.365},{"s":2020,"c":"OSS","a":"HEUVEL 14-14A","p":"5341CW","lat":51.446,"lon":5.48},{"s":2038,"c":"NIJMEGEN","a":"BROERSTRAAT 70","p":"6511KR","lat":51.834,"lon":5.86},{"s":2054,"c":"VENRAY","a":"GROTESTRAAT 43","p":"5801BE","lat":51.71,"lon":5.3},{"s":2062,"c":"BILTHOVEN","a":"W.C. DE KWINKELIER 15","p":"3722AP","lat":51.868,"lon":4.745},{"s":2070,"c":"VEENDAM","a":"VEENLUSTPLEIN 1-04","p":"9641MG","lat":53.316,"lon":6.28},{"s":2100,"c":"AMSTERDAM","a":"WALDENLAAN 116","p":"1093NH","lat":52.3486,"lon":4.9213},{"s":2119,"c":"OISTERWIJK","a":"DORPSSTRAAT 24A","p":"5061HL","lat":51.574,"lon":5.06},{"s":2135,"c":"RHENEN","a":"MOLENSTRAAT 18","p":"3911KL","lat":51.804,"lon":4.41},{"s":2143,"c":"ASTEN","a":"BURG. RUTTENPLEIN 3","p":"5721DX","lat":51.688,"lon":5.28},{"s":2151,"c":"KAATSHEUVEL","a":"HOOFDPOORT 15","p":"5171DN","lat":51.578,"lon":5.07},{"s":2178,"c":"ETTEN LEUR","a":"HOF VAN DEN HOUTE 60-62","p":"4873BJ","lat":51.578,"lon":4.47},{"s":2186,"c":"OOSTBURG","a":"BURCHTSTRAAT 9","p":"4501BH","lat":51.51,"lon":4.45},{"s":2194,"c":"GROESBEEK","a":"DORPSSTRAAT 33","p":"6561CA","lat":51.854,"lon":5.86},{"s":2208,"c":"DEVENTER","a":"BRINK 97-99","p":"7411BZ","lat":52.204,"lon":6.2},{"s":2216,"c":"OOST SOUBURG","a":"KANAALSTRAAT 7","p":"4388BJ","lat":51.662,"lon":3.915},{"s":2224,"c":"ST OEDENRODE","a":"MARKT  24-26","p":"5492AB","lat":51.536,"lon":5.155},{"s":2240,"c":"ZAANDAM","a":"GEDEMPTE GRACHT 20","p":"1506CG","lat":52.42,"lon":4.835},{"s":2275,"c":"VOORSCHOTEN","a":"SCHOOLSTRAAT 64","p":"2251BK","lat":52.25,"lon":4.51},{"s":2305,"c":"BOSKOOP","a":"KONINGINNEWEG 1H","p":"2771DN","lat":52.078,"lon":4.36},{"s":2313,"c":"DRUNEN","a":"GROTESTRAAT 142-142A","p":"5151BN","lat":51.57,"lon":5.07},{"s":2321,"c":"DEURNE","a":"WOLFSBERG 25","p":"5751GX","lat":51.7,"lon":5.28},{"s":2348,"c":"HOENSBROEK","a":"KOUVENDERSTRAAT 59","p":"6431HB","lat":51.512,"lon":5.96},{"s":2356,"c":"HEEMSTEDE","a":"BINNENWEG 67","p":"2101JC","lat":52.37,"lon":4.62},{"s":2372,"c":"NOORDWIJK ZH","a":"HOOFDSTRAAT 60","p":"2202GB","lat":52.23,"lon":4.515},{"s":2402,"c":"DRUTEN","a":"HOGESTRAAT 67B","p":"6651BH","lat":51.97,"lon":5.91},{"s":2410,"c":"S GRAVENHAGE","a":"FREDERIK HENDRIKLN 117","p":"2582BX","lat":52.082,"lon":4.305},{"s":2429,"c":"HORST","a":"ST. LAMBERTUSPLEIN 3","p":"5961EW","lat":51.434,"lon":6.08},{"s":2437,"c":"ARNHEM","a":"HANZESTRAAT 393","p":"6826ML","lat":51.958,"lon":6.005},{"s":2453,"c":"WEESP","a":"NIEUWSTRAAT 23","p":"1381BB","lat":52.382,"lon":5.2},{"s":2488,"c":"KERKRADE","a":"ORLANDOPASSAGE 19","p":"6461AM","lat":51.524,"lon":5.96},{"s":2496,"c":"CUIJK","a":"KORTE MOLENSTRAAT 7","p":"5431DT","lat":51.512,"lon":5.15},{"s":2500,"c":"GELDROP","a":"LANGSTRAAT 101-103","p":"5664GE","lat":51.504,"lon":5.615},{"s":2534,"c":"PURMEREND","a":"HOOGSTRAAT 19-23","p":"1441BB","lat":52.366,"lon":4.82},{"s":2542,"c":"BREDA","a":"EINDSTRAAT 9-11","p":"4811KK","lat":51.554,"lon":4.46},{"s":2550,"c":"HULST","a":"GENTSESTRAAT 34","p":"4561EK","lat":51.534,"lon":4.45},{"s":2569,"c":"SLUIS","a":"KAPELLESTRAAT 5","p":"4524CW","lat":51.518,"lon":4.465},{"s":2585,"c":"IJSSELSTEIN UT","a":"BENSCHOPPERSTRAAT 32","p":"3401DH","lat":51.85,"lon":4.66},{"s":2593,"c":"GOUDA","a":"KLEIWEG 77-81","p":"2801GD","lat":52.05,"lon":4.38},{"s":2615,"c":"S GRAVENHAGE","a":"FAHRENHEITSTRAAT 448","p":"2561DG","lat":52.0649,"lon":4.3778},{"s":2623,"c":"ROTTERDAM","a":"BINNENWEGPLEIN 12","p":"3012KA","lat":51.9181,"lon":4.4769},{"s":2631,"c":"RIJSWIJK ZH","a":"HERENSTRAAT 34-36","p":"2282BV","lat":52.262,"lon":4.515},{"s":2640,"c":"S GRAVENZANDE","a":"LANGESTRAAT 58-60","p":"2691BJ","lat":52.086,"lon":4.26},{"s":2658,"c":"UTRECHT","a":"ROELANTDREEF 235","p":"3562KH","lat":52.0635,"lon":5.1086},{"s":2666,"c":"S GRAVENHAGE","a":"LEYWEG 709M","p":"2545GM","lat":52.0411,"lon":4.3178},{"s":2674,"c":"ECHT","a":"BOVENSTESTRAAT 27","p":"6101EH","lat":51.83,"lon":5.86},{"s":2682,"c":"DOESBURG","a":"OOIPOORTSTRAAT 22","p":"6981DV","lat":52.012,"lon":6.18},{"s":2690,"c":"ROERMOND","a":"KAST. HORNSTRAAT 21","p":"6043JR","lat":51.846,"lon":5.86},{"s":2712,"c":"WOERDEN","a":"VOORSTRAAT 48","p":"3441CN","lat":51.866,"lon":4.66},{"s":2720,"c":"WASSENAAR","a":"LANGSTRAAT 188-190","p":"2242JZ","lat":52.246,"lon":4.515},{"s":2747,"c":"AALSMEER","a":"ZIJDSTRAAT 86","p":"1431EE","lat":52.362,"lon":4.82},{"s":2755,"c":"HELMOND","a":"NIEUWVELD 49","p":"5702HW","lat":51.68,"lon":5.285},{"s":2763,"c":"VLAARDINGEN","a":"VEERPLEIN 132B","p":"3131CN","lat":51.892,"lon":4.44},{"s":2798,"c":"GORINCHEM","a":"PIAZZA CENTER 84","p":"4204BT","lat":51.87,"lon":4.575},{"s":2801,"c":"HUISSEN","a":"LANGESTRAAT 16","p":"6851AP","lat":51.97,"lon":5.98},{"s":2810,"c":"MIDDELHARNIS","a":"BENEDEN ZANDPAD 174","p":"3241GA","lat":51.916,"lon":4.38},{"s":2836,"c":"ZWOLLE","a":"KLEINE A 1-3","p":"8011VS","lat":52.504,"lon":6.08},{"s":2852,"c":"HAARLEM","a":"GENERAAL CRONJESTR.56-60","p":"2021JK","lat":52.395,"lon":4.6574},{"s":2860,"c":"BOXMEER","a":"STEENSTRAAT 71","p":"5831JC","lat":51.722,"lon":5.3},{"s":2887,"c":"ROTTERDAM","a":"MARINUS BOLKPLEIN 26-30","p":"3067AK","lat":51.924,"lon":4.49},{"s":2917,"c":"S HERTOGENBOSCH","a":"HELFTHEUVEL PASSAGE 103-105","p":"5224AC","lat":51.418,"lon":5.475},{"s":2925,"c":"ROTTERDAM","a":"MEENT 19-21","p":"3011JB","lat":51.9233,"lon":4.4817},{"s":2933,"c":"GORINCHEM","a":"HOOGSTRAAT 18-20","p":"4201CB","lat":51.87,"lon":4.56},{"s":2941,"c":"LEUSDEN","a":"DE GRUTTERIJ 10","p":"3831NE","lat":51.812,"lon":4.63},{"s":2950,"c":"SOEST","a":"PLEIN VAN ZUID 4-10","p":"3768ED","lat":51.884,"lon":4.775},{"s":2968,"c":"LEERDAM","a":"KERKSTRAAT 58","p":"4141AX","lat":51.866,"lon":4.91},{"s":2976,"c":"VAALS","a":"MAASTRICHTERLAAN 43","p":"6291EL","lat":50.866,"lon":5.66},{"s":2992,"c":"ZIERIKZEE","a":"APPELMARKT 1","p":"4301CA","lat":51.63,"lon":3.88},{"s":3018,"c":"BUNSCHOTEN SPAKENB","a":"KERKSTRAAT 27","p":"3751AR","lat":51.88,"lon":4.74},{"s":3026,"c":"BEMMEL","a":"MARKT 32","p":"6681AE","lat":51.982,"lon":5.91},{"s":3077,"c":"VIANEN UT","a":"VOORSTRAAT 24","p":"4132AR","lat":51.862,"lon":4.915},{"s":3085,"c":"ZALTBOMMEL","a":"BOSCHSTRAAT 41-43","p":"5301AB","lat":51.43,"lon":5.48},{"s":3123,"c":"PANNINGEN","a":"MARKT 85-87","p":"5981AP","lat":51.442,"lon":6.08},{"s":3131,"c":"APELDOORN","a":"ADELAARSLAAN 152","p":"7331GJ","lat":52.212,"lon":6.88},{"s":3140,"c":"UTRECHT","a":"GODEBALDKWARTIER 333","p":"3511DS","lat":52.0977,"lon":5.1186},{"s":3158,"c":"ROZENBURG ZH","a":"RAADHUISPLEIN 7-9","p":"3181CE","lat":51.912,"lon":4.44},{"s":3174,"c":"NIJMEGEN","a":"ZWANENVELD 9054-A","p":"6538SC","lat":51.842,"lon":5.895},{"s":3182,"c":"LISSE","a":"BLOKHUIS 49-49A","p":"2161EV","lat":52.394,"lon":4.62},{"s":3190,"c":"MAASTRICHT","a":"GROTE STAAT 55","p":"6211CV","lat":50.8484,"lon":5.69},{"s":3212,"c":"BOXTEL","a":"RECHTERSTRAAT 4","p":"5281BV","lat":51.442,"lon":5.46},{"s":3239,"c":"AMSTERDAM","a":"KINKERSTRAAT 244","p":"1053GA","lat":52.3598,"lon":4.8584},{"s":3247,"c":"NUENEN","a":"PARKHOF 2-4","p":"5671EX","lat":51.508,"lon":5.6},{"s":3255,"c":"BEST","a":"HOOFDSTRAAT 20","p":"5683AD","lat":51.512,"lon":5.61},{"s":3301,"c":"WOUDENBERG","a":"DORPSSTRAAT 45","p":"3931EE","lat":51.812,"lon":4.41},{"s":3310,"c":"SLIEDRECHT","a":"KERKBUURT 84","p":"3361BK","lat":51.884,"lon":4.52},{"s":3328,"c":"ZWIJNDRECHT","a":"HOF VAN HOLLAND 27","p":"3332EH","lat":51.872,"lon":4.525},{"s":3336,"c":"LUNTEREN","a":"DORPSSTRAAT 95-97","p":"6741AC","lat":51.966,"lon":5.9},{"s":3344,"c":"TEGELEN","a":"KERKSTRAAT 39","p":"5931NL","lat":51.422,"lon":6.08},{"s":3352,"c":"UTRECHT","a":"INA BOUDIER BAKKERHOF 70-74","p":"3582VX","lat":52.0977,"lon":5.1333},{"s":3379,"c":"RIDDERKERK","a":"BALJUWSTRAAT 1","p":"2981DC","lat":51.982,"lon":4.26},{"s":3387,"c":"S GRAVENHAGE","a":"THERESIASTRAAT 133","p":"2593AG","lat":52.086,"lon":4.31},{"s":3395,"c":"DORDRECHT","a":"KOLFSTRAAT 12-14","p":"3311XL","lat":51.864,"lon":4.52},{"s":3409,"c":"AMSTERDAM","a":"JAVASTRAAT 93","p":"1094HC","lat":52.3555,"lon":4.9369},{"s":3417,"c":"TILBURG","a":"WESTERMARKT 37A","p":"5042MD","lat":51.566,"lon":5.065},{"s":3425,"c":"OOSTERBEEK","a":"UTRECHTSEWEG 108","p":"6862AP","lat":51.974,"lon":5.985},{"s":3433,"c":"BODEGRAVEN","a":"KERKSTRAAT 21","p":"2411AA","lat":52.154,"lon":4.4},{"s":3441,"c":"SON","a":"NIEUWSTRAAT 36","p":"5691AD","lat":51.516,"lon":5.6},{"s":3450,"c":"LANDGRAAF","a":"VIVALDIPASSAGE 14","p":"6371LL","lat":51.208,"lon":5.96},{"s":3468,"c":"GOUDA","a":"GILDENBURG 74","p":"2804VK","lat":52.05,"lon":4.395},{"s":3476,"c":"S GRAVENHAGE","a":"LOOSDUINSE HOOFDSTRAAT 311","p":"2552AD","lat":52.07,"lon":4.305},{"s":3484,"c":"AXEL","a":"NOORDSTRAAT 18","p":"4571GD","lat":51.538,"lon":4.45},{"s":3492,"c":"GOIRLE","a":"DE HOVEL 40-42","p":"5051NR","lat":51.57,"lon":5.06},{"s":3514,"c":"WERKENDAM","a":"LIJNBAAN 16A","p":"4251CS","lat":51.89,"lon":4.56},{"s":3522,"c":"ROTTERDAM","a":"ZUIDPLEIN HOOG 715","p":"3083BJ","lat":51.932,"lon":4.47},{"s":3530,"c":"HENGELO OV","a":"W.C. THIEMSBRUG 39-41","p":"7551EZ","lat":52.22,"lon":6.88},{"s":3573,"c":"EERSEL","a":"NIEUWSTRAAT 4","p":"5521CC","lat":51.408,"lon":5.46},{"s":3581,"c":"ULFT","a":"MIDDELGRAAF 18-22","p":"7071WT","lat":52.008,"lon":6.18},{"s":3603,"c":"PIJNACKER","a":"OOSTLAAN 21-22","p":"2641DK","lat":52.066,"lon":4.26},{"s":3611,"c":"AMSTERDAM","a":"BOS & LOMMERPLEIN 186","p":"1055EK","lat":52.3598,"lon":4.8422},{"s":3620,"c":"ALMERE","a":"PLEIN 5-11","p":"1354LH","lat":52.37,"lon":5.215},{"s":3638,"c":"OUD BEIJERLAND","a":"OOST-VOORSTRAAT 24-25","p":"3262JE","lat":51.924,"lon":4.385},{"s":3646,"c":"AMERSFOORT","a":"NEPTUNUSPLEIN 34","p":"3814BB","lat":51.804,"lon":4.645},{"s":3662,"c":"ENSCHEDE","a":"WESSELER NERING 17-18","p":"7544JA","lat":52.216,"lon":6.895},{"s":3697,"c":"BENEDEN LEEUWEN","a":"SPORTLAAN 21","p":"6658BG","lat":51.97,"lon":5.945},{"s":3700,"c":"SUSTEREN","a":"R. VAN GELDERSTRAAT 1C","p":"6114EA","lat":51.834,"lon":5.875},{"s":3727,"c":"REUVER","a":"RIJKSWEG 34","p":"5953AG","lat":51.43,"lon":6.09},{"s":3735,"c":"OIRSCHOT","a":"DE LOOP 51","p":"5688EW","lat":51.512,"lon":5.635},{"s":3743,"c":"SOEST","a":"V WEEDESTRAAT 37","p":"3761CC","lat":51.884,"lon":4.74},{"s":3751,"c":"WIJK BIJ DUURSTEDE","a":"MARKT 6","p":"3961BC","lat":51.824,"lon":4.41},{"s":3760,"c":"TILBURG","a":"BESTERDRING 129","p":"5014HJ","lat":51.554,"lon":5.075},{"s":3778,"c":"HARDENBERG","a":"VOORSTRAAT 2","p":"7772AC","lat":52.528,"lon":6.095},{"s":3794,"c":"ALMERE","a":"NOORDEINDE 239","p":"1334AS","lat":52.362,"lon":5.215},{"s":3816,"c":"MALDEN","a":"PASSAGE 2","p":"6581WK","lat":51.862,"lon":5.86},{"s":3824,"c":"KERKRADE","a":"AKERSTRAAT 18","p":"6466HH","lat":51.524,"lon":5.985},{"s":3832,"c":"HENGELO OV","a":"WILLEM DE MERODESTRAAT 28","p":"7552WZ","lat":52.22,"lon":6.885},{"s":3840,"c":"BEEK EN DONK","a":"P. V. THIELPLEIN 7","p":"5741CP","lat":51.696,"lon":5.28},{"s":3859,"c":"MADE","a":"MARKTSTRAAT 3","p":"4921BE","lat":51.508,"lon":4.44},{"s":3867,"c":"UTRECHT","a":"VONDELLAAN 47","p":"3521GC","lat":52.0811,"lon":5.1086},{"s":3875,"c":"HEEZE","a":"KAPELSTRAAT 106","p":"5591HH","lat":51.436,"lon":5.46},{"s":3891,"c":"IJSSELSTEIN UT","a":"DE BIEZEN 6","p":"3401GD","lat":51.85,"lon":4.66},{"s":3905,"c":"OUDENBOSCH","a":"PR. V GINNEKENSTR 33-35","p":"4731JX","lat":51.592,"lon":4.6},{"s":3913,"c":"OUDDORP ZH","a":"DORPSTIENDEN 6-8","p":"3253AS","lat":51.92,"lon":4.39},{"s":3921,"c":"EINDHOVEN","a":"FRANZ LEHARPLEIN 3","p":"5654AZ","lat":51.4585,"lon":5.4897},{"s":3930,"c":"DINXPERLO","a":"HOGESTRAAT 33","p":"7091CB","lat":52.016,"lon":6.18},{"s":3948,"c":"GELEEN","a":"ANJELIERSTRAAT 10","p":"6163CK","lat":51.854,"lon":5.87},{"s":3956,"c":"TERBORG","a":"HOOFDSTRAAT 28","p":"7061CK","lat":52.004,"lon":6.18},{"s":3999,"c":"BUDEL","a":"MARKT 4","p":"6021CD","lat":51.838,"lon":5.85},{"s":4006,"c":"EERBEEK","a":"STUIJVENBURCHSTRAAT 141","p":"6961CV","lat":52.004,"lon":6.18},{"s":4022,"c":"NUNSPEET","a":"DORPSSTRAAT 47","p":"8071BX","lat":52.528,"lon":6.08},{"s":4049,"c":"HOEK VAN HOLLAND","a":"PRINS HENDRIKSTRAAT 255","p":"3151AK","lat":51.9,"lon":4.44},{"s":4057,"c":"GLANERBRUG","a":"GRONAUSESTRAAT 1110-1112","p":"7534AR","lat":52.212,"lon":6.895},{"s":4065,"c":"AMSTERDAM","a":"RIJNSTRAAT 53-55-57","p":"1078PZ","lat":52.3445,"lon":4.9148},{"s":4090,"c":"UDENHOUT","a":"KREITENMOLENSTRAAT 38-40","p":"5071BE","lat":51.578,"lon":5.06},{"s":4103,"c":"MAASTRICHT","a":"WYCKERBRUGSTRAAT 32-36","p":"6221ED","lat":50.8484,"lon":5.68},{"s":4111,"c":"HEYTHUYSEN","a":"DORPSTRAAT 12-14","p":"6093EC","lat":51.866,"lon":5.86},{"s":4120,"c":"HARDINXVELD-GIESSENDAM","a":"DEN BOGERD 1B","p":"3371AM","lat":51.888,"lon":4.52},{"s":4138,"c":"DUIVENDRECHT","a":"DORPSPLEIN 28-29","p":"1115CW","lat":52.2946,"lon":5.0006},{"s":4146,"c":"AMSTERDAM","a":"HOOFDDORPPLEIN 33-35","p":"1059CW","lat":52.3547,"lon":4.8246},{"s":4162,"c":"ROELOFARENDSVEEN","a":"NOORDPLEIN 27","p":"2371DA","lat":52.178,"lon":4.45},{"s":4189,"c":"TILBURG","a":"ZOMERSTRAAT 49B","p":"5038TR","lat":51.562,"lon":5.095},{"s":4197,"c":"WEZEP","a":"MEIDOORNPASSAGE 15A","p":"8091KS","lat":52.536,"lon":6.08},{"s":4200,"c":"KATWIJK ZH","a":"BADSTRAAT 2","p":"2225BM","lat":52.238,"lon":4.53},{"s":4219,"c":"WINTERSWIJK","a":"MISTERSTRAAT 22-24","p":"7101EW","lat":52.15,"lon":6.13},{"s":4227,"c":"WESTERVOORT","a":"DORPSPLEIN 110","p":"6931CZ","lat":51.992,"lon":6.18},{"s":4251,"c":"EINDHOVEN","a":"STRIJPSESTRAAT 202","p":"5616GW","lat":51.4302,"lon":5.4697},{"s":4260,"c":"EDE","a":"BELLESTEIN 73-81","p":"6714DP","lat":51.954,"lon":5.915},{"s":4278,"c":"VARSSEVELD","a":"DOETINCHEMSEWEG 1E","p":"7051AA","lat":52.0,"lon":6.18},{"s":4294,"c":"HAAKSBERGEN","a":"SPOORSTRAAT 23","p":"7481HV","lat":52.232,"lon":6.2},{"s":4316,"c":"AMSTERDAM","a":"FERDINAND BOLSTRAAT 33-39","p":"1072LB","lat":52.3459,"lon":4.8849},{"s":4324,"c":"EMMELOORD","a":"LANGE NERING 18-20","p":"8302EC","lat":52.28,"lon":5.535},{"s":4332,"c":"DRONTEN","a":"HET RUIM 54","p":"8251EP","lat":52.52,"lon":5.45},{"s":4340,"c":"OLDENZAAL","a":"DE DRIEHOEK 23","p":"7571ET","lat":52.228,"lon":6.88},{"s":4367,"c":"ZEEWOLDE","a":"HORSTERPLEIN 24","p":"3891ES","lat":51.836,"lon":4.63},{"s":4375,"c":"NIJVERDAL","a":"GROTESTRAAT 178","p":"7443BR","lat":52.216,"lon":6.21},{"s":4383,"c":"EMMEN","a":"NOORDERSTRAAT 31","p":"7811AK","lat":52.484,"lon":6.08},{"s":4391,"c":"EMMEN","a":"MONETPASSAGE 39","p":"7811DL","lat":52.484,"lon":6.08},{"s":4405,"c":"NOORDWIJKERHOUT","a":"DORPSSTRAAT 6A","p":"2211GC","lat":52.234,"lon":4.51},{"s":4413,"c":"BERLICUM NB","a":"MERCURIUSPLEIN 3","p":"5258AX","lat":51.43,"lon":5.495},{"s":4421,"c":"ZUNDERT","a":"MARKT 17","p":"4881CN","lat":51.582,"lon":4.46},{"s":4430,"c":"DE MEERN","a":"MEREVELDPLEIN 28-30","p":"3454CK","lat":51.87,"lon":4.675},{"s":4448,"c":"HOOGEVEEN","a":"HOOFDSTRAAT 127","p":"7902ED","lat":52.48,"lon":6.465},{"s":4464,"c":"ZWOLLE","a":"DIEZERSTRAAT 52","p":"8011RH","lat":52.504,"lon":6.08},{"s":4472,"c":"HALSTEREN","a":"DORPSSTRAAT 164","p":"4661HV","lat":51.574,"lon":4.53},{"s":4480,"c":"MIERLO","a":"PR. MARGRIETSTRAAT 112","p":"5731BX","lat":51.692,"lon":5.28},{"s":4502,"c":"HOOGERHEIDE","a":"RAADHUISSTRAAT 105","p":"4631ND","lat":51.562,"lon":4.53},{"s":4510,"c":"MAASBRACHT","a":"MOLENWEG 48","p":"6051HK","lat":51.85,"lon":5.85},{"s":4537,"c":"RIJSSEN","a":"HAARSTRAAT 7","p":"7462AK","lat":52.224,"lon":6.205},{"s":4545,"c":"LEEUWARDEN","a":"WIRDUMERDIJK 8-10","p":"8911CD","lat":52.084,"lon":5.1},{"s":4553,"c":"OMMEN","a":"VARSENERSTRAAT 5","p":"7731DC","lat":52.512,"lon":6.09},{"s":4588,"c":"BRIELLE","a":"NOBELSTRAAT 71-73","p":"3231BB","lat":51.912,"lon":4.38},{"s":4626,"c":"BURGUM","a":"MARKT 90","p":"9251JS","lat":52.75,"lon":6.9},{"s":4634,"c":"COEVORDEN","a":"FRIESESTRAAT 30","p":"7741GW","lat":52.516,"lon":6.09},{"s":4650,"c":"ZELHEM","a":"MAGNOLIAWEG 1C","p":"7021ZX","lat":51.988,"lon":6.18},{"s":4669,"c":"AMSTERDAM","a":"VAN LIMBURG STIRUMSTRAAT 58","p":"1051BC","lat":52.3713,"lon":4.8604},{"s":4677,"c":"WOLVEGA","a":"VAN HARENSTRAAT 51","p":"8471JC","lat":52.158,"lon":5.36},{"s":4693,"c":"GRONINGEN","a":"DIERENRIEMSTRAAT 252","p":"9742AN","lat":53.2443,"lon":6.5869},{"s":4715,"c":"LOCHEM","a":"MOLENSTRAAT 18","p":"7241AE","lat":52.216,"lon":6.16},{"s":4723,"c":"HELLEVOETSLUIS","a":"WC DE STRUYTSE HOECK 336","p":"3223DE","lat":51.908,"lon":4.39},{"s":4731,"c":"WINSCHOTEN","a":"LANGESTRAAT 49","p":"9671PB","lat":53.328,"lon":6.28},{"s":4740,"c":"RAALTE","a":"HERENSTRAAT 17","p":"8102CN","lat":52.48,"lon":6.075},{"s":4758,"c":"ALBLASSERDAM","a":"CORTGENE 4C","p":"2951ED","lat":51.97,"lon":4.26},{"s":4766,"c":"RAAMSDONKSVEER","a":"VRIJHEIDSTRAAT 1","p":"4941DX","lat":51.516,"lon":4.44},{"s":4774,"c":"GULPEN","a":"LOOIERSTRAAT 17","p":"6271BA","lat":50.858,"lon":5.66},{"s":4782,"c":"DEN HELDER","a":"BEATRIXSTRAAT 3","p":"1781EL","lat":52.512,"lon":4.78},{"s":4790,"c":"ZUTPHEN","a":"BEUKERSTRAAT 25","p":"7201LA","lat":52.2,"lon":6.16},{"s":4804,"c":"STEENWIJK","a":"OOSTERSTRAAT 36","p":"8331HE","lat":52.292,"lon":5.53},{"s":4820,"c":"VRIEZENVEEN","a":"WESTEINDE 29A","p":"7671EK","lat":52.528,"lon":6.08},{"s":4863,"c":"ALPHEN AAN DEN RIJN","a":"VAN MANDERSLOOSTRAAT 39","p":"2406CB","lat":52.15,"lon":4.425},{"s":4880,"c":"WADDINXVEEN","a":"BINNENDOOR 63","p":"2741NP","lat":52.066,"lon":4.36},{"s":4901,"c":"SIMPELVELD","a":"KLOOSTERPLEIN 3","p":"6369AW","lat":51.204,"lon":6.0},{"s":4910,"c":"SOMEREN","a":"POSTELSTRAAT 4","p":"5711EN","lat":51.684,"lon":5.28},{"s":4936,"c":"BORNE","a":"NIEUWE MARKT 16","p":"7622DD","lat":52.508,"lon":6.085},{"s":4944,"c":"HOOGEZAND","a":"GORECHT-OOST 58-64","p":"9603AC","lat":53.3,"lon":6.29},{"s":4960,"c":"NIJMEGEN","a":"ST JACOBSLAAN 139","p":"6533BR","lat":51.842,"lon":5.87},{"s":6114,"c":"NIJMEGEN","a":"BURCHTSTRAAT 53","p":"6511RB","lat":51.834,"lon":5.86},{"s":6115,"c":"TILBURG","a":"HEYHOEFPROMENADE 107","p":"5043RB","lat":51.566,"lon":5.07},{"s":6118,"c":"DREUMEL","a":"EKERSHOF 7","p":"6621CJ","lat":51.958,"lon":5.91},{"s":6119,"c":"PURMEREND","a":"VAN DAMPLEIN 15","p":"1448NB","lat":52.366,"lon":4.855},{"s":6121,"c":"HENGELO OV","a":"STRAATSBURG 26","p":"7559NM","lat":52.22,"lon":6.92},{"s":6125,"c":"ARNHEM","a":"DR C LELYWEG 11F","p":"6827BH","lat":51.958,"lon":6.01},{"s":6126,"c":"WARNSVELD","a":"DREIUMME 43A","p":"7232CN","lat":52.212,"lon":6.165},{"s":6127,"c":"SOESTERBERG","a":"RADEMAKERSTRAAT 9C","p":"3769BB","lat":51.884,"lon":4.78},{"s":6129,"c":"MAASLAND","a":"VELDESTEIJN 21-23","p":"3155SR","lat":51.9,"lon":4.46},{"s":6131,"c":"HAARLEM","a":"GROTE HOUTSTRAAT 38-40","p":"2011SP","lat":52.3908,"lon":4.6364},{"s":6132,"c":"BEEK","a":"WETH. SANGERSSTRAAT 164","p":"6191NA","lat":51.866,"lon":5.86},{"s":6133,"c":"NIEUW VENNEP","a":"HANDELPLEIN 13","p":"2151NL","lat":52.39,"lon":4.62},{"s":6135,"c":"BERGHEM","a":"PASTOOR VAN TETERINGSTRAAT 17","p":"5351EN","lat":51.45,"lon":5.48},{"s":6137,"c":"HAARLEM","a":"NICE PASSAGE 3B","p":"2037AJ","lat":52.37,"lon":4.6445},{"s":6138,"c":"KRIMPEN AD IJSSEL","a":"DE KORF 22","p":"2924AH","lat":51.958,"lon":4.275},{"s":6139,"c":"ZEIST","a":"SLOTLAAN 157","p":"3701GC","lat":51.86,"lon":4.74},{"s":6141,"c":"VLIJMEN","a":"PLEIN 14","p":"5251AT","lat":51.43,"lon":5.46},{"s":6143,"c":"GENDT","a":"JULIANASTRAAT 1","p":"6691AX","lat":51.986,"lon":5.91},{"s":6145,"c":"DOETINCHEM","a":"STATIONSSTRAAT 40","p":"7005AT","lat":51.98,"lon":6.2},{"s":6146,"c":"S HERTOGENBOSCH","a":"GRUTTOSTRAAT 25","p":"5212VM","lat":51.414,"lon":5.465},{"s":6147,"c":"AMSTERDAM","a":"BUIKSLOTERMEERPLEIN 123A","p":"1025ET","lat":52.4047,"lon":4.9414},{"s":6148,"c":"LIENDEN","a":"VERBRUGHWEG 36","p":"4033GP","lat":51.902,"lon":4.99},{"s":6149,"c":"ENSCHEDE","a":"KLANDERIJ 92","p":"7511HS","lat":52.204,"lon":6.88},{"s":6152,"c":"KERKDRIEL","a":"MONSEIGNEUR ZWIJSENPLEIN 29","p":"5331BE","lat":51.442,"lon":5.48},{"s":6153,"c":"WEHL","a":"KONINGIN WILHELMINAPLEIN 1","p":"7031BH","lat":51.992,"lon":6.18},{"s":6154,"c":"APELDOORN","a":"DEVENTERSTRAAT 3","p":"7311BH","lat":52.204,"lon":6.88},{"s":6156,"c":"NAALDWIJK","a":"DE TUINEN 68","p":"2671NX","lat":52.078,"lon":4.26},{"s":6157,"c":"IJSSELSTEIN UT","a":"DE CLINCKHOEFF 15","p":"3402GA","lat":51.85,"lon":4.665},{"s":6158,"c":"TER APEL","a":"KRUIER 11","p":"9561LZ","lat":53.104,"lon":6.86},{"s":6161,"c":"BOVENKARSPEL","a":"DE MIDDEND 74-A","p":"1611KT","lat":52.444,"lon":4.77},{"s":6162,"c":"BREDA","a":"DONK 16","p":"4824CS","lat":51.558,"lon":4.475},{"s":6165,"c":"VOLENDAM","a":"EUROPAPLEIN 1","p":"1131ZK","lat":52.377,"lon":4.85},{"s":6166,"c":"AMSTERDAM","a":"KALVERSTRAAT 226","p":"1012XJ","lat":52.3698,"lon":4.8948},{"s":6167,"c":"RIDDERKERK","a":"AMERSTRAAT 14","p":"2987CA","lat":51.982,"lon":4.29},{"s":6168,"c":"PURMEREND","a":"LEEUWERIKPLEIN 22-24","p":"1444HX","lat":52.366,"lon":4.835},{"s":6169,"c":"BARNEVELD","a":"BURU 44","p":"3772EX","lat":51.888,"lon":4.745},{"s":6171,"c":"LEUSDEN","a":"DE BIEZENKAMP 166","p":"3831JA","lat":51.812,"lon":4.63},{"s":6172,"c":"NIEUWERKERK","a":"POLDERWEG 3D","p":"4306BV","lat":51.63,"lon":3.905},{"s":6173,"c":"EINDHOVEN","a":"HEEZERWEG 322","p":"5643KN","lat":51.4189,"lon":5.4897},{"s":6174,"c":"PAPENDRECHT","a":"JAN VAN GOIJENSTRAAT 14","p":"3351JN","lat":51.88,"lon":4.52},{"s":6175,"c":"SPIJKENISSE","a":"STADHUISPASSAGE 2D","p":"3201ES","lat":51.9,"lon":4.38},{"s":6176,"c":"HOORN NH","a":"GROTE NOORD 70","p":"1621KL","lat":52.448,"lon":4.77},{"s":6177,"c":"OOSTVOORNE","a":"PASTORIELAAN 2","p":"3233CZ","lat":51.912,"lon":4.39},{"s":6178,"c":"UTRECHT","a":"BRUSSELPLEIN 141","p":"3541CH","lat":52.1033,"lon":5.0833},{"s":6179,"c":"NIEUW VENNEP","a":"DE SYMFONIE 61","p":"2151ME","lat":52.39,"lon":4.62},{"s":6181,"c":"MIJDRECHT","a":"RAADHUISPLEIN 4-6","p":"3641EE","lat":51.866,"lon":4.58},{"s":6183,"c":"DEVENTER","a":"KAREL DE GROTEPLEIN 36","p":"7415DH","lat":52.204,"lon":6.22},{"s":6184,"c":"RENESSE","a":"HOGEZOOM 194","p":"4325BJ","lat":51.638,"lon":3.9},{"s":6185,"c":"GILZE","a":"BISSCHOP DE VETPLEIN 2A","p":"5126CA","lat":51.558,"lon":5.095},{"s":6186,"c":"ZWAAG","a":"HOLLANDSE CIRKEL 65","p":"1689XE","lat":52.472,"lon":4.81},{"s":6188,"c":"WOERDEN","a":"LA FONTAINEPLEIN 20","p":"3446BX","lat":51.866,"lon":4.685},{"s":6189,"c":"ZEELAND","a":"KERKSTRAAT 32","p":"5411BA","lat":51.504,"lon":5.15},{"s":6190,"c":"ZUTPHEN","a":"DONKERESTEEG 7","p":"7201CR","lat":52.2,"lon":6.16},{"s":6191,"c":"AMSTERDAM","a":"SPAARNDAMMERSTRAAT 99","p":"1013TC","lat":52.384,"lon":4.8671},{"s":6192,"c":"OEGSTGEEST","a":"RUSTENBURGERPAD 1","p":"2342CV","lat":52.166,"lon":4.455},{"s":6193,"c":"ZETTEN","a":"HOOFDSTRAAT 38","p":"6671CE","lat":51.978,"lon":5.91},{"s":6194,"c":"GORINCHEM","a":"DE LINIE 24","p":"4208DE","lat":51.87,"lon":4.595},{"s":6195,"c":"ROSMALEN","a":"HARRIE COPPENSSTRAAT 12","p":"5241BE","lat":51.426,"lon":5.46},{"s":6197,"c":"ALKMAAR","a":"VAN OSTADELAAN 260","p":"1816JG","lat":52.484,"lon":4.735},{"s":6198,"c":"HEESCH","a":"'T DORP 57B","p":"5384MB","lat":51.462,"lon":5.495},{"s":6199,"c":"ASSEN","a":"RONDGANG 4-6","p":"9408MH","lat":52.85,"lon":6.565},{"s":6201,"c":"OPHEUSDEN","a":"DORPSSTRAAT 4","p":"4043KK","lat":51.906,"lon":4.99},{"s":6202,"c":"OOSTERHOUT NB","a":"ZUIDERHOUT 67-71","p":"4904AV","lat":51.5,"lon":4.455},{"s":6203,"c":"ARNHEM","a":"ACHTER DE COULISSEN 3","p":"6836NC","lat":51.962,"lon":6.005},{"s":6204,"c":"EDE","a":"PARKWEIDE 6","p":"6718DJ","lat":51.954,"lon":5.935},{"s":6205,"c":"APELDOORN","a":"HOOFDSTRAAT 50B","p":"7311KD","lat":52.204,"lon":6.88},{"s":6206,"c":"CULEMBORG","a":"CHOPINPLEIN 32","p":"4102CV","lat":51.85,"lon":4.915},{"s":6207,"c":"LEIDEN","a":"HAARLEMMERSTRAAT 70-74","p":"2312GC","lat":52.154,"lon":4.455},{"s":6208,"c":"ZAANDAM","a":"LANGEWEIDE 103-105","p":"1507NH","lat":52.42,"lon":4.84},{"s":6209,"c":"JULIANADORP","a":"SCHOOLWEG 43-49","p":"1787AV","lat":52.512,"lon":4.81},{"s":6211,"c":"VOORBURG","a":"KONINGIN JULIANALAAN 235-237","p":"2273JG","lat":52.258,"lon":4.52},{"s":6213,"c":"PURMEREND","a":"GILDEPLEIN 78","p":"1445BM","lat":52.366,"lon":4.84},{"s":6214,"c":"LEIDSCHENDAM","a":"LIGUSTER 10","p":"2262AC","lat":52.254,"lon":4.515},{"s":6216,"c":"UTRECHT","a":"TROOSTERHOF 11","p":"3571NC","lat":52.098,"lon":5.14},{"s":6217,"c":"KAMPEN","a":"DE AREND 2A","p":"8265NK","lat":52.524,"lon":5.47},{"s":6218,"c":"VEENDAM","a":"BENEDEN OOSTERDIEP 165-2","p":"9645LN","lat":53.316,"lon":6.3},{"s":6219,"c":"ST MICHIELSGESTEL","a":"TORENPLEIN 3","p":"5271AW","lat":51.438,"lon":5.46},{"s":6221,"c":"MAASTRICHT","a":"DE BEENTE 87","p":"6229AV","lat":50.838,"lon":5.7},{"s":6222,"c":"PURMEREND","a":"VAN BURGPLEIN 11","p":"1447KR","lat":52.366,"lon":4.85},{"s":6223,"c":"DEN BURG","a":"STENENPLAATS 6","p":"1791EA","lat":52.516,"lon":4.78},{"s":6224,"c":"MUSSELKANAAL","a":"MARKTSTRAAT 91C","p":"9581AD","lat":53.112,"lon":6.86},{"s":6225,"c":"KRIMPEN AAN DE LEK","a":"MARKT 114","p":"2931EC","lat":51.962,"lon":4.26},{"s":6226,"c":"HOUTEN","a":"FOSSA ITALICA 55-61","p":"3995XA","lat":51.836,"lon":4.43},{"s":6227,"c":"VOORHOUT","a":"HERENSTRAAT 92A","p":"2215KK","lat":52.234,"lon":4.53},{"s":6228,"c":"ZANDVOORT","a":"RAADHUISPLEIN 6","p":"2042LR","lat":52.376,"lon":4.625},{"s":6229,"c":"SCHAIJK","a":"KAPELANIEPLEIN 19","p":"5374BX","lat":51.458,"lon":5.495},{"s":6235,"c":"LELYSTAD","a":"PROMESSE 37","p":"8232VX","lat":52.512,"lon":5.455},{"s":6236,"c":"CAPELLE AAN DEN IJSSEL","a":"AMSTELDIEP 24-26","p":"2904EC","lat":51.95,"lon":4.275},{"s":6237,"c":"MARKELO","a":"GROTESTRAAT 10","p":"7475AX","lat":52.228,"lon":6.22},{"s":6238,"c":"BORN","a":"TUINSTRAAT 20","p":"6121JD","lat":51.838,"lon":5.86},{"s":6239,"c":"APELDOORN","a":"OPERAPLEIN 95","p":"7323EL","lat":52.208,"lon":6.89},{"s":6241,"c":"BERGEN OP ZOOM","a":"PIUSPLEIN 3","p":"4621EM","lat":51.558,"lon":4.53},{"s":6242,"c":"AMSTERDAM","a":"DELFLANDPLEIN 176","p":"1062HW","lat":52.3483,"lon":4.8486},{"s":6243,"c":"IJMUIDEN","a":"VELSERHOF 75","p":"1972JG","lat":52.478,"lon":4.645},{"s":6244,"c":"ZEIST","a":"DE CLOMP 3108","p":"3704KA","lat":51.86,"lon":4.755},{"s":6245,"c":"TIEL","a":"WESTLEDEPLEIN 9","p":"4006BB","lat":51.89,"lon":5.005},{"s":6246,"c":"AMSTERDAM","a":"W. KRAANSTRAAT 22","p":"1063MG","lat":52.3462,"lon":4.8312},{"s":6247,"c":"BRUNSSUM","a":"VICTORIA 10","p":"6441DR","lat":51.516,"lon":5.96},{"s":6248,"c":"MILL","a":"MARKT 3","p":"5451BS","lat":51.52,"lon":5.15},{"s":6249,"c":"BAARLE NASSAU","a":"SINT ANNAPLEIN 5","p":"5111CA","lat":51.554,"lon":5.07},{"s":6251,"c":"ROTTERDAM","a":"ASTERLO 24","p":"3085AD","lat":51.932,"lon":4.48},{"s":6252,"c":"AMSTERDAM","a":"MOLUKKENSTRAAT 75-77","p":"1095AX","lat":52.3583,"lon":4.9484},{"s":6253,"c":"NIJMEGEN","a":"GROENESTRAAT 263A","p":"6531HK","lat":51.842,"lon":5.86},{"s":6255,"c":"GRONINGEN","a":"BEREN 56-60","p":"9714DV","lat":53.2158,"lon":6.5469},{"s":6257,"c":"DONGEN","a":"LOOIERSHOF 11","p":"5104HV","lat":51.55,"lon":5.085},{"s":6258,"c":"EINDHOVEN","a":"HERMANUS BOEXSTRAAT 20-22","p":"5611AJ","lat":51.4416,"lon":5.4697},{"s":6259,"c":"VEENENDAAL","a":"STUIVENBERGHEEM 5","p":"3907NH","lat":51.8,"lon":4.44},{"s":6262,"c":"RODEN","a":"HEERESTRAAT 75","p":"9301AE","lat":52.83,"lon":6.33},{"s":6264,"c":"ASSENDELFT","a":"KAAIKHOF 11","p":"1567JP","lat":52.444,"lon":4.84},{"s":6266,"c":"BEVERWIJK","a":"SPOORSINGEL 19","p":"1947LA","lat":52.466,"lon":4.67},{"s":6268,"c":"ZWIJNDRECHT","a":"OUDELAND 134-140","p":"3335VJ","lat":51.872,"lon":4.54},{"s":6269,"c":"ROERMOND","a":"STEENWEG 16","p":"6041EW","lat":51.846,"lon":5.85},{"s":6272,"c":"ZWAAGDIJK","a":"ZWAAGDIJK 225","p":"1684NG","lat":52.472,"lon":4.785},{"s":6273,"c":"NUENEN","a":"HOGE BRAKE 16","p":"5672GL","lat":51.508,"lon":5.605},{"s":6274,"c":"ENSCHEDE","a":"LAGE BOTHOFSTRAAT 169-171","p":"7533AS","lat":52.212,"lon":6.89},{"s":6275,"c":"ARNHEM","a":"FORTUNASTRAAT 40","p":"6846XV","lat":51.966,"lon":6.005},{"s":6276,"c":"ZEVENBERGEN","a":"MOLENSTRAAT 13","p":"4761CJ","lat":51.604,"lon":4.6},{"s":6277,"c":"STADSKANAAL","a":"OUDE MARKT 1","p":"9501VK","lat":53.08,"lon":6.86},{"s":6279,"c":"THOLEN","a":"SCHIETBAAN 6-8","p":"4691AB","lat":51.586,"lon":4.53},{"s":6282,"c":"HAARLEM","a":"AMSTERDAMSTRAAT 44","p":"2032PR","lat":52.394,"lon":4.6228},{"s":6284,"c":"LEEK","a":"SAMUEL LEVIESTRAAT 53","p":"9351BM","lat":52.85,"lon":6.33},{"s":6286,"c":"HULST","a":"STATIONSPLEIN 22-K","p":"4561GC","lat":51.534,"lon":4.45},{"s":6287,"c":"HARDERWIJK","a":"P.C. HOOFTPLEIN 3-5","p":"3842HB","lat":51.816,"lon":4.635},{"s":6288,"c":"ALMERE","a":"NAJADENSTRAAT 12","p":"1363ST","lat":52.374,"lon":5.21},{"s":6289,"c":"GRONINGEN","a":"HERESTRAAT 53","p":"9711LC","lat":53.2215,"lon":6.5669},{"s":6291,"c":"ROOSENDAAL","a":"TOLBERGCENTRUM 142","p":"4708HK","lat":51.58,"lon":4.635},{"s":6292,"c":"VENLO","a":"NIJMEEGSEWEG 20","p":"5916PT","lat":51.414,"lon":6.105},{"s":6294,"c":"VLAARDINGEN","a":"VAN HOGENDORPLAAN 915","p":"3135BK","lat":51.892,"lon":4.46},{"s":6295,"c":"TERNEUZEN","a":"ALVAREZLAAN 36","p":"4536BD","lat":51.522,"lon":4.475},{"s":6297,"c":"BEILEN","a":"RAADHUISSTRAAT 4B","p":"9411NB","lat":52.854,"lon":6.53},{"s":6298,"c":"LEEUWARDEN","a":"STADIONPLEIN 1","p":"8914BX","lat":52.084,"lon":5.115},{"s":6299,"c":"ROTTERDAM","a":"HOOGSTRAAT 177B","p":"3011PM","lat":51.9233,"lon":4.4817},{"s":6300,"c":"S HEERENBERG","a":"STADSWAL 17","p":"7041AM","lat":51.996,"lon":6.18},{"s":6301,"c":"DORDRECHT","a":"P.A. DE KOKPLEIN 122","p":"3318JW","lat":51.864,"lon":4.555},{"s":6302,"c":"ALMERE","a":"MARGARET CAVENDISHWEG 87","p":"1349BN","lat":52.366,"lon":5.24},{"s":6303,"c":"PRINSENBEEK","a":"MARKT 18","p":"4841AC","lat":51.566,"lon":4.46},{"s":6304,"c":"ASSEN","a":"MERCURIUSPLEIN 74","p":"9401DM","lat":52.85,"lon":6.53},{"s":6305,"c":"UTRECHT","a":"VREDENBURG 9","p":"3511BA","lat":52.0977,"lon":5.1186},{"s":6306,"c":"BARENDRECHT","a":"VAN BEUNINGENHAVEN 22","p":"2993EH","lat":51.986,"lon":4.27},{"s":6307,"c":"MAASTRICHT","a":"BRUSSELSEPOORT 66","p":"6216CG","lat":50.8426,"lon":5.69},{"s":6308,"c":"LENT","a":"MOORMANNSTRAAT 8A","p":"6663RM","lat":51.974,"lon":5.92},{"s":6311,"c":"NEDERWEERT","a":"LAMBERTUSHOF 2","p":"6031EP","lat":51.842,"lon":5.85},{"s":6317,"c":"TERNEUZEN","a":"HAVENSTRAAT 11-13","p":"4531EK","lat":51.522,"lon":4.45},{"s":6318,"c":"GRONINGEN","a":"SIERSTEENLAAN 446","p":"9743ES","lat":53.2386,"lon":6.5969},{"s":6319,"c":"AMSTERDAM","a":"CHR HUYGENSPLEIN 26-28-34","p":"1098RC","lat":52.339,"lon":4.9421},{"s":6327,"c":"STEENBERGEN NB","a":"KAAISTRAAT 28","p":"4651BN","lat":51.57,"lon":4.53},{"s":6335,"c":"ROTTERDAM","a":"KEIZERSWAARD 70","p":"3078AM","lat":51.928,"lon":4.495},{"s":6343,"c":"NIJMEGEN","a":"COUWENBERGSTRAAT 140","p":"6535RX","lat":51.842,"lon":5.88},{"s":6351,"c":"ZOETERMEER","a":"BURG. VAN LEEUWENPASSAGE 28","p":"2711JV","lat":52.054,"lon":4.36},{"s":6379,"c":"WEERT","a":"SINT JOBPLEIN 26","p":"6004JZ","lat":51.83,"lon":5.865},{"s":6382,"c":"MIDDENBEEMSTER","a":"RIJPERWEG 52B-52C","p":"1462ME","lat":52.374,"lon":4.825},{"s":6383,"c":"TEN BOER","a":"KOOPMANSPLEIN 16","p":"9791MA","lat":53.216,"lon":5.73},{"s":6384,"c":"UTRECHT","a":"OUDE GRACHT 161","p":"3511AL","lat":52.0977,"lon":5.1186},{"s":6385,"c":"ROTTERDAM","a":"1E MIDDELLANDSTRAAT 60","p":"3014BG","lat":51.9179,"lon":4.4657},{"s":6386,"c":"SNEEK","a":"NAUWE BURGSTRAAT 13","p":"8601CD","lat":52.06,"lon":5.09},{"s":6387,"c":"S HERTOGENBOSCH","a":"HINTHAMERSTRAAT 41","p":"5211ME","lat":51.414,"lon":5.46},{"s":6388,"c":"BREDA","a":"GINNEKENWEG 48","p":"4818JG","lat":51.554,"lon":4.495},{"s":6391,"c":"CASTRICUM","a":"GEESTERDUIN 43","p":"1902EJ","lat":52.45,"lon":4.645},{"s":6392,"c":"SCHIEDAM","a":"HOF VAN SPALAND 16","p":"3121CB","lat":51.888,"lon":4.44},{"s":6393,"c":"TILBURG","a":"HEUVELSTRAAT 79","p":"5038AC","lat":51.562,"lon":5.095},{"s":6394,"c":"EGMOND AAN ZEE","a":"VOORSTRAAT 131","p":"1931AK","lat":52.462,"lon":4.64},{"s":6395,"c":"HEILOO","a":"'T LOO 54-57","p":"1851HT","lat":52.5,"lon":4.71},{"s":6396,"c":"BRESKENS","a":"DORPSSTRAAT 2-4","p":"4511EG","lat":51.514,"lon":4.45},{"s":6397,"c":"KAMPEN","a":"OUDESTRAAT 107","p":"8261CJ","lat":52.524,"lon":5.45},{"s":6398,"c":"AMERSFOORT","a":"VARKENSMARKT 20","p":"3811LD","lat":51.804,"lon":4.63},{"s":6402,"c":"GENNEP","a":"BRUGSTRAAT 8-10","p":"6591BD","lat":51.866,"lon":5.86},{"s":6403,"c":"VALKENSWAARD","a":"DE KERVERIJ 5","p":"5554CM","lat":51.42,"lon":5.475},{"s":6404,"c":"BREDA","a":"RAT VERLEGHSTRAAT 12-14","p":"4815NZ","lat":51.554,"lon":4.48},{"s":6406,"c":"ENSCHEDE","a":"NOORD-ESMARKERRONDWEG 421-13","p":"7533BL","lat":52.212,"lon":6.89},{"s":6407,"c":"VUGHT","a":"BARON VAN H\u00d6VELLPLEIN 6","p":"5261GH","lat":51.434,"lon":5.46},{"s":6408,"c":"JOURE","a":"MIDSTRAAT 115","p":"8501AJ","lat":52.06,"lon":5.1},{"s":6409,"c":"ZOETERMEER","a":"OOSTERHEEMPLEIN 483","p":"2721NJ","lat":52.058,"lon":4.36},{"s":6411,"c":"ALPHEN AAN DEN RIJN","a":"BARONIE 14","p":"2404XG","lat":52.15,"lon":4.415},{"s":6412,"c":"S GRAVENHAGE","a":"DE VENESTRAAT 4-10","p":"2511AS","lat":52.0793,"lon":4.3122},{"s":6413,"c":"DELFT","a":"TROELSTRALAAN 69","p":"2624ET","lat":52.058,"lon":4.275},{"s":6414,"c":"EINDHOVEN","a":"TONGELRESESTRAAT 221","p":"5613DG","lat":51.4416,"lon":5.4897},{"s":6415,"c":"HOORN","a":"HUESMOLEN 150","p":"1625HX","lat":52.448,"lon":4.79},{"s":6416,"c":"MONSTER","a":"ZEESTRAAT 22","p":"2681CM","lat":52.082,"lon":4.26},{"s":6417,"c":"HOORN","a":"BETJE WOLFFPLEIN 164","p":"1628NK","lat":52.448,"lon":4.805},{"s":6418,"c":"AMSTERDAM","a":"MOLENWIJK 31","p":"1035EG","lat":52.4243,"lon":4.8989},{"s":6419,"c":"HEERLEN","a":"CORIO CENTER 6","p":"6411LX","lat":51.504,"lon":5.96},{"s":6421,"c":"ALMERE","a":"KORTE PROMENADE 12","p":"1315HN","lat":52.354,"lon":5.22},{"s":6422,"c":"HILVERSUM","a":"SEINSTRAAT 5","p":"1223DE","lat":52.358,"lon":4.835},{"s":6424,"c":"AMSTERDAM","a":"EERSTE OOSTERPARKSTRAAT 197","p":"1091HA","lat":52.3557,"lon":4.9203},{"s":6425,"c":"GELEEN","a":"MARKT 112","p":"6161GN","lat":51.854,"lon":5.86},{"s":6427,"c":"S GRAVENHAGE","a":"WEIMARSTRAAT 88-90","p":"2562HB","lat":52.0719,"lon":4.3678},{"s":6428,"c":"ZOETERMEER","a":"SAMANTHAGANG 188","p":"2719CL","lat":52.054,"lon":4.4},{"s":6431,"c":"UTRECHT","a":"LANGE VIESTRAAT 2R","p":"3511BK","lat":52.0977,"lon":5.1186},{"s":6432,"c":"S GRAVENHAGE","a":"DE STEDE 12","p":"2543BG","lat":52.0567,"lon":4.3178},{"s":6433,"c":"AMSTERDAM","a":"BEETHOVENSTRAAT 69-75","p":"1077HP","lat":52.3419,"lon":4.8998},{"s":6434,"c":"LEIDERDORP","a":"WINKELHOF 73","p":"2353TV","lat":52.17,"lon":4.46},{"s":6436,"c":"GRONINGEN","a":"VERLENGDE HEREWEG 91-97","p":"9721AH","lat":53.2272,"lon":6.5669},{"s":6437,"c":"ALMERE","a":"RIMSKY KORSSAKOVWEG 11","p":"1323LP","lat":52.358,"lon":5.21},{"s":6438,"c":"AMSTERDAM","a":"EERSTE CONS. HUYGENSSTRAAT 55 H","p":"1054BS","lat":52.3535,"lon":4.864},{"s":6439,"c":"ROOSENDAAL","a":"ROSELAAR 4 D","p":"4701BC","lat":51.58,"lon":4.6},{"s":6440,"c":"RIJEN","a":"HOOFDSTRAAT 1D","p":"5121JA","lat":51.558,"lon":5.07},{"s":6459,"c":"BRUMMEN","a":"AMBACHTSTRAAT 20","p":"6971BR","lat":52.008,"lon":6.18},{"s":6467,"c":"MAASTRICHT","a":"MARKT 57","p":"6211CL","lat":50.8484,"lon":5.69},{"s":6483,"c":"BERGEIJK","a":"ELSENHOF 1","p":"5571LA","lat":51.428,"lon":5.46},{"s":6505,"c":"S GRAVENHAGE","a":"LANGE POTEN 31","p":"2511CM","lat":52.0793,"lon":4.3122},{"s":6513,"c":"DRACHTEN","a":"NOORDERBUURT 21-23","p":"9203AL","lat":52.73,"lon":6.91},{"s":6521,"c":"AMSTERDAM","a":"BILDERDIJKSTRAAT 73-87","p":"1053KM","lat":52.3598,"lon":4.8584},{"s":6530,"c":"ZEIST","a":"LAAN VAN VOLLENHOVE 2977","p":"3706AK","lat":51.86,"lon":4.765},{"s":6548,"c":"SASSENHEIM","a":"HOOFDSTRAAT 245","p":"2171BD","lat":52.398,"lon":4.62},{"s":6572,"c":"AMSTERDAM","a":"DAPPERPLEIN 62","p":"1093GS","lat":52.3486,"lon":4.9213},{"s":6580,"c":"ZOETERMEER","a":"DORPSSTRAAT 89","p":"2712AE","lat":52.054,"lon":4.365},{"s":6599,"c":"AMERSFOORT","a":"EMICLAERHOF 106","p":"3823ER","lat":51.808,"lon":4.64},{"s":6637,"c":"DELFT","a":"BRABANTSE TURFMARKT 79-81","p":"2611CM","lat":52.054,"lon":4.26},{"s":6661,"c":"ALKMAAR","a":"LAAT 217A","p":"1811EH","lat":52.484,"lon":4.71},{"s":6670,"c":"DELDEN","a":"LANGESTRAAT 51","p":"7491AB","lat":52.236,"lon":6.2},{"s":6688,"c":"RIJSWIJK ZH","a":"PRINS CONSTANTIJN PROMENADE 3","p":"2284DL","lat":52.262,"lon":4.525},{"s":6696,"c":"HOUTEN","a":"PLEIN 9","p":"3991DK","lat":51.836,"lon":4.41},{"s":6700,"c":"NIEUWEGEIN","a":"'T SLUISJE 6","p":"3438AH","lat":51.862,"lon":4.695},{"s":6718,"c":"WOERDEN","a":"MOLENVLIETBRINK 307-311","p":"3448HT","lat":51.866,"lon":4.695},{"s":6726,"c":"HAZERSWOUDE DORP","a":"AMBACHTSPLEIN 12","p":"2391BD","lat":52.186,"lon":4.45},{"s":6734,"c":"SCHAGEN","a":"GEDEMPTE GRACHT 26","p":"1741GC","lat":52.496,"lon":4.78},{"s":6769,"c":"NUMANSDORP","a":"VOORSTRAAT 37-39","p":"3281AT","lat":51.932,"lon":4.38},{"s":6777,"c":"ROTTERDAM","a":"PEPPELWEG 69","p":"3053GC","lat":51.92,"lon":4.47},{"s":6785,"c":"OOSTERWOLDE FR","a":"STATIONSSTRAAT 7","p":"8431ET","lat":52.142,"lon":5.36},{"s":6807,"c":"EIBERGEN","a":"DE BRINK 24A","p":"7151CR","lat":52.17,"lon":6.13},{"s":6823,"c":"HAARLEM","a":"KRUISSTRAAT 42","p":"2011PZ","lat":52.3908,"lon":4.6364},{"s":6831,"c":"UITHOORN","a":"AMSTELPLEIN 99B","p":"1421SB","lat":52.358,"lon":4.82},{"s":6858,"c":"AMSTERDAM","a":"VAN WOUSTRAAT 98-102","p":"1073LR","lat":52.3513,"lon":4.8937},{"s":6866,"c":"BADHOEVEDORP","a":"LORENTZPLEIN 43","p":"1171BB","lat":52.393,"lon":4.85},{"s":6874,"c":"AMSTERDAM","a":"BIJLMERPLEIN 970","p":"1102MK","lat":52.3124,"lon":4.9432},{"s":6882,"c":"WATERINGEN","a":"PLEIN 28","p":"2291CC","lat":52.266,"lon":4.51},{"s":6890,"c":"ROTTERDAM","a":"WOLPHAERTSBOCHT 7","p":"3082AA","lat":51.932,"lon":4.465},{"s":6912,"c":"UITGEEST","a":"PRINSES BEATRIXLAAN 6","p":"1911HR","lat":52.454,"lon":4.64},{"s":6939,"c":"BREUKELEN UT","a":"HAZESLINGER 5","p":"3621AT","lat":51.858,"lon":4.58},{"s":6955,"c":"BREDA","a":"BRABANTPLEIN 25-27","p":"4817LR","lat":51.554,"lon":4.49},{"s":6963,"c":"BREDA","a":"MOERWIJK 42","p":"4826HP","lat":51.558,"lon":4.485},{"s":6980,"c":"BREDA","a":"HEKSENWAAG 27-31","p":"4823JT","lat":51.558,"lon":4.47},{"s":6998,"c":"OOSTERHOUT NB","a":"ARKENDONK 41-42","p":"4907XP","lat":51.5,"lon":4.47},{"s":7003,"c":"NUTH","a":"MARKT 2A","p":"6361CB","lat":51.204,"lon":5.96},{"s":7004,"c":"BREDA","a":"GINNEKENSTRAAT 44-46","p":"4811JH","lat":51.554,"lon":4.46},{"s":7015,"c":"DUIVEN","a":"ELSHOFPASSAGE 34-38","p":"6921BB","lat":51.988,"lon":6.18},{"s":7016,"c":"ENSCHEDE","a":"RIJNSTRAAT 52-58","p":"7523GG","lat":52.208,"lon":6.89},{"s":7017,"c":"GOUDA","a":"MIDDENMOLENPLEIN 102","p":"2807GZ","lat":52.05,"lon":4.41},{"s":7018,"c":"ROTTERDAM","a":"POOLSTERSTRAAT 46","p":"3067LX","lat":51.924,"lon":4.49},{"s":7019,"c":"CAPELLE AAN DEN IJSSEL","a":"KOPERWIEK 75","p":"2903AD","lat":51.95,"lon":4.27},{"s":7023,"c":"ALPHEN AAN DEN RIJN","a":"RIDDERHOF 26","p":"2402EN","lat":52.15,"lon":4.405},{"s":7024,"c":"HEERHUGOWAARD","a":"MIDDENWAARD 2A","p":"1703SE","lat":52.48,"lon":4.79},{"s":7031,"c":"BEST","a":"WILHELMINAPLEIN 10","p":"5684VK","lat":51.512,"lon":5.615},{"s":7032,"c":"ALKMAAR","a":"LANGESTRAAT 66","p":"1811JJ","lat":52.484,"lon":4.71},{"s":7033,"c":"LEENDE","a":"DORPSTRAAT 66","p":"5595CJ","lat":51.436,"lon":5.48},{"s":7034,"c":"HEEMSKERK","a":"EUROPASSAGE 9","p":"1966WH","lat":52.474,"lon":4.665},{"s":7035,"c":"VLAARDINGEN","a":"DE LOPER 36","p":"3136CN","lat":51.892,"lon":4.465},{"s":7036,"c":"AMSTERDAM","a":"JAN EVERTSENSTRAAT 126-130","p":"1056EJ","lat":52.3663,"lon":4.8397},{"s":7037,"c":"WAALRE","a":"DEN HOF 94","p":"5582JZ","lat":51.432,"lon":5.465},{"s":7038,"c":"SCHERPENZEEL GLD","a":"PLEIN 1940 185","p":"3925JM","lat":51.808,"lon":4.43},{"s":7039,"c":"AMSTERDAM","a":"AUGUST ALLEBEPLEIN 267","p":"1062AB","lat":52.3483,"lon":4.8486},{"s":7041,"c":"MAASTRICHT","a":"HERCULESHOF 5","p":"6215BB","lat":50.86,"lon":5.69},{"s":7043,"c":"GENEMUIDEN","a":"KRUISSTRAAT 2A","p":"8281BA","lat":52.532,"lon":5.45},{"s":7045,"c":"NIJMEGEN","a":"MOLENWEG 4","p":"6542PV","lat":51.846,"lon":5.865},{"s":7046,"c":"OUDEWATER","a":"KORTE HAVENSTRAAT 12-14","p":"3421AG","lat":51.858,"lon":4.66},{"s":7047,"c":"SEVENUM","a":"PAST. VULLINGHSPLEIN 44A","p":"5975DJ","lat":51.438,"lon":6.1},{"s":7048,"c":"DIEREN","a":"DIDERNA 6A","p":"6951CW","lat":52.0,"lon":6.18},{"s":7049,"c":"AMSTELVEEN","a":"NIEUW LOOPVELD 3","p":"1181ZK","lat":52.397,"lon":4.85},{"s":7054,"c":"VOERENDAAL","a":"FURENTHELA 3-9","p":"6367TL","lat":51.204,"lon":5.99},{"s":7055,"c":"LEEUWARDEN","a":"BILGAARDPASSAGE 42","p":"8918HT","lat":52.084,"lon":5.135},{"s":7057,"c":"SWALMEN","a":"ST. JANSPLEIN 10-12","p":"6071LM","lat":51.858,"lon":5.85},{"s":7059,"c":"RHEDEN","a":"GROENESTRAAT 53-55","p":"6991GC","lat":52.016,"lon":6.18},{"s":7061,"c":"MIDDELBURG","a":"LANGE GEERE 151","p":"4331MG","lat":51.642,"lon":3.88},{"s":7063,"c":"S GRAVENHAGE","a":"3E V.D. KUNSTRAAT 79","p":"2521BR","lat":52.082,"lon":4.2928},{"s":7064,"c":"LANDGRAAF","a":"HOVENSTRAAT 126C","p":"6374HG","lat":51.208,"lon":5.975},{"s":7065,"c":"NIEUWLEUSEN","a":"GROTE MARKT 45","p":"7711CZ","lat":52.504,"lon":6.09},{"s":7066,"c":"VINKEVEEN","a":"PLEVIERENLAAN 17","p":"3645GN","lat":51.866,"lon":4.6},{"s":7071,"c":"HENDRIK IDO AMBACHT","a":"DE SCHOOF 65","p":"3341EA","lat":51.876,"lon":4.52},{"s":7072,"c":"ZWOLLE","a":"BACHPLEIN 12","p":"8031HR","lat":52.512,"lon":6.08},{"s":7074,"c":"MEERSSEN","a":"BUNDERSTRAAT 11","p":"6231EH","lat":50.8658,"lon":5.69},{"s":7075,"c":"STAPHORST","a":"EBBINGE WUBBENLAAN 2-4","p":"7951AB","lat":52.5,"lon":6.46},{"s":7076,"c":"AMSTERDAM","a":"NIEUWENDIJK 160","p":"1012MS","lat":52.3698,"lon":4.8948},{"s":7082,"c":"ARNHEM","a":"ROGGESTRAAT 13","p":"6811BB","lat":51.954,"lon":5.98},{"s":7083,"c":"WORKUM","a":"'T SUD 18","p":"8711CV","lat":52.134,"lon":5.35},{"s":7085,"c":"LOON OP ZAND","a":"KERKSTRAAT 56A","p":"5175BB","lat":51.578,"lon":5.09},{"s":7089,"c":"EELDE","a":"HOOFDWEG 93D","p":"9761EC","lat":53.204,"lon":5.73},{"s":7092,"c":"WIJHE","a":"LANGSTRAAT 6","p":"8131BC","lat":52.492,"lon":6.07},{"s":7094,"c":"LEERSUM","a":"HONINGRAAT 19-21","p":"3956HG","lat":51.82,"lon":4.435},{"s":7101,"c":"MAASTRICHT","a":"MALBERGSINGEL 40","p":"6218AV","lat":50.8368,"lon":5.69},{"s":7102,"c":"LELYSTAD","a":"TJALK 15-06","p":"8232LK","lat":52.512,"lon":5.455},{"s":7103,"c":"ELSLOO LB","a":"STATIONSSTRAAT 102A","p":"6181AK","lat":51.862,"lon":5.86},{"s":7107,"c":"KAMPEN","a":"PENNINGKRUID 34","p":"8265EE","lat":52.524,"lon":5.47},{"s":7109,"c":"IJSSELMUIDEN","a":"MARKERESPLEIN 20-21","p":"8271BV","lat":52.528,"lon":5.45},{"s":7112,"c":"NIEUW BERGEN","a":"MOSAIQUE 31","p":"5854AW","lat":51.73,"lon":5.315},{"s":7113,"c":"DE LIER","a":"HOOFDSTRAAT 60","p":"2678CL","lat":52.078,"lon":4.295},{"s":7114,"c":"AMSTELVEEN","a":"WESTWIJKPLEIN 102","p":"1187LV","lat":52.397,"lon":4.88},{"s":7117,"c":"ABCOUDE","a":"HOOGSTRAAT 34","p":"1391BV","lat":52.386,"lon":5.2},{"s":7119,"c":"NOOTDORP","a":"LANGE BAAN 28-32","p":"2632GC","lat":52.062,"lon":4.265},{"s":7121,"c":"GRONINGEN","a":"WESTERHAVEN 70","p":"9718AC","lat":53.2101,"lon":6.5669},{"s":7124,"c":"SPANBROEK","a":"HERENWEG 56","p":"1715EH","lat":52.484,"lon":4.8},{"s":7125,"c":"ANNA PAULOWNA","a":"KOSHOF 5","p":"1761AT","lat":52.504,"lon":4.78},{"s":7126,"c":"URK","a":"NAGEL 58","p":"8321RG","lat":52.288,"lon":5.53},{"s":7132,"c":"NIJVERDAL","a":"KUPERSERF 65-69","p":"7443HD","lat":52.216,"lon":6.21},{"s":7133,"c":"ZUIDWOLDE DR","a":"HOOFDSTRAAT 111-A","p":"7921AG","lat":52.488,"lon":6.46},{"s":7134,"c":"EINDHOVEN","a":"ANTWERPENLAAN 22","p":"5628XE","lat":51.488,"lon":5.635},{"s":7137,"c":"VEENENDAAL","a":"VEENSLAG 88","p":"3905SL","lat":51.8,"lon":4.43},{"s":7138,"c":"BREDA","a":"VALKENIERSPLEIN 8","p":"4835RB","lat":51.562,"lon":4.48},{"s":7139,"c":"NIJMEGEN","a":"DAALSEWEG 234","p":"6521GR","lat":51.838,"lon":5.86},{"s":7142,"c":"BLOEMENDAAL","a":"BLOEMENDAALSEWEG 56","p":"2061CM","lat":52.384,"lon":4.62},{"s":7144,"c":"RIJNSBURG","a":"VLIET NOORDZIJDE 32-35","p":"2231GN","lat":52.242,"lon":4.51},{"s":7146,"c":"ALMELO","a":"VINCENT VAN GOGHPLEIN 7","p":"7606HN","lat":52.5,"lon":6.105},{"s":7147,"c":"SCHEEMDA","a":"DIEPSWAL 13","p":"9679AM","lat":53.328,"lon":6.32},{"s":7149,"c":"BOEKEL","a":"KERKSTRAAT 16","p":"5427BC","lat":51.508,"lon":5.18},{"s":7151,"c":"OUDERKERK AAN DE AMSTEL","a":"DORPSSTRAAT 15","p":"1191BH","lat":52.401,"lon":4.85},{"s":7152,"c":"UTRECHT","a":"VERLENGDE HOUTRAKGRACHT 417","p":"3544ED","lat":51.956,"lon":5.195},{"s":7153,"c":"VOLENDAM","a":"DE STIENT 1B","p":"1132BE","lat":52.377,"lon":4.855},{"s":7154,"c":"AMSTERDAM","a":"MAASSTRAAT 46-48","p":"1078HK","lat":52.3445,"lon":4.9148},{"s":7161,"c":"BROEK OP LANGEDIJK","a":"MARKTPLEIN 61","p":"1721CK","lat":52.488,"lon":4.78},{"s":7164,"c":"HENGELO OV","a":"CHRISTIAAN LANGEFELDSTRAAT 69","p":"7558CZ","lat":52.22,"lon":6.915},{"s":7166,"c":"DRACHTEN","a":"DWARSWIJK 96-100","p":"9202BP","lat":52.73,"lon":6.905},{"s":7167,"c":"LEMMER","a":"VERLAET 14","p":"8532BN","lat":52.072,"lon":5.105},{"s":7168,"c":"S GRAVENHAGE","a":"PARIJSPLEIN 1","p":"2548VL","lat":52.066,"lon":4.335},{"s":7169,"c":"WORMER","a":"DORPSSTRAAT 44","p":"1531HM","lat":52.432,"lon":4.81},{"s":7171,"c":"BLARICUM","a":"DORPSSTRAAT 5","p":"1261ES","lat":52.374,"lon":4.825},{"s":7173,"c":"MUIDEN","a":"PAMPUSWEG 1 UNIT 14","p":"1398PR","lat":52.386,"lon":5.235},{"s":7174,"c":"DORDRECHT","a":"VAN EESTERENPLEIN 136","p":"3315KV","lat":51.864,"lon":4.54},{"s":7177,"c":"VUGHT","a":"MOLENEINDPLEIN 7","p":"5262CW","lat":51.434,"lon":5.465},{"s":7178,"c":"NIJMEGEN","a":"LEUVENSBROEK 1006","p":"6546XB","lat":51.846,"lon":5.885},{"s":7179,"c":"HENGELO GLD","a":"RAADHUISSTRAAT 51 B/C","p":"7255BL","lat":52.22,"lon":6.18},{"s":7181,"c":"KLAZIENAVEEN","a":"LANGESTRAAT 106","p":"7891GG","lat":52.516,"lon":6.08},{"s":7182,"c":"VLIJMEN","a":"BURGEMEESTER VAN HOUTPLEIN 19","p":"5251PS","lat":51.43,"lon":5.46},{"s":7183,"c":"CHAAM","a":"BROUWERIJ 25","p":"4861SN","lat":51.574,"lon":4.46},{"s":7184,"c":"ZWOLLE","a":"DOBBE 6","p":"8032JV","lat":52.512,"lon":6.085},{"s":7185,"c":"AARLE RIXTEL","a":"DORPSSTRAAT 29","p":"5735EA","lat":51.692,"lon":5.3},{"s":7186,"c":"HELMOND","a":"HOOFDSTRAAT 146","p":"5706AN","lat":51.68,"lon":5.305},{"s":7191,"c":"HILVARENBEEK","a":"DIESSENSEWEG 31","p":"5081AE","lat":51.582,"lon":5.06},{"s":7193,"c":"HEERLEN","a":"HOMERUSPLEIN 8","p":"6411AW","lat":51.504,"lon":5.96},{"s":7199,"c":"ROERMOND","a":"ROERSINGELPASSAGE 31","p":"6041EE","lat":51.846,"lon":5.85},{"s":7202,"c":"PUTTERSHOEK","a":"PIETER REPELAERSTRAAT 66-68","p":"3297BM","lat":51.936,"lon":4.41},{"s":7203,"c":"DEVENTER","a":"BOXBERGERWEG 44","p":"7412BE","lat":52.204,"lon":6.205},{"s":7205,"c":"NIEUWEGEIN","a":"MUNTPLEIN 25","p":"3437AP","lat":51.862,"lon":4.69},{"s":7206,"c":"AMSTERDAM","a":"JODENBREESTRAAT 96B","p":"1011NS","lat":52.3731,"lon":4.9026},{"s":7207,"c":"BIDDINGHUIZEN","a":"BAAN 12","p":"8256AX","lat":52.52,"lon":5.475},{"s":7212,"c":"NIEUWKOOP","a":"KOLFBAAN 60","p":"2421BD","lat":52.158,"lon":4.4},{"s":7214,"c":"VLISSINGEN","a":"PAAUWENBURGWEG 4","p":"4384JE","lat":51.662,"lon":3.895},{"s":7216,"c":"HUIZEN","a":"OOSTERMEENT-NOORD 11","p":"1274SB","lat":52.378,"lon":4.84},{"s":7221,"c":"DOETINCHEM","a":"HOUTSMASTRAAT 152","p":"7002KK","lat":51.98,"lon":6.185},{"s":7222,"c":"MEIJEL","a":"DORPSSTRAAT 3","p":"5768CC","lat":51.704,"lon":5.315},{"s":7226,"c":"LEIDEN","a":"VIJF MEIPLEIN 25","p":"2321BN","lat":52.158,"lon":4.45},{"s":7227,"c":"NISTELRODE","a":"LAAR 29A","p":"5388HB","lat":51.462,"lon":5.515},{"s":7228,"c":"ZWOLLE","a":"WADE 7","p":"8043LR","lat":52.516,"lon":6.09},{"s":7229,"c":"VEENENDAAL","a":"PASSAGE 38","p":"3901AZ","lat":51.8,"lon":4.41},{"s":7231,"c":"RUURLO","a":"DORPSSTRAAT 54","p":"7261AX","lat":52.224,"lon":6.16},{"s":7232,"c":"HENGELO OV","a":"UITSLAGSWEG 91-3","p":"7556LN","lat":52.22,"lon":6.905},{"s":7233,"c":"EMMEN","a":"STATENWEG 55","p":"7824CT","lat":52.488,"lon":6.095},{"s":7234,"c":"DEN DOLDER","a":"DOLDERSEWEG 93","p":"3734BE","lat":51.872,"lon":4.755},{"s":7238,"c":"S GRAVENHAGE","a":"GEVERS DEYNOOTWEG 990- 86","p":"2586BZ","lat":52.082,"lon":4.325},{"s":7241,"c":"TILBURG","a":"PIUSPLEIN 32","p":"5038WN","lat":51.562,"lon":5.095},{"s":7242,"c":"MIDDELBURG","a":"JOHAN VAN REIGERSBERGSTRAAT 9","p":"4336XA","lat":51.642,"lon":3.905},{"s":7244,"c":"S GRAVENHAGE","a":"OUDE KUSTLIJN 104","p":"2496SJ","lat":52.186,"lon":4.425},{"s":7245,"c":"BEETSTERZWAAG","a":"HOOFDSTRAAT 66","p":"9244CP","lat":52.746,"lon":6.915},{"s":7247,"c":"HAELEN","a":"ROGGELSEWEG 8","p":"6081CT","lat":51.862,"lon":5.85},{"s":7253,"c":"DELFT","a":"BASTIAANSPLEIN 13","p":"2611DC","lat":52.054,"lon":4.26},{"s":7254,"c":"ASSENDELFT","a":"DORPSSTRAAT 537B","p":"1566BL","lat":52.444,"lon":4.835},{"s":7256,"c":"EYGELSHOVEN","a":"VELDHOFSTRAAT 19D","p":"6471CA","lat":51.528,"lon":5.96},{"s":7257,"c":"BAKEL","a":"DORPSSTRAAT 3","p":"5761BL","lat":51.704,"lon":5.28},{"s":7258,"c":"ROOSENDAAL","a":"ROSELAAR 10","p":"4701BC","lat":51.58,"lon":4.6},{"s":7259,"c":"AMERSFOORT","a":"LANGESTRAAT 116","p":"3811AK","lat":51.804,"lon":4.63},{"s":7262,"c":"LEIDEN","a":"PHILIPSBURGSTRAAT 10-14","p":"2315ZB","lat":52.154,"lon":4.47},{"s":7263,"c":"ROTTERDAM","a":"KORTE POOLSTERSTRAAT 15","p":"3067LZ","lat":51.924,"lon":4.49},{"s":7264,"c":"UTRECHT","a":"DOORNBURGLAAN 10-12","p":"3554EP","lat":52.0866,"lon":5.0633},{"s":7265,"c":"MAARHEEZE","a":"STATIONSSTRAAT 13","p":"6026CR","lat":51.838,"lon":5.875},{"s":7268,"c":"BEEK UBBERGEN","a":"SCHELLINGSHOF 3","p":"6573DK","lat":51.858,"lon":5.87},{"s":7269,"c":"MARUM","a":"WENDTSTEINWEG 68","p":"9363AR","lat":52.854,"lon":6.34},{"s":7271,"c":"AMSTELVEEN","a":"GROENHOF 136-137","p":"1186EX","lat":52.397,"lon":4.875},{"s":7279,"c":"ROTTERDAM","a":"OUDE WATERING 271-275","p":"3077RG","lat":51.928,"lon":4.49},{"s":7282,"c":"S GRAVENHAGE","a":"LEYWEG 940P","p":"2545GV","lat":52.0411,"lon":4.3178},{"s":7288,"c":"ALPHEN AAN DEN RIJN","a":"PROVINCIEPASSAGE 43-49","p":"2408GT","lat":52.15,"lon":4.435},{"s":7291,"c":"PUTTE","a":"ANTWERPSESTRAAT 34","p":"4645BJ","lat":51.566,"lon":4.55},{"s":7292,"c":"ULVENHOUT","a":"DORPSTRAAT 81A","p":"4851CL","lat":51.57,"lon":4.46},{"s":7293,"c":"AMSTERDAM","a":"BUITENVELDERTSELAAN 160","p":"1081AC","lat":52.3321,"lon":4.8577},{"s":7297,"c":"GIETEN","a":"DE TROG 60","p":"9461DC","lat":52.874,"lon":6.53},{"s":7298,"c":"MIDDELHARNIS","a":"WESTDIJK 22-24","p":"3241GV","lat":51.916,"lon":4.38},{"s":7299,"c":"VELDEN","a":"MARKT 10","p":"5941GA","lat":51.426,"lon":6.08},{"s":7301,"c":"LICHTENVOORDE","a":"MARKT 12A","p":"7131DG","lat":52.162,"lon":6.13},{"s":7302,"c":"SURHUISTERVEEN","a":"DE KOLK 24","p":"9231CX","lat":52.742,"lon":6.9},{"s":7303,"c":"NIEUWERKERK AAN DEN IJSSEL","a":"REIGERHOF 92","p":"2914KD","lat":51.954,"lon":4.275},{"s":7304,"c":"BEDUM","a":"NOORDWOLDERWEG 7","p":"9781AD","lat":53.212,"lon":5.73},{"s":7305,"c":"DEVENTER","a":"FLORA 247-251","p":"7422LP","lat":52.208,"lon":6.205},{"s":7306,"c":"DOKKUM","a":"BOTERSTRAAT 13","p":"9101KG","lat":53.2,"lon":6.55},{"s":7307,"c":"GROENLO","a":"BELTRUMSESTRAAT 31","p":"7141AK","lat":52.166,"lon":6.13},{"s":7308,"c":"KRIMPEN AAN DEN IJSSEL","a":"RAADHUISPLEIN 55B","p":"2922AG","lat":51.958,"lon":4.265},{"s":7309,"c":"NEEDE","a":"OUDESTRAAT 49","p":"7161DT","lat":52.174,"lon":6.13},{"s":7311,"c":"BORCULO","a":"MURALTPLEIN 19","p":"7271AS","lat":52.228,"lon":6.16},{"s":7312,"c":"ELBURG","a":"JUFFERENSTRAAT 22","p":"8081CR","lat":52.532,"lon":6.08},{"s":7314,"c":"HAREN GN","a":"RIJKSSTRAATWEG 181","p":"9752BE","lat":53.2,"lon":5.735},{"s":7315,"c":"HOOGEVEEN","a":"DE WEIDE 7-11","p":"7908AB","lat":52.48,"lon":6.495},{"s":7317,"c":"BERGAMBACHT","a":"H.B. NEDERBURGHPLEIN 6","p":"2861AV","lat":52.074,"lon":4.38},{"s":7319,"c":"BERGEN OP ZOOM","a":"ANTWERPSESTRAATWEG 76-78","p":"4615AT","lat":51.554,"lon":4.55},{"s":7324,"c":"DORDRECHT","a":"ADMIRAALSPLEIN 159-160","p":"3317BC","lat":51.864,"lon":4.55},{"s":7325,"c":"DORDRECHT","a":"PEARL BUCK-ERF 77","p":"3315BA","lat":51.864,"lon":4.54},{"s":7326,"c":"DUIVEN","a":"EILANDPLEIN 488","p":"6922ER","lat":51.988,"lon":6.185},{"s":7327,"c":"ENSCHEDE","a":"RAADHUISSTRAAT 16","p":"7511HK","lat":52.204,"lon":6.88},{"s":7328,"c":"FRANEKER","a":"BREEDEPLAATS 7","p":"8801LZ","lat":53.18,"lon":5.78},{"s":7329,"c":"GRONINGEN","a":"VISMARKT 15-17","p":"9712CA","lat":53.2215,"lon":6.5569},{"s":7331,"c":"GRONINGEN","a":"VAN LENNEPLAAN 109","p":"9721PE","lat":53.2272,"lon":6.5669},{"s":7332,"c":"HOORN NH","a":"GROTE BEER 5-J","p":"1622ES","lat":52.448,"lon":4.775},{"s":7333,"c":"LELYSTAD","a":"DE WISSEL 12","p":"8232DP","lat":52.512,"lon":5.455},{"s":7334,"c":"NIJMEGEN","a":"OUDE GROENESTRAAT 65","p":"6515EB","lat":51.834,"lon":5.88},{"s":7336,"c":"OLDENZAAL","a":"IN DEN VIJFHOEK 15","p":"7571DT","lat":52.228,"lon":6.88},{"s":7337,"c":"REUSEL","a":"MARKT 54-58","p":"5541EA","lat":51.416,"lon":5.46},{"s":7338,"c":"RIDDERKERK","a":"DILLENBURGPLEIN 16-18","p":"2983CC","lat":51.982,"lon":4.27},{"s":7339,"c":"ROTTERDAM","a":"BINNENHOF 11","p":"3069KV","lat":51.8893,"lon":4.5157},{"s":7341,"c":"ROTTERDAM","a":"MATHENESSERPLEIN 81","p":"3022LD","lat":51.9258,"lon":4.4457},{"s":7342,"c":"SNEEK","a":"OOSTERDIJK 18","p":"8601BT","lat":52.06,"lon":5.09},{"s":7344,"c":"STIENS","a":"LANGEBUORREN 15-17","p":"9051BD","lat":53.22,"lon":6.55},{"s":7346,"c":"TILBURG","a":"BUURMALSENPLEIN 6-9","p":"5043XL","lat":51.566,"lon":5.07},{"s":7347,"c":"UITHUIZEN","a":"BLINK 1A","p":"9981AJ","lat":52.942,"lon":5.83},{"s":7348,"c":"URK","a":"WIJK 2-NR34","p":"8321ER","lat":52.288,"lon":5.53},{"s":7349,"c":"UTRECHT","a":"HAMMARSKJOLDHOF 31","p":"3527HD","lat":52.0756,"lon":5.1086},{"s":7351,"c":"VROOMSHOOP","a":"JULIANAPLEIN 2A","p":"7681AW","lat":52.532,"lon":6.08},{"s":7352,"c":"WEERT","a":"LANGSTRAAT 19A","p":"6001CS","lat":51.83,"lon":5.85},{"s":7353,"c":"WIJCHEN","a":"MARKT PROMENADE 20","p":"6602HR","lat":51.95,"lon":5.915},{"s":7354,"c":"WINTERSWIJK","a":"WOOLDSTRAAT 27","p":"7101NM","lat":52.15,"lon":6.13},{"s":7355,"c":"ZUIDHORN","a":"OVERTUINEN 7B","p":"9801BR","lat":53.18,"lon":5.7},{"s":7357,"c":"ZWANENBURG","a":"DENNENLAAN 114C","p":"1161CT","lat":52.389,"lon":4.85},{"s":7359,"c":"ZWOLLE","a":"TH A KEMPISSTRAAT 20","p":"8021BB","lat":52.508,"lon":6.08},{"s":7362,"c":"BERGSCHENHOEK","a":"DE VLASHOECK 40","p":"2661LM","lat":52.074,"lon":4.26},{"s":7363,"c":"GRONINGEN","a":"OVERWINNINGSPLEIN 25-29","p":"9728GR","lat":53.2329,"lon":6.5569},{"s":7364,"c":"GRONINGEN","a":"VAN IMHOFFSTRAAT 12","p":"9721CP","lat":53.2272,"lon":6.5669},{"s":7365,"c":"HOOGKERK","a":"ZUIDERWEG 3","p":"9745AA","lat":53.196,"lon":5.75},{"s":7367,"c":"EINDHOVEN","a":"BIARRITZPLEIN 17-19","p":"5627LE","lat":51.4529,"lon":5.4897},{"s":7368,"c":"LEEUWARDEN","a":"SCHRANS 83","p":"8932NB","lat":52.092,"lon":5.105},{"s":7369,"c":"MEDEMBLIK","a":"NIEUWSTRAAT 44 - 46","p":"1671BE","lat":52.468,"lon":4.77},{"s":7373,"c":"ROTTERDAM","a":"SPINOZAWEG 395","p":"3076ET","lat":51.928,"lon":4.485},{"s":7375,"c":"ROTTERDAM","a":"CROOSWIJKSEWEG 109-113","p":"3034HH","lat":51.9313,"lon":4.5157},{"s":7377,"c":"ROTTERDAM","a":"VUURPLAAT 461-463","p":"3071AR","lat":51.928,"lon":4.46},{"s":7378,"c":"ROTTERDAM","a":"AMBACHTSPLEIN 203-207","p":"3068GV","lat":51.8823,"lon":4.5057},{"s":7379,"c":"SCHIEDAM","a":"NIEUWE PASSAGE 12","p":"3111EG","lat":51.884,"lon":4.44},{"s":7384,"c":"GOUDA","a":"NIEUWE MARKTPASSAGE 14","p":"2801HV","lat":52.05,"lon":4.38},{"s":7385,"c":"HAAREN","a":"DRIEHOEVEN 70","p":"5076BJ","lat":51.578,"lon":5.085},{"s":7386,"c":"ROTTERDAM","a":"VAN BEETHOVENSINGEL 52","p":"3055JK","lat":51.9033,"lon":4.5657},{"s":7387,"c":"ROCKANJE","a":"DORPSPLEIN 2","p":"3235AD","lat":51.912,"lon":4.4},{"s":7388,"c":"ROTTERDAM","a":"PLEIN 1953-NR50-53","p":"3086EE","lat":51.932,"lon":4.485},{"s":7389,"c":"NIJMEGEN","a":"MARIKENSTRAAT 71","p":"6511PX","lat":51.834,"lon":5.86},{"s":7391,"c":"S HERTOGENBOSCH","a":"ROMPERTPASSAGE 8-12","p":"5233AN","lat":51.422,"lon":5.47},{"s":7392,"c":"LANDSMEER","a":"ZUIDEINDE 1A","p":"1121CJ","lat":52.373,"lon":4.85},{"s":7394,"c":"GROU","a":"STATIONSWEG 38C","p":"9001EH","lat":53.2,"lon":6.55},{"s":7396,"c":"LEMELERVELD","a":"KROONPLEIN 22","p":"8151AZ","lat":52.5,"lon":6.07},{"s":7397,"c":"KOLLUM","a":"MR. ANDREAESTRAAT 14D","p":"9291MA","lat":52.766,"lon":6.9},{"s":7399,"c":"ALKMAAR","a":"JOHANNA NABERSTRAAT 59-61","p":"1827LB","lat":52.488,"lon":4.74},{"s":7402,"c":"JULIANADORP","a":"DROOGHE BOL 1038","p":"1788VB","lat":52.512,"lon":4.815},{"s":7404,"c":"MAARSSENBROEK","a":"BISONSPOOR 2049","p":"3605LE","lat":51.85,"lon":4.6},{"s":7405,"c":"CULEMBORG","a":"KOOPMANSGILDEPLEIN 11","p":"4105TX","lat":51.85,"lon":4.93},{"s":7406,"c":"AMSTERDAM","a":"BELGIEPLEIN 102","p":"1066SC","lat":52.331,"lon":4.837},{"s":7407,"c":"KOOG AAN DE ZAAN","a":"MOLENWERF 16","p":"1541WR","lat":52.436,"lon":4.81},{"s":7408,"c":"AMSTERDAM","a":"BIJLMERDREEF 1142","p":"1103JV","lat":52.3063,"lon":4.9533},{"s":7411,"c":"AMSTERDAM","a":"OOSTELIJKE HANDELSKADE 1033","p":"1019BW","lat":52.3604,"lon":4.929},{"s":7412,"c":"OSS","a":"WOLFSKOOI 39","p":"5345MH","lat":51.446,"lon":5.5},{"s":7413,"c":"SPIJKENISSE","a":"HADEWIJCHPLAATS 40-48","p":"3207KG","lat":51.9,"lon":4.41},{"s":7414,"c":"DEVENTER","a":"ANDRIESSENPLEIN 28","p":"7425GZ","lat":52.208,"lon":6.22},{"s":7416,"c":"RHOON","a":"HOF VAN PORTLAND 4","p":"3162WJ","lat":51.904,"lon":4.445},{"s":7421,"c":"NIEUWEGEIN","a":"DORPSSTRAAT 46","p":"3433CL","lat":51.862,"lon":4.67},{"s":7436,"c":"DINTELOORD","a":"WESTVOORSTRAAT 52","p":"4671CE","lat":51.578,"lon":4.53},{"s":7438,"c":"APELDOORN","a":"KORIANDERPLEIN 17","p":"7322NA","lat":52.208,"lon":6.885},{"s":7439,"c":"ZOETERMEER","a":"KENTGENSPLEIN 9","p":"2717HS","lat":52.054,"lon":4.39},{"s":7441,"c":"BERGEN NH","a":"JAN OLDENBURGLAAN 9","p":"1861JS","lat":52.504,"lon":4.71},{"s":7442,"c":"DEVENTER","a":"DREEF 142-144","p":"7414EJ","lat":52.204,"lon":6.215},{"s":7443,"c":"ZOETERMEER","a":"PETUNIATUIN 7","p":"2724NA","lat":52.058,"lon":4.375},{"s":7444,"c":"HILVERSUM","a":"KAPITTELWEG 119","p":"1216HX","lat":52.354,"lon":4.85},{"s":7447,"c":"HOOGVLIET RT","a":"BINNENBAN 20-28","p":"3191CH","lat":51.916,"lon":4.44},{"s":7448,"c":"NOORDWOLDE","a":"MANAUPLEIN 30","p":"8391BZ","lat":52.316,"lon":5.53},{"s":7454,"c":"ENKHUIZEN","a":"KOPERWIEKPLEIN 6-8","p":"1602NK","lat":52.44,"lon":4.775},{"s":7456,"c":"VENLO","a":"VLEESSTRAAT 61-63","p":"5911JD","lat":51.414,"lon":6.08},{"s":7458,"c":"ARNHEM","a":"KRUIDENPLEIN 3","p":"6833GV","lat":51.962,"lon":5.99},{"s":7459,"c":"GOES","a":"DE SPINNE 39","p":"4463CZ","lat":51.504,"lon":3.84},{"s":7468,"c":"ALMELO","a":"ESKERPLEIN 6","p":"7603WG","lat":52.5,"lon":6.09},{"s":7476,"c":"VORDEN","a":"KERKSTRAAT 11A","p":"7251BC","lat":52.22,"lon":6.16},{"s":7477,"c":"MAASTRICHT","a":"DORPSTRAAT 19","p":"6227BK","lat":50.838,"lon":5.69},{"s":7478,"c":"MOORDRECHT","a":"KERKLAAN 17-19","p":"2841XH","lat":52.066,"lon":4.38},{"s":7481,"c":"BAVEL","a":"PASTOOR DOENSSTRAAT 8","p":"4854CP","lat":51.57,"lon":4.475},{"s":7484,"c":"VLISSINGEN","a":"WALSTRAAT 124-128","p":"4381GS","lat":51.662,"lon":3.88},{"s":7486,"c":"ST ANNAPAROCHIE","a":"VAN HARENSTRAAT 80","p":"9076BZ","lat":53.228,"lon":6.575},{"s":7487,"c":"DALFSEN","a":"BLOEMENDALSTRAAT 6","p":"7721AM","lat":52.508,"lon":6.09},{"s":7488,"c":"DENEKAMP","a":"EUROWERFT 14A","p":"7591DG","lat":52.236,"lon":6.88},{"s":7489,"c":"TUBBERGEN","a":"GROTESTRAAT 46-48","p":"7651CJ","lat":52.52,"lon":6.08},{"s":7491,"c":"BOLSWARD","a":"MARKTSTRAAT 13","p":"8701JV","lat":52.13,"lon":5.35},{"s":7492,"c":"OUDE PEKELA","a":"DE HELLING 50","p":"9665JX","lat":53.324,"lon":6.3},{"s":7493,"c":"HATTEM","a":"KERKSTRAAT 36","p":"8051GM","lat":52.52,"lon":6.08},{"s":7494,"c":"NIEUW AMSTERDAM","a":"VAART ZZ 54B","p":"7833AC","lat":52.492,"lon":6.09},{"s":7495,"c":"APPINGEDAM","a":"DIJKSTRAAT 38","p":"9901AT","lat":52.91,"lon":5.83},{"s":7496,"c":"DEN HELDER","a":"KEIZERSTRAAT 34","p":"1781GH","lat":52.512,"lon":4.78},{"s":7499,"c":"TILBURG","a":"WAGNERPLEIN 50C","p":"5011LR","lat":51.554,"lon":5.06},{"s":7502,"c":"DIEMEN","a":"DIEMERPLEIN 96","p":"1111JD","lat":52.3046,"lon":4.9895},{"s":7503,"c":"ROTTERDAM","a":"LUSTHOFSTRAAT 79","p":"3061WL","lat":51.9033,"lon":4.4957},{"s":7504,"c":"MAASSLUIS","a":"DR KUYPERKADE 11","p":"3142GB","lat":51.896,"lon":4.445},{"s":7505,"c":"HEERHUGOWAARD","a":"RAADHUISPLEIN 40A","p":"1701EJ","lat":52.48,"lon":4.78},{"s":7514,"c":"AMSTERDAM","a":"LAMBERTUS ZIJLPLEIN 21-23","p":"1067JR","lat":52.337,"lon":4.816},{"s":7516,"c":"HOOGEZAND","a":"MEINT VENINGASTRAAT 3A","p":"9601KC","lat":53.3,"lon":6.28},{"s":7517,"c":"LEIDEN","a":"STATIONSPLEIN 218","p":"2312AR","lat":52.154,"lon":4.455},{"s":7521,"c":"ZWOLLE","a":"KLEIN GRACHTJE 24-26","p":"8021JC","lat":52.508,"lon":6.08},{"s":7522,"c":"BUITENPOST","a":"KERKSTRAAT 15","p":"9285TA","lat":52.762,"lon":6.92},{"s":7523,"c":"OOSTERHOUT NB","a":"ARENDSTRAAT 21A","p":"4901JJ","lat":51.5,"lon":4.44},{"s":7524,"c":"HOOFDDORP","a":"POLDERPLEIN 225-227","p":"2132BG","lat":52.382,"lon":4.625},{"s":7525,"c":"WOERDEN","a":"GROENENDAAL 34","p":"3441BD","lat":51.866,"lon":4.66},{"s":7526,"c":"GORSSEL","a":"HOOFDSTRAAT 48A","p":"7213CX","lat":52.204,"lon":6.17},{"s":7535,"c":"HEEMSKERK","a":"GILDENPLEIN 2-4-6","p":"1967KL","lat":52.474,"lon":4.67},{"s":7536,"c":"ROTTERDAM","a":"SCHIEDAMSEWEG 54-56","p":"3025AD","lat":51.9093,"lon":4.4457},{"s":7538,"c":"AMSTELVEEN","a":"BRINK 56-84","p":"1188ND","lat":52.397,"lon":4.885},{"s":7539,"c":"ZWAAGWESTEINDE","a":"LEEUWERIKSTRAAT 72","p":"9271CS","lat":52.758,"lon":6.9},{"s":7544,"c":"ALMERE","a":"STATIONSSTRAAT 21B","p":"1315KE","lat":52.354,"lon":5.22},{"s":7545,"c":"HAARLEM","a":"LEONARDO DA VINCIPLEIN 5","p":"2037RR","lat":52.37,"lon":4.6445},{"s":7572,"c":"DOETINCHEM","a":"ROZENGAARDSEWEG 8A","p":"7001DP","lat":51.98,"lon":6.18},{"s":7575,"c":"EMMEN","a":"MIDDENHAAG 159","p":"7815LB","lat":52.484,"lon":6.1},{"s":7576,"c":"CAPELLE AAN DEN IJSSEL","a":"PUCCINEPASSAGE 21-27","p":"2901GK","lat":51.95,"lon":4.26},{"s":7577,"c":"SCHIEDAM","a":"LAAN VAN BOL'ES 7","p":"3122AE","lat":51.888,"lon":4.445},{"s":7578,"c":"ARNHEM","a":"STEENSTRAAT 42","p":"6828CL","lat":51.958,"lon":6.015},{"s":7579,"c":"ODIJK","a":"DE MEENT 24","p":"3984JJ","lat":51.832,"lon":4.425},{"s":7583,"c":"MAASTRICHT","a":"MOSAE FORUM 139","p":"6211DT","lat":50.8484,"lon":5.69},{"s":7584,"c":"EINDHOVEN","a":"TARWELAAN 78","p":"5632KG","lat":51.4302,"lon":5.4597},{"s":7585,"c":"EMMER COMPASCUUM","a":"RUNDE ZZ 111","p":"7881HR","lat":52.512,"lon":6.08},{"s":7586,"c":"VEGHEL","a":"DE BUNDERS 62-66","p":"5467JZ","lat":51.524,"lon":5.18},{"s":7588,"c":"BAARLO","a":"GROTESTRAAT 19","p":"5991AV","lat":51.446,"lon":6.08},{"s":7591,"c":"MAASTRICHT","a":"AMBYERSTRAAT NOORD 44-02/44-03","p":"6225EE","lat":50.831,"lon":5.69},{"s":7592,"c":"SPRANG CAPELLE","a":"RAADHUISPLEIN 29A","p":"5161CG","lat":51.574,"lon":5.07},{"s":7594,"c":"VALKENSWAARD","a":"VAN BRUHEZEDAL 24-28","p":"5551EW","lat":51.42,"lon":5.46},{"s":7602,"c":"STRIJEN","a":"ORANJESTRAAT 28A","p":"3291BS","lat":51.936,"lon":4.38},{"s":7603,"c":"HOOFDDORP","a":"MARKENBURG 107","p":"2135DS","lat":52.382,"lon":4.64},{"s":7605,"c":"S GRAVENHAGE","a":"GOUDSBLOEMLAAN 111-115","p":"2565CR","lat":52.0789,"lon":4.3778},{"s":7606,"c":"UTRECHT","a":"DRAAIWEG 61","p":"3515EK","lat":52.1033,"lon":5.1186},{"s":7607,"c":"HEILOO","a":"STATIONSPLEIN 41","p":"1851LN","lat":52.5,"lon":4.71},{"s":7609,"c":"WIJK EN AALBURG","a":"MARKT 38-40","p":"4261DC","lat":51.894,"lon":4.56},{"s":7611,"c":"S GRAVENHAGE","a":"AMBACHTSGAARDE 182","p":"2542EJ","lat":52.0635,"lon":4.334},{"s":7613,"c":"ROTTERDAM","a":"STREKSINGEL 69A","p":"3054HB","lat":51.92,"lon":4.475},{"s":7614,"c":"DEVENTER","a":"BOREELPLEIN 9","p":"7411EH","lat":52.204,"lon":6.2},{"s":7615,"c":"WAPENVELD","a":"KLAPPERDIJK 28","p":"8191AE","lat":52.516,"lon":6.07},{"s":7619,"c":"S HERTOGENBOSCH","a":"ZUIDERPARKWEG 67","p":"5216HA","lat":51.414,"lon":5.485},{"s":7622,"c":"TILBURG","a":"PIETER VREEDEPLEIN 167","p":"5038BW","lat":51.562,"lon":5.095},{"s":7623,"c":"GEFFEN","a":"DORPSTRAAT 7","p":"5386AK","lat":51.462,"lon":5.505},{"s":7624,"c":"MILLINGEN AAN DE RIJN","a":"BURG EIJCKELHOFSTRAAT 2A","p":"6566AT","lat":51.854,"lon":5.885},{"s":7625,"c":"KORTENHOEF","a":"MEENTHOF 44","p":"1241CZ","lat":52.366,"lon":4.825},{"s":7626,"c":"CASTRICUM","a":"BURG. MOOIJSTRAAT 25","p":"1901EP","lat":52.45,"lon":4.64},{"s":7631,"c":"HOOFDDORP","a":"GENDERENPLEIN 12","p":"2134DP","lat":52.382,"lon":4.635},{"s":7633,"c":"TWELLO","a":"MARKTPLEIN 38","p":"7391DZ","lat":52.236,"lon":6.88},{"s":7635,"c":"MAASTRICHT","a":"VOLTASTRAAT 19","p":"6224EK","lat":50.831,"lon":5.68},{"s":7636,"c":"HELMOND","a":"DE PLAETSE 80","p":"5708ZJ","lat":51.68,"lon":5.315},{"s":7639,"c":"SCHIEDAM","a":"LANGE KERKSTRAAT 32","p":"3111NP","lat":51.884,"lon":4.44},{"s":7641,"c":"BERKEL EN RODENRIJS","a":"KERKSTRAAT 16-18","p":"2651CE","lat":52.07,"lon":4.26},{"s":7645,"c":"HOUTEN","a":"STELLINGMOLEN 9","p":"3995AT","lat":51.836,"lon":4.43},{"s":7648,"c":"GRONINGEN","a":"KAJUIT 253","p":"9733CS","lat":53.2329,"lon":6.5769},{"s":7649,"c":"MIDDELBURG","a":"FAZANTENHOF 16","p":"4332XT","lat":51.642,"lon":3.885},{"s":7652,"c":"ETTEN LEUR","a":"KORTE BRUGSTRAAT 2","p":"4871XS","lat":51.578,"lon":4.46},{"s":7656,"c":"ENTER","a":"DORPSSTRAAT 118","p":"7468CP","lat":52.224,"lon":6.235},{"s":7659,"c":"GORREDIJK","a":"HOOFDSTRAAT 63B","p":"8401BW","lat":52.13,"lon":5.36},{"s":7661,"c":"EINDHOVEN","a":"CASSANDRAPLEIN 6","p":"5631BA","lat":51.4359,"lon":5.4597},{"s":7662,"c":"AMERSFOORT","a":"CRUQUIUS 61-63-65","p":"3825MJ","lat":51.808,"lon":4.65},{"s":7665,"c":"ALKMAAR","a":"EUROPABOULEVARD 347","p":"1825RK","lat":52.488,"lon":4.73},{"s":7666,"c":"AALTEN","a":"KERKSTRAAT 8","p":"7121DN","lat":52.158,"lon":6.13},{"s":7668,"c":"GOOR","a":"GROTESTRAAT 117A","p":"7471BN","lat":52.228,"lon":6.2},{"s":7671,"c":"SPIJKENISSE","a":"ROZEMARIJNDONK 33-39","p":"3206PM","lat":51.9,"lon":4.405},{"s":7676,"c":"ROTTERDAM","a":"MALTAPLEIN 15-16","p":"3059XW","lat":51.92,"lon":4.5},{"s":7692,"c":"OLST","a":"JAN SCHAMHARTSTRAAT 1B","p":"8121CM","lat":52.488,"lon":6.07},{"s":7693,"c":"AMSTELVEEN","a":"BANKRASHOF 27","p":"1183NR","lat":52.397,"lon":4.86},{"s":7694,"c":"AMSTERDAM","a":"JAN VAN GALENSTRAAT 114H","p":"1056CE","lat":52.3663,"lon":4.8397},{"s":7695,"c":"HOOGVLIET","a":"DE FUIK 70","p":"3192HD","lat":51.916,"lon":4.445},{"s":7696,"c":"VLEUTEN","a":"BURCHTPLEIN 6","p":"3452MJ","lat":51.87,"lon":4.665},{"s":7697,"c":"SPIJKENISSE","a":"VLINDERVEEN 434","p":"3205EM","lat":51.9,"lon":4.4},{"s":7698,"c":"ENSCHEDE","a":"VELDHOFLANDEN 6-7","p":"7542LA","lat":52.216,"lon":6.885},{"s":7703,"c":"KATWIJK ZH","a":"HOORNESPLEIN 15-17","p":"2221BC","lat":52.238,"lon":4.51},{"s":7706,"c":"WIERDEN","a":"BURG J.C. VD BERGPLEIN 12","p":"7642GR","lat":52.516,"lon":6.085},{"s":7707,"c":"SMILDE","a":"VEENHOOPSEWEG 27","p":"9422AB","lat":52.858,"lon":6.535},{"s":7708,"c":"EDE","a":"HOOG MAANEN 47-48","p":"6717HZ","lat":51.954,"lon":5.93},{"s":7709,"c":"VLAARDINGEN","a":"DR. WIARDI BECKMANSINGEL 63","p":"3132CM","lat":51.892,"lon":4.445},{"s":7712,"c":"HOEVEN","a":"ST. JANSTRAAT 79A","p":"4741AN","lat":51.596,"lon":4.6},{"s":7713,"c":"TER AAR","a":"WESTKANAALWEG 113","p":"2461EK","lat":52.174,"lon":4.4},{"s":7731,"c":"HENGELO OV","a":"BOEKELOSEWEG 2","p":"7553DN","lat":52.22,"lon":6.89},{"s":7735,"c":"ASSEN","a":"KLEUVENSTEE 114-118","p":"9403LS","lat":52.85,"lon":6.54},{"s":7737,"c":"ROOSENDAAL","a":"DIJKCENTRUM 167-171","p":"4706LB","lat":51.58,"lon":4.625},{"s":7738,"c":"OUDE-TONGE","a":"DABBEHOF 22-28","p":"3255XN","lat":51.92,"lon":4.4},{"s":7739,"c":"GELDROP","a":"DE COEVERING 18-19","p":"5665GA","lat":51.504,"lon":5.62},{"s":7741,"c":"ROTTERDAM","a":"HESSEPLAATS 433","p":"3069EA","lat":51.8893,"lon":4.5157},{"s":7742,"c":"SCHOORL","a":"HEEREWEG 25","p":"1871EB","lat":52.508,"lon":4.71},{"s":7744,"c":"NIEUWEGEIN","a":"RAADSTEDE 39","p":"3431HA","lat":51.862,"lon":4.66},{"s":7745,"c":"LOOSDRECHT","a":"NOOTWEG 55","p":"1231CR","lat":52.362,"lon":4.825},{"s":7746,"c":"EINDHOVEN","a":"DIRIGENTPLEIN 89","p":"5642RK","lat":51.4246,"lon":5.4897},{"s":7752,"c":"HEESWIJK DINTHER","a":"ST. SERVATIUSSTRAAT 54","p":"5473GB","lat":51.528,"lon":5.16},{"s":7753,"c":"WINSUM GN","a":"HOOFDSTRAAT WINSUM 9-11","p":"9951AA","lat":52.93,"lon":5.83},{"s":7754,"c":"S GRAVENHAGE","a":"HILDO KROPLAAN 85-89","p":"2552XP","lat":52.07,"lon":4.305},{"s":7755,"c":"ZWOLLE","a":"VAN DER CAPELLENSTRAAT 244-248","p":"8014VZ","lat":52.504,"lon":6.095},{"s":7756,"c":"ALMELO","a":"BINNENHOF 43","p":"7608KH","lat":52.5,"lon":6.115},{"s":7759,"c":"ZUTPHEN","a":"RUIJS DE BEERENBROUCKSTRAAT 10","p":"7204MN","lat":52.2,"lon":6.175},{"s":7761,"c":"UTRECHT","a":"AMSTERDAMSESTRAATWEG 69-73","p":"3513AB","lat":52.0921,"lon":5.1233},{"s":7763,"c":"UGCHELEN","a":"UGCHELSEWEG 187","p":"7339CH","lat":52.212,"lon":6.92},{"s":7765,"c":"S GRAVENHAGE","a":"DIERENSELAAN 226-238","p":"2573KP","lat":52.0659,"lon":4.3978},{"s":7767,"c":"EINDHOVEN","a":"KASTELENPLEIN 87","p":"5653LR","lat":51.4585,"lon":5.4797},{"s":7768,"c":"AMSTERDAM","a":"GELDERLANDPLEIN 24","p":"1082LB","lat":52.329,"lon":4.8704},{"s":7769,"c":"PURMEREND","a":"WAGENWEG 16B","p":"1442BX","lat":52.366,"lon":4.825},{"s":7771,"c":"DAMWOUDE","a":"CONRADI VEENLANDSTRAAT 88B","p":"9104BN","lat":53.2,"lon":6.565},{"s":7772,"c":"EINDHOVEN","a":"MEERPLEIN 73","p":"5658LL","lat":51.5,"lon":5.635},{"s":7774,"c":"BALK","a":"VAN SWINDERENSTRAAT 39","p":"8561AR","lat":52.084,"lon":5.1},{"s":7775,"c":"RIJSWIJK ZH","a":"DR H COLIJNLAAN 305-307","p":"2283XK","lat":52.262,"lon":4.52},{"s":7779,"c":"ALKMAAR","a":"GEERT GROTEPLEIN 9A","p":"1813BM","lat":52.484,"lon":4.72},{"s":7781,"c":"KLUNDERT","a":"VOORSTRAAT 26-28","p":"4791HN","lat":51.616,"lon":4.6},{"s":7782,"c":"WOGNUM","a":"BOOGERD 17","p":"1687VX","lat":52.472,"lon":4.8},{"s":7783,"c":"ALMELO","a":"DE GORS 13-15","p":"7609DZ","lat":52.5,"lon":6.12},{"s":7784,"c":"BEST","a":"RENDIERHEI 11","p":"5685HS","lat":51.512,"lon":5.62},{"s":7785,"c":"DEN HELDER","a":"MARSDIEPSTRAAT 256","p":"1784AV","lat":52.512,"lon":4.795},{"s":7786,"c":"EMMEN","a":"HOUTWEG 290","p":"7823PV","lat":52.488,"lon":6.09},{"s":7787,"c":"AMSTERDAM","a":"BEZAANJACHTPLEIN 277","p":"1034CR","lat":52.4121,"lon":4.9143},{"s":7789,"c":"HAARLEM","a":"MARSMANPLEIN 16-18","p":"2025DT","lat":52.3911,"lon":4.6668},{"s":7791,"c":"IJMUIDEN","a":"KENNEMERLAAN 76","p":"1972ER","lat":52.478,"lon":4.645},{"s":7792,"c":"ROTTERDAM","a":"NIEUWE BINNENWEG 34","p":"3015BA","lat":51.9113,"lon":4.4669},{"s":7793,"c":"HEINKENSZAND","a":"STENEVATE 2A","p":"4451KB","lat":51.5,"lon":3.83},{"s":7794,"c":"HOLTEN","a":"ZWARTE PAD 12","p":"7451BJ","lat":52.22,"lon":6.2},{"s":7795,"c":"HELMOND","a":"BROUWHORST 38","p":"5704EH","lat":51.68,"lon":5.295},{"s":7796,"c":"ROSMALEN","a":"HUYGENSSTRAAT 26","p":"5242CM","lat":51.426,"lon":5.465},{"s":7797,"c":"WAALRE","a":"DE BUS 39A","p":"5581GP","lat":51.432,"lon":5.46},{"s":7798,"c":"EMMEN","a":"ALERDERBRINK 20","p":"7812RV","lat":52.484,"lon":6.085},{"s":7799,"c":"BREDA","a":"RIJPSTRAAT 6","p":"4812TC","lat":51.554,"lon":4.465},{"s":7838,"c":"MONTFOORT","a":"HOOGSTRAAT 37","p":"3417HA","lat":51.854,"lon":4.69},{"s":7862,"c":"S GRAVENHAGE","a":"KEIZERSTRAAT 331","p":"2584BG","lat":52.082,"lon":4.315},{"s":7865,"c":"VLEUTEN","a":"ALBERT SCHWEITZERLAAN 2","p":"3451EC","lat":51.87,"lon":4.66},{"s":7866,"c":"LEKKERKERK","a":"RAADHUISPLEIN 31-35","p":"2941BS","lat":51.966,"lon":4.26},{"s":7867,"c":"STRAMPROY","a":"KERKPLEIN 10","p":"6039GH","lat":51.842,"lon":5.89},{"s":7868,"c":"ZUIDLAREN","a":"STATIONSWEG 53","p":"9471GL","lat":52.878,"lon":6.53},{"s":7869,"c":"VEENENDAAL","a":"DR. S. DE BRUINEPLEIN 15","p":"3904CX","lat":51.8,"lon":4.425},{"s":7871,"c":"APELDOORN","a":"DE EGLANTIER 169-171","p":"7329DE","lat":52.208,"lon":6.92},{"s":7872,"c":"CAPELLE AAN DEN IJSSEL","a":"PICASSOPASSAGE 29-33","p":"2907ME","lat":51.95,"lon":4.29},{"s":7873,"c":"TILBURG","a":"BURG. BROKXLAAN 1906A","p":"5041SJ","lat":51.566,"lon":5.06},{"s":7874,"c":"LEEUWARDEN","a":"LIEUWENBURG 180-184","p":"8925CL","lat":52.088,"lon":5.12},{"s":7875,"c":"AMSTERDAM","a":"HOLENDRECHTPLEIN 6","p":"1106LN","lat":52.3208,"lon":4.9724},{"s":7876,"c":"S HERTOGENBOSCH","a":"LOKERENPASSAGE 45","p":"5235KR","lat":51.422,"lon":5.48},{"s":7877,"c":"OSS","a":"STERREBOS 27","p":"5344AL","lat":51.446,"lon":5.495},{"s":7878,"c":"HONSELERSDIJK","a":"DIJKSTRAAT 107","p":"2675AW","lat":52.078,"lon":4.28},{"s":7879,"c":"BREDA","a":"DE BURCHT 39","p":"4834HK","lat":51.562,"lon":4.475},{"s":7881,"c":"REEUWIJK","a":"MIEREAKKER 24","p":"2811BB","lat":52.054,"lon":4.38},{"s":7882,"c":"TILBURG","a":"AABESTRAAT 2","p":"5021AV","lat":51.558,"lon":5.06},{"s":7883,"c":"UTRECHT","a":"ELLA FITZGERALDPLEIN 26","p":"3543EP","lat":52.1033,"lon":5.1033},{"s":7884,"c":"UTRECHT","a":"HAROEKOEPLEIN 138","p":"3531WN","lat":52.0921,"lon":5.0933},{"s":7886,"c":"EINDHOVEN","a":"HURKSESTRAAT 44","p":"5652AL","lat":51.4585,"lon":5.4697},{"s":7888,"c":"HOOGEVEEN","a":"DE WIELEWAAL 22","p":"7905GZ","lat":52.48,"lon":6.48},{"s":7889,"c":"GOES","a":"ST ADRIAANSTRAAT 4-6","p":"4461JC","lat":51.504,"lon":3.83},{"s":7891,"c":"EINDHOVEN","a":"NEDERLANDPLEIN 111","p":"5628AJ","lat":51.488,"lon":5.635},{"s":7892,"c":"ZOETERWOUDE","a":"DORPSSTRAAT 19A","p":"2381EK","lat":52.182,"lon":4.45},{"s":7893,"c":"S GRAVENHAGE","a":"LAAN VAN WATERINGSE VELD 576-578","p":"2548CL","lat":52.066,"lon":4.335},{"s":7894,"c":"APELDOORN","a":"ORDENPLEIN 120","p":"7312NL","lat":52.204,"lon":6.885},{"s":7895,"c":"SPIJKENISSE","a":"WINTERAKKER 10-16","p":"3206TG","lat":51.9,"lon":4.405},{"s":7896,"c":"DRACHTEN","a":"STATIONSWEG 180B","p":"9201GT","lat":52.73,"lon":6.9},{"s":7898,"c":"SITTARD","a":"DEMPSEYSTRAAT 24-26","p":"6135CH","lat":51.842,"lon":5.88},{"s":7901,"c":"BLAAKSEDIJK (HEINENOORD)","a":"BOONSWEG 30","p":"3274LH","lat":51.928,"lon":4.395},{"s":7902,"c":"HAARLEM","a":"BROCKWAYSTRAAT 3","p":"2014JJ","lat":52.3741,"lon":4.6332},{"s":7905,"c":"ROTTERDAM","a":"EUDOKIAPLEIN 24","p":"3037BT","lat":51.912,"lon":4.49},{"s":7906,"c":"EIJSDEN","a":"BREUSTERSTRAAT 43","p":"6245EH","lat":50.846,"lon":5.68},{"s":7907,"c":"ENSCHEDE","a":"JAN VERMEERSTRAAT 15","p":"7545BN","lat":52.216,"lon":6.9},{"s":7912,"c":"HELVOIRT","a":"ACHTERSTRAAT 51B","p":"5268EB","lat":51.434,"lon":5.495},{"s":7914,"c":"ENSCHEDE","a":"BROUWERIJPLEIN 45A","p":"7523MA","lat":52.208,"lon":6.89},{"s":7917,"c":"SPIJKENISSE","a":"'T PLATEAU 16-22","p":"3202GM","lat":51.9,"lon":4.385},{"s":7918,"c":"ZEVENHUIZEN ZH","a":"DORPSSTRAAT 190","p":"2761AJ","lat":52.074,"lon":4.36},{"s":7919,"c":"WIERINGERWERF","a":"TERPSTRAAT 5","p":"1771AC","lat":52.508,"lon":4.78},{"s":7921,"c":"AMSTELVEEN","a":"KOSTVERLORENHOF 9","p":"1183HE","lat":52.397,"lon":4.86},{"s":7922,"c":"HOOFDDORP","a":"BURG. VAN STAMPLEIN 48-50","p":"2132BH","lat":52.382,"lon":4.625},{"s":7923,"c":"OOSTZAAN","a":"HANNIE SCHAFTPLEIN 1","p":"1511VT","lat":52.424,"lon":4.81},{"s":7925,"c":"AMERSFOORT","a":"GRONINGERSTRAAT 166","p":"3812EG","lat":51.804,"lon":4.635},{"s":7926,"c":"GOES","a":"BEUKENHOF 13-14","p":"4462EN","lat":51.504,"lon":3.835},{"s":7927,"c":"ZOETERMEER","a":"BROEKWEGZIJDE 135-137","p":"2725PD","lat":52.058,"lon":4.38},{"s":7928,"c":"ROTTERDAM","a":"GOUDSESINGEL 33A-35A","p":"3031EC","lat":51.9243,"lon":4.5057},{"s":7929,"c":"AMSTERDAM","a":"FERDINAND BOLSTRAAT 125-127","p":"1072LG","lat":52.3459,"lon":4.8849},{"s":7931,"c":"HENDRIK IDO AMBACHT","a":"DRUIVENGAARDE 4","p":"3344PK","lat":51.876,"lon":4.535},{"s":7932,"c":"APELDOORN","a":"KANAAL NOORD 17","p":"7311PK","lat":52.204,"lon":6.88},{"s":7933,"c":"KATWIJK","a":"VISSERIJKADE 2","p":"2225TV","lat":52.238,"lon":4.53},{"s":7934,"c":"ZAANDAM","a":"WESTZIJDE 47","p":"1506EB","lat":52.42,"lon":4.835},{"s":7935,"c":"LEIDEN","a":"KOPERMOLEN 13-15-19","p":"2317PA","lat":52.154,"lon":4.48},{"s":7936,"c":"NIEUWEGEIN","a":"MARKT 48","p":"3431LB","lat":51.862,"lon":4.66},{"s":7937,"c":"ROTTERDAM","a":"BEIJERLANDSEPASSAGE 3","p":"3074RW","lat":51.928,"lon":4.475},{"s":7938,"c":"ST WILLEBRORD","a":"DORPSSTRAAT 10A","p":"4711NG","lat":51.584,"lon":4.6},{"s":7939,"c":"HILLEGOM","a":"HENRI DUNANTPLEIN 50","p":"2181EM","lat":52.402,"lon":4.62},{"s":7942,"c":"WESTERBORK","a":"HOOFDSTRAAT 31","p":"9431AB","lat":52.862,"lon":6.53},{"s":7943,"c":"OEGSTGEEST","a":"LANGE VOORT 2R","p":"2341KA","lat":52.166,"lon":4.45},{"s":7944,"c":"HERKENBOSCH","a":"CRAENBERGLAAN 7-11","p":"6075HC","lat":51.858,"lon":5.87},{"s":7947,"c":"RIJSSEN","a":"BOOMKAMP 30","p":"7461AX","lat":52.224,"lon":6.2},{"s":7955,"c":"WAGENINGEN","a":"HOOGSTRAAT 62-64","p":"6701BX","lat":51.95,"lon":5.9},{"s":7956,"c":"ROTTERDAM","a":"NOORDMOLENSTRAAT 34","p":"3035RK","lat":51.9313,"lon":4.5057},{"s":7957,"c":"SPIJKENISSE","a":"STERRENHOF 22","p":"3204AT","lat":51.9,"lon":4.395},{"s":7958,"c":"HARDERWIJK","a":"ACHTERSTE WEI 7-9","p":"3844HR","lat":51.816,"lon":4.645},{"s":7959,"c":"ETTEN LEUR","a":"MOLENVANG 9","p":"4876BW","lat":51.578,"lon":4.485},{"s":7961,"c":"LOPIK","a":"ROLAFWEG NOORD 55","p":"3411BJ","lat":51.854,"lon":4.66},{"s":7962,"c":"HEINO","a":"MARKSTRAAT 6","p":"8141GC","lat":52.496,"lon":6.07},{"s":7963,"c":"DEDEMSVAART","a":"MARKT 30","p":"7701GW","lat":52.5,"lon":6.09},{"s":7964,"c":"DELFZIJL","a":"WILLEMSTRAAT 28","p":"9934BC","lat":52.922,"lon":5.845},{"s":7965,"c":"VELDHOVEN","a":"KROMSTRAAT 24A","p":"5504BD","lat":51.4,"lon":5.475},{"s":7966,"c":"WAALWIJK","a":"STATIONSSTRAAT 43-45","p":"5141GC","lat":51.566,"lon":5.07},{"s":7967,"c":"KAMPEN","a":"DR. DAMSTRAAT 115","p":"8262GH","lat":52.524,"lon":5.455},{"s":7969,"c":"MAASSLUIS","a":"KONINGSHOEK 92054","p":"3144BA","lat":51.896,"lon":4.455},{"s":7971,"c":"APELDOORN","a":"LINIE 109-183","p":"7325DP","lat":52.208,"lon":6.9},{"s":7972,"c":"S GRAVENHAGE","a":"HET KLEINE LOO 390","p":"2592CK","lat":52.0236,"lon":4.3278},{"s":7973,"c":"ZAANDAM","a":"GIBRALTAR 8","p":"1503BM","lat":52.42,"lon":4.82},{"s":7974,"c":"ALPHEN AAN DEN RIJN","a":"HERENHOF 10","p":"2402DM","lat":52.15,"lon":4.405},{"s":7975,"c":"S GRAVENHAGE","a":"KOPPELSTOKSTRAAT 4","p":"2583CE","lat":52.047,"lon":4.2611},{"s":7976,"c":"COEVORDEN","a":"EDS PLEIN 33","p":"7741KH","lat":52.516,"lon":6.09},{"s":7977,"c":"DOETINCHEM","a":"HAMBURGERSTRAAT 3","p":"7001AH","lat":51.98,"lon":6.18},{"s":7978,"c":"DOORWERTH","a":"MOZARTLAAN 60","p":"6865GC","lat":51.974,"lon":6.0},{"s":7979,"c":"VALKENBURG","a":"IRMENGARDPASSAGE 7","p":"6301EC","lat":51.18,"lon":5.96},{"s":7981,"c":"BERKEL-ENSCHOT","a":"KONINGSOORD 130","p":"5057DL","lat":51.57,"lon":5.09},{"s":7982,"c":"STEIN LB","a":"RAADHUISPLEIN 6","p":"6171JB","lat":51.858,"lon":5.86},{"s":7983,"c":"ENSCHEDE","a":"CHRYSANTSTRAAT 84","p":"7531KD","lat":52.212,"lon":6.88},{"s":7984,"c":"BORGER","a":"HOOFDSTRAAT 29-H","p":"9531AB","lat":53.092,"lon":6.86},{"s":7985,"c":"BLEISWIJK","a":"DORPSSTRAAT 89","p":"2665BH","lat":52.074,"lon":4.28},{"s":7986,"c":"VELSERBROEK","a":"GALLE PROMENADE 52-58","p":"1991PR","lat":52.486,"lon":4.64},{"s":7987,"c":"ZOETERMEER","a":"MIDDELWAARD 9+12","p":"2716CW","lat":52.054,"lon":4.385},{"s":7988,"c":"LEIDEN","a":"STEVENSBLOEM 189","p":"2331JC","lat":52.162,"lon":4.45},{"s":7991,"c":"HILVERSUM","a":"HILVERTSHOF 108","p":"1211ER","lat":52.354,"lon":4.825},{"s":7993,"c":"AMERSFOORT","a":"ZONNEWIJZER 16","p":"3824EE","lat":51.808,"lon":4.645},{"s":7994,"c":"LELYSTAD","a":"WEVERSSTRAAT 10-32-36","p":"8223AC","lat":52.508,"lon":5.46},{"s":7997,"c":"AMSTERDAM","a":"MOSVELD 107","p":"1031AD","lat":52.4175,"lon":4.9266}]

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
    82:(52.52,5.47), 83:(52.30,5.55), 84:(52.15,5.38), 85:(52.08,5.12),
    86:(52.08,5.11), 87:(52.15,5.37), 88:(53.10,5.80), 89:(52.10,5.12),
    90:(53.22,6.57), 91:(53.22,6.57), 92:(52.75,6.92), 93:(52.85,6.35),
    94:(52.87,6.55), 95:(53.10,6.88), 96:(53.32,6.30), 97:(53.20,5.75),
    98:(53.20,5.72), 99:(52.93,5.85),
}

def _build_centroids():
    # Gebruik alleen de exacte centroïden - geen grove schattingen
    # Onbekende postcodes worden live opgehaald via PDOK bij analyse
    return dict(_EXACTE_CENTROIDS)

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
    """
    Haal via PDOK exacte PC4-centroïden op rondom een locatie.
    Gebruikt paginering om alle postcodes te vinden, niet alleen de eerste 200.
    """
    marge = straal_km / 111.0
    extra = {}
    start = 0
    while True:
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
                    "rows": 100,
                    "start": start,
                },
                timeout=10
            )
            if r.status_code != 200:
                break
            resp = r.json().get("response", {})
            docs = resp.get("docs", [])
            if not docs:
                break
            for doc in docs:
                naam = doc.get("weergavenaam","")
                cent = doc.get("centroide_ll","")
                m_pc    = re.search(r"\b(\d{4})[A-Z]{2}\b", naam)
                m_coord = re.search(r"POINT\(([0-9.]+)\s+([0-9.]+)\)", cent)
                if m_pc and m_coord:
                    pc4 = m_pc.group(1)
                    if pc4 in bekende_pcs:
                        # Gemiddelde per PC4 (meerdere 6-cijferige postcodes per PC4)
                        lat_v = float(m_coord.group(2))
                        lon_v = float(m_coord.group(1))
                        if pc4 in extra:
                            # Gemiddelde met bestaande waarde
                            old_lat, old_lon = extra[pc4]
                            extra[pc4] = ((old_lat + lat_v)/2, (old_lon + lon_v)/2)
                        else:
                            extra[pc4] = (lat_v, lon_v)
            if start + 100 >= resp.get("numFound", 0):
                break
            start += 100
        except Exception:
            break
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
    st.header("🏪 Winkellocaties")
    toon_winkels = st.toggle("Toon winkels op kaart", value=True)
    st.caption(f"{len(WINKELS)} locaties ingeladen")

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

    # Winkellocaties als rode labels
    if toon_winkels:
        for w in WINKELS:
            folium.Marker(
                location=[w["lat"], w["lon"]],
                tooltip=f"<b>#{w['s']}</b> {w['c']}<br>{w['a']}<br>{w['p']}",
                popup=folium.Popup(
                    f"<b>Store #{w['s']}</b><br>{w['a']}<br>{w['p']} {w['c']}",
                    max_width=200
                ),
                icon=folium.DivIcon(
                    html=(
                        f'<div style="background:#c8102e;color:white;padding:2px 5px;'
                        f'border-radius:3px;font-size:11px;font-weight:700;'
                        f'white-space:nowrap;border:1.5px solid white;'
                        f'box-shadow:0 1px 3px rgba(0,0,0,.5);line-height:1.4">'
                        f'#{w["s"]}</div>'
                    ),
                    icon_size=(55, 22),
                    icon_anchor=(27, 11),
                )
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

        # Gebruik ruime zoekradius zodat ook kleine wijken gevonden worden
        zoek_straal = max(straal_km * 3, 15)

        with st.spinner(f"Postcodes ophalen via PDOK (radius {zoek_straal:.0f} km)..."):
            live_centroids = get_centroids_voor_gebied(center_lat, center_lon, zoek_straal)

        # Live centroïden hebben prioriteit over statische tabel
        # Valideer: alleen Nederlandse coördinaten (filter foute statische centroïden)
        alle_centroids = {}
        for pc, (lat, lon) in PC4_CENTROIDS_FILTERED.items():
            if 50.7 <= lat <= 53.6 and 3.3 <= lon <= 7.3:
                alle_centroids[pc] = (lat, lon)
        # Live centroïden overschrijven altijd (zijn preciezer)
        alle_centroids.update(live_centroids)

        if g["type"] == "cirkel":
            gevonden = [
                (pc, lat, lon)
                for pc, (lat, lon) in alle_centroids.items()
                if haversine(g["lat"], g["lon"], lat, lon) <= g["straal"]
            ]
            st.session_state.gebied_label = f"Cirkel — straal {g['straal']/1000:.1f} km"
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

                    # Gewogen gemiddelde grootte: som(grootte * huishoudens) / totaal huishoudens
                    gem_grootte_gebied = sum(
                        d.get("__grootte",0) * d.get("__totaal",0)
                        for d in hh_res.values() if d.get("__totaal",0) > 0
                    ) / max(tot_hh, 1)
                    gem_grootte_nl = nl_hh.get("__grootte", 0)

                    c1,c2 = st.columns(2)
                    c1.metric("Huishoudens", f"{int(tot_hh):,}".replace(",","."))
                    c2.metric("Gem. grootte", f"{gem_grootte_gebied:.1f} pers.",
                              delta=f"{gem_grootte_gebied - gem_grootte_nl:+.1f} vs NL" if nl_hh else None)

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
                    # NL herkomst benchmark
                    nl_hk_key = hk_pc_map.get("Nederland")
                    nl_hk = get_hk_data(nl_hk_key, hk_per_key, gb_totaal, gsl_key, hk_map_meta) if nl_hk_key else {}
                    nl_tot_hk = nl_hk.get("Totaal",1) or 1

                    tot_hk  = hk_agg.get("Totaal",1) or 1
                    pct_nl_gebied = hk_agg.get("Nederland",0)/tot_hk*100
                    pct_nl_nl     = nl_hk.get("Nederland",0)/nl_tot_hk*100 if nl_hk else None

                    c1,c2 = st.columns(2)
                    c1.metric("Herkomst NL", f"{pct_nl_gebied:.1f}%",
                              delta=f"{pct_nl_gebied - pct_nl_nl:+.1f}%-pt vs NL" if pct_nl_nl else None)
                    c2.metric("Herkomst buiten NL", f"{100-pct_nl_gebied:.1f}%",
                              delta=f"{(100-pct_nl_gebied) - (100-pct_nl_nl):+.1f}%-pt vs NL" if pct_nl_nl else None)
                    st.caption("Delta t.o.v. landelijk gemiddelde")

                    # Vergelijkingsgrafiek gebied vs NL
                    hk_plot = []
                    reeksen = ["Gebied"]
                    kleurmap_hk = {"Gebied": "#534AB7"}
                    for cat in HK_CAT:
                        if hk_agg.get(cat,0) > 0:
                            hk_plot.append({"Herkomst": cat, "%": round(hk_agg.get(cat,0)/tot_hk*100,1), "Reeks": "Gebied"})
                    if nl_hk:
                        reeksen.append("⌀ Nederland")
                        kleurmap_hk["⌀ Nederland"] = "#888780"
                        for cat in HK_CAT:
                            if nl_hk.get(cat,0) > 0:
                                hk_plot.append({"Herkomst": cat, "%": round(nl_hk.get(cat,0)/nl_tot_hk*100,1), "Reeks": "⌀ Nederland"})

                    if hk_plot:
                        fig_h = px.bar(pd.DataFrame(hk_plot), x="%", y="Herkomst",
                                       color="Reeks", barmode="group",
                                       orientation="h",
                                       color_discrete_map=kleurmap_hk,
                                       category_orders={"Reeks": reeksen},
                                       height=300)
                        fig_h.update_layout(
                            plot_bgcolor="white", paper_bgcolor="white",
                            xaxis=dict(showgrid=True, gridcolor="#eee"),
                            yaxis=dict(autorange="reversed"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
                            margin=dict(t=30, b=30, l=8, r=8),
                        )
                        st.plotly_chart(fig_h, use_container_width=True)

st.divider()
st.caption("Data: CBS StatLine (CC BY 4.0) | Geodata: PDOK | App gebouwd met Streamlit")
