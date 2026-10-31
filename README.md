# ENARM Watcher

**Observatorio Nacional del ENARM · by Doctor Data MX**

Una plataforma pública e interactiva para explorar los resultados históricos del ENARM y la oferta de formación médica especializada en México, a partir de documentos oficiales y métodos reproducibles.

**[Explorar el observatorio](https://doctordatamx.github.io/enarmwatcher/)** · [Fuentes y metodología](https://doctordatamx.github.io/enarmwatcher/#/methodology) · [Reportar un problema](https://github.com/doctordatamx/enarmwatcher/issues)

## ¿Qué es el ENARM?

El **Examen Nacional para Aspirantes a Residencias Médicas (ENARM)** evalúa conocimientos de medicina general mediante casos clínicos y forma parte del proceso de selección de quienes aspiran a realizar una especialidad médica en México. La convocatoria oficial lo sitúa como la primera etapa para ingresar al Sistema Nacional de Residencias Médicas. La selección en el examen no sustituye los requisitos y procedimientos de las instituciones de salud y educativas. Véase la [convocatoria oficial de la CIFRHS](https://cifrhs.salud.gob.mx/site1/enarm/2026/site/docs/50-ENARM_Convocatoria.pdf).

Sus resultados y la oferta de plazas permiten estudiar distintas dimensiones de la formación médica: la procedencia académica de los sustentantes, los umbrales publicados por especialidad y la distribución de oportunidades entre instituciones y sedes receptoras.

## ¿Por qué existe este repositorio?

Los documentos oficiales están distribuidos entre distintas ediciones, formatos y tablas. Para investigar su evolución es necesario organizarlos, revisar sus definiciones y conservar la relación entre cada observación y su fuente.

**ENARM Watcher busca facilitar ese trabajo y hacerlo verificable.** El repositorio reúne el código de la aplicación, documentos fuente, datos estructurados, procedimientos de extracción, controles de calidad y documentación metodológica. Esto permite consultar los resultados, reproducir los cálculos y revisar cómo se construyó cada indicador.

El proyecto puede apoyar a:

- **Aspirantes y comunidad médica**, que buscan contexto histórico sobre especialidades y oferta de formación.
- **Docentes e instituciones educativas**, que necesitan interpretar resultados con sus denominadores y limitaciones.
- **Investigadores**, que requieren datos trazables y procedimientos reproducibles.
- **Personas interesadas en salud pública y planificación**, que estudian la distribución de oportunidades de especialización.

## ¿Qué se puede consultar?

- **Panorama nacional:** participaciones, selección y resultados académicos por edición.
- **Universidades de procedencia:** perfiles históricos, tasas observadas, denominadores, intervalos y comparación entre instituciones.
- **Specialty Intelligence:** puntajes publicados, cobertura histórica y comparación de especialidades.
- **Instituciones receptoras y sedes:** oferta de plazas por institución, especialidad y ubicación documentada.
- **Atlas y herramientas de análisis:** visualizaciones, exploración de datos, ajustes estadísticos y evaluación de requisitos para modelos.
- **Descargas y reportes:** tablas, figuras y documentos para consulta y análisis, con referencias a sus fuentes.

## Cobertura incorporada

Los conjuntos tienen coberturas diferentes. La existencia de documentos de una nueva edición no significa que sus datos ya estén incorporados y validados.

| Conjunto | Ediciones incorporadas |
|---|---|
| Resultados académicos de categoría mexicana | 2001–2025 |
| Puntajes publicados por especialidad | 2022–2025 |
| Matrices de oferta de plazas R1 | 2023–2025 |
| Detalle de oferta por sede | 2025 |

Las tablas académicas contienen **2,528 filas**. Se conservan las denominaciones y entidades originales; las equivalencias históricas revisadas se documentan por separado. Un perfil universitario puede reunir distintas etiquetas del mismo origen institucional sin equiparar sus puntajes ni acreditar automáticamente comparabilidad de población.

La fuente de referencia es la **Comisión Interinstitucional para la Formación de Recursos Humanos para la Salud (CIFRHS), de la Secretaría de Salud**. Consulta el [portal oficial](https://cifrhs.salud.gob.mx/) y las referencias específicas dentro del observatorio.

## ¿Con qué frecuencia se actualiza?

El proyecto distingue **vigilar nuevas publicaciones** de **incorporar datos verificados**:

| Actividad | Frecuencia y funcionamiento |
|---|---|
| Revisión de fuentes oficiales | Monitor programado cada lunes a las 14:00 UTC, mediante [GitHub Actions](.github/workflows/update-data.yml). También puede ejecutarse manualmente. |
| Detección de cambios y documentos nuevos | El monitor compara las huellas SHA-256 de las fuentes registradas y busca enlaces nuevos en los índices oficiales. Produce un reporte y separa los documentos candidatos. |
| Incorporación al conjunto publicado | Cuando hay fuentes nuevas o corregidas y se completa la revisión de formato, población, etapa, extracción y controles. No tiene un plazo fijo ni ocurre automáticamente al detectar un enlace. |
| Publicación de cambios aprobados | Cada actualización enviada a `main` activa la reconstrucción, las pruebas y el despliegue del sitio en GitHub Pages. |

Por tanto, **la vigilancia es semanal y la actualización de datos depende de la publicación oficial y de su validación**. Una edición puede incorporarse por conjuntos: por ejemplo, disponer de resultados académicos antes de completar el detalle de sedes. El sitio identifica la cobertura y las fuentes de cada módulo.

## Cómo interpretar los resultados

- Una tasa observada describe seleccionados respecto de sustentantes de la misma fila, edición y categoría; **no es la probabilidad individual de ingreso**.
- Los resultados de una escuela **no demuestran la calidad causal de su formación**. El volumen y la composición de sus participantes importan.
- Los puntajes históricos pueden cambiar de escala, componentes o estadístico; no se equiparan medias y medianas de forma automática.
- La oferta de plazas publicada **no equivale a asignación u ocupación**. Los niveles de institución y sede no deben sumarse si representan la misma oferta.
- Los ajustes exploratorios no ajustados se identifican como tales y se distinguen de los análisis que exigen comparabilidad acreditada. Los pronósticos requieren suficiencia temporal y validación; no se publican por el solo hecho de disponer de más años.
- Los datos ausentes se conservan como faltantes. No se infieren cruces individuales entre universidad, especialidad y destino a partir de agregados independientes.

## Transparencia y reproducibilidad

Se preservan documentos originales, identificadores de fuente, huellas de integridad y controles de extracción. La reconstrucción de los datos aprobados puede ejecutarse desde los archivos del repositorio. La consulta pública funciona como un sitio estático, sin requerir un servidor de análisis.

Para profundizar:

- [Metodología académica](docs/academic_methodology.md) y [de especialidades](docs/specialty_methodology.md).
- [Fuentes](docs/receiving_institutions_sources.md), [cobertura](docs/receiving_institutions_coverage.md) y [metodología de instituciones receptoras](docs/receiving_institutions_methodology.md).
- [Desarrollo, reconstrucción y mantenimiento](docs/development.md).
- [Historial de cambios](CHANGELOG.md), [verificaciones](docs/verification.md) y [guía para contribuir](CONTRIBUTING.md).

## Participación y contacto

Las observaciones sobre errores de extracción, fuentes oficiales, equivalencias históricas o mejoras metodológicas pueden enviarse mediante los [issues del repositorio](https://github.com/doctordatamx/enarmwatcher/issues). Conviene incluir la edición, el documento y la página o fila correspondiente.

**Contacto:** [dr.avalos.mi.ds@gmail.com](mailto:dr.avalos.mi.ds@gmail.com).

ENARM Watcher es una **iniciativa independiente**. No representa ni está afiliada oficialmente a la CIFRHS o a la Secretaría de Salud, y no sustituye sus convocatorias, resultados ni procedimientos.

El código original se distribuye bajo [licencia MIT](LICENSE). Los documentos fuente y la cartografía conservan sus derechos y atribuciones respectivos.
