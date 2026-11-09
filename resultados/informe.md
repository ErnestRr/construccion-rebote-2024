# Análisis 05. ¿El titular nacional oculta una caída en tu mercado?

**Problema.** El titular dice que la construcción crece. ¿Presupuestamos e invertimos con ese número? **Pregunta contrastable:** ¿el número nacional refleja tu mercado (estado, tipo de obra, quién contrata) o lo esconde? Datos: valor de producción de las empresas constructoras (ENEC, INEGI), corte de agosto de 2026, pesos constantes de 2018. No se calculan variaciones en pesos corrientes.

**Respuesta corta:** depende del titular. Con el del año corrido, sí oculta una caída; con el del mes, no.

**Comprador al que sirve:** director general o dueño de una constructora o proveedora de la construcción que fija metas e inversión con el titular nacional.

## Hallazgos verificados (cifras en `titulares.csv`, `descomposicion.csv`, `resultados.csv`, `sensibilidad.csv`)

1. **Tres titulares, tres lecturas.**
   - Mes (ago-2026 vs. ago-2025): +10.7%. Caen 11 de 32 estados (37.6% del valor); mediana ponderada +1.0%.
   - Año corrido (ene-ago): +4.4%. Caen 17 de 32 estados (63.1% del valor); mediana ponderada −2.9%.
   - 12 meses: −1.0%. Caen 18 de 32 estados (53.9% del valor); mediana ponderada −1.4%.
   La regla se fijó antes de ver los datos: titular positivo y más de 40% del valor en estados que caen, o mediana ponderada negativa. Solo el año corrido la cumple.
2. **El total esconde partes que suben y partes que caen (12 meses).** Transporte y urbanización +18.9% (aporta +3.8 puntos) y electricidad y telecomunicaciones +22.8% (+1.2) compensan edificación −3.7% (−1.8), petróleo y petroquímica −37.6% (−3.0), agua −14.8% (−0.6) y otras construcciones −4.6% (−0.7).
3. **Por tipo de cliente.** El sector privado cae 3.6% (aporta −2.4 puntos) y el sector público sube 4.4% (+1.4): el total de −1.0% suaviza la caída del privado.
4. **Del agregado al detalle.** 73 de 125 mercados (estado × tipo de obra, con al menos 0.1% del total) caen. Concentran 61.8% del valor y su mediana ponderada es −6.4%. Con umbrales de 0.05% y 0.25% la lectura se mantiene (entre 59% y 62% del valor cae).
5. **El titular depende de dos estados.** Sin México e Hidalgo, el año corrido pasa de +4.4% a −3.2% y el de 12 meses de −1.0% a −7.0%. Sin petróleo y petroquímica, el total de 12 meses pasa de −1.0% a +2.1%: esa rama explica buena parte de la caída del total.

## Interpretación (hipótesis, no verificada con estos datos)
- El titular refleja sobre todo obra de transporte en pocos estados.
- Quien vende edificación o trabaja para clientes privados vive un mercado distinto al del titular. Estos datos no identifican las obras ni a las empresas.

## Efecto en la empresa (implicación para la dirección; interpretación del autor)
- **Presupuesto e ingresos:** presupuestar con el titular del año corrido (+4.4%) sobreestima si el mercado propio es edificación (−3.7%) o cliente privado (−3.6%). La meta de ventas debe partir del Δ real del mercado propio.
- **Capital y expansión:** 63.1% del valor está en estados que caen aunque el total suba; asignar capital con el titular puede dirigirlo a mercados que no crecen.
- **Precios y margen (hipótesis):** en mercados que caen hay menos volumen para repartir, con posible presión sobre precios; los datos no miden márgenes.
- **Decisión propuesta (a validar):** definir el mercado propio (estado, tipo de obra, cliente) y seguir cada mes su Δ real y su brecha contra el titular. Regla de decisión: si la brecha es menor a −5 puntos durante 3 cortes seguidos, revisar el plan comercial.
- **Qué significa:** el titular nacional no sirve para fijar metas ni inversión de un mercado específico. La dirección debe responder: ¿qué parte de la cartera está en mercados que caen aunque el titular nacional suba?

## Información adicional que un director necesitaría
Cartera propia por estado, tipo de obra y cliente; márgenes y plazos de pago por tipo de cliente; competidores locales; qué obras explican el alza de transporte.

## Límites
- La ENEC es una muestra de empresas constructoras (CV estatal de 5% a 9%); mide actividad ejecutada, no demanda capturable ni rentabilidad. Un mercado que cae en los datos no implica que una empresa concreta pierda ventas.
- El estado es el de la obra, no el domicilio de la empresa.
- Valores constantes con el deflactor implícito nacional de INEGI (INPP de la construcción); cifras de 2026 revisadas o preliminares.
- Las celdas de mercados pequeños se dejan en blanco (no son cero) y los porcentajes de bases pequeñas se exageran.
- Los titulares de mes, año corrido y 12 meses miden periodos distintos: no se mezclan en una misma comparación.
- No se estimó ningún modelo.
