# Diccionario de datos · v1.0.0

Unidad: especialidad × edición × población × etapa documental.

| Campo | Definición / unidad / regla |
|---|---|
| specialty_id | Identificador normalizado del nombre, preservando denominación oficial por separado |
| official_name | Texto de la tabla oficial, con saltos de línea unidos |
| year | Año de edición, no fecha de publicación |
| minimum / maximum | Puntajes publicados; puntos, no probabilidades |
| original_values | Celdas originales en orden de aparición, sin inversión destructiva |
| population | mexicana, exclusivamente en esta extracción |
| stage | Documento de seleccionados publicado; ronda no especificada en tabla |
| source_id / page | Fuente y página en PDF |
| applicants / places / selected / mean | Null: no incorporados; no imputados |
| demand_comparable | False hasta verificar ámbito y definición conjunta de aspirantes/plazas |
| comparable_group | Null hasta revisión documental; no derivado de rango numérico |
| validation | extracted_checked: controles automáticos de extracción superados |
| comparability | pending_review; no equivalencia estadística declarada |

Derivados: rango = maximum − minimum, puntos dentro de una fila. Presión = applicants / places, aspirantes/plaza, solo con ambos valores, places > 0 y `demand_comparable=True`. La compatibilidad debe documentar misma especialidad, edición, población y corte; la bandera no la sustituye.

Cada indicador se vincula a las fuentes de sus filas y a la versión metodológica 1.0.0. Numerador y denominador no aplican a mínimo, máximo, rango y pendiente. Para presión son aspirantes y plazas respectivamente. Consultar `specialty_methodology.md` y diccionario visible por perfil para fórmulas, restricciones e interpretación.
