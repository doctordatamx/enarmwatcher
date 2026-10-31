# Desarrollo y mantenimiento de ENARM Watcher

Esta guía reúne las instrucciones técnicas del proyecto. Para conocer su propósito, consulta el [README principal](../README.md).

## Ejecutar

```powershell
npm ci
npm run dev
```

Abrir `http://127.0.0.1:5173/enarmwatcher/`.

## Reconstruir y verificar

Python 3.12+ y Node 22+.

```powershell
python -m pip install -r requirements.txt
npm ci
npm run data
npm test
npm run build
```

`npm run data` extrae DOC con word-extractor, DOCX con XML y PDF con pdfplumber; valida, concilia y genera análisis y API JSON por módulo, DuckDB y Parquet Zstandard. Reconstruye desde originales sin red. El sitio no necesita backend ni Python durante la consulta.

Arquitectura: `pipeline/` → `data/normalized/` + `data/warehouse/` → `public/data/` → React/TypeScript/Vite/ECharts → `dist/`. La carga se separa por módulo.

## Actualizar fuentes

`python -m pipeline.discover` descarga fuentes sin sobrescribir capturas aprobadas. `python -m pipeline.check_updates` compara hashes y descubre enlaces, con reporte de diferencias y candidatos separados. El monitor semanal está en `.github/workflows/update-data.yml`.

Una nueva edición requiere revisar fuente, formato, corte, población y etapa; adaptar parser y controles, añadir pruebas y reconstruir. Los candidatos de formato o metodología desconocidos no se promueven silenciosamente. No se procesan folios de aspirantes.

## Despliegue

La aplicación está publicada en [GitHub Pages](https://doctordatamx.github.io/enarmwatcher/).

Los cambios enviados a `main` activan `.github/workflows/deploy.yml`: instalación de dependencias, reconstrucción de datos, pruebas, compilación, comprobación de la subruta estática y despliegue de `dist/`. `quality-check.yml` ejecuta los controles de los pull requests.

Las nuevas fuentes detectadas por el monitor semanal no se incorporan al sitio sin revisión. El flujo de publicación reconstruye los archivos ya aprobados; no convierte automáticamente los documentos candidatos en datos publicados.

Las equivalencias históricas de procedencia se registran explícitamente en `data/university_identity_links.json`, vinculadas a años e identificadores de fuente y SHA-256. No se realiza una unión difusa de escuelas o campus. Consulta la [revisión de Panamericana](panamericana-history-review.md).
