# Este script recibe un fichero con datos exportados de Screaming Frog.
# Es imprescindible que contenga los campos "Address", "Indexability", "datePublished 1" (resultado de extraer los valores del campo datePublished), published_time (extraer los valores de article:published_time)
# Adicionalmente podemos añadir que se filtren únicamente aquellas URL ("Address") que contengan cierto texto (con el objetivo de eliminar URL que no sean posts)
# Finalmente devolverá el número de posts publicados en cada mes
# Además, se pueden agrupar los resultados por pahts (en el caso de que la URL contenga la categoría como path) indicando la profundidad del path que se quiera extraer

import streamlit as st
import pandas as pd
from datetime import datetime
import re
from urllib.parse import unquote, urlparse
from pathlib import  PurePosixPath

#extrae el año y el mes, de una fecha con formaro YYYY-MM-DD 
def extractYearMonth(str_fecha):
    mes=str_fecha[:7]
    return mes

# Convierte la fecha en formatos:
# YYYY-MM-DD.*
# %b(Abbreviated month name) DD, AAAA 
# Al formato YYYY-MM-DD
def convertDate(str_fecha):
    fecha=''
    regex=r'(\d\d\d\d-\d\d-\d\d).*'
    match = re.search(regex, str_fecha)
    if match:
        fecha=match.group(1)
    else:
        match=r'(\w\w\w \d\d, \d\d\d\d).*'
        if match:
            fecha=str(datetime.strptime(str_fecha, "%b %d, %Y").date())
    if len(fecha)>0:
        mes=fecha[5:7]
        dia=fecha[8:10]
        #si el mes es mayor que 12, ser trata del día
        if int(mes)>12:
            fecha=fecha[:5]+dia+"-"+mes
    return fecha




#Añade el campo "date" con el formato YYYY-MM-DD y el campo "month" con el formato YYYY-MM al dataFrame
def addFechaDataFrame(df):
    df['date'] = df.apply (lambda row: asignarFecha(row), axis=1)    
    df['month']=df.apply(lambda x: extractYearMonth(x['date']), 
                        axis=1)
    return df  

#Devuelve el nombre del path de la URL que esté al nivel que le pasemos
def getPathUrl(url,nivel):
    ruta=''
    paths = urlparse(url).path
    partes=PurePosixPath(unquote(paths)).parts
    if nivel < len(partes):
        ruta=partes[nivel]
    return ruta

#Añade el campo "path" al dataframe
def addPathDataFrame(df,nivel_cat):
    #Obtenemos el campo path a partir de la URL
    df['path']=df.apply(lambda x: getPathUrl(x['Address'],nivel_cat), 
                        axis=1)
    return df

#Filtramos resultados: datePublished no es null y que sean Indexable
def filtraResultados(df,url_contains=""):
    df_filtro=df['datePublished 1'].notnull()&df['Indexability'].isin(["Indexable"])
    if len(url_contains):
        df_filtro=df_filtro&df["Address"].str.contains(url_contains)
    df=df[df_filtro].reset_index(drop = True)
    return df

st.set_page_config(
   page_title="Obtener volumen de contenidos creados por mes",
   layout="wide"
)
st.title("Obtener volumen de contenidos creados por mes")
st.text('Este script recibe un fichero con datos exportados de Screaming Frog.\nEs imprescindible que contenga los campos "Address", "Indexability", "datePublished 1" (resultado de extraer los valores del campo datePublished), published_time (extraer los valores de article:published_time).\nSe filtrarán autimáticamente los resultados con valor Indexability=Indexable y datePublished 1 not null\nAdicionalmente podemos añadir que se filtres únicamente aquellas URL (Address) que contengan cierto texto (con el objetivo de eliminar URL que no sean posts)\nFinalmente devolverá el número de posts publicados en cada mes\nAdemás, se pueden agrupar los resultados por pahts (en el caso de que la URL contenga la categoría como path) indicando la profundidad del path que se quiera extraer')

#Obtiene la fecha de datePublished 1 o published_time 1 con el formato YYYY-MM-DD
def asignarFecha(row):
    fecha=''
    if row['datePublished 1']==None:
       fecha= convertDate(row['published_time 1'])
    else:
       fecha= convertDate(row['datePublished 1'])
    return fecha

uploaded_file = st.file_uploader("Fichero con el listado de URL", type='csv')
if uploaded_file is not None:
    df_entrada = pd.read_csv(uploaded_file)
    #QUitamos los que tienen fecha null y los de URL no indexables
    #Si además, debemos dejar los que contengan ciertos caracteres en las URL
    filtro_url=st.text_input("Introduzca el texto por el que debemos filtar las URL en caso de ser necesario","")
    df_entrada=filtraResultados(df_entrada,filtro_url)
    st.dataframe(df_entrada[["Address","datePublished 1", "published_time 1"]])
    #Si tras filtrar no tenemos un dataframe vacío continuamos
    if not df_entrada.empty:
        ##Añadimos la columna "date" con la fecha en el formato que queremos, y la columna "month" con el formato YYYY-MM 
        df_nuevo=addFechaDataFrame(df_entrada)
        #Creamos dataframe con datos agrupados por mes
        df_agrupado=df_nuevo.groupby(['month'],as_index=False).agg(total=('month','size'))
        st.dataframe(df_agrupado)
        st.download_button(
                label="Descargar como CSV",
                data=df_agrupado.to_csv(index=False).encode('utf-8'),
                file_name='agrupado_mes.csv',
                mime='text/csv'
                )
        nivel=st.slider('Profundidad del path que identifica la categoría cuyos datos quedemos agrupar', 1, 5, 1)
        if nivel > 0:
            deep_copy = df_nuevo.copy()
            df_nuevo = addPathDataFrame(deep_copy,nivel)
            #Calculamos los valores agrupados
            df_final=df_nuevo.groupby(['month', 'path'],as_index=False).agg(total=('month','size'))
            st.dataframe(df_final)
            st.download_button(
                label="Descargar como CSV",
                data=df_final.to_csv(index=False).encode('utf-8'),
                file_name='agrupado_mes_path.csv',
                mime='text/csv'
                )
    else:
        st.warning("No se ha obtenido ningún resultado con los filtros aplicados")