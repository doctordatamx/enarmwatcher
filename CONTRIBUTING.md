# Contribuir y corregir

Reportar módulo, edición, campo y URL oficial en las incidencias del repositorio `doctordatamx/enarmwatcher`, cuando esté disponible. No adjuntar folios ni datos personales de aspirantes.

Para cambiar datos: preservar archivo anterior, descargar candidato oficial con hash nuevo, revisar formato/etapa/población, añadir pruebas y reconstruir con `npm run data`. Una publicación que cambia no sustituye silenciosamente la captura aprobada. Registrar diferencias y documentar reglas de normalización.

Una equivalencia entre instituciones exige evidencia documental; coincidencias de nombres o ciudades no bastan. La comparabilidad de puntajes debe sustentarse en documentos de cada edición, sin equiparar medianas con medias. Los datos ausentes permanecen null.

Ejecutar `npm test` y `npm run build`. Las nuevas salidas deben funcionar bajo `/enarmwatcher/` y sin backend permanente. Datos sintéticos exclusivamente en pruebas. Conservar separadas universidad de procedencia, institución receptora, sede, subsede y aval académico.
