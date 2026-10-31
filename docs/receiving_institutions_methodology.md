# Metodología receptora · 2.0.0

## Grano y doble conteo

Hecho A: edición × fila institucional × especialidad × categoría × snapshot de oferta.
Hecho B: código oficial de oferta × sede × especialidad × entidad × categoría × snapshot.

Son niveles alternativos, no componentes sumables. La matriz se usa para totales y concentración institucional; el detalle de sedes para consultas territoriales. No sumar rondas ni atribuir movimientos de residentes a la distribución de plazas. El mapa utiliza entidad de sede una vez por código; la subsede conserva su propio campo. No se deduplican códigos distintos solo por compartir hospital/especialidad.

## Normalización

Identificadores por denominación normalizada (acentos, mayúsculas y separadores). Equivalencias explícitas de cuatro instituciones nacionales por su nombre y acrónimo. No se fusionan otros nombres históricos, grupos hospitalarios o niveles administrativos mediante similitud. Los cambios de institución observada entre ediciones pueden ser cambios de nomenclatura o composición.

## Indicadores

- Participación: plazas de fila / total del universo de referencia ×100. El perfil identifica el total nacional de la edición; otras vistas identifican su selección.
- HHI: suma de participaciones al cuadrado ×10,000. Si el universo está filtrado a una institución, ese HHI entre instituciones sería trivial; el perfil usa concentración de especialidades y el panel analítico señala el universo completo de la matriz.
- Gini y Lorenz: distribución entre filas publicadas, no personas. Top3/Top5: suma de participaciones de las mayores filas.
- Diversidad Shannon: −Σ p log(p). Número efectivo exp(Shannon). Separar diversidad del volumen de plazas. HHI interno sobre participaciones de especialidades.
- Especialización relativa: `(plazas_ij / plazas_i) / (plazas_j / total)`. No mide calidad o superioridad. La vista ordenada exige al menos diez plazas en celda y declara el universo nacional usado.
- Correspondencias: SVD de residuos estandarizados de tabla de contingencia. Se reporta inercia de ejes. Proximidad refleja composición, no flujos personales.
- Clustering exploratorio: Ward sobre raíz cuadrada de participaciones (perfiles Hellinger), k=3. Cien remuestreos de especialidades con semilla47; acuerdo de coasignación entre pares ≥0.80 para publicar grupos. No es validación longitudinal o externa; sensible al remuestreo y selección de k.

## Historia, predicción y redes

Tres snapshots permiten describir oferta publicada. No acreditan escala/etapa equivalente ni bastan para predicción temporal validada. No se presentan aumentos como nuevas plazas ocupadas, ni pronósticos como anuncios. No se infieren convenios, rotaciones o redes académicas de avales marginales. No hay red de origen–destino porque no existen datos conjuntos incorporados.

## Geografía

Límites estatales de referencia 2020, origen INEGI vía geoBoundaries. Se preservan metadatos, versión/commit, licencia y hash; simplificación tolerancia0.015° con topología preservada. Este mapa no verifica la localización precisa de hospitales. No hay puntos sin coordenadas verificadas. Plazas por habitante desactivado por ausencia de denominadores poblacionales compatibles.

Se eliminó exclusivamente el token redundante `(cid:141)` que sigue a la letra Í en la matriz de 2025 (por ejemplo SECRETARÍA y CLÍNICOS). Otros glifos sin mapear no se eliminan ni se adivinan. El PDF original permanece inalterado y con su hash.
