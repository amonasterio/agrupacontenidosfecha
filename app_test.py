#Recibe una lista de URL con la fecha de publicación.
#columnas: "Address","Status Code","Status","datePublished 1"
import pandas as pd
from datetime import datetime
import re
from urllib.parse import unquote, urlparse
from pathlib import  PurePosixPath

def formatFecha(fecha_in,formato):
    fecha_out=datetime.strptime(fecha_in, formato).date()
    return str(fecha_out)

def extractMonthYear(str_fecha):
    mes=str_fecha[:7]
    return mes

def extractDate(str_fecha):
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


def addFechaDataFrame2(df):
    df['fecha']=df.apply(lambda x: extractDate(x['datePublished 1']), 
                        axis=1)
    df['month']=df.apply(lambda x: extractMonthYear(x['fecha']), 
                        axis=1)
    return df   

#Añade la columna "fecha" don formato datetime.date
def addFechaDataFrame(df,formato):
    df['fecha']=df.apply(lambda x: formatFecha(x['datePublished 1'],formato), 
                        axis=1)
    df['month']=df.apply(lambda x: extractMonthYear(x['fecha']), 
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

f_entrada='lista2.csv'

df_entrada=pd.read_csv(f_entrada)
print(df_entrada)
#QUitamos los que son null

#df_filtro=df_entrada['Indexability'].isin(["Indexable"])
print(df_entrada[['Indexability']])
#df_entrada=df_entrada[df_filtro].reset_index(drop = True)

df_entrada=filtraResultados(df_entrada,'/articulos/')


format_fecha_in="%b %d, %Y"

#Añadimos la columna con la fecha en el formato que queremos
df_nuevo=addFechaDataFrame2(df_entrada)
print(df_nuevo)

#Agrupamos por mes
df_agrupado=df_nuevo.groupby(['month'],as_index=False).size()
print(df_agrupado)
deep_copy = df_entrada.copy()
#deep_copy.columns=["Address","date","month"]
df_nuevo = addPathDataFrame(deep_copy,2)
df_final=df_nuevo.groupby(['month', 'path']).size()
#df_final=df_nuevo.groupby(['month', 'path'],as_index=False).agg(total=('month','size'))
print(df_final)
df_final.to_csv("final_v.csv")



