> Auditoría inicial de puntajes, v0.1. Para la ampliación v0.2 ver `academic_methodology.md` y `receiving_institutions_sources.md`. Las limitaciones de este documento corresponden al módulo inicial.

# Auditoría inicial · Specialty Intelligence

Fecha: 2026-10-31. Versión del parser: 1.0.0.

La carpeta del proyecto estaba vacía; no existía arquitectura ni ETL anterior que reutilizar. Se creó un módulo independiente con salida estática. No se encontró el script R mencionado en el prompt maestro y no se declara haberlo revisado.

## Fuentes

Punto de partida: https://cifrhs.salud.gob.mx/site1/enarm/reportes_academicos.html . La página consultada anuncia archivo 2001–2025. Se localizaron y descargaron cuatro documentos oficiales de máximos y mínimos por especialidad. El inventario exacto, URL, archivo local, descarga UTC, edición, hash y versión están en `source_inventory.csv` y `data/sources.json`.

| Edición | Filas mexicanas extraídas | Diseño | Orden de columnas |
|---|---:|---|---|
| 2022 | 27 | Dos tablas laterales | máximo, mínimo |
| 2023 | 26 | Dos tablas laterales, nombres multilínea | máximo, mínimo |
| 2024 | 27 | Dos tablas laterales | mínimo, máximo |
| 2025 | 27 | Una categoría por página | mínimo, máximo |

Se preservan ambas categorías en los PDF originales, pero se extrae exclusivamente la mexicana. No se mezclan extranjeros. Medicina Legal figura únicamente en la tabla incorporada de 2022; Medicina Paliativa en 2024–2025. Ausencia en una tabla no prueba cierre o apertura de una especialidad. El catálogo normaliza diacríticos para identificadores y conserva los nombres oficiales.

## Controles

Verificación SHA-256 antes de extracción; recorte de la tabla mexicana en 2022–2024; pares de celdas numéricas y bandas verticales para nombres multilínea; exclusión del pie de página; conteos exactos por documento; unicidad especialidad–año; rango 0 ≤ mínimo ≤ máximo ≤ 100; valores originales preservados. Las pruebas verifican puntos concretos de Medicina Interna y nombres multilínea contra las tablas consultadas. Estado: extracción controlada automáticamente, sin declarar revisión humana completa ni equivalencia psicométrica.

El dominio `www.cifrhs.salud.gob.mx` presentó un certificado que no correspondía al hostname. Se utilizó `cifrhs.salud.gob.mx` con verificación TLS normal; no se desactivó validación de certificados.

## Límites y pendientes

No se auditó exhaustivamente todo el archivo histórico. No se incorporaron aspirantes, seleccionados, plazas, medias, percentiles, sedes ni datos conjuntos universidad–especialidad. Hay documentos complementarios potenciales, que requieren auditoría propia. No se afirma que esas variables sean inexistentes en fuentes públicas.

La fecha de corte y ronda concreta no están identificadas en las tablas extraídas. El año de edición es distinto del año de publicación/actualización; el documento de 2025 se encontraba publicado en 2026. No se asigna una etiqueta de definitivo a una ronda no documentada. Resultados de 2026 no incorporados.

Comparabilidad histórica: pendiente para todas las filas. Se requieren convocatorias, ponderaciones, número de reactivos, criterios de selección y población comparable antes de asignar `comparable_group`. La escala numérica 0–100 es un control de dominio y visualización, no una prueba de equivalencia.
