"""Análisis 05: ¿el crecimiento nacional oculta una caída en tu mercado?

Lee la base común (datos/procesados/enec_vp_entidad_corr_const.csv, pesos constantes de 2018) y escribe en
resultados/05_promedio_y_mercado/: resultados.csv (mercados), titulares.csv, descomposicion.csv, series_segmentos.csv,
sensibilidad.csv y cifras_clave.json.  No se calculan variaciones en pesos corrientes.
Uso (desde la raíz):  .venv\\Scripts\\python.exe analisis\\05_promedio_y_mercado\\calcular.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ))
CFG = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))
SAL = RAIZ / "resultados" / "05_promedio_y_mercado"
CORTE = pd.Timestamp(CFG["corte"])
ESTADOS = [f"{i:02d}" for i in range(1, 33)]
UMBRAL = 0.001  # mercado relevante: >= 0.1% del total nacional previo (config.json)
SEGMENTOS = {"o110a_real": ("Total del estado", "total"),
             "o110a_1_real": ("Edificación", "tipo de obra"), "o110a_2_real": ("Agua, riego y saneamiento", "tipo de obra"),
             "o110a_3_real": ("Electricidad y telecomunicaciones", "tipo de obra"), "o110a_4_real": ("Transporte y urbanización", "tipo de obra"),
             "o110a_5_real": ("Petróleo y petroquímica", "tipo de obra"), "o110a_6_real": ("Otras construcciones", "tipo de obra"),
             "o110b_1_real": ("Sector público", "quién contrata"), "o110b_2_real": ("Sector privado", "quién contrata")}


def cargar():
    d = pd.read_csv(RAIZ / "datos" / "procesados" / "enec_vp_entidad_corr_const.csv", dtype={"codigo_entidad": str}, parse_dates=["fecha"])
    return d[d.codigo_entidad.isin(ESTADOS)].sort_values(["codigo_entidad", "fecha"]).reset_index(drop=True)


def ventana12(e, f):
    return (e.fecha > f - pd.DateOffset(months=12)) & (e.fecha <= f)


def mediana_ponderada(valores, pesos):
    v = pd.DataFrame({"v": valores, "w": pesos}).dropna().sort_values("v")
    if v.w.sum() <= 0:
        return np.nan
    return float(v.v[v.w.cumsum() / v.w.sum() >= 0.5].iloc[0])


def mercados(e):
    """Una fila por estado x segmento (total, 6 tipos de obra, 2 sectores) con acumulado 12m actual y previo."""
    act = e[ventana12(e, CORTE)].groupby("codigo_entidad")[list(SEGMENTOS)].sum()
    prv = e[ventana12(e, CORTE - pd.DateOffset(years=1))].groupby("codigo_entidad")[list(SEGMENTOS)].sum()
    total_prev = float(prv.o110a_real.sum())
    nombres = e.drop_duplicates("codigo_entidad").set_index("codigo_entidad").entidad
    filas = []
    for col, (seg, tipo) in SEGMENTOS.items():
        for c in act.index:
            a, p = float(act.loc[c, col]), float(prv.loc[c, col])
            filas.append({"codigo_entidad": c, "entidad": nombres[c], "segmento": seg, "tipo_segmento": tipo, "acum12_real_mmdp_2018": a / 1e6,
                          "acum12_prev_real_mmdp_2018": p / 1e6, "delta_mmdp_2018": (a - p) / 1e6,
                          "dpct": (a / p - 1) * 100 if p > 0 else np.nan, "contrib_pp": (a - p) / total_prev * 100,
                          "part_prev_pct": p / total_prev * 100, "relevante": bool(p >= UMBRAL * total_prev)})
    m = pd.DataFrame(filas)
    m["cae"] = m.relevante & (m.dpct < 0)
    return m, total_prev / 1e6


def titulares(e, excluir=(), tipos_excluir=()):
    """Tres titulares nacionales y qué parte del valor previo está en estados que caen."""
    x = e[~e.codigo_entidad.isin(excluir)]
    col = "o110a_real" if not tipos_excluir else None
    if tipos_excluir:
        x = x.assign(o110a_real=x.o110a_real - x[[f"{t}_real" for t in tipos_excluir]].sum(axis=1))
    def agrega(mascara_act, mascara_prv):
        a = x[mascara_act].groupby("codigo_entidad").o110a_real.sum()
        p = x[mascara_prv].groupby("codigo_entidad").o110a_real.sum()
        ok = p > 0
        d = (a[ok] / p[ok] - 1) * 100
        return {"delta_pct": float((a.sum() / p.sum() - 1) * 100), "estados_que_caen": int((d < 0).sum()), "estados": int(ok.sum()),
                "valor_prev_en_caida_pct": float(p[ok][d < 0].sum() / p.sum() * 100), "mediana_ponderada_estados_pct": mediana_ponderada(d, p[ok])}
    f = CORTE
    prev = f - pd.DateOffset(years=1)
    ytd = lambda anio: (x.fecha.dt.year == anio) & (x.fecha.dt.month <= f.month)
    return {"Variación del mes (ago-2026 vs. ago-2025)": agrega(x.fecha == f, x.fecha == prev),
            "Acumulado del año (ene-ago 2026 vs. ene-ago 2025)": agrega(ytd(f.year), ytd(f.year - 1)),
            "Acumulado de 12 meses (sep-2025 a ago-2026 vs. previos)": agrega(ventana12(x, f), ventana12(x, prev))}


def series_segmentos(e):
    """Δ% del acumulado de 12 meses por estado y segmento (desde 2022-01), para el selector de mercado."""
    filas = []
    for col, (seg, _) in SEGMENTOS.items():
        d = e[["codigo_entidad", "entidad", "fecha", col]].copy()
        d["a12"] = d.groupby("codigo_entidad")[col].transform(lambda s: s.rolling(12, min_periods=12).sum())
        d["dpct"] = (d.a12 / d.groupby("codigo_entidad").a12.shift(12).where(lambda s: s > 0) - 1) * 100
        d["segmento"] = seg
        filas.append(d[d.fecha >= "2022-01-01"].dropna(subset=["dpct"])[["codigo_entidad", "entidad", "segmento", "fecha", "dpct"]])
    return pd.concat(filas)


def main():
    SAL.mkdir(parents=True, exist_ok=True)
    e = cargar()
    m, total_prev = mercados(e)
    m.round(6).to_csv(SAL / "resultados.csv", index=False, encoding="utf-8")
    tit = {k: v for k, v in titulares(e).items()}
    pd.DataFrame(tit).T.rename_axis("titular").reset_index().round(4).to_csv(SAL / "titulares.csv", index=False, encoding="utf-8")
    nac = m[m.tipo_segmento != "total"].groupby(["segmento", "tipo_segmento"])[["acum12_real_mmdp_2018", "acum12_prev_real_mmdp_2018", "delta_mmdp_2018", "contrib_pp"]].sum().reset_index()
    nac["dpct"] = (nac.acum12_real_mmdp_2018 / nac.acum12_prev_real_mmdp_2018 - 1) * 100
    nac.round(6).to_csv(SAL / "descomposicion.csv", index=False, encoding="utf-8")
    series_segmentos(e).round({"dpct": 2}).assign(fecha=lambda s: s.fecha.dt.strftime("%Y-%m-%d")).to_csv(SAL / "series_segmentos.csv", index=False, encoding="utf-8")
    # sensibilidad
    filas = []
    for nombre, (exc, texc) in {"Todos los estados": ((), ()), "Sin México ni Hidalgo": (("13", "15"), ()), "Sin petróleo y petroquímica": ((), ("o110a_5",))}.items():
        for k, v in titulares(e, exc, texc).items():
            filas.append({"escenario": nombre, "titular": k, **v})
    sens = pd.DataFrame(filas)
    sens.round(4).to_csv(SAL / "sensibilidad.csv", index=False, encoding="utf-8")
    mt = m[m.tipo_segmento == "tipo de obra"]
    umbrales = {}
    for u in (0.0005, 0.001, 0.0025):
        r = mt[mt.acum12_prev_real_mmdp_2018 >= u * total_prev]
        umbrales[f"{u * 100:.2f}%"] = {"celdas": int(len(r)), "valor_prev_en_celdas_que_caen_pct": float(r[r.dpct < 0].acum12_prev_real_mmdp_2018.sum() / total_prev * 100),
                                         "mediana_ponderada_pct": mediana_ponderada(r.dpct, r.acum12_prev_real_mmdp_2018)}
    rel = mt[mt.relevante]
    cifras = {"total_prev_mmdp": total_prev, "celdas_relevantes": int(len(rel)), "celdas_totales": int(len(mt)), "celdas_que_caen": int((rel.dpct < 0).sum()),
              "valor_cubierto_pct": float(rel.acum12_prev_real_mmdp_2018.sum() / total_prev * 100),
              "valor_prev_en_celdas_que_caen_pct": float(rel[rel.dpct < 0].acum12_prev_real_mmdp_2018.sum() / total_prev * 100),
              "mediana_ponderada_celdas_pct": mediana_ponderada(rel.dpct, rel.acum12_prev_real_mmdp_2018), "umbrales": umbrales, "titulares": tit,
              "regla_caida_oculta": "titular > 0 y más de 40% del valor previo en estados que caen, o mediana ponderada negativa"}
    cifras["caida_oculta_por_titular"] = {k: bool(v["delta_pct"] > 0 and (v["valor_prev_en_caida_pct"] > 40 or v["mediana_ponderada_estados_pct"] < 0)) for k, v in tit.items()}
    (SAL / "cifras_clave.json").write_text(json.dumps(cifras, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    return m, nac, tit, sens, cifras


if __name__ == "__main__":
    main()
    print("resultados escritos en", SAL)
