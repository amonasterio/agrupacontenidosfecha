# agrupacontenidosfecha
Agrupa los contenidos publicados por fecha
Este script recibe un fichero con datos exportados de ScreamingFrog
Es imprescindible que contenga los campos "Address", "Indexability", "datePublished 1" (resultado de extraer los valores del campo datePublished)
Se filtrarán autimáticamente los resultados con valor Indexability=Indexable y datePublished 1 not null
Adicionalmente podemos añadir que se filtres únicamente aquellas URL ("Address") que contengan cierto texto (con el objetivo de eliminar URL que no sean posts)
Finalmente devolverá el número de posts publicados en cada mes
Además, se pueden agrupar los resultados por pahts (en el caso de que la URL contenga la categoría como path) indicando la profundidad del path que se quiera extraer
