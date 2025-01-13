<h1 style="text-align:center;">TECHNICAL DOCUMENT</h1>

<h2>Process of <span style="color:blue;">Detection and Delimitation of Agricultural Borders</span> using <span style="color:blue;">Geospatial Processing</span> and <span style="color:blue;">Deep Learning</span></h2>

<h3>Requirements and Compliance</h3>
<p>
This document describes the <span style="color:green;">technical process</span> that we follow to comply with the <span style="color:green;">requirements</span> specified in the <b>REF</b> document.
We include a <span style="color:green;">full detail</span> of each stage of the flow, the <span style="color:green;">scripts used</span>, the <span style="color:green;">technologies implemented</span> and the <span style="color:green;">deliverables generated</span>.
We ensure that the <span style="color:blue;">geospatial information</span> of the <span style="color:blue;">polygons</span> defined in the <b>original KML</b> file is preserved at all times.
</p>

<h3>Processing Flow</h3>

<h4 style="color:darkorange;">Satellite data download</h4>
<p>
At this stage we use the <b>sentinel_download_script.py</b> script to download <span style="color:blue;">key bands</span> from Sentinel-2 (<b>B8</b>, <b>B4</b>, <b>B3</b>, <b>B2</b>). These bands
were downloaded for the nine <span style="color:blue;">polygonal areas</span> defined in the <b>KML</b> file provided and cover three seasonal periods: <b>initial</b>, <b>refresh</b> and <b>finalize</b>.
</p>
<p>
To achieve this, we leveraged <b>Google Earth Engine</b> and <b>Geemap</b>, with a quality filter that limited downloads to images with less than <b>30% cloud cover</b>.
This allowed us to ensure that the downloaded bands were useful for further processing.
</p>
<p>
Additionally, the downloaded images were cropped to perfectly fit the <span style="color:blue;">polygons</span>, while maintaining <span style="color:blue;">geospatial attributes</span> such as <b>CRS</b> and <b>bounds</b>.
This step ensures <span style="color:green;">geospatial integrity</span> for later stages.
</p>
<p>
<b>Deliverables:</b> Band-wise <b>TIFF</b> files for each <span style="color:blue;">polygon</span> and seasonal period, with <span style="color:blue;">geospatial attributes</span> intact.
</p>

<h4 style="color:darkorange;">Sobel mask generation</h4>
<p>
To highlight the <span style="color:blue;">agricultural edges</span> visible in the downloaded images, we use the <b>generate_sobel_sentinel.py</b> script.
This script applies the <b>Sobel</b> operator tuned to detect edges, followed by <span style="color:green;">line enhancement</span> and <span style="color:green;">contrast</span> techniques
to improve the results. </p>
<p>
We implemented <b>OpenCV</b> and <b>Rasterio</b> for this processing, making sure to preserve the <span style="color:blue;">geospatial information</span> of the original bands in each generated mask. Each mask highlights the <span style="color:blue;">relevant edges</span>, making segmentation easier
in later stages.
</p>
<p>
<b>Deliverables:</b> <b>TIFF</b> masks with edges highlighted for each band, <span style="color:blue;">polygon</span>, and seasonal period.
</p>

<h4 style="color:darkorange;">Symmetry Check</h4>
<p>
Using the <b>verify_symmetry.py</b> script, we validate that the generated masks and the original bands have the same resolution,
spatial alignment, and <b>CRS</b>. This validation is critical to maintaining <span style="color:green;">consistency</span> throughout the pipeline.
</p>
<p>
We automatically compare the <b>dimensions</b>, <b>bounds</b>, and <b>CRS</b> between the images and the masks, generating <span style="color:green;">detailed alerts</span> if
<span style="color:red;">inconsistencies</span> are detected. This step ensures that the data is perfectly aligned before proceeding to segmentation.
</p>
<p>
<b>Deliverables:</b> Consistency report for each data set. If <span style="color:red;">inconsistencies</span> are detected, the problem is detailed.
</p>

<h4 style="color:darkorange;">Segmentation with SAM</h4>
<p>
The segmentation of the generated masks was performed with the script <b>sam_2_apply_colored.py</b>, using the <b>SAM (Segment Anything Model)</b> model.
This step allowed us to identify and delimit <span style="color:blue;">agricultural areas</span> in the masks.
</p>
<p>
In addition, we generated files in <b>GPKG</b> and <b>GeoJSON</b> formats, including attributes such as <b>acreage</b> and <b>polygon count</b>. The <b>GPKG</b> files were
integrated with <b>GIS</b> tools such as <b>ArcGIS</b>, ensuring compatibility with enterprise platforms.
</p>
<p>
We also produced <b>RGBA</b> masks for visual inspection. These masks allow manual validation of the results, ensuring that the
<span s<span style="color:green;">segmentation</span> is consistent with the <span style="color:blue;">detected edges</span>.
</p>
<p>
<b>Deliverables:</b> <b>GPKG</b> files with rich attributes, <b>GeoJSON</b> files for <b>GIS</b> integration, and <b>RGBA</b> masks for visual inspection.
</p>

<h3 style="color:darkblue;">Generated Metrics</h3>
<table style="border-collapse:collapse;width:100%;border:1px solid black;">
 <tr style="background-color:lightgray;">
 <th style="border:1px solid black;padding:5px;">METRICS</th>
 <th style="border:1px solid black;padding:5px;">DETAIL</th>
 </tr>
 <tr>
 <td style="border:1px solid black;padding:5px;">Area in acres</td>
 <td style="border:1px solid black;padding:5px;">Calculated for each polygon.</td>
 </tr>
 <tr>
 <td style="border:1px solid black;padding:5px;">Count polygons</td>
 <td style="border:1px solid black;padding:5px;">Included in GPKG and GeoJSON.</td>
 </tr>
 <tr>
 <td style="border:1px solid black;padding:5px;">Percentage of clouds</td>
 <td style="border:1px solid black;padding:5px;">Registered from Sentinel-2.</td>
 </tr>
 <tr>
 <td style="border:1px solid black;padding:5px;">Precision</td>
 <td style="border:1px solid black;padding:5px;">Consisting of 68% borders.</td>
 </tr>
 <tr>
 <td style="border:1px solid black;padding:5px;">Margin of error</td>
 <td style="border:1px solid black;padding:5px;">Less than 5% or 20 acres.</td>
</tr>
</table>

<h3 style="color:darkblue;">Preparation for Fine-Tuning</h3>
<p>
We designed a preliminary flow to perform <span style="color:blue;">Fine-Tuning</span> of the <b>SAM</b> model. This includes the creation of <b>directory structures</b> and
data examples in <b>COCO</b> format for manual annotations. Although this stage was not fully implemented, we left the environment
ready to train the model in future iterations.
</p>
<p>
<b>Deliverables:</b> Directory structure and JSON examples ready for manual annotations.
</p>

<h3 style="color:darkblue;">API Prototype</h3>
<p>
Finally, we developed a functional prototype using <b>FastAPI</b>, which allows access to the processed results through a <span style="color:green;">programmatic interface</span>.
This <span style="color:green;">API</span> is compatible with enterprise tools such as <b>ArcGIS</b> and <b>Microsoft Azure</b>.
</p>
<p>
<b>Deliverables:</b> Functional API prototype with documented endpoints for access to the processed data.
</p>

<h3 style="color:darkred;">Final Notes</h3>
<p>
This workflow meets the requirements of the <b>RFP/AFSC</b> document. Each stage was validated to ensure that <span style="color:blue;">geospatial information</span>
is preserved and that results are consistent with specifications. In addition, we left components ready for future iterations,
such as <span style="color:blue;">Fine-Tuning</span> of the model and full integration with <b>GIS</b> and enterprise systems.
</p>
