# Metodología académica · 2.0.0

## Fuentes

Se incorporaron 25 reportes oficiales CIFRHS: DOC 2001–2019, DOCX 2020 y PDF 2021–2025. Los reportes de 2024 y 2025 se localizaron fuera de las entradas activas del catálogo histórico. No se reconstruyen resultados de 2026 desde fuentes secundarias. Puntajes y oferta tienen cobertura independiente. Las capturas conservan URL, descarga UTC, SHA-256, parser y estado.

DOC se lee con word-extractor; DOCX por filas/celdas XML; PDF por posiciones y bandas de filas, límites de columna y nombres multilínea. Se excluyen totales para no sumarlos de nuevo y tablas posteriores de categoría extranjera. Los valores originales se preservan.

## Unidad e identidad

Denominación exacta normalizada + entidad reportada × edición × categoría mexicana. Se conservan campus y nombres originales. No se fusionan instituciones por coincidencias difusas. Las 471 claves incluyen cambios de denominación y categorías residuales; no representan 471 universidades diferentes.

La entidad es la de la escuela según la fuente, no residencia del sustentante. Algunas etiquetas pueden ser inconsistentes con el nombre del campus; no se corrigen por intuición. Agregados estatales excluyen filas sin entidad identificada.

## Indicadores

- Tasa = 100 × seleccionados / sustentantes de la misma fila y edición. Falta de conteo se conserva null. Se exige 0 ≤ seleccionados ≤ sustentantes.
- Wilson 95%: intervalo binomial descriptivo. No incorpora toda la heterogeneidad de población/reglas, no predice ingreso individual y no es calidad causal.
- Puntajes: media o mediana según encabezado. En 2005/2006 se publican medianas. El total histórico y componentes se preservan sin asumir aditividad o equivalencia entre años.
- Agregados nacionales: suma de filas publicadas. Si falta seleccionados en alguna fila, total y tasa son null. Media ponderada por sustentantes solo si todas las filas tienen medias disponibles; el redondeo original limita precisión. No se promedian medianas.
- Acumulados entre ediciones: participaciones, no personas únicas.

## Investigación por edición

Pearson y Spearman entre volumen y tasa usan filas completas de una edición. El denominador compartido puede inducir asociación. Se reporta n, sin interpretación causal o prueba de calidad.

Rankings: rango medio para empates y percentil 100(n−rango)/(n−1). El catálogo admite filtro de volumen mínimo. La movilidad longitudinal exige comparabilidad y composición controlada, pendiente.

Beta-binomial empírico Bayes: α y β por máxima verosimilitud marginal en log-parámetros; posterior Beta(k+α,n−k+β). Intervalos posteriores 95% condicionados a hiperparámetros estimados, sin incorporar toda su incertidumbre. Modelo exploratorio de intercambio institucional, sin efectos causales ni jerarquía geográfica completa.

Varianza de tasas de instituciones: total = entre entidades + dentro de entidades; ponderación por sustentantes, excluyendo entidades ausentes. Unidad puntos porcentuales²; no es dispersión individual de puntajes ni desigualdad de oportunidades individuales.

HHI/Gini/Lorenz describen volúmenes entre filas institucionales. Pareto identifica filas no dominadas simultáneamente en volumen y tasa, sin estimar eficiencia causal.

## Comparabilidad

Los bloques comparables académicos permanecen null. Tener 25 ediciones no acredita equivalencia de escalas, composición o reglas de selección. Las series de tasas y puntajes son observaciones independientes. No se publican predicciones académicas, resultados universidad–especialidad ni inferencias de origen–destino.

El archivo R mencionado en el prompt no fue proporcionado entre los adjuntos disponibles. No se inventan objetos ni se declara equivalencia R–Python no verificada.

## Incorporación académica 2024 y 2025

Fuentes oficiales: `2024/docs/2024-ENARx_Reporte-Academico.pdf` y `2025/docs/2025-ENARM_Reporte-Academico.pdf` bajo CIFRHS. Se incorporan 153 y 159 filas respectivamente. El nombre de archivo de 2024 contiene ENARx; se conserva exactamente, sin sustituirlo por una URL inferida.

Parser 2.1.0: anclaje por puntaje y límites de celdas impresas. Conserva conteos vacíos para no descartar filas con seleccionados ausentes. Une la fragmentación tipográfica C AMPUS en CAMPUS y conserva `name_original`. La tabla de 2024 publica tres sustentantes en ESC. MÉDICO - NAVAL SEMAR y deja seleccionados en blanco; 2025 publica cinco y cero, respectivamente. Se conserva esa diferencia.

Agregados 2024: 49,226 sustentantes; subtotal observado de seleccionados 18,180 en filas informadas, una fila sin dato. Total completo y tasa nacional permanecen null. En 2025: 44,911 sustentantes y 15,779 seleccionados de las filas publicadas. Estos agregados no se equiparan con plazas ofertadas ni con personas únicas entre ediciones.
