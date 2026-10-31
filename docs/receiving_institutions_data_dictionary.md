# Diccionario de instituciones receptoras · v2.0.0

| Campo | Definición |
|---|---|
| institution_id | Clave de fila institucional; solo cuatro equivalencias explícitas revisadas: SSA, IMSS, ISSSTE, PEMEX |
| institution_name | Denominación preservada tal como se publica, uniendo líneas |
| specialty_id / specialty | Especialidad normalizada y denominación oficial; no incluye una inferencia de selección individual |
| year | Edición ENARM, distinta de fecha de actualización del PDF |
| places | Número entero de plazas/oferta publicada; cero explícito conservado en matriz |
| place_type | `oferta_publicada_R1`; nunca sinónimo de asignada, aceptada, ocupada o incorporada |
| stage | `snapshot_matriz_publicada` o `snapshot_listado_sedes_publicado`; nunca se suman ambos niveles |
| population | Categoría mexicana, R1, entrada directa |
| code | Código CODUNI oficial del registro de oferta, no CLUES ni identificador de una persona |
| site_id / name | Clave documental de institución+nombre+entidad de sede; no enlace CLUES validado |
| state / state_original | Entidad de sede normalizada por equivalencias de estado y etiqueta original |
| subsite / substate | Subsede y entidad de subsede cuando se publican, especialmente IMSS; no se duplican plazas al representarlas |
| academic_endorsement | Aval académico publicado; no universidad de procedencia del sustentante |
| clues / latitude / longitude | Null: no vinculados mediante evidencia verificada; no se aproximan por nombre |
| source_id / page | Documento y página exacta |
| cutoff | Null cuando la tabla no identifica corte inequívoco; no se reemplaza con descarga |

Los documentos mezclan a veces instituciones nacionales, organismos, hospitales y otros actores como filas de un mismo cuadro. La aplicación analiza **filas publicadas**; no inventa una jerarquía para agruparlas o volverlas a sumar. Hospitales universitarios receptores y universidades de procedencia permanecen en conjuntos independientes.
