"""Análisis 05, extensión: ¿el crecimiento de 2026 es crecimiento o rebote sobre una base baja?

Compara enero a agosto de 2026 contra enero a agosto de 2025 y de 2024 (valor de producción real, pesos constantes de 2018), por
segmento (6 tipos de obra y 2 tipos de cliente), nacional y por estado. Escribe en resultados/05_promedio_y_mercado/:
rebote_segmentos.csv, rebote_estado_segmento.csv, serie_indice_mensual.csv y cifras_rebote.json.
Uso (desde la raíz del repositorio):  python src/rebote.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1]))
import calcular as C  # noqa: E402

SAL = AQUI.parent / "resultados"  # ajusta si guardas los resultados en otra carpeta
E = C.cargar()
Y, M = E.fecha.dt.year, E.fecha.dt.month
COLS = list(C.SEGMENTOS)
NOMBRE = {c: n for c, (n, _) in C.SEGMENTOS.items()}
TIPO = {c: t for c, (n, t) in C.SEGMENTOS.items()}


def ytd(anio):
    return E[(Y == anio) & (M <= 8)]


# --- Nacional por segmento -----------------------------------------------------------------------------------------------------
v = {a: ytd(a)[COLS].sum() / 1e6 for a in (2024, 2025, 2026)}  # miles de millones de pesos de 2018
rows = []
for c in COLS:
    v24, v25, v26 = v[2024][c], v[2025][c], v[2026][c]
    rows.append({"segmento": NOMBRE[c], "tipo_segmento": TIPO[c], "ene_ago_2024": v24, "ene_ago_2025": v25, "ene_ago_2026": v26,
                 "peso_2025_pct": v25 / v[2025]["o110a_real"] * 100,
                 "var_26_vs_25_pct": (v26 / v25 - 1) * 100, "var_25_vs_24_pct": (v25 / v24 - 1) * 100,
                 "var_26_vs_24_pct": (v26 / v24 - 1) * 100,
                 "falta_para_2024_pct": (v24 / v26 - 1) * 100})
seg = pd.DataFrame(rows)
seg.to_csv(SAL / "rebote_segmentos.csv", index=False, encoding="utf-8-sig")

# --- Estado x segmento ---------------------------------------------------------------------------------------------------------
nombres = E.drop_duplicates("codigo_entidad").set_index("codigo_entidad").entidad
g = {a: ytd(a).groupby("codigo_entidad")[COLS].sum() / 1e6 for a in (2024, 2025, 2026)}
tot25 = float(g[2025]["o110a_real"].sum())
filas = []
for c in COLS:
    for cod in g[2026].index:
        a24, a25, a26 = float(g[2024].loc[cod, c]), float(g[2025].loc[cod, c]), float(g[2026].loc[cod, c])
        ok = a25 > 0 and a24 > 0 and a26 > 0
        filas.append({"codigo_entidad": cod, "entidad": nombres[cod], "segmento": NOMBRE[c], "tipo_segmento": TIPO[c],
                      "ene_ago_2024": a24, "ene_ago_2025": a25, "ene_ago_2026": a26,
                      "var_26_vs_25_pct": (a26 / a25 - 1) * 100 if a25 > 0 else None,
                      "var_26_vs_24_pct": (a26 / a24 - 1) * 100 if a24 > 0 else None,
                      "falta_para_2024_pct": (a24 / a26 - 1) * 100 if a26 > 0 else None,
                      "peso_nacional_2025_pct": a25 / tot25 * 100, "relevante": bool(ok and a25 >= 0.001 * tot25)})
pd.DataFrame(filas).to_csv(SAL / "rebote_estado_segmento.csv", index=False, encoding="utf-8-sig")

# --- Serie mensual: promedio móvil de 3 meses, índice con base en el promedio mensual de enero a agosto de 2024 = 100 -------------
mens = E.groupby("fecha")[["o110a_real", "o110b_1_real", "o110b_2_real"]].sum() / 1e6
mens.columns = ["Total", "Obra pública", "Obra privada"]
base = mens[(mens.index.year == 2024) & (mens.index.month <= 8)].mean()
idx = (mens.rolling(3).mean() / base * 100)
idx = idx[idx.index >= "2024-03-01"].round(2)
idx.to_csv(SAL / "serie_indice_mensual.csv", encoding="utf-8-sig")

# --- Cifras clave y verificación contra el análisis 05 ---------------------------------------------------------------------------
K = json.loads((SAL / "cifras_clave.json").read_text(encoding="utf-8"))
nac26 = float(seg.loc[seg.segmento == "Total del estado", "var_26_vs_25_pct"].iloc[0])
assert abs(nac26 - list(K["titulares"].values())[1]["delta_pct"]) < 1e-6, "la cifra nacional no coincide con cifras_clave.json"
t = seg.set_index("segmento")
cifras = {
    "corte": "enero a agosto de 2026 contra enero a agosto de 2025 y de 2024, pesos constantes de 2018",
    "total_var_26_vs_25": nac26, "total_var_25_vs_24": float(t.loc["Total del estado", "var_25_vs_24_pct"]),
    "total_var_26_vs_24": float(t.loc["Total del estado", "var_26_vs_24_pct"]), "total_falta_para_2024": float(t.loc["Total del estado", "falta_para_2024_pct"]),
    "publico_var_25_vs_24": float(t.loc["Sector público", "var_25_vs_24_pct"]), "publico_var_26_vs_25": float(t.loc["Sector público", "var_26_vs_25_pct"]),
    "publico_var_26_vs_24": float(t.loc["Sector público", "var_26_vs_24_pct"]), "publico_falta_para_2024": float(t.loc["Sector público", "falta_para_2024_pct"]),
    "privado_var_25_vs_24": float(t.loc["Sector privado", "var_25_vs_24_pct"]), "privado_var_26_vs_25": float(t.loc["Sector privado", "var_26_vs_25_pct"]),
    "privado_var_26_vs_24": float(t.loc["Sector privado", "var_26_vs_24_pct"]), "privado_falta_para_2024": float(t.loc["Sector privado", "falta_para_2024_pct"]),
    "pico_ene_ago_total": {"anio": int(pd.Series({a: E[(Y == a) & (M <= 8)].o110a_real.sum() for a in range(2018, 2027)}).idxmax())},
}
tot_anios = pd.Series({a: E[(Y == a) & (M <= 8)].o110a_real.sum() / 1e6 for a in range(2018, 2027)})
cifras["total_var_26_vs_pico"] = float((tot_anios[2026] / tot_anios.max() - 1) * 100)
(SAL / "cifras_rebote.json").write_text(json.dumps(cifras, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: (round(x, 2) if isinstance(x, float) else x) for k, x in cifras.items()}, ensure_ascii=False, indent=1))
print(seg.round(1)[["segmento", "peso_2025_pct", "var_25_vs_24_pct", "var_26_vs_25_pct", "var_26_vs_24_pct", "falta_para_2024_pct"]].to_string())
