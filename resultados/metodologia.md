# Metodología. Análisis 05

## Datos
- **Fuente:** INEGI, ENEC Serie 2018, datos abiertos (descarga 2026-10-31), datos hasta agosto de 2026. Misma base que el análisis 02: `datos/procesados/enec_vp_entidad_corr_const.csv`, valor de producción en miles de pesos constantes de 2018 (deflactor implícito de INEGI; ver `documentacion/diccionario_datos.md`). No se volvió a descargar ni a reconstruir nada.
- **Universo:** 32 entidades (sin el total nacional ni "Obra en el extranjero"). El total de los 32 estados coincide con el nacional.
- **Mercados:** estado × tipo de obra (6 tipos, suman el total) y estado × quién contrata (sector público y privado, suman el total). La ENEC no publica el cruce tipo de obra × quién contrata.

## Criterios fijados antes de ver resultados (`analisis/05_promedio_y_mercado/config.json`)
- **Medida principal:** acumulado de 12 meses (sep-2025 a ago-2026) frente a los 12 meses previos, en pesos constantes.
- **Titulares a contrastar:** variación del mes (ago-2026 vs. ago-2025), año corrido (ene-ago) y 12 meses, sobre la suma de los 32 estados. No se mezclan en una misma comparación.
- **Mercado relevante:** acumulado previo de al menos 0.1% del total nacional; las demás celdas se muestran en blanco y no entran en los conteos.
- **Ponderación:** las comparaciones usan como peso el valor del periodo previo; no se promedian tasas estatales sin ponderar.
- **Caída oculta:** titular positivo y más de 40% del valor previo en estados que caen, o mediana ponderada negativa.

## Fórmulas
- Δ% de una parte = valor actual / valor previo − 1 (faltante si el previo es cero o negativo).
- Aporte (puntos) = (valor actual − valor previo) de la parte / valor previo nacional × 100; suma el total para cada corte (tipo de obra o quién contrata).
- % del valor en caída = suma del valor previo de los estados con Δ < 0 / valor previo nacional.
- Mediana ponderada = valor de Δ en el que el peso acumulado (ordenado de menor a mayor Δ) alcanza 50%.
- Sensibilidad: sin México e Hidalgo; sin petróleo y petroquímica; umbrales de relevancia de 0.05%, 0.1% y 0.25%.

## Comprobaciones
- `python -m pytest controles -q`: incluye que los tipos de obra y los tipos de cliente sumen el total, que los aportes sumen el Δ total, que los titulares coincidan con un cálculo independiente y que el texto use las cifras de los CSV.
- Los titulares de mes (+10.7%) coinciden con el boletín 636/26 de INEGI.

## Comandos para regenerar
```
.venv\Scripts\python.exe analisis\05_promedio_y_mercado\calcular.py
.venv\Scripts\python.exe analisis\05_promedio_y_mercado\construir_entregables.py
```
