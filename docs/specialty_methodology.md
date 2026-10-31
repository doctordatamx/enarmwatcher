# Specialty Intelligence · metodología 1.0.0

## Principios

Separar dato oficial, indicador calculado, estimación, proyección, simulación y ausencia. No equiparar puntaje mínimo con probabilidad individual, correlación con causalidad ni plazas con calidad. No inferir cruces universidad–especialidad a partir de agregados marginales. No agrupar distintas categorías, rondas o escalas sin revisión documental.

## Elegibilidad

El motor exige datos presentes, años consecutivos sin duplicados, un mismo bloque comparable documentado y una sola población/etapa. Los mínimos de longitud son decisiones conservadoras del proyecto, no garantías universales. En la entrega actual los bloques son null y todas las series tienen ≤4 años: las estimaciones se bloquean.

## Tendencias y variabilidad

Theil–Sen: mediana de pendientes entre pares; IC de pendiente 95%, ≥6 ediciones comparables. SD muestral de mínimos temporales, diferencias anuales y dispersión por especialidad no son variabilidad de puntajes individuales. El rango máximo−mínimo es exclusivamente una medida intraedición entre extremos publicados.

Regresión segmentada: ≥10 años, modelo continuo con bisagra. Búsqueda de candidato con ≥3 observaciones a cada lado, minimización BIC penalizando cuatro parámetros (incluye búsqueda del corte); comparación con recta de dos parámetros. Ganancia >6 indica apoyo exploratorio, nunca causalidad. Es necesaria sensibilidad a longitudes de segmento y documentos de cambios de proceso antes de interpretar.

## Convergencia y perfiles

Panel balanceado de ≥5 especialidades, ≥6 años comunes comparables y mismo bloque entre especialidades. Sigma = SD entre mínimos de especialidades por año; brecha P90−P10; beta = pendiente entre nivel inicial y cambio anualizado. Reportar composición. Posible regresión a la media y selección de observados impiden conclusiones causales.

Clustering Ward en perfiles z estandarizados entre especialidades por año; varianza nula usa divisor 1. Máximo tres grupos; 100 remuestreos de años con reemplazo, semilla 47. Acuerdo de coasignación entre pares ≥0.80 para habilitar partición. Esta prueba exploratoria no garantiza estabilidad externa; no asigna etiquetas valorativas y requiere sensibilidad a k y remuestreo por bloques en series autocorrelacionadas antes de conclusiones sustantivas.

## Predicción

≥14 observaciones consecutivas comparables, entrenamiento inicial de 6 y ≥8 validaciones de un paso con origen móvil. Naive del último valor y Theil–Sen temporal. MAE y RMSE; selección exploratoria por MAE en las mismas ventanas, por lo que no es evaluación externa independiente. Intervalo predictivo empírico nominal 90% a partir del cuantil superior de errores absolutos fuera de muestra; los intervalos de cobertura retrospectiva usan solo errores anteriores. Cobertura prequential ≥75% para habilitar proyección. Pocos errores y selección de modelo limitan calibración; el nominal 90% no garantiza cobertura futura. Debe ampliarse validación anidada/calibración antes de uso decisional.

Umbrales limitados al dominio 0–100 al presentar intervalos. Presión de demanda exige valores compatibles por año; no se reconstruye desde agregados separados. Las proyecciones disponibles en código no se publican para las series actuales.

## Sensibilidad

Entradas manuales hipotéticas: A′/P′ = A(1+ΔA/100) / [P(1+ΔP/100)]. P >0, A ≥0. Umbral ajustado = umbral supuesto + desplazamiento manual. No se estima elasticidad, probabilidad individual, número de admitidos ni vínculo causal entre plazas y mínimo. La interfaz distingue simulación de predicción.

## Reportes

CSV de observaciones y matriz, PNG de gráficas, HTML autónomo con figura SVG interna, resumen, tabla, metodología, límites y referencias/hashes. PDF mediante impresión del HTML en navegador. Los informes actuales describen la cobertura y los análisis bloqueados, sin resultados de modelos inexistentes.
