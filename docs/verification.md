# Verificación de la entrega

- Construcción estática: `npm run build`, TypeScript estricto y Vite.
- Pruebas: 27 aprobadas mediante `python -m unittest discover -s tests -v`. Fixtures estadísticos sintéticos aislados de la API pública; comprobaciones de hashes, conteos, valores oficiales seleccionados y reproducción del parser.
- HTTP local: respuesta 200 en `/enarmwatcher/`.
- Navegador: portada inspeccionada en 360×800, 390×844, 768×1024, 1024×768, 1440×900 y 1920×1080. Sin desbordamiento horizontal global en estas dimensiones. No equivale a una auditoría WCAG completa.
- Comparador: selección de cinco perfiles; una sexta casilla queda deshabilitada; vista heatmap funcional y tabla de valores exactos.
- Perfil de Medicina Interna: datos visibles, descarga HTML verificada y bloqueos de análisis longitudinal visibles.
- Temas claro y oscuro inspeccionados; ejes ECharts utilizan tema oscuro nativo cuando corresponde.
- Informe HTML: contiene resumen ejecutivo, figura SVG interna, tabla, cobertura, metodología, limitaciones, referencias y hashes. PDF se obtiene por impresión del navegador, no mediante un generador PDF independiente.

La compilación informa un bundle de gráficas mayor de 500 kB sin comprimir. Se importan solamente tipos y componentes ECharts usados; queda pendiente dividir por carga de ruta si crece el módulo. No se declara medición Lighthouse ni validación clínica, psicométrica o humana integral.

GitHub Pages no se ha ejecutado en remoto: la carpeta inicial no contenía `.git` ni remoto configurado. Se entrega workflow y artefacto `dist/` listos para vincular al repositorio objetivo.

La consulta de lectura `git ls-remote https://github.com/doctordatamx/enarmwatcher.git HEAD` respondió `Repository not found`. Esto no permite distinguir repositorio inexistente de uno privado sin acceso. GitHub CLI no está disponible en el entorno. Publicar requiere acceso autenticado al repositorio objetivo y habilitar Pages con GitHub Actions; no se modificó visibilidad ni configuración remota.

## Ampliación 0.2.0

- Reconstrucción completa `npm run data` completada desde los originales, sin fuentes en cuarentena. 2,216 registros académicos, 4,267 celdas de matrices y 2,544 códigos de oferta de sede.
- 44 pruebas de datos/estadística aprobadas; compilación TypeScript/Vite correcta.
- Portada completa revisada en los seis tamaños solicitados, sin desbordamiento horizontal global.
- Cambio de módulo y búsqueda universitaria comprobados; sexta universidad bloqueada tras seleccionar cinco.
- Atlas con 32 entidades; selección de Ciudad de México devuelve 3,703 plazas documentadas y filtra registros.
- Partial pooling beta-binomial visible en la interfaz con intervalos posteriores y límites.
- PDF de IMSS 2025 descargado, tres páginas renderizadas y revisadas; sin solapamiento o recorte de texto. Ejemplo en `output/pdf/imss-oferta-2025.pdf`.
- Monitor real: 36 documentos conocidos sin cambios; 91 enlaces candidatos no validados. Un cierre transitorio de conexión del emisor se resolvió al reintentar solo esa fuente.
- GitHub objetivo continúa devolviendo `Repository not found`; no hay despliegue remoto verificado.

- Validación del artefacto estático aprobada: subruta Pages, particiones JSON, mapa y manifest/iconos.
- Capturas actuales: `enarm-watcher-desktop.jpg` y `receiving-institutions-desktop.jpg`.

## Ampliación académica 0.2.1

- Reportes oficiales de 2024 y 2025 preservados con SHA-256 e incorporados con parser 2.1.0.
- Cobertura actual 2001–2025: 2,528 filas. Nuevas ediciones: 153 filas en 2024 y 159 en 2025.
- Fila naval de 2024 revisada visualmente en el PDF: tres sustentantes y seleccionados en blanco; se conserva null. En 2025 la fuente publica cinco sustentantes y cero seleccionados.
- Panorama de 2025 comprobado en navegador: 44,911 sustentantes, 15,779 seleccionados, tasa de filas agregadas 35.13%.
- Panorama de 2024 comprobado: 49,226 sustentantes; subtotal informado de 18,180 seleccionados y una fila ausente, sin total completo ni tasa nacional imputada.
- Pruebas específicas de valores oficiales, conteos y reproducción de ambos parsers.

- Verificación final de esta ampliación: 47 pruebas aprobadas; build y validación de subruta/particiones/manifest aprobados. Portada y selector universitario 2025 verificados en navegador.

## Tendencias y Predicciones 0.2.2

- `/predictions` y `/lab` muestran series actualizadas, incluidas las ediciones académicas 2024 y 2025.
- Cobertura derivada de los datos: académico 2001–2025, especialidades 2022–2025 y oferta institucional 2023–2025.
- Selectores de conjunto, entidad e indicador; exportación de observaciones y evaluación de elegibilidad.
- Los valores faltantes y la comparabilidad pendiente bloquean modelos aunque se alcance la longitud mínima; no se publican proyecciones sin validación suficiente.
- 52 pruebas aprobadas; compilación y comprobación estática de subruta y particiones aprobadas.
- Navegador: carga de las nuevas series, cambio de conjunto e indicador y ausencia de desbordamiento horizontal a 360 px.
- Evidencia visual: `trends-predictions-desktop.jpg`.

## Revisión acotada de comparabilidad

- Conteo agregado de sustentantes de categoría mexicana, bloque 2017–2025, revisado contra los nueve reportes oficiales preservados. Definición y límites en `trends-comparability-review.md`.
- Revisión vinculada a identificadores y SHA-256; no se extiende automáticamente a nuevos documentos o indicadores.
- Tendencia Theil–Sen calculada y verificada en navegador. Intervalo de confianza incluye cero y la interfaz lo comunica.
- Selector conserva acceso al historial 2001–2025 sin acreditar comparabilidad del bloque completo.
- Segmentación y pronóstico del bloque revisado siguen bloqueados por longitud; no se publica una proyección.
- 53 pruebas aprobadas; compilación y validación estática aprobadas. Captura: `trends-reviewed-block.jpg`.

## Gráficas de modelos y perfiles universitarios

- Tendencia habilitada: puntos observados y ajuste Theil–Sen dentro del periodo revisado; exportación PNG/SVG. La incertidumbre de pendiente no se representa como intervalo predictivo.
- Visualizaciones de segmentación y pronóstico condicionadas a modelos disponibles; no se dibujan proyecciones de modelos bloqueados.
- Sustituido el aviso fijo del perfil universitario por diagnóstico específico para las 471 claves normalizadas de procedencia.
- Gráficas de intervalos Wilson, denominadores y seleccionados, y diferencias aritméticas entre ediciones consecutivas. No se cruzan huecos ni se imputan valores faltantes.
- Rango y percentil limitados al universo completo de la edición seleccionada; sin interpretación de movilidad longitudinal o calidad causal.
- Panamericana 2025: diferencia respecto de 2024 de -9 sustentantes y -12.5510204 puntos porcentuales; 10 ediciones 2016–2025. La longitud habilita el requisito de segmentación, pero la comparabilidad institucional sigue pendiente.
- JSON de diagnóstico con registros y fuentes descargable por institución.
- 57 pruebas aprobadas; compilación y verificación estática aprobadas. Navegador: gráficas revisadas y sin desbordamiento horizontal a 360 px.
- Capturas: `university-analysis.jpg`, `trends-theil-sen-chart.jpg`.

## Ajustes exploratorios universitarios

- Habilitados Theil–Sen y regresión continua con bisagra sobre tasas publicadas, con los mínimos de seis y diez ediciones, valores completos, dominio 0–100 y años consecutivos.
- Separados de los modelos que exigen comparabilidad acreditada. Los cálculos exploratorios no modifican los grupos de comparabilidad ni habilitan pronósticos.
- En Panamericana se preserva explícitamente la diferencia de encabezados entre mexicanos civiles (2016) y categoría mexicana (2017–2025). Los ajustes no corrigen composición, reglas ni dependencia temporal.
- Modo estricto y modo exploratorio comprobados en navegador: el estricto conserva los tres bloqueos; el exploratorio muestra dos curvas y mantiene el pronóstico bloqueado con 10/14 ediciones.
- Pruebas de la separación entre modos, falta de mutación de comparabilidad, controles de huecos y valores ausentes.
- Captura: `university-models-enabled.jpg`.
