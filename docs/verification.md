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
