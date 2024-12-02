<h1 style="text-align:center;">DOCUMENTO TÉCNICO</h1>

<h2>Proceso de <span style="color:blue;">Detección y Delimitación de Bordes Agrícolas</span> mediante <span style="color:blue;">Procesamiento Geoespacial</span> y <span style="color:blue;">Aprendizaje Profundo</span></h2>

<h3>Requerimientos y Cumplimiento</h3>
<p>
Este documento describe el <span style="color:green;">proceso técnico</span> que seguimos para cumplir con los <span style="color:green;">requerimientos</span> especificados en el documento <b>REF</b>. 
Incluimos un <span style="color:green;">detalle completo</span> de cada etapa del flujo, los <span style="color:green;">scripts utilizados</span>, las <span style="color:green;">tecnologías implementadas</span> y los <span style="color:green;">entregables generados</span>. 
Aseguramos que en todo momento se preserve la <span style="color:blue;">información geoespacial</span> de los <span style="color:blue;">polígonos</span> definidos en el archivo <b>KML original</b>.
</p>

<h3>Flujo de Procesamiento</h3>

<h4 style="color:darkorange;">Descarga de datos satelitales</h4>
<p>
En esta etapa utilizamos el script <b>sentinel_download_script.py</b> para descargar <span style="color:blue;">bandas clave</span> de Sentinel-2 (<b>B8</b>, <b>B4</b>, <b>B3</b>, <b>B2</b>). Estas bandas 
se descargaron para las nueve <span style="color:blue;">áreas poligonales</span> definidas en el archivo <b>KML</b> proporcionado y abarcan tres períodos estacionales: <b>initial</b>, <b>refresh</b> y <b>finalize</b>.
</p>
<p>
Para lograrlo, aprovechamos <b>Google Earth Engine</b> y <b>Geemap</b>, con un filtro de calidad que limitó las descargas a imágenes con menos del <b>30% de nubes</b>. 
Esto nos permitió garantizar que las bandas descargadas fueran útiles para el procesamiento posterior.
</p>
<p>
Además, las imágenes descargadas se recortaron para ajustarse perfectamente a los <span style="color:blue;">polígonos</span>, manteniendo <span style="color:blue;">atributos geoespaciales</span> como <b>CRS</b> y <b>bounds</b>. 
Este paso nos asegura la <span style="color:green;">integridad geoespacial</span> para las etapas posteriores.
</p>
<p>
<b>Entregables:</b> Archivos <b>TIFF</b> por banda para cada <span style="color:blue;">polígono</span> y período estacional, con <span style="color:blue;">atributos geoespaciales</span> intactos.
</p>

<h4 style="color:darkorange;">Generación de máscaras mediante Sobel</h4>
<p>
Para resaltar los <span style="color:blue;">bordes agrícolas</span> visibles en las imágenes descargadas, usamos el script <b>generate_sobel_sentinel.py</b>. 
Este script aplica el operador <b>Sobel</b> ajustado para detectar bordes, seguido de técnicas de <span style="color:green;">realce de líneas</span> y <span style="color:green;">contraste</span> 
para mejorar los resultados.
</p>
<p>
Implementamos <b>OpenCV</b> y <b>Rasterio</b> para este procesamiento, asegurándonos de conservar la <span style="color:blue;">información geoespacial</span> de las 
bandas originales en cada máscara generada. Cada máscara destaca los <span style="color:blue;">bordes relevantes</span>, lo que facilita la segmentación 
en etapas posteriores.
</p>
<p>
<b>Entregables:</b> Máscaras <b>TIFF</b> con bordes resaltados para cada banda, <span style="color:blue;">polígono</span> y período estacional.
</p>

<h4 style="color:darkorange;">Verificación de simetría</h4>
<p>
Con el script <b>verificar_simetria.py</b>, validamos que las máscaras generadas y las bandas originales tengan la misma resolución, 
alineación espacial y <b>CRS</b>. Esta validación es crítica para mantener la <span style="color:green;">consistencia</span> en todo el flujo.
</p>
<p>
Comparamos automáticamente las <b>dimensiones</b>, <b>bounds</b> y <b>CRS</b> entre las imágenes y las máscaras, generando <span style="color:green;">alertas detalladas</span> si 
se detectan <span style="color:red;">inconsistencias</span>. Este paso asegura que los datos estén perfectamente alineados antes de proceder a la segmentación.
</p>
<p>
<b>Entregables:</b> Reporte de consistencia para cada conjunto de datos. En caso de detectar <span style="color:red;">inconsistencias</span>, se detalla el problema.
</p>

<h4 style="color:darkorange;">Segmentación con SAM</h4>
<p>
La segmentación de las máscaras generadas se realizó con el script <b>sam_2_apply_colored.py</b>, utilizando el modelo <b>SAM (Segment Anything Model)</b>. 
Este paso nos permitió identificar y delimitar <span style="color:blue;">áreas agrícolas</span> en las máscaras.
</p>
<p>
Además, generamos archivos en formato <b>GPKG</b> y <b>GeoJSON</b>, incluyendo atributos como <b>área en acres</b> y <b>conteo de polígonos</b>. Los archivos <b>GPKG</b> se 
integraron con herramientas <b>GIS</b> como <b>ArcGIS</b>, asegurando compatibilidad con plataformas empresariales.
</p>
<p>
También producimos máscaras <b>RGBA</b> para inspección visual. Estas máscaras permiten validar manualmente los resultados, asegurando que la 
<span style="color:green;">segmentación</span> sea consistente con los <span style="color:blue;">bordes detectados</span>.
</p>
<p>
<b>Entregables:</b> Archivos <b>GPKG</b> con atributos enriquecidos, archivos <b>GeoJSON</b> para integración <b>GIS</b>, y máscaras <b>RGBA</b> para inspección visual.
</p>

<h3 style="color:darkblue;">Métricas Generadas</h3>
<table style="border-collapse:collapse;width:100%;border:1px solid black;">
  <tr style="background-color:lightgray;">
    <th style="border:1px solid black;padding:5px;">MÉTRICA</th>
    <th style="border:1px solid black;padding:5px;">DETALLE</th>
  </tr>
  <tr>
    <td style="border:1px solid black;padding:5px;">Área en acres</td>
    <td style="border:1px solid black;padding:5px;">Calculada para cada polígono.</td>
  </tr>
  <tr>
    <td style="border:1px solid black;padding:5px;">Conteo de polígonos</td>
    <td style="border:1px solid black;padding:5px;">Incluido en los GPKG y GeoJSON.</td>
  </tr>
  <tr>
    <td style="border:1px solid black;padding:5px;">Porcentaje de nubes</td>
    <td style="border:1px solid black;padding:5px;">Registrado desde Sentinel-2.</td>
  </tr>
  <tr>
    <td style="border:1px solid black;padding:5px;">Precisión</td>
    <td style="border:1px solid black;padding:5px;">Consistente en 68% de bordes.</td>
  </tr>
  <tr>
    <td style="border:1px solid black;padding:5px;">Margen de error</td>
    <td style="border:1px solid black;padding:5px;">Menor al 5% o 20 acres.</td>
  </tr>
</table>

<h3 style="color:darkblue;">Preparación para Fine-Tuning</h3>
<p>
Diseñamos un flujo preliminar para realizar el <span style="color:blue;">Fine-Tuning</span> del modelo <b>SAM</b>. Esto incluye la creación de <b>estructuras de directorios</b> y 
ejemplos de datos en formato <b>COCO</b> para anotaciones manuales. Aunque esta etapa no se implementó completamente, dejamos listo el entorno 
para entrenar el modelo en futuras iteraciones.
</p>
<p>
<b>Entregables:</b> Estructura de directorios y ejemplos de JSON listos para anotaciones manuales.
</p>

<h3 style="color:darkblue;">Prototipo de API</h3>
<p>
Finalmente, desarrollamos un prototipo funcional utilizando <b>FastAPI</b>, que permite acceder a los resultados procesados mediante una <span style="color:green;">interfaz programática</span>. 
Esta <span style="color:green;">API</span> es compatible con herramientas empresariales como <b>ArcGIS</b> y <b>Microsoft Azure</b>.
</p>
<p>
<b>Entregables:</b> Prototipo de API funcional con endpoints documentados para acceso a los datos procesados.
</p>

<h3 style="color:darkred;">Notas Finales</h3>
<p>
Este flujo de trabajo cumple con los requerimientos del documento <b>RFP/AFSC</b>. Se validó cada etapa para garantizar que la <span style="color:blue;">información geoespacial</span> 
se preserve y que los resultados sean consistentes con las especificaciones. Además, dejamos componentes preparados para futuras iteraciones, 
como el <span style="color:blue;">Fine-Tuning</span> del modelo y la integración completa con <b>GIS</b> y sistemas empresariales.
</p>
