"""Reporte ejecutivo del análisis 05: la cifra nacional de la construcción es un rebote sobre una base baja.
Escribe index.html (autocontenido, sin Plotly). Las cifras salen de rebote.py.
Uso:  python src/rebote.py && python src/construir_ejecutivo.py
"""
import base64
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
SAL = AQUI.parent / "resultados"
R = json.loads((SAL / "cifras_rebote.json").read_text(encoding="utf-8"))
SEG = pd.read_csv(SAL / "rebote_segmentos.csv").set_index("segmento")
EST = pd.read_csv(SAL / "rebote_estado_segmento.csv", dtype={"codigo_entidad": str})
SER = pd.read_csv(SAL / "serie_indice_mensual.csv", index_col=0, parse_dates=True)
EST["entidad"] = EST.entidad.replace({"México": "Estado de México", "Veracruz de Ignacio de la Llave": "Veracruz", "Coahuila de Zaragoza": "Coahuila",
                                      "Michoacán de Ocampo": "Michoacán"})


def b64(n):
    return base64.b64encode((AQUI / "fuentes_post" / n).read_bytes()).decode()


def p1(v):
    s = f"{abs(v):.1f}"
    return s[:-2] if s.endswith(".0") else s


def sg(v):
    return f'<span class="d {"pos" if v > 0 else "neg"}"><span class="tri">{"▲" if v > 0 else "▼"}</span>{"+" if v > 0 else "−"}{p1(v)}%</span>'


# --- Gráfica (misma que la infografía) -------------------------------------------------------------------------------------------
W, H, L, T, B, RM = 1000, 250, 34, 10, 24, 160
lo, hi = float(SER.min().min()) - 6, float(SER.max().max()) + 6
n = len(SER)
X = lambda i: L + i * (W - L - RM) / (n - 1)
Yv = lambda v: T + (hi - v) / (hi - lo) * (H - T - B)
g = ""
for v in range(int(lo // 20 * 20) + 20, int(hi), 20):
    g += f'<line x1="{L}" x2="{W - RM}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}" stroke="#E3DBC9"/><text x="{L - 6}" y="{Yv(v) + 4:.1f}" text-anchor="end" font-size="12" fill="#5B6573">{v}</text>'
g += f'<line x1="{L}" x2="{W - RM}" y1="{Yv(100):.1f}" y2="{Yv(100):.1f}" stroke="#12213C" stroke-width="1.6" stroke-dasharray="6 4"/>'
for i, d in enumerate(SER.index):
    if d.month == 1:
        g += f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{T}" y2="{H - B}" stroke="#D9D2C2"/><text x="{X(i) + 4:.1f}" y="{H - 8}" font-size="13" fill="#5B6573">{d.year}</text>'
g += f'<text x="{X(0) + 4:.1f}" y="{H - 8}" font-size="13" fill="#5B6573">2024</text>'
fin = []
for col, (color, w, dash) in {"Obra pública": ("#C4533A", 3.4, ""), "Obra privada": ("#12213C", 3.4, ""), "Total": ("#4A6785", 2.2, "6 4")}.items():
    pts = " ".join(f"{X(i):.1f},{Yv(v):.1f}" for i, v in enumerate(SER[col]))
    g += f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else "") + ' stroke-linejoin="round" stroke-linecap="round"/>'
    fin.append([col, color, float(SER[col].iloc[-1])])
fin.sort(key=lambda r: r[2])
ys = [Yv(r[2]) for r in fin]
for k in range(1, len(ys)):
    ys[k] = min(ys[k], ys[k - 1] - 19)
for (col, color, v), yl in zip(fin, ys):
    g += f'<circle cx="{X(n - 1):.1f}" cy="{Yv(v):.1f}" r="4.5" fill="{color}"/><text x="{X(n - 1) + 10:.1f}" y="{yl + 4:.1f}" font-size="14" font-weight="600" fill="{color}">{"Cifra nacional" if col == "Total" else col} {v:.0f}</text>'
GRAF = f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Índice mensual de valor de producción, 2024 = 100">{g}</svg>'

# --- Tabla de segmentos --------------------------------------------------------------------------------------------------------------
FILAS = [("Total del estado", "Cifra nacional"), ("Sector público", "Obra pública"), ("Sector privado", "Obra privada"), ("Edificación", "Edificación"),
         ("Transporte y urbanización", "Transporte"), ("Petróleo y petroquímica", "Petróleo"), ("Electricidad y telecomunicaciones", "Electricidad"),
         ("Agua, riego y saneamiento", "Agua"), ("Otras construcciones", "Otras construcciones")]
filas = ""
for clave, nombre in FILAS:
    r = SEG.loc[clave]
    falta = f'+{p1(r.falta_para_2024_pct)}%' if r.falta_para_2024_pct > 0 else '<span class="pos">ya arriba</span>'
    peso = "" if clave == "Total del estado" else f"{p1(r.peso_2025_pct)}%"
    filas += (f'<tr{" class=nac" if clave == "Total del estado" else ""}><td><b>{nombre}</b></td><td class="n g">{peso}</td><td class="n">{sg(r.var_26_vs_25_pct)}</td>'
              f'<td class="n">{sg(r.var_26_vs_24_pct)}</td><td class="n f">{falta}</td></tr>')
TABLA = f'<table class="cortes"><tr><th>Segmento</th><th class="n">Peso</th><th class="n">vs. 2025</th><th class="n">vs. 2024</th><th class="n">Falta para volver a 2024</th></tr>{filas}</table>'

# --- Datos del selector -----------------------------------------------------------------------------------------------------------------
nac = SEG.reset_index().rename(columns={"var_26_vs_25_pct": "v25", "var_26_vs_24_pct": "v24", "falta_para_2024_pct": "falta", "peso_2025_pct": "peso"})
nac["entidad"] = "Nacional (32 estados)"
nac["relevante"] = True
est = EST.rename(columns={"var_26_vs_25_pct": "v25", "var_26_vs_24_pct": "v24", "falta_para_2024_pct": "falta", "peso_nacional_2025_pct": "peso"})
cols = ["entidad", "segmento", "v25", "v24", "falta", "peso", "relevante"]
filas_sel = pd.concat([nac[cols], est[cols]]).round(2)
filas_sel = filas_sel.astype(object).where(filas_sel.notna(), None)
orden = ["Nacional (32 estados)"] + EST[EST.segmento == "Total del estado"].sort_values("ene_ago_2025", ascending=False).entidad.tolist()
DATOS = {"filas": filas_sel.to_dict("records"), "estados": orden,
         "segmentos": [("Total del estado", "Todo el estado"), ("Edificación", "Edificación"), ("Transporte y urbanización", "Transporte y urbanización"),
                       ("Electricidad y telecomunicaciones", "Electricidad y telecom."), ("Petróleo y petroquímica", "Petróleo y petroquímica"),
                       ("Agua, riego y saneamiento", "Agua, riego y saneamiento"), ("Otras construcciones", "Otras construcciones"),
                       ("Sector público", "Cliente: obra pública"), ("Sector privado", "Cliente: obra privada")]}

# =====================================================================================================================
# DETALLE: serie por segmento, aportes, estados, mapa de calor y cortes
# =====================================================================================================================
KK = json.loads((SAL / "cifras_clave.json").read_text(encoding="utf-8"))
SENS = pd.read_csv(SAL / "sensibilidad.csv")
SERS = pd.read_csv(SAL / "serie_indice_segmentos.csv", index_col=0, parse_dates=True)
DATOS["fechas"] = [d.strftime("%Y-%m") for d in SERS.index]
DATOS["series"] = {c: [None if pd.isna(x) else round(float(x), 1) for x in SERS[c]] for c in SERS.columns}


def pts(v):
    return f'<span class="d {"pos" if v > 0 else "neg"}"><span class="tri">{"▲" if v > 0 else "▼"}</span>{"+" if v > 0 else "−"}{abs(v):.1f}</span>'


NOMB = {"Sector público": "Obra pública", "Sector privado": "Obra privada", "Transporte y urbanización": "Transporte y urbanización",
        "Electricidad y telecomunicaciones": "Electricidad y telecom.", "Agua, riego y saneamiento": "Agua, riego y saneamiento",
        "Petróleo y petroquímica": "Petróleo y petroquímica", "Otras construcciones": "Otras construcciones", "Edificación": "Edificación"}
T24, T25 = float(SEG.loc["Total del estado", "ene_ago_2024"]), float(SEG.loc["Total del estado", "ene_ago_2025"])


def tabla_aportes(tipo, titulo):
    sub = SEG[SEG.tipo_segmento == tipo].copy()
    sub["a25"] = (sub.ene_ago_2025 - sub.ene_ago_2024) / T24 * 100
    sub["a26"] = (sub.ene_ago_2026 - sub.ene_ago_2025) / T25 * 100
    sub["a24"] = (sub.ene_ago_2026 - sub.ene_ago_2024) / T24 * 100
    filas = ""
    for nom, r in sub.sort_values("a26", ascending=False).iterrows():
        filas += f'<tr><td><b>{NOMB[nom]}</b></td><td class="n">{pts(r.a25)}</td><td class="n">{pts(r.a26)}</td><td class="n">{pts(r.a24)}</td></tr>'
    filas += (f'<tr class="nac"><td><b>Suma = cifra nacional</b></td><td class="n">{pts(sub.a25.sum())}</td><td class="n">{pts(sub.a26.sum())}</td><td class="n">{pts(sub.a24.sum())}</td></tr>')
    return f'<tr class="g"><td colspan="4">{titulo}</td></tr>{filas}'


APORTES = ('<table class="cortes"><tr><th>Segmento</th><th class="n">2025 vs. 2024</th><th class="n">2026 vs. 2025</th><th class="n">2026 vs. 2024</th></tr>'
           + tabla_aportes("tipo de obra", "Por tipo de obra") + tabla_aportes("quién contrata", "Por cliente") + "</table>")

# estados (ordenable)
ET = EST[EST.segmento == "Total del estado"].sort_values("peso_nacional_2025_pct", ascending=False)
filas = ""
for r in ET.itertuples():
    falta = f"+{p1(r.falta_para_2024_pct)}%" if r.falta_para_2024_pct > 0 else '<span class="pos">ya arriba</span>'
    filas += (f'<tr><td data-v="{r.entidad}"><b>{r.entidad}</b></td><td class="n g" data-v="{r.peso_nacional_2025_pct:.3f}">{p1(r.peso_nacional_2025_pct)}%</td>'
              f'<td class="n" data-v="{r.var_26_vs_25_pct:.3f}">{sg(r.var_26_vs_25_pct)}</td><td class="n" data-v="{r.var_26_vs_24_pct:.3f}">{sg(r.var_26_vs_24_pct)}</td>'
              f'<td class="n f" data-v="{r.falta_para_2024_pct:.3f}">{falta}</td></tr>')
ESTADOS = ('<table class="cortes ord" id="tedo"><thead><tr><th>Estado</th><th class="n">Peso 2025</th><th class="n">vs. 2025</th><th class="n">vs. 2024</th>'
           f'<th class="n">Falta para volver a 2024</th></tr></thead><tbody>{filas}</tbody></table>')

# mapa de calor estado x segmento (contra 2024)
COLS_H = ["Edificación", "Transporte y urbanización", "Electricidad y telecomunicaciones", "Agua, riego y saneamiento", "Petróleo y petroquímica",
          "Otras construcciones", "Sector público", "Sector privado"]
CORTO_H = {"Edificación": "Edifi-<br>cación", "Transporte y urbanización": "Transp. y<br>urbaniz.", "Electricidad y telecomunicaciones": "Electr. y<br>telecom.",
           "Agua, riego y saneamiento": "Agua y<br>saneam.", "Petróleo y petroquímica": "Petróleo y<br>petroq.", "Otras construcciones": "Otras<br>constr.",
           "Sector público": "Obra<br>pública", "Sector privado": "Obra<br>privada"}
piv = EST.pivot(index="entidad", columns="segmento", values="var_26_vs_24_pct")
rel = EST.pivot(index="entidad", columns="segmento", values="relevante")


def celda(v, ok):
    if v is None or pd.isna(v) or not ok:
        return '<td class="hc" style="background:var(--pista)"></td>'
    a = min(abs(v) / 60, 1) * 0.8 + 0.12
    rgb = "43,106,82" if v > 0 else "143,43,62"
    tc = "#F6F1E8" if a > 0.55 else "#1B1F27"
    return f'<td class="hc" style="background:rgba({rgb},{a:.2f});color:{tc}">{"" if p1(v) == "0" else ("+" if v > 0 else "−")}{p1(v)}</td>'


cab = "".join(f"<th>{CORTO_H[c]}</th>" for c in COLS_H)
cuerpo = ""
for e in ET.entidad:
    cuerpo += f'<tr><td class="hl">{e}</td>' + "".join(celda(piv.loc[e, c], bool(rel.loc[e, c])) for c in COLS_H) + "</tr>"
CALOR = (f'<div class="calor"><table class="heat"><tr><th></th>{cab}</tr>{cuerpo}</table></div>'
         '<div class="nota"><span class="lg" style="background:rgba(143,43,62,.85)"></span> abajo de 2024 · <span class="lg" style="background:rgba(43,106,82,.85)"></span> arriba de 2024 · '
         '<span class="lg" style="background:var(--pista)"></span> segmento menor a 0.1% del valor nacional. Escala hasta ±60%. Las variaciones muy altas vienen de bases pequeñas: tómalas con cautela. Estados ordenados por su peso en 2025.</div>')

# tres cortes y sensibilidad
nombres_cortes = ["Mes (ago-26 vs. ago-25)", "Enero a agosto (2026 vs. 2025)", "12 meses (sep-25 a ago-26 vs. previos)"]
filas = ""
for (clave, t), nom in zip(KK["titulares"].items(), nombres_cortes):
    oculta = KK["caida_oculta_por_titular"][clave]
    filas += (f'<tr><td><b>{nom}</b></td><td class="n">{sg(t["delta_pct"])}</td><td class="n">{t["estados_que_caen"]} de 32</td>'
              f'<td class="n">{p1(t["valor_prev_en_caida_pct"])}%</td><td class="n">{"Caída oculta" if oculta else "Sin caída oculta"}</td></tr>')
CORTES = ('<table class="cortes"><tr><th>Corte</th><th class="n">Cifra nacional</th><th class="n">Estados que caen</th><th class="n">Valor en esos estados</th><th class="n">Lectura</th></tr>'
          + filas + "</table>")
filas = ""
for esc in ["Todos los estados", "Sin México ni Hidalgo", "Sin petróleo y petroquímica"]:
    sub = SENS[SENS.escenario == esc]
    v = [float(x) for x in sub.delta_pct]
    filas += f'<tr><td><b>{esc}</b></td>' + "".join(f'<td class="n">{sg(x)}</td>' for x in v) + "</tr>"
SENSIB = '<table class="cortes"><tr><th>Escenario</th><th class="n">Mes</th><th class="n">Enero a agosto</th><th class="n">12 meses</th></tr>' + filas + "</table>"

SEGS_SERIE = ["Sector público", "Sector privado", "Edificación", "Transporte y urbanización", "Electricidad y telecomunicaciones", "Agua, riego y saneamiento",
              "Petróleo y petroquímica", "Otras construcciones"]
OPC = "".join(f'<option value="{s_}">{NOMB[s_]}</option>' for s_ in SEGS_SERIE)

DETALLE = f'''
<section class="card graf"><h2>Cada segmento contra la cifra nacional</h2>
<p class="nota" style="margin:0 0 6px">Elige un segmento. Índice de valor de producción, promedio móvil de 3 meses, nivel de 2024 = 100.</p>
<div class="sel" style="grid-template-columns:1fr"><div><label for="segs">Segmento</label><select id="segs">{OPC}</select></div></div>
<div id="gserie"></div><div class="nota" id="nserie"></div></section>

<section class="card graf"><h2>Quién hundió 2025 y quién rebota en 2026</h2>
<p class="nota" style="margin:0 0 4px">Puntos que cada segmento suma o resta a la cifra nacional. Cada grupo suma lo mismo.</p>{APORTES}
<div class="nota">Puntos = (valor del segmento en el periodo − valor previo) ÷ valor nacional previo × 100. Enero a agosto de cada año.</div></section>

<section class="card graf"><h2>Los 32 estados: dónde se rebota y dónde no</h2>
<p class="nota" style="margin:0 0 4px">Todo el estado, enero a agosto. Haz clic en un encabezado para ordenar.</p>{ESTADOS}</section>

<section class="card graf"><h2>Estado por segmento: cuánto queda por recuperar contra 2024</h2>
<p class="nota" style="margin:0 0 6px">Variación real de enero a agosto de 2026 contra 2024, en %.</p>{CALOR}</section>

<section class="card graf"><h2>Tres cortes: la cifra nacional cambia según el periodo</h2>{CORTES}
<div class="nota">Caída oculta = la cifra nacional sube pero más de 40% del valor está en estados que caen (criterio fijado antes de ver los datos).</div>
<h3 style="font-family:'Instrument Serif',serif;font-weight:400;font-size:22px;margin:14px 0 2px">Cuánto depende de unos pocos estados y del petróleo</h3>{SENSIB}</section>
'''

CSS_EXTRA = '\nh3{margin:0}\n.calor{overflow-x:auto}\ntable.heat{border-collapse:separate;border-spacing:3px;width:100%;min-width:640px;font-size:13.5px}\ntable.heat th{font-size:11.5px;font-weight:600;color:var(--gris);text-align:center;line-height:1.15;padding-bottom:3px;border:0}\ntable.heat td.hl{font-weight:600;font-size:14px;white-space:nowrap;border:0;padding:0 6px 0 0}\ntable.heat td.hc{height:26px;text-align:center;font-weight:600;border:0;padding:0}\n.lg{display:inline-block;width:12px;height:12px;vertical-align:-1px;margin-right:3px}\ntr.g td{font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--acero);font-weight:600;border-top:2px solid var(--marino);padding:7px 0 2px}\ntable.ord th{cursor:pointer;user-select:none} table.ord th:hover{color:var(--grafito)} table.ord th.asc::after{content:" ▲";font-size:10px} table.ord th.desc::after{content:" ▼";font-size:10px}\n'
JS_EXTRA = '\nfunction dibujaSerie(seg) {\n  const f = D.fechas, n = f.length, W = 1000, H = 250, L = 34, T = 10, B = 24, RM = 175;\n  const a = D.series["Total del estado"], b = D.series[seg];\n  const todos = a.concat(b).filter(v => v !== null);\n  const lo = Math.min.apply(null, todos) - 6, hi = Math.max.apply(null, todos) + 6;\n  const X = i => L + i * (W - L - RM) / (n - 1), Y = v => T + (hi - v) / (hi - lo) * (H - T - B);\n  let s = "";\n  for (let v = Math.ceil(lo / 20) * 20; v < hi; v += 20) s += \'<line x1="\' + L + \'" x2="\' + (W - RM) + \'" y1="\' + Y(v) + \'" y2="\' + Y(v) + \'" stroke="#E3DBC9"/><text x="\' + (L - 6) + \'" y="\' + (Y(v) + 4) + \'" text-anchor="end" font-size="12" fill="#5B6573">\' + v + \'</text>\';\n  s += \'<line x1="\' + L + \'" x2="\' + (W - RM) + \'" y1="\' + Y(100) + \'" y2="\' + Y(100) + \'" stroke="#12213C" stroke-width="1.6" stroke-dasharray="6 4"/>\';\n  f.forEach((d, i) => { if (d.slice(5) === "01" || i === 0) s += \'<text x="\' + (X(i) + 4) + \'" y="\' + (H - 8) + \'" font-size="13" fill="#5B6573">\' + d.slice(0, 4) + \'</text>\'; if (d.slice(5) === "01") s += \'<line x1="\' + X(i) + \'" x2="\' + X(i) + \'" y1="\' + T + \'" y2="\' + (H - B) + \'" stroke="#D9D2C2"/>\'; });\n  const pl = (arr, color, w, dash) => \'<polyline points="\' + arr.map((v, i) => v === null ? "" : X(i) + "," + Y(v)).filter(Boolean).join(" ") + \'" fill="none" stroke="\' + color + \'" stroke-width="\' + w + \'"\' + (dash ? \' stroke-dasharray="6 4"\' : "") + \' stroke-linejoin="round" stroke-linecap="round"/>\';\n  s += pl(a, "#4A6785", 2.4, true) + pl(b, "#C4533A", 3.4, false);\n  const la = a[n - 1], lb = b[n - 1];\n  let ya = Y(la), yb = Y(lb); if (Math.abs(ya - yb) < 18) { if (ya < yb) ya = yb - 18; else yb = ya - 18; }\n  s += \'<circle cx="\' + X(n - 1) + \'" cy="\' + Y(la) + \'" r="4.5" fill="#4A6785"/><text x="\' + (X(n - 1) + 10) + \'" y="\' + (ya + 4) + \'" font-size="14" font-weight="600" fill="#4A6785">Cifra nacional \' + Math.round(la) + \'</text>\';\n  s += \'<circle cx="\' + X(n - 1) + \'" cy="\' + Y(lb) + \'" r="4.5" fill="#C4533A"/><text x="\' + (X(n - 1) + 10) + \'" y="\' + (yb + 4) + \'" font-size="14" font-weight="600" fill="#C4533A">\' + $("segs").selectedOptions[0].textContent + \' \' + Math.round(lb) + \'</text>\';\n  $("gserie").innerHTML = \'<svg viewBox="0 0 \' + W + \' \' + H + \'" width="100%" role="img">\' + s + \'</svg>\';\n  const fila = D.filas.find(x => x.entidad === "Nacional (32 estados)" && x.segmento === seg);\n  $("nserie").innerHTML = fila ? "Enero a agosto: " + dl(fila.v25) + " contra 2025 y " + dl(fila.v24) + " contra 2024. " + (fila.falta > 0 ? "Falta crecer " + f1(fila.falta) + "% para volver a 2024." : "Ya superó su nivel de 2024.") : "";\n}\n$("segs").addEventListener("input", () => dibujaSerie($("segs").value));\ndibujaSerie($("segs").value);\ndocument.querySelectorAll("table.ord th").forEach((th, ci) => th.addEventListener("click", () => {\n  const tb = th.closest("table").querySelector("tbody"), asc = !th.classList.contains("asc");\n  th.parentNode.querySelectorAll("th").forEach(x => x.classList.remove("asc", "desc")); th.classList.add(asc ? "asc" : "desc");\n  const val = tr => { const v = tr.children[ci].dataset.v; return isNaN(parseFloat(v)) ? v : parseFloat(v); };\n  [...tb.rows].sort((r1, r2) => { const a = val(r1), b = val(r2); return (a > b ? 1 : a < b ? -1 : 0) * (asc ? 1 : -1); }).forEach(r => tb.appendChild(r));\n}));\n'

SELLO = ('<svg viewBox="0 0 100 100" width="46" height="46"><path d="M0 0 H84 L100 16 V100 H0 Z" fill="#F5F0E6"/>'
         '<g fill="none" stroke="#12213C" stroke-width="6.5" stroke-linecap="square" stroke-linejoin="miter">'
         '<path d="M28 32 H14 V68 H28"/><path d="M38 68 V32 H48 A9 9 0 0 1 48 50 H38 M48 50 L57 68"/>'
         '<path d="M68 68 V32 H78 A9 9 0 0 1 78 50 H68 M78 50 L87 68"/></g>'
         '<line x1="14" y1="50" x2="25" y2="50" stroke="#C4533A" stroke-width="6.5" stroke-linecap="square"/></svg>')

HTML = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La construcción crece 4.4%, pero sigue abajo de 2024</title>
<meta name="description" content="La cifra nacional de la construcción sube {p1(R['total_var_26_vs_25'])}% contra 2025, pero sigue {p1(R['total_var_26_vs_24'])}% abajo de 2024. Calcula cuánto le falta a tu estado y a tu segmento.">
<style>
@font-face{{font-family:"Instrument Serif";font-style:normal;font-weight:400;src:url(data:font/woff2;base64,{b64('instrument-serif-latin-400-normal.woff2')}) format("woff2")}}
@font-face{{font-family:"Instrument Serif";font-style:italic;font-weight:400;src:url(data:font/woff2;base64,{b64('instrument-serif-latin-400-italic.woff2')}) format("woff2")}}
@font-face{{font-family:"Inter";font-weight:400;src:url(data:font/woff2;base64,{b64('inter-latin-400-normal.woff2')}) format("woff2")}}
@font-face{{font-family:"Inter";font-weight:600;src:url(data:font/woff2;base64,{b64('inter-latin-600-normal.woff2')}) format("woff2")}}
:root{{--marino:#12213C;--acero:#4A6785;--terra:#C4533A;--marfil:#F5F0E6;--marfil-texto:#F6F1E8;--grafito:#1B1F27;--gris:#5B6573;
--tarjeta:#FBF8F1;--borde:#E3DBC9;--pista:#ECE5D6;--linea:#D9D2C2;--verde:#2B6A52;--vino:#8F2B3E;--suave:#CFC9BF}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--marfil);color:var(--grafito);font-family:"Inter",Arial,sans-serif;font-size:16px;line-height:1.45}}
.marco{{border:14px solid var(--marino);min-height:100vh;display:flex;flex-direction:column}}
main{{max-width:1120px;width:100%;margin:0 auto;padding:22px 28px 8px;flex:1}}
.etq{{font-weight:600;font-size:13px;letter-spacing:.16em;text-transform:uppercase;border-bottom:2px solid var(--acero);display:inline-block;padding-bottom:3px}}
h1{{font-family:"Instrument Serif",serif;font-weight:400;font-size:50px;line-height:1.03;margin:12px 0 6px}} h1 em{{color:var(--terra)}}
.sub{{color:var(--gris);font-size:19px;max-width:900px}} .sub b{{color:var(--grafito);font-weight:600}}
.card{{background:var(--tarjeta);border:1px solid var(--borde);border-radius:4px;padding:16px 18px}}
.pos{{color:var(--verde)}}.neg{{color:var(--vino)}}.d{{font-weight:600}} .tri{{font-size:.62em;vertical-align:.12em;margin-right:3px;font-family:Inter,Arial,sans-serif}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}}
.kpi{{padding:12px 16px}} .kpi .t{{font-size:15px;color:var(--gris);min-height:40px}}
.kpi .v{{font-family:"Instrument Serif",serif;font-size:56px;line-height:1.1;color:var(--marino);white-space:nowrap}} .kpi .v .d{{font-weight:400}}
.kpi .p{{font-size:14px;color:var(--gris)}}
.graf{{margin-top:16px}} .graf h2{{font-family:"Instrument Serif",serif;font-weight:400;font-size:28px;line-height:1.1;margin-bottom:2px}}
.nota{{font-size:13.5px;color:var(--gris);margin-top:6px}}
svg text{{font-family:"Inter",Arial,sans-serif}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:15.5px}}
th{{text-align:left;font-weight:600;font-size:12.5px;color:var(--gris);border-bottom:1px solid var(--linea);padding:6px 10px 6px 0;text-transform:uppercase;letter-spacing:.04em}}
td{{padding:8px 10px 8px 0;border-top:1px solid var(--pista)}} td.n,th.n{{text-align:right;white-space:nowrap}} td.g{{color:var(--gris)}} td.f{{font-weight:600;color:var(--terra)}}
tr.nac td{{background:var(--pista);padding-left:6px}}
.sel{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px}} label{{display:block;font-weight:600;font-size:13px;margin-bottom:4px}}
select{{width:100%;font:inherit;font-size:17px;padding:8px 10px;border:1px solid var(--linea);border-radius:4px;background:var(--marfil);color:var(--grafito)}}
.res{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px}} .res .v{{font-family:"Instrument Serif",serif;font-size:44px;line-height:1.1;color:var(--marino);white-space:nowrap}}
.res .t{{font-size:14px;color:var(--gris)}} #frase{{margin-top:10px;font-size:18px}}
.dec{{margin-top:16px;background:var(--marino);color:var(--marfil-texto);border-radius:4px;padding:16px 22px}}
.dec h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--suave);font-weight:600}}
.dec .l{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:8px}} .dec .l b{{display:block;color:#EE8A5A;font-size:18px;margin-bottom:2px;font-weight:600}} .dec .l div{{font-size:16px;line-height:1.35}}
.dec .rent{{margin-top:12px;border-top:1px solid #3a4a66;padding-top:10px;font-size:16px}} .dec .rent b{{font-weight:600}}
details{{margin-top:14px;font-size:14px}} details summary{{cursor:pointer;color:var(--acero);font-weight:600;font-size:15px}} details li{{font-size:13.5px;color:var(--gris);margin:6px 0 0 20px}}
.fuentes{{max-width:1120px;margin:8px auto 0;padding:0 28px 14px;width:100%}} .fuentes table{{font-size:11.5px;color:var(--gris)}} .fuentes th{{font-size:11.5px;color:var(--grafito)}} .fuentes td{{padding:3px 6px 3px 0}}
.fuentes p{{font-size:12.5px;color:var(--gris);margin-top:6px}} .fuentes p.legal{{font-style:italic}} .fuentes p b{{font-weight:600;color:var(--grafito)}}
.filete{{height:4px;background:var(--terra)}}
footer{{background:var(--marino);color:var(--marfil-texto);display:flex;justify-content:space-between;align-items:center;padding:12px 28px;gap:12px}}
footer .n{{display:flex;align-items:center;gap:12px;font-family:"Instrument Serif",serif;font-size:26px}} footer .r{{font-weight:600;font-size:12px;letter-spacing:.06em}}
@media(max-width:900px){{.kpis,.sel,.res,.dec .l{{grid-template-columns:1fr}}h1{{font-size:34px}}.kpi .v{{font-size:46px}}.cortes,.fuentes table{{display:block;overflow-x:auto}}}}
{CSS_EXTRA}</style></head>
<body><div class="marco"><main>
<span class="etq">Constructoras en México · Enero a agosto 2026</span>
<h1>La construcción «crece» <em>+{p1(R['total_var_26_vs_25'])}%</em>. Sigue {p1(R['total_var_26_vs_24'])}% abajo de 2024.</h1>
<p class="sub">Es un rebote: en 2025 la obra cayó <b>{p1(R['total_var_25_vs_24'])}%</b>, sobre todo por la obra pública. Para volver al nivel de 2024 le falta crecer <b>{p1(R['total_falta_para_2024'])}%</b>. Valor de producción real de las empresas constructoras (INEGI, ENEC).</p>

<div class="kpis">
<div class="card kpi"><div class="t">Contra enero a agosto de 2025</div><div class="v">{sg(R['total_var_26_vs_25'])}</div><div class="p">lo que dice la cifra nacional</div></div>
<div class="card kpi"><div class="t">Contra enero a agosto de 2024</div><div class="v">{sg(R['total_var_26_vs_24'])}</div><div class="p">el nivel que hay que recuperar</div></div>
<div class="card kpi"><div class="t">Falta para volver a 2024</div><div class="v">+{p1(R['total_falta_para_2024'])}%</div><div class="p">crecimiento que aún se necesita</div></div>
</div>

<section class="card graf"><h2>La obra pública se desplomó y rebota. La privada se mantiene cerca de su nivel de 2024.</h2>
<p class="nota" style="margin:0 0 4px">Valor de producción, promedio móvil de 3 meses. Nivel de 2024 = 100 (línea punteada).</p>{GRAF}</section>

<section class="card graf"><h2>Crece contra 2025, pero no contra 2024</h2>{TABLA}
<div class="nota">Peso = parte del valor nacional de 2025. «Falta para volver a 2024» = valor de 2024 ÷ valor de 2026 − 1. Enero a agosto de cada año. Cifras de una encuesta (coeficiente de variación estatal de 5% a 9%) y preliminares: diferencias pequeñas pueden no ser reales.</div></section>

<section class="card graf"><h2>¿Cuánto le falta a tu estado y a tu segmento?</h2>
<div class="sel"><div><label for="edo">Tu estado</label><select id="edo"></select></div><div><label for="seg">Tu segmento</label><select id="seg"></select></div></div>
<div class="res"><div class="card"><div class="t">Contra 2025</div><div class="v" id="r1">–</div></div><div class="card"><div class="t">Contra 2024</div><div class="v" id="r2">–</div></div>
<div class="card"><div class="t">Falta para volver a 2024</div><div class="v" id="r3">–</div></div></div><div id="frase"></div></section>

{DETALLE}
<div class="dec"><h2>Qué hacer</h2><div class="l">
<div><b>1. Metas contra 2024</b>La base de 2025 está hundida: crecer contra ella no es crecer.</div>
<div><b>2. Mira tu segmento</b>Pública: faltan +{p1(R['publico_falta_para_2024'])}% para volver. Privada: +{p1(R['privado_falta_para_2024'])}%, y en jun–ago ya está en su nivel de 2024.</div>
<div><b>3. Dimensiona a tu volumen</b>Plantilla y equipo, para la obra de tu segmento, no para la de 2024.</div></div>
<div class="rent"><b>Rentabilidad:</b> el volumen nacional es {p1(R['total_var_26_vs_24'])}% menor que en 2024. Si tu estructura sigue dimensionada para 2024, la capacidad sin usar pega en tu margen. Los datos no miden márgenes: es una consecuencia, no una medición.</div></div>

<details><summary>Cómo se calculó y límites</summary><ul>
<li>Valor de producción real (pesos constantes de 2018) de las empresas constructoras que cubre la ENEC, suma de los 32 estados, de enero a agosto de 2024, 2025 y 2026.</li>
<li>Segmento = tipo de obra (6) o tipo de cliente (público o privado). La ENEC no publica el cruce entre ambos.</li>
<li>Por estado, los segmentos con menos de 0.1% del valor nacional se marcan como segmento pequeño: su variación se exagera por la base.</li>
<li>La gráfica usa un promedio móvil de 3 meses con base en el promedio mensual de enero a agosto de 2024. La tabla usa enero a agosto completo.</li>
<li>Cifras de 2026 revisadas o preliminares; INEGI publica la siguiente el 24-nov-2026. Son cifras de una encuesta (coeficiente de variación estatal de 5% a 9%): diferencias pequeñas pueden no ser reales. No mide márgenes, costos ni demanda.</li></ul></details>
</main>

<div class="fuentes">
<table><tr><th>Dato</th><th>Fuente</th><th>Consulta</th><th>Estatus</th></tr>
<tr><td>Valor de producción de empresas constructoras, por estado, tipo de obra y cliente, pesos constantes de 2018</td><td>INEGI, Encuesta Nacional de Empresas Constructoras (ENEC), Serie 2018, datos abiertos</td><td>31-oct-2026</td><td>Oficial</td></tr></table>
<p><b>Fuente:</b> elaboración propia con datos de INEGI, ENEC Serie 2018, corte agosto de 2026.</p>
<p class="legal">Contenido informativo; no constituye asesoría legal, financiera ni comercial. Sin aval ni relación con INEGI.</p></div>
<div class="filete"></div>
<footer><div class="n">{SELLO}<span>Ernesto Roldán</span></div><div class="r">Business Intelligence &amp; Analytics</div></footer></div>
<script>
const D = {json.dumps(DATOS, ensure_ascii=False)};
const $ = id => document.getElementById(id);
const f1 = v => (Math.round(Math.abs(v) * 10) / 10).toLocaleString("es-MX", {{minimumFractionDigits: 0, maximumFractionDigits: 1}});
const dl = v => v === null ? "–" : '<span class="d ' + (v > 0 ? "pos" : "neg") + '"><span class="tri">' + (v > 0 ? "▲" : "▼") + "</span>" + (v > 0 ? "+" : "−") + f1(v) + "%</span>";
D.estados.forEach(e => {{ const o = document.createElement("option"); o.value = o.textContent = e; $("edo").appendChild(o); }});
D.segmentos.forEach(([v, t]) => {{ const o = document.createElement("option"); o.value = v; o.textContent = t; $("seg").appendChild(o); }});
$("edo").value = "Nacional (32 estados)"; $("seg").value = "Sector privado";
function render() {{
  const r = D.filas.find(x => x.entidad === $("edo").value && x.segmento === $("seg").value);
  if (!r || r.v24 === null) {{ ["r1", "r2", "r3"].forEach(i => $(i).textContent = "–"); $("frase").textContent = "Ese segmento no tiene valor para comparar."; return; }}
  $("r1").innerHTML = dl(r.v25); $("r2").innerHTML = dl(r.v24);
  $("r3").innerHTML = r.falta > 0 ? '<span class="d" style="color:var(--terra)">+' + f1(r.falta) + "%</span>" : '<span class="d pos">ya arriba</span>';
  let t;
  if (!r.relevante) t = "Segmento muy pequeño: pesa menos de 0.1% del valor nacional y su variación se exagera por la base. Tómala como referencia. ";
  else if (r.v24 >= 0) t = "Tu segmento ya superó su nivel de 2024 (+" + f1(r.v24) + "%). ";
  else if (r.v25 > 0) t = "Crece contra 2025, pero sigue " + f1(r.v24) + "% abajo de 2024: la base de 2025 estaba deprimida. Necesita crecer " + f1(r.falta) + "% para volver. ";
  else t = "Cae contra 2025 y está " + f1(r.v24) + "% abajo de 2024. Necesita crecer " + f1(r.falta) + "% para volver. ";
  if (r.relevante && (Math.abs(r.v25) > 100 || Math.abs(r.v24) > 100)) t += "Variación extrema: la base de ese segmento es muy pequeña; tómala con cautela. ";
  $("frase").textContent = t + "Pesa " + (r.peso < 0.1 ? "menos de 0.1%" : f1(r.peso) + "%") + " del valor nacional de 2025.";
}}
["edo", "seg"].forEach(id => $(id).addEventListener("input", render));
render();
{JS_EXTRA}
</script></body></html>
"""
(AQUI.parent / "index.html").write_text(HTML, encoding="utf-8")
print("index.html", round(len(HTML) / 1024), "KB")
