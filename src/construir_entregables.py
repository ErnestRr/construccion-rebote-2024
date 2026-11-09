"""Genera resultados/05_promedio_y_mercado/analisis.html a partir de plantilla.html.
Las cifras del texto salen de los CSV y de cifras_clave.json escritos por calcular.py.
Uso (desde la raíz):  .venv\\Scripts\\python.exe analisis\\05_promedio_y_mercado\\construir_entregables.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from plotly.offline import get_plotlyjs

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import calcular  # noqa: E402

SAL = calcular.SAL
K = json.loads((SAL / "cifras_clave.json").read_text(encoding="utf-8"))
M = pd.read_csv(SAL / "resultados.csv", dtype={"codigo_entidad": str})
D = pd.read_csv(SAL / "descomposicion.csv")
SS = pd.read_csv(SAL / "series_segmentos.csv", dtype={"codigo_entidad": str})
SENS = pd.read_csv(SAL / "sensibilidad.csv")
EDOMEX = "Estado de México (Edomex)"
M["entidad"] = M.entidad.replace({"México": EDOMEX})
SS["entidad"] = SS.entidad.replace({"México": EDOMEX})
tot_est = M[M.segmento == "Total del estado"].set_index("entidad")
priv = M[(M.segmento == "Sector privado") & M.relevante]
priv_cae = priv[priv.dpct < 0]


def pc(v, d=1):
    return f'<span class="{"pos" if v >= 0 else "neg"}"><small>{"▲" if v >= 0 else "▼"} </small>{"+" if v >= 0 else "−"}{abs(v):.{d}f}%</span>'


def pp(v, d=1):
    return f'<span class="{"pos" if v >= 0 else "neg"}"><small>{"▲" if v >= 0 else "▼"} </small>{"+" if v >= 0 else "−"}{abs(v):.{d}f}</span>'


tit = K["titulares"]
n_mes, n_ytd, n_12 = tit.keys()
CORTOS = ["Mes (ago-26 vs. ago-25)", "Año corrido (ene–ago)", "12 meses (sep-25 a ago-26)"]
TIT = [{"corto": c, "d": v["delta_pct"], "v": v["valor_prev_en_caida_pct"], "n": v["estados_que_caen"]} for c, v in zip(CORTOS, tit.values())]
nac_tot = D.acum12_prev_real_mmdp_2018.sum()
d = D.set_index("segmento")
sens = lambda esc, i: SENS[(SENS.escenario == esc)].iloc[i]
tok = {
    "HDR_NUM": pc(tit[n_12]["delta_pct"]), "HDR_TXT": f'{tit[n_ytd]["estados_que_caen"]} de 32 estados ({tit[n_ytd]["valor_prev_en_caida_pct"]:.1f}% del valor) caen',
    "EDOMEX_PTS": f'+{tot_est.loc[EDOMEX, "contrib_pp"]:.2f}', "HGO_PTS": f'+{tot_est.loc["Hidalgo", "contrib_pp"]:.2f}',
    "PRIV_N": str(len(priv_cae)), "PRIV_V": f'{priv_cae.acum12_prev_real_mmdp_2018.sum() / priv.acum12_prev_real_mmdp_2018.sum() * 100:.0f}',
    "T_MES": pc(tit[n_mes]["delta_pct"]), "T_YTD": pc(tit[n_ytd]["delta_pct"]), "T_12M": pc(tit[n_12]["delta_pct"]),
    "N_MES": f'{tit[n_mes]["estados_que_caen"]} de 32', "N_YTD": f'{tit[n_ytd]["estados_que_caen"]} de 32', "N_12M": f'{tit[n_12]["estados_que_caen"]} de 32',
    "V_MES": f'{tit[n_mes]["valor_prev_en_caida_pct"]:.1f}', "V_YTD": f'{tit[n_ytd]["valor_prev_en_caida_pct"]:.1f}', "V_12M": f'{tit[n_12]["valor_prev_en_caida_pct"]:.1f}',
    "M_MES": pc(tit[n_mes]["mediana_ponderada_estados_pct"]), "M_YTD": pc(tit[n_ytd]["mediana_ponderada_estados_pct"]), "M_12M": pc(tit[n_12]["mediana_ponderada_estados_pct"]),
    "SIN_PETR": pc(float(sens("Sin petróleo y petroquímica", 2).delta_pct)), "SIN_YTD": pc(float(sens("Sin México ni Hidalgo", 1).delta_pct)), "SIN_12M": pc(float(sens("Sin México ni Hidalgo", 2).delta_pct)),
    "CELDAS_REL": str(K["celdas_relevantes"]), "CELDAS_CAEN": str(K["celdas_que_caen"]), "V_CELDAS": f'{K["valor_prev_en_celdas_que_caen_pct"]:.1f}', "MED_CELDAS": pc(K["mediana_ponderada_celdas_pct"]),
    "U_MIN": f'{min(v["valor_prev_en_celdas_que_caen_pct"] for v in K["umbrales"].values()):.0f}', "U_MAX": f'{max(v["valor_prev_en_celdas_que_caen_pct"] for v in K["umbrales"].values()):.0f}',
    "TRANSP_PCT": pc(d.loc["Transporte y urbanización", "dpct"]), "ELEC_PCT": pc(d.loc["Electricidad y telecomunicaciones", "dpct"]), "EDIF_PCT": pc(d.loc["Edificación", "dpct"]),
    "PETR_PCT": pc(d.loc["Petróleo y petroquímica", "dpct"]), "PRIV_PCT": pc(d.loc["Sector privado", "dpct"]), "PUB_PCT": pc(d.loc["Sector público", "dpct"]),
}

# datos para la página
nombres_tipos = [v[0] for v in calcular.SEGMENTOS.values() if v[1] == "tipo de obra"]
mt = M[M.tipo_segmento == "tipo de obra"]
orden_estados = M[M.segmento == "Total del estado"].sort_values("acum12_prev_real_mmdp_2018", ascending=False).entidad.tolist()
z = mt.pivot(index="entidad", columns="segmento", values="dpct").reindex(index=orden_estados, columns=nombres_tipos)
rel = mt.pivot(index="entidad", columns="segmento", values="relevante").reindex(index=orden_estados, columns=nombres_tipos)
base = mt.pivot(index="entidad", columns="segmento", values="acum12_prev_real_mmdp_2018").reindex(index=orden_estados, columns=nombres_tipos)
z = z.where(rel)
lst = lambda df: [[None if pd.isna(v) else round(float(v), 2) for v in fila] for fila in df.values]
e = calcular.cargar()
nac_series = {}
for col, (seg, _) in calcular.SEGMENTOS.items():
    s = e.groupby("fecha")[col].sum()
    a12 = s.rolling(12, min_periods=12).sum()
    y = ((a12 / a12.shift(12) - 1) * 100)[lambda x: x.index >= "2022-01-01"].dropna()
    nac_series[seg] = {"x": y.index.strftime("%Y-%m-%d").tolist(), "y": y.round(2).tolist()}
series = {}
for (ent, seg), g in SS.groupby(["entidad", "segmento"]):
    series.setdefault(ent, {})[seg] = {"x": g.fecha.tolist(), "y": g.dpct.round(2).tolist()}
nac_total_prev = float(M[M.tipo_segmento == 'total'].acum12_prev_real_mmdp_2018.sum())
cortos = {"Edificación": "Edificación", "Agua, riego y saneamiento": "Agua y saneam.", "Electricidad y telecomunicaciones": "Electricidad y telecom.",
          "Transporte y urbanización": "Transporte y urbaniz.", "Petróleo y petroquímica": "Petróleo y petroquím.", "Otras construcciones": "Otras constr."}
mr = mt[mt.relevante].sort_values("contrib_pp", ascending=False)
sel_top = pd.concat([mr.head(8), mr.tail(8)]).sort_values("contrib_pp", ascending=False)
top_mercados = [{"nombre": f"{r.entidad} · {cortos[r.segmento]}", "aporte": round(float(r.contrib_pp), 3), "dpct": round(float(r.dpct), 1)} for r in sel_top.itertuples()]
DATA = {
    "foco": ["Total nacional (32 estados)", "Total del estado"], "top_mercados": top_mercados, "segmentos": [v[0] for v in calcular.SEGMENTOS.values()],
    "titulares": TIT, "nacional": nac_series, "series": series,
    "desc": [{"segmento": r.segmento, "grupo": r.tipo_segmento, "prev": round(r.acum12_prev_real_mmdp_2018, 3), "act": round(r.acum12_real_mmdp_2018, 3), "dpct": round(r.dpct, 3), "aporte": round(r.contrib_pp, 3)} for r in D.itertuples()],
    "nac_mercado": {**{r.segmento: {"part": round(r.acum12_prev_real_mmdp_2018 / nac_total_prev * 100, 3), "act": round(r.acum12_real_mmdp_2018, 4), "prev": round(r.acum12_prev_real_mmdp_2018, 4), "dpct": round(r.dpct, 3), "aporte": round(r.contrib_pp, 4), "relevante": True} for r in D.itertuples()},
                     "Total del estado": {"part": 100.0, "act": round(float(M[M.tipo_segmento == "total"].acum12_real_mmdp_2018.sum()), 4), "prev": round(float(nac_total_prev), 4), "dpct": round(tit[n_12]["delta_pct"], 3), "aporte": round(tit[n_12]["delta_pct"], 4), "relevante": True}},
    "desc_nac": {**{r.segmento: round(float(r.dpct), 3) for r in D.itertuples()}, "Total del estado": round(tit[n_12]["delta_pct"], 3)},
    "heat": {"cortos": ["Edificación", "Agua, riego<br>y saneam.", "Electricidad<br>y telecom.", "Transporte<br>y urbaniz.", "Petróleo y<br>petroquím.", "Otras<br>constr."], "tipos": nombres_tipos, "estados": orden_estados, "z": lst(z), "base": lst(base)},
    "mercados": [{"entidad": r.entidad, "segmento": r.segmento, "part": round(r.part_prev_pct, 4), "act": round(r.acum12_real_mmdp_2018, 4), "prev": round(r.acum12_prev_real_mmdp_2018, 4),
                  "dpct": None if pd.isna(r.dpct) else round(r.dpct, 3), "aporte": round(r.contrib_pp, 4), "relevante": bool(r.relevante)} for r in M.itertuples()],
}
import base64
def _ff(fam, peso, estilo, arch):
    b = base64.b64encode((AQUI / "fuentes_post" / arch).read_bytes()).decode()
    return f"@font-face{{font-family:'{fam}';font-weight:{peso};font-style:{estilo};src:url(data:font/woff2;base64,{b}) format('woff2')}}"
FONTS = "".join([_ff("Instrument Serif", 400, "normal", "instrument-serif-latin-400-normal.woff2"), _ff("Instrument Serif", 400, "italic", "instrument-serif-latin-400-italic.woff2"),
                 _ff("Inter", 400, "normal", "inter-latin-400-normal.woff2"), _ff("Inter", 500, "normal", "inter-latin-500-normal.woff2")])
html = (AQUI / "plantilla.html").read_text(encoding="utf-8").replace("[[FONTS]]", FONTS)
for k, v in tok.items():
    html = html.replace(f"[[{k}]]", v)
assert sorted(set(re.findall(r"\[\[([A-Z_0-9]+)\]\]", html))) == ["DATA", "PLOTLY"], set(re.findall(r"\[\[([A-Z_0-9]+)\]\]", html))
html = html.replace("[[DATA]]", json.dumps(DATA, ensure_ascii=False)).replace("[[PLOTLY]]", get_plotlyjs())
(SAL / "analisis.html").write_text(html, encoding="utf-8")
print("analisis.html", round(len(html) / 1e6, 2), "MB")
