# Auditoría de fuentes receptoras · 2.0.0

Se inspeccionaron las páginas oficiales por edición y sus enlaces complementarios. Los reportes académicos de universidades no se utilizaron para inferir destino de residentes.

| Edición | Fuente oficial | Desagregación incorporada | Total conciliado |
|---|---|---|---:|
| 2023 | `2023/docs/2023-ENARM-Plaza-Especialidad-Mex.pdf` | Fila institucional × 26 especialidades | 18,167 |
| 2024 | `2024/docs/2024-ENARM-Plazas-mex.pdf` | Fila institucional × 27 especialidades | 18,207 |
| 2025 | `2025/plazas/Plazas_sicco_plazas-mex-directa.pdf` | Fila institucional × 27 especialidades | 18,515 |
| 2025 | Listados `...-salud.pdf`, `...-imss.pdf`, `...-issste.pdf`, `...-pemex.pdf`, `...-total.pdf` | Código de oferta × sede × especialidad × entidad × aval | 18,515 |

Base: `https://cifrhs.salud.gob.mx/site1/enarm/`. URLs completas, hashes, emisor, descarga, tipo, estado y parser están en `platform_source_inventory.csv`, `data/platform_validation.json` y la interfaz Fuentes. Los originales se conservan en `data/raw/platform/`.

Los listados se enlazan desde la sección de primera vuelta de 2025, pero se describen conservadoramente como snapshot del documento publicado: las URL pueden haber sido reemplazadas por el emisor y la tabla no identifica inequívocamente fecha de corte. No se declara que sea oferta inicial histórica inmutable ni asignación final.

Se localizaron otras vueltas y categoría extranjera en las páginas. Se registraron sus enlaces en `data/discovery.json`, pero no se suman ni se mezclan. El archivo de otras instituciones lleva sufijo `total`; pese al nombre, su contenido es un listado con campo institución de otras receptoras, no el total nacional para sumar otra vez.

## Controles de conciliación

- Todas las filas de las matrices coinciden con su total horizontal.
- Todas las especialidades coinciden con el total de columna.
- Total nacional por documento comprobado.
- Los 2,544 códigos de oferta de sedes son únicos entre archivos.
- Por institución principal: SSA 5,325; IMSS 10,000; ISSSTE 1,903; PEMEX 320. El resto del listado suma 967.
- Detalle por especialidad de sedes y matriz nacional 2025 concilian exactamente.

Estas verificaciones controlan extracción y doble conteo, no garantizan equivalencia entre snapshots de distintas ediciones ni validez de dimensiones no publicadas.
