#!/usr/bin/env python
import datetime
import psycopg2
from psycopg2 import connect

# request url
import time
try:
    import cookielib
except:
    import http.cookiejar
    cookielib = http.cookiejar

import sys
from io import BytesIO
import json
import os
import zipfile
from sqlalchemy import create_engine
import psycopg2.extras as extras
import pandas as pd
from pathlib import Path as path
from sentinelsat import SentinelAPI
from senfarming_util import generate_all_bands , get_immediate_subdirectories \
                            , decimal, isclose1,sampleRaster,get_tallinn_polygon_ge
import shutil
from geotiff import GeoTiff
import rasterio
import numpy as np
from osgeo import gdal,ogr,osr
from rasterio.crs import CRS
from rasterio.windows import Window
import struct


#modificamos webdriver
# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))
def listardatosdataframe(df):
    print(list(df.columns))

def crearTablaSentinel(df,table):
    #conexion a la bbdd
    engine = create_engine('postgresql+psycopg2://'+ srvconf['PYSRV_DATABASE_USER'] 
                           + ':' + srvconf['PYSRV_DATABASE_PASSWORD']
                           + '@' + srvconf['PYSRV_DATABASE_HOST_POSTGRESQL']
                           + ':' + srvconf['PYSRV_DATABASE_PORT']
                           + '/' + srvconf['PYSRV_DATABASE_NAME'] )
    df.to_sql(table,engine, schema='public')

def guardardatosbusquedaSentinel(df,table,idpeticion):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    step = 10
    cursor = conn.cursor()
    #df.to_sql('tbl_lista_archivos_sentinel',engine,if_exists='append',index='true',
    #          index_label='sequence', method='multi')
    # adding column with constant value
    df['reference'] = pd.Series([idpeticion for x in range(len(df.index))])
    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))
    #delete old items for the same refference
    deletequery = "delete from %s where reference = '%s'" % ( table,idpeticion)
    cursor.execute(deletequery) 
    # SQL query to execute 
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
 
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
    return 1
def borrardatosbusquedaSentinel(table,idpeticion):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    step = 10
    cursor = conn.cursor()
   


    try:
        deletequery = "delete from %s where reference = '%s'" % ( table,idpeticion)
        cursor.execute(deletequery) 
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
    return 1

def guardardatosbusquedaSentinel(df,table,idpeticion,userid, groupid):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    step = 10
    cursor = conn.cursor()
    #df.to_sql('tbl_lista_archivos_sentinel',engine,if_exists='append',index='true',
    #          index_label='sequence', method='multi')
    # adding column with constant value
    for x in range(len(df.index)):
        df.loc[df.index[x],'reference'] = idpeticion
        df.loc[df.index[x],'userid'] = idpeticion
        df.loc[df.index[x],'groupid'] = idpeticion
    
    #df['reference'] = pd.Series([idpeticion for x in range(len(df.index))])
    #df['userid'] = pd.Series([userid for x in range(len(df.index))])
    #df['groupid'] = pd.Series([groupid for x in range(len(df.index))])
    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))
    
    # SQL query to execute sentinelhub
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
 
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
    return 1


  
def descargarzip(uuid):
    #eliminamos todos los archivos antes de descargar
    print('En descargarzip entrada:' + uuid )
    source = srvconf['PYSRV_SRC_ROOT_DATA_DIR' ]
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    zipfiles = [f for f in os.listdir(source) if '.zip' in f.lower()]

    #for f in zipfiles:
    #    old_path = source +'/' + f
    #    path(old_path).remove()
    #desargamos el nuevo zip
    hub = SentinelAPI(srvconf['PYSRV_USERNAME'], srvconf['PYSRV_PASSWORD'], "https://scihub.copernicus.eu/dhus")
    info = hub.get_product_odata(uuid)

    print(info)
    
    is_online = info['Online']

    if is_online:
        print(f'Product {uuid} is online. Starting download.')
        dicthub = hub.download(uuid,source)
    else:
        print(f'Product {uuid} is not online.')
        dicthub = hub.trigger_offline_retrieval(uuid)



    #zip file with folder
    zipfilestr = "/"
    basename = "1"
    for file in os.listdir(source):
        if os.path.isfile(os.path.join(source, file)):
            zipfilestr = source + "/" +  file
            basename =  os.path.basename( zipfilestr)
            
            if basename != 1:
                if os.path.isdir(data_safe + "/" + basename[:-3] + "SAFE") :
                    print('Already extracted')
                else:
                    zipf = zipfile.ZipFile(zipfilestr)
                    zipf.extractall(data_safe)
                    print("Extracting Done")
    return dicthub

def descomprimirzip(uuid):
    print('En descomprimirzip entrada:' + uuid )
    #eliminamos todos los archivos antes de descargar

    source = srvconf['PYSRV_SRC_ROOT_DATA_DIR' ]
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    count = 0
    for path in os.listdir(source):
        # check if current path is a file
        if os.path.isfile(os.path.join(source, path)):
            count += 1
    print('File count:', count)
    filename = uuid + '.zip'
    print('list files')
    for basename in os.listdir(source):
        if (basename ==  filename):
            print(basename)
            zipfilestr = source + "/" +  basename
            print('Fichero a extraer: ' + basename)
            if os.path.isdir(data_safe + "/" + basename[:-3] + "SAFE") :
                print('Already extracted')
            else:
                zipf = zipfile.ZipFile(zipfilestr)
                zipf.extractall(data_safe)
                print("Extracting Done")
    print('end list files')

    return 1


def generateallbands(uuid):
    print('En generateallbands entrada:' + uuid )
    basename = ""
    productName = ""
    source = srvconf['PYSRV_SRC_ROOT_DATA_DIR' ]
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    src_root_data_dir_processs_gdal = srvconf['PYSRV_SRC_ROOT_DATA_DIR_PROCESS_GDAL' ]
    count = 0
    for path in os.listdir(source):
        # check if current path is a file
        if os.path.isfile(os.path.join(source, path)):
            count += 1
    print('File count:', count)
    filename = uuid + '.zip'
    print('list files')
    for basename in os.listdir(source):
        if (basename ==  filename):
            zipfilestr = source + "/" +  basename
            productName = os.path.basename(zipfilestr)[:-4]
            
    
            #valores iniciales para descargas
            bands = ["B02", "B03", "B04","B05","B06","B07", "B08", "B8A", "B11", "B12"]
            band_resolutions = ["10m", "10m", "10m","20m","20m","20m","10m", "20m", "20m", "20m"]
            resolutions = ["R10m", "R10m", "R10m","R20m","R20m","R20m","R10m", "R20m", "R20m", "R20m"]
            bands_and_resolutions = list(zip(bands, resolutions,band_resolutions))
            
            print('Procesando el producto:' + productName)
            #variables para los directorios
            directoryName = data_safe +"/" + basename[:-3] + "SAFE/GRANULE"

            
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED"
            subDirectorys = get_immediate_subdirectories(directoryName)
            results = []
            for granule in subDirectorys:
                unprocessedBandPath = data_safe +"/"+ productName + ".SAFE/GRANULE/" + granule + "/" + "IMG_DATA/"
                #print(unprocessedBandPath)
                results.append(generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory,bands_and_resolutions))
        else:
            print( 'No se encontraron archivos')

    return productName
    
def eliminarresultadosintermedios():
    #Eliminamos resultados intermedios
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    shutil.rmtree(data_safe)
    #creamos el directorio de nuevo
    os.mkdir(data_safe)
    return 1
def moverdatosaproc( ref):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()
    step = 10
    try:
        df = pd.DataFrame()
        #Leemos los datos 
        
        query = "SELECT fnc_copy_unique_values('%s')" % (ref)
        print('Moviendo datos : ' + query)
        cursor.execute(query) 
        conn.commit
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    
    cursor.close()
    conn.close()
    return df

def listarDatosSentinel( table,idpeticion):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()
    step = 10
    try:
        df = pd.DataFrame()
        #Leemos los datos 
        query = "SELECT * FROM %s WHERE REFERENCE = '%s'" % (table,idpeticion)
        cursor.execute(query) 
        rowd = cursor.fetchall()
        step = 20
        if rowd == None:
            step = 30
            print("Dato no encontrado ")
        else:
            step = 40
            df = pd.DataFrame(rowd)
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    
    cursor.close()
    conn.close()
    return df
def listarDatosSentinelNew( table,idpeticion,userid):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()
    step = 10
    try:
        df = pd.DataFrame()
        #Leemos los datos 
        query = "SELECT * FROM %s WHERE REFERENCE = '%s' and userid = '%s' " % (table,idpeticion,userid)
        cursor.execute(query) 
        rowd = cursor.fetchall()
        step = 20
        if rowd == None:
            step = 30
            print("Dato no encontrado ")
        else:
            step = 40
            df = pd.DataFrame(rowd)
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    
    cursor.close()
    conn.close()
    return df
def CSVDatosSentinel():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()
    step = 10
    try:
        df = pd.DataFrame()
        #Leemos los datos 
        query = "select  row_number() over () as id, t.id as datoid , substring(sent.band,2,2) as band,  sent.longitude, \
                sent.latitude, t.materiaorganica as read, avg(sent.relectance) as map, avg(sent.relectance)/10000 as map_rescaled \
                from tbl_datos_jc t \
                join tbl_coord_tiff_values sent on sent.fuente = 'jc' and  sent.internalid = t.id \
                where camp like '%vid%' \
                group by t.id , sent.band,  sent.longitude , sent.latitude, t.materiaorganica \
                order by t.id "
        cursor.execute(query) 
        rowd = cursor.fetchall()
        step = 20
        if rowd == None:
            step = 30
            print("Dato no encontrado ")
        else:
            step = 40
            df = pd.DataFrame(rowd)
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    
    cursor.close()
    conn.close()
    return df

def obtenerPuntos(ref, filtro):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    step = 5
    if ( ref == 'test'):
        print("leemos los datos de test")
        points = [
        [-4.27254326,	42.08352779],
        [-4.27217104,	42.08376982] ,
        [-4.2727401,	42.08221765] ,
        [-4.27296015,	42.08213388] ,
        [-4.27268713,	42.08182134],
        [-4.21574342,	42.44570320],
        [-3.68352864,   42.295119665]
        ]
    elif (ref == 'jcyl'):
        print("leemos los datos de la junta de castilla y leon, tabla tbl_datos_carga_JCyL")
        #En este caso hay que convertir las coordenadas
        #En este caso las coordenadas se usam tal cual vienen
        step = 10
        try:
            df = pd.DataFrame()
            table = 'tbl_datos_carga_JCyL'
            #Leemos los datos 
            query = ''
            if len(filtro) > 8:
                query = "SELECT coor_x_etr , coor_y_etr, objectid FROM %s where %s " % (table,filtro)
            else:
                query = "SELECT coor_x_etr , coor_y_etr, objectid FROM %s where origen = 'Ines' " % (table)
            cursor.execute(query) 
            rowd = cursor.fetchall()
            for row in rowd:
                coor_x_etr , coor_y_etr , objectid = row
                step = 20
                #points.append([coor_x_etr, coor_y_etr,objectid])
            
                #convertimos coordenadas 
                pointX = coor_x_etr
                pointY = coor_y_etr

                # Spatial Reference System
                inputEPSG = 3857
                outputEPSG = 4326

                # create a geometry from coordinates
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(pointX, pointY)

                # create coordinate transformation
                inSpatialRef = osr.SpatialReference()
                inSpatialRef.ImportFromEPSG(inputEPSG)

                outSpatialRef = osr.SpatialReference()
                outSpatialRef.ImportFromEPSG(outputEPSG)

                coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

                # transform point
                point.Transform(coordTransform)

                # print point in EPSG 4326
                points.append([point.GetX(), point.GetY()])
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step)    
    elif (ref == 'jc'):
        print("leemos los datos de Juan Carlos: tbl_datos_jc")
        #En este caso las coordenadas se usam tal cual vienen
        step = 80
        try:
            df = pd.DataFrame()
            table = 'tbl_datos_jc'
            #Leemos los datos 
            if len(filtro) > 8:
                query = "SELECT longuitud, latitud , id FROM %s where %s " % (table,filtro)
            else:
                query = "SELECT longuitud, latitud , id FROM %s " % (table)
            cursor.execute(query) 
            rowd = cursor.fetchall() 
            for row in rowd:
                longuitud , latitud , id = row
                step = 110
                points.append([longuitud, latitud])
            #print(points)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    elif (ref == 'lucas'):
        print("leemos los datos de lucas: tbl_coord_lucasdb")
        #En este caso las coordenadas se usam tal cual vienen
        step = 100
        try:
            df = pd.DataFrame()
            table = 'tbl_coord_lucasdb'
            #Leemos los datos 
            if len(filtro) > 8:
                query = "select x_wgs84 as longuitud, y_wgs84 as  latitud , point_id as id from  %s where %s " % (table,filtro)
            else:
                query = "select x_wgs84 as longuitud, y_wgs84 as  latitud , point_id as id  FROM %s " % (table)
            cursor.execute(query) 
            rowd = cursor.fetchall() 
            for row in rowd:
                longuitud , latitud , id = row
                step = 120
                points.append([longuitud, latitud])
            #print(points)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('Matriz de puntos')
    #print(points)
    return points
   
def obtenerPuntosLucas(filtro):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        df = pd.DataFrame()
        #Leemos los datos 
        if len(filtro) > 8:
            query = ( 'select a.th_long as longuitud, a.th_lat as  latitud , a.point_id as id , a.survey_date as fecha ' 
                     ' from tbl_coord_lucasdb_2018 a '
                     ' join public.datoslucasdb b on cast(b.point_id AS INTEGER) = cast(a.point_id AS INTEGER) '
                     ' where '  + filtro 
                    )
        else:
            query = ( 'select a.th_long as longuitud, a.th_lat as  latitud , a.point_id as id , a.survey_date as fecha ' 
                     ' from tbl_coord_lucasdb_2018 a '
                     ' join public.datoslucasdb b on cast(b.point_id AS INTEGER) = cast(a.point_id AS INTEGER) '
                    )
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , fecha ,id = row
            step = 120
            points.append([longuitud, latitud,fecha])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosLucas: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('Matriz de puntos')
    #print(points)
    return points
def obtenerPuntosLucasPoligono2015(minmax, fecha):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        
        #Leemos los datos 
        wherecond = ' where a.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and a.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        wherecond += ' and a.survey_date = \'' + fecha + '\' '
        wherecond += ' order by a.survey_date  desc '
        query = ( 'select a.th_long as longuitud, a.th_lat as  latitud , a.point_id as id , a.survey_date as fecha ' 
                    ' from tbl_datos_lucas_eu_2015_20200225 a '
                    ' join tbl_datos_lucas_Topsoil_2015_20200323 b on  b.point_id = a.point_id ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, fecha  = row
            step = 120
            points.append([longuitud, latitud,id ,fecha])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosLucasPoligono: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('Matriz de puntos')
    #print(points)
    return points

def contarPuntosLucasPoligono2015(minmax):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    num = -1
    resultados=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_datos_lucas_eu_2015_20200225")
    print(minmax)
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        step = 110
        wherecond = ' where a.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and a.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        wherecond += ' and a.survey_date >= \'01/01/2016\''
        wherecond += ' group by a.survey_date' 
        query = ( 'select a.survey_date as fecha , count(*) as num ' 
                    ' from tbl_datos_lucas_eu_2015_20200225 a '
                    ' join tbl_datos_lucas_Topsoil_2015_20200323 b  on  b.point_id = a.point_id ' + wherecond
        )
        step = 120
        print(query)
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            fecha ,num = row
            step = 120
            resultados.append([fecha, num])

    except (Exception, psycopg2.Error) as error:
        print("contarPuntosLucasPoligono: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de fechas
    #print('Matriz de fechas')
    #print(resultados)
    return resultados

def obtenerPuntosLucasPoligono(minmax, fecha):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        '''
        wherecond += ' and a.point_id not in (  '
        wherecond += ' 30602044,30622070,30662054,30662118,30682052,30702108,30742058,30742170,30782134,30802052,30842132,30882130,30902056,30902242,30962066,30962290, '
        wherecond += ' 31002188,31022060,31082232,31122298,31162082,31182188,31202176,31282278,31362128,31362156,31362264,31422138,31422166,31422234,31422336,31482178, '
        wherecond += ' 31482262,31522142,31522178,31542128,31542174,31542242,31582170,31602108,31602144,31602148,31602166,31602256,31642144,31662172,31682260,31702250, '
        wherecond += ' 31702280,31722134,31722156,31742108,31742212,31742280,31762164,31762214,31782138,31782246,31802196,31802268,31802344,31822338,31842178,31842222, '
        wherecond += ' 31862228,31862260,31882258,31962306,32022340,32062352 '
        wherecond += ')'
        '''
        #Leemos los datos 
        wherecond = ' where a.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and a.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        wherecond += ' and a.survey_date = \'' + fecha + '\' '
        wherecond += ' order by a.survey_date  desc '
        query = ( 'select a.th_long as longuitud, a.th_lat as  latitud , a.point_id as id , a.survey_date as fecha ' 
                    ' from tbl_coord_lucasdb_2018 a '
                    ' join public.datoslucasdb b on cast(b.point_id AS INTEGER) = cast(a.point_id AS INTEGER) ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, fecha  = row
            step = 120
            points.append([longuitud, latitud,id ,fecha])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosLucasPoligono: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('Matriz de puntos')
    #print(points)
    return points

def contarPuntosLucasPoligono(minmax):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    num = -1
    resultados=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    print(minmax)
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        step = 110
        wherecond = ' where a.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and a.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        wherecond += ' group by a.survey_date' 
        query = ( 'select a.survey_date as fecha , count(*) as num ' 
                    ' from tbl_coord_lucasdb_2018 a '
                    ' join public.datoslucasdb b on cast(b.point_id AS INTEGER) = cast(a.point_id AS INTEGER) ' + wherecond
        )
        step = 120
        print(query)
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            fecha ,num = row
            step = 120
            resultados.append([fecha, num])

    except (Exception, psycopg2.Error) as error:
        print("contarPuntosLucasPoligono: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de fechas
    #print('Matriz de fechas')
    #print(resultados)
    return resultados

def obtenerPuntosPath(reference):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where path like \'%response.tiff\' and reference = \'' + reference + '\' '
        query = (   'select b.th_long as longuitud, b.th_lat as  latitud , b.point_id as id , a.path as path '
                    'FROM public.tbl_files_tiff_for_coord  a  '
                    'join public.tbl_coord_lucasdb_2018 b on b.point_id = a.id ' + wherecond
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, path  = row
            step = 120
            points.append([longuitud, latitud,id ,path])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosPath: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('obtenerPuntosPath :Matriz de puntos')
    #print(points)
    return points


def obtenerPuntosLucasPoint(pointid):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("obtenerPuntosLucasPoint leemos los datos de lucas: tbl_datos_lucas_eu_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        #Leemos los datos 
        wherecond = ' where a.point_id = '+ str(pointid) 
        query = ( 'select a.th_long as longuitud, a.th_lat as  latitud , a.point_id as id , a.survey_date as fecha , a.date_ini_search , a.date_end_search ' 
                    ' from tbl_datos_lucas_eu_2018 a ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, fecha ,date_ini_search,date_end_search = row
            step = 120
            points.append([longuitud, latitud,id ,fecha,date_ini_search,date_end_search])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosLucasPoint: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('Matriz de puntos')
    #print(points)
    return points


def obtenerPuntosLucasPoligonoOC(minmax, fecha):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_datos_lucas_eu_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        #Leemos los datos 
        wherecond = ' where a.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and a.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        wherecond += ' and a.survey_date = \'' + fecha + '\' and a.date_ini_search  is not null '
        wherecond += ' order by a.survey_date  desc '
        query = ( 'select a.th_long as longuitud, a.th_lat as  latitud , a.point_id as id , a.survey_date as fecha , a.date_ini_search , a.date_end_search ' 
                    ' from tbl_datos_lucas_eu_2018 a ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, fecha ,date_ini_search,date_end_search = row
            step = 120
            points.append([longuitud, latitud,id ,fecha,date_ini_search,date_end_search])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosLucasPoligonoOC: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('Matriz de puntos')
    #print(points)
    return points

def contarPuntosLucasPoligonoOC(minmax):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    num = -1
    resultados=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_datos_lucas_eu_2018")
    print(minmax)
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        step = 110
        wherecond = ' where a.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and a.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        wherecond += ' group by a.survey_date' 
        query = ( 'select a.survey_date as fecha , count(*) as num ' 
                    ' from tbl_datos_lucas_eu_2018 a ' + wherecond
        )
        step = 120
        print(query)
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            fecha ,num = row
            step = 120
            resultados.append([fecha, num])

    except (Exception, psycopg2.Error) as error:
        print("contarPuntosLucasPoligono: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de fechas
    #print('Matriz de fechas')
    #print(resultados)
    return resultados

def contarPuntosLucasPoligonoOCImproved(minmax,numrows):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    num = -1
    resultados=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_datos_lucas_eu_2018")
    print(minmax)
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        step = 110
        wherecond = ' where a.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and a.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        wherecond += ' group by a.survey_date '
        wherecond += ' limit ' + str(numrows)
        query = ( 'select a.survey_date as fecha , count(*) as num ' 
                    ' from tbl_datos_lucas_eu_2018 a ' + wherecond
        )
        step = 120
        print(query)
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            fecha ,num = row
            step = 120
            resultados.append([fecha, num])

    except (Exception, psycopg2.Error) as error:
        print("contarPuntosLucasPoligonoOCImproved: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de fechas
    #print('Matriz de fechas')
    #print(resultados)
    return resultados

def obtenerPuntosPathOC(reference):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("obtenerPuntosPathOC leemos los datos de lucas: tbl_datos_lucas_eu_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where path like \'%response.tiff\' and reference = \'' + reference + '\' '
        query = (   'select b.th_long as longuitud, b.th_lat as  latitud , b.point_id as id , a.path as path '
                    'FROM public.tbl_files_tiff_for_coord  a  '
                    'join public.tbl_datos_lucas_eu_2018 b on b.point_id = a.id ' + wherecond
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, path  = row
            step = 120
            points.append([longuitud, latitud,id ,path])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosPathOC: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('obtenerPuntosPath :Matriz de puntos')
    #print(points)
    return points

def obtenerPuntosPathOCAux(reference,path):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("obtenerPuntosPathOCAux leemos los datos de lucas: tbl_datos_lucas_eu_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where path like \'%response.tiff\' and reference = \'' + reference + '\' '
        query = (   'select b.th_long as longuitud, b.th_lat as  latitud , b.point_id as id , a.path as path '
                    'FROM public.tbl_files_tiff_for_coord  a  '
                    'join public.tbl_datos_lucas_eu_2018 b on b.point_id = a.id ' + wherecond
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, path  = row
            step = 120
            points.append([longuitud, latitud,id ,path])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosPathOCAux: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('obtenerPuntosPath :Matriz de puntos')
    #print(points)
    return points

def obtenerPuntosPathCsv(userid,csvid,num):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de csv: tbl_files_tiff_for_coord")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where a.userid = ' + str(userid) + ' and a.linefile = ' + str(num) + ' and a.id = ' + str(csvid)  + ' and  a.path like \'%response.tiff\' '
        query = (   'select a.index,  a.path as path '
                    'FROM public.tbl_files_tiff_for_coord  a  '+ wherecond
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            index , path  = row
            step = 120
            points.append([index,path])
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerPuntosPathCsv: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    #Matriz de puntos
    #print('obtenerPuntosPath :Matriz de puntos')
    #print(points)
    return points 

def guardardatoscoordenadasSentOC(opt, version):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    points=[]
    cursor = conn.cursor()
    step = 5
    if (opt == 'lucas2018OC'):
        print("guardardatoscoordenadasSentOC: leemos los datos de Lucas: tbl_coord_lucasdb_2018")
        #En este caso las coordenadas se usam tal cual vienen
        step = 80
        try:
            points = obtenerPuntosPathOC(opt)
        except (Exception, psycopg2.Error) as error:
            print("guardardatoscoordenadasSentOC: Error while fetching data from PostgreSQL", error,"; step :", step) 
    if (opt == 'lucas2018OCN'):
        print("leemos los datos de Lucas: tbl_datos_lucas_eu_2018")
        #En este caso las coordenadas se usam tal cual vienen
        step = 85
        try:
            points = obtenerPuntosPathOC(opt)
            print("guardardatoscoordenadasSentOC: datos leidos")
        except (Exception, psycopg2.Error) as error:
            print("guardardatoscoordenadasSentOC: Error while fetching data from PostgreSQL", error,"; step :", step) 
    if (opt == 'lucas2018OCND'):
        print("leemos los datos de Lucas: tbl_datos_lucas_eu_2018")
        #En este caso las coordenadas se usam tal cual vienen
        step = 86
        try:
            points = obtenerPuntosPathOCAux(opt,'FLOAT32')
            print("guardardatoscoordenadasSentOC: datos leidos")
        except (Exception, psycopg2.Error) as error:
            print("guardardatoscoordenadasSentOC: Error while fetching data from PostgreSQL", error,"; step :", step) 
    #Si encontramos puntos buscamos en los archivos
    for x in points:
        # LOs campo del array son
        # x[0] long
        # x[1] lat
        # x[2] point_id
        # x[3] path

        # Del path obtenemos la banda 
        # Ejemplo del path
        # 
        #/app/files/src_data_safe/appsharedfiles/0/lucas2018/0/tiff/s2l1c/31762214/12/482d49845b24396d0700e225b35619b8/response.tiff
        #appfilessrc_data_safeappsharedfiles0lucas20180tiffs2l1c3176221412482d49845b24396d0700e225b35619b8/response.tiff

        # la banda viene despues del id  pos + 1 y siempre 2 dígitos
        path = x[3]
        point_id = x[2]
        long_db  = x[0]
        lat_db = x[1]
        userid = 0
        
        band =   path[path.find(str(point_id)) + len(str(point_id)) + 1:path.find(str(point_id)) + len(str(point_id)) + 3]

        # Create an empty DataFrame with column names
        df = pd.DataFrame(columns=['fuente','internalid','path', 'longitude', 'latitude','relectance','band','userid'])
        #print('Tras crear Nº de filas del df:' )
        #print(len(df.index))
        tabledata = ''
        point_x = long_db # lon
        point_y = lat_db  # lat
        #eliminamos los datos de la tabla para el archivo
        if version == '0':
            tabledata = 'tbl_coord_tiff_reflectance'
            cursor.execute("DELETE FROM " + tabledata + " WHERE 'path' = %s and 'fuente' = %s", (path,opt,))
            conn.commit()
            #procesamos obteniendo los valores con gdal
            ds = gdal.Open(path)
            rb=ds.GetRasterBand(1)
            width = ds.RasterXSize
            height = ds.RasterYSize
            gt = ds.GetGeoTransform()
            gp = ds.GetProjection()
            #data = np.array(ds.ReadAsArray())

            point_srs = osr.SpatialReference()
            point_srs.ImportFromEPSG(4326) # hardcode for lon/lat

            # GDAL>=3: make sure it's x/y
            # see https://trac.osgeo.org/gdal/wiki/rfc73_proj6_wkt2_srsbarn
            point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)     

            file_srs = osr.SpatialReference()
            file_srs.ImportFromWkt(gp)
            num_dec_x = decimal(long_db)
            #print(num_dec_x)
            num_dec_y = decimal(lat_db)

            #Creating the coordinate transformation, and using it to convert the point from lon/lat 
            # to mapx/mapy coordinates (whatever projection it is) with:
            ct = osr.CoordinateTransformation(point_srs, file_srs)
            
            mapx, mapy, z = ct.TransformPoint(point_x, point_y)
            #To go from map coordinates to pixel coordinates, the geotransform needs to be inverted
            #  first. And can then be used to retrieve the pixel coordinates like:
            gt_inv = gdal.InvGeoTransform(gt)
            pixel_x, pixel_y = gdal.ApplyGeoTransform(gt_inv, mapx, mapy)
            # round to pixel
            pixel_x = round(pixel_x)
            pixel_y = round(pixel_y)

            # clip to file extent
            pixel_x = max(min(pixel_x, width-1), 0)
            pixel_y = max(min(pixel_y, height-1), 0)

            #pixel_data = data[pixel_y, pixel_x]
            print('pixel_x:pixel_y:data')
            print(pixel_x)
            print(pixel_y)
            try: #in case raster isnt full extent
                structval=rb.ReadRaster(pixel_x,pixel_y,1,1, buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
                #print(structval)
                print ("Valor de la reflectancia intval")
                print(structval)
                intval = struct.unpack('f' , structval) #assume float
                print(intval)
                val=intval[0]
                print ("Valor de la reflectancia")
                print(val)
                #Insertamos el valor en dl dataframe
                df.loc[len(df.index)] = [opt,point_id,path, point_x, point_y, val,band,userid]
                #Numero de filas del df
                #print('Nº de filas del df:')
                #print(len(df.index))
            except Exception as e:
                print(e)
                val=-9999 #or some value to indicate a fail
                #print ("Valor de la reflectancia KO")
                #print(val)
        elif version == '1':
            tabledata = 'tbl_coord_tiff_reflectance_v1'
            cursor.execute("DELETE FROM " + tabledata + " WHERE 'path' = %s and 'fuente' = %s", (path,opt,))
            conn.commit()
            #procesamos obteniendo los valores con gdal
            dataset = gdal.Open(path)
            if not dataset:
                raise FileNotFoundError(f"Cannot open {path}")

            # Get the geotransform and projection
            geotransform = dataset.GetGeoTransform()
            projection = dataset.GetProjection()

            # Create a spatial reference object from the projection
            spatial_ref = osr.SpatialReference()
            spatial_ref.ImportFromWkt(projection)
            if spatial_ref.IsGeographic():
                spatial_ref.ImportFromEPSG(4326)  # WGS84

            # Create a coordinate transformation object
            coord_transform = osr.CoordinateTransformation(spatial_ref.CloneGeogCS(), spatial_ref)

            # Transform the latitude and longitude to the dataset's coordinate system
            x_geo, y_geo, _ = coord_transform.TransformPoint(long_db, lat_db)
            # Compute pixel coordinates
            y_pixel = int((y_geo - geotransform[0]) / geotransform[1])
            x_pixel = int((x_geo - geotransform[3]) / geotransform[5])

            # Ensure the coordinates are within the image bounds
            if x_pixel < 0 or x_pixel >= dataset.RasterXSize or y_pixel < 0 or y_pixel >= dataset.RasterYSize:
                pixel_value = -99
                print("Coordinates are outside the bounds of the image")
                print('Properties y_pixel: ' + y_pixel + ',x_pixel:' + x_pixel )
                print('Properties geoTransform[0]: ' + geoTransform[0] + ',geoTransform[1]:' + geoTransform[1])
                print('Properties geoTransform[3]: ' + geoTransform[3] + ',geoTransform[5]:' + geoTransform[5])
                raise ValueError("Coordinates are outside the bounds of the image")
            else:
                # Read the pixel value
                rband=dataset.GetRasterBand(1)
                #band = dataset.GetRasterBand(1)  # Assuming we're interested in the first band
                #pixel_value = band.ReadAsArray(x_pixel, y_pixel, 1, 1)[0, 0]
                structval=rband.ReadRaster(x_pixel,y_pixel,1,1, buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
                intval = struct.unpack('f' , structval) #assume float
                print(intval)
                pixel_value=intval[0] 
        
            #Insertamos el valor en dl dataframe
            df.loc[len(df.index)] = [opt,point_id,path, point_x, point_y, pixel_value,band,userid]
        elif version == '2':
            tabledata = 'tbl_coord_tiff_reflectance_v2'
            cursor.execute("DELETE FROM " + tabledata + " WHERE 'path' = %s and 'fuente' = %s", (path,opt,))
            conn.commit()
            #procesamos obteniendo los valores con gdal
            dataset = gdal.Open(path)
            if not dataset:
                raise FileNotFoundError(f"Cannot open {path}")

            # Get the geotransform and projection
            geotransform = dataset.GetGeoTransform()
            projection = dataset.GetProjection()

            # Create a spatial reference object from the projection
            spatial_ref = osr.SpatialReference()
            spatial_ref.ImportFromWkt(projection)
            if spatial_ref.IsGeographic():
                spatial_ref.ImportFromEPSG(4326)  # WGS84

            # Create a coordinate transformation object
            coord_transform = osr.CoordinateTransformation(spatial_ref.CloneGeogCS(), spatial_ref)

            # Transform the latitude and longitude to the dataset's coordinate system
            x_geo, y_geo, _ = coord_transform.TransformPoint(long_db, lat_db)
            # Compute pixel coordinates
            y_pixel = int((y_geo - geotransform[0]) / geotransform[1])
            x_pixel = int((x_geo - geotransform[3]) / geotransform[5])

            # Ensure the coordinates are within the image bounds
            if x_pixel < 0 or x_pixel >= dataset.RasterXSize or y_pixel < 0 or y_pixel >= dataset.RasterYSize:
                pixel_value = -99
                print("Coordinates are outside the bounds of the image")
                print('Properties y_pixel: ' + y_pixel + ',x_pixel:' + x_pixel )
                print('Properties geoTransform[0]: ' + geoTransform[0] + ',geoTransform[1]:' + geoTransform[1])
                print('Properties geoTransform[3]: ' + geoTransform[3] + ',geoTransform[5]:' + geoTransform[5])
                raise ValueError("Coordinates are outside the bounds of the image")
            else:
                # Read the pixel value
                rband=dataset.GetRasterBand(1)
                #band = dataset.GetRasterBand(1)  # Assuming we're interested in the first band
                #pixel_value = band.ReadAsArray(x_pixel, y_pixel, 1, 1)[0, 0]
                structval=rband.ReadRaster(x_pixel,y_pixel,1,1, buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
                intval = struct.unpack('f' , structval) #assume float
                print(intval)
                pixel_value=intval[0] 
        
            #Insertamos el valor en dl dataframe
            df.loc[len(df.index)] = [opt,point_id,path, point_x, point_y, pixel_value,band,userid]
            
        print('Antes de guardar Nº de filas del df para version:' + version )
        print(len(df.index))

            
        tuples = [tuple(x) for x in df.to_numpy()]

        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES %%s" % (tabledata, cols)
        
        try:
            extras.execute_values(cursor, query, tuples)
            conn.commit()
            print("the dataframe is inserted")
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error INSERT : %s" % error)
            conn.rollback()     
            raise ValueError("Error INSERT : %s" % error)
    cursor.close()



def guardardatoscoordenadasSent(opt, version):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    points=[]
    cursor = conn.cursor()
    step = 5
    if (opt == 'lucas2018'):
        print("leemos los datos de Lucas: tbl_coord_lucasdb_2018")
        #En este caso las coordenadas se usam tal cual vienen
        step = 80
        try:
            points = obtenerPuntosPath(opt)
        except (Exception, psycopg2.Error) as error:
            print("guardardatoscoordenadasSent: Error while fetching data from PostgreSQL", error,"; step :", step) 
    #Si encontramos puntos buscamos en los archivos
    for x in points:
        # LOs campo del array son
        # x[0] long
        # x[1] lat
        # x[2] point_id
        # x[3] path

        # Del path obtenemos la banda 
        # Ejemplo del path
        # 
        #/app/files/src_data_safe/appsharedfiles/0/lucas2018/0/tiff/s2l1c/31762214/12/482d49845b24396d0700e225b35619b8/response.tiff
        #appfilessrc_data_safeappsharedfiles0lucas20180tiffs2l1c3176221412482d49845b24396d0700e225b35619b8/response.tiff

        # la banda viene despues del id  pos + 1 y siempre 2 dígitos
        path = x[3]
        point_id = x[2]
        long_db  = x[0]
        lat_db = x[1]
        userid = 0
        
        band =   path[path.find(str(point_id)) + len(str(point_id)) + 1:path.find(str(point_id)) + len(str(point_id)) + 3]

        # Create an empty DataFrame with column names
        df = pd.DataFrame(columns=['fuente','internalid','path', 'longitude', 'latitude','relectance','band','userid'])
        #print('Tras crear Nº de filas del df:' )
        #print(len(df.index))
        tabledata = ''
        #eliminamos los datos de la tabla para el archivo
        if version == 0:
            tabledata = 'tbl_coord_tiff_reflectance'
        elif version == 1:
            tabledata = 'tbl_coord_tiff_reflectance_v1'
        elif version == 1:
            tabledata = 'tbl_coord_tiff_reflectance_v2'
        cursor.execute("DELETE FROM " + tabledata + " WHERE 'path' = %s and 'fuente' = %s", (path,opt,))
        conn.commit()

        ds = gdal.Open(path)
        rb=ds.GetRasterBand(1)
        width = ds.RasterXSize
        height = ds.RasterYSize
        gt = ds.GetGeoTransform()
        gp = ds.GetProjection()
        #data = np.array(ds.ReadAsArray())

        point_srs = osr.SpatialReference()
        point_srs.ImportFromEPSG(4326) # hardcode for lon/lat

        # GDAL>=3: make sure it's x/y
        # see https://trac.osgeo.org/gdal/wiki/rfc73_proj6_wkt2_srsbarn
        point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)     

        file_srs = osr.SpatialReference()
        file_srs.ImportFromWkt(gp)
        num_dec_x = decimal(long_db)
        #print(num_dec_x)
        num_dec_y = decimal(lat_db)

        #Creating the coordinate transformation, and using it to convert the point from lon/lat 
        # to mapx/mapy coordinates (whatever projection it is) with:
        ct = osr.CoordinateTransformation(point_srs, file_srs)
        point_x = long_db # lon
        point_y = lat_db  # lat
        mapx, mapy, z = ct.TransformPoint(point_x, point_y)
        #To go from map coordinates to pixel coordinates, the geotransform needs to be inverted
        #  first. And can then be used to retrieve the pixel coordinates like:
        gt_inv = gdal.InvGeoTransform(gt)
        pixel_x, pixel_y = gdal.ApplyGeoTransform(gt_inv, mapx, mapy)
        # round to pixel
        pixel_x = round(pixel_x)
        pixel_y = round(pixel_y)

        # clip to file extent
        pixel_x = max(min(pixel_x, width-1), 0)
        pixel_y = max(min(pixel_y, height-1), 0)

        #pixel_data = data[pixel_y, pixel_x]
        print('pixel_x:pixel_y:data')
        print(pixel_x)
        print(pixel_y)
        try: #in case raster isnt full extent
            structval=rb.ReadRaster(pixel_x,pixel_y,1,1, buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
            #print(structval)
            print ("Valor de la reflectancia intval")
            print(structval)
            intval = struct.unpack('f' , structval) #assume float
            print(intval)
            val=intval[0]
            print ("Valor de la reflectancia")
            print(val)
            #Insertamos el valor en dl dataframe
            df.loc[len(df.index)] = [opt,point_id,path, point_x, point_y, val,band,userid]
            #Numero de filas del df
            #print('Nº de filas del df:')
            #print(len(df.index))
        except Exception as e:
            print(e)
            val=-9999 #or some value to indicate a fail
            #print ("Valor de la reflectancia KO")
            #print(val)
            
        #si se han obtenido datos los insertamos
        print('Antes de guardar Nº de filas del df:' )
        print(len(df.index))

            
        tuples = [tuple(x) for x in df.to_numpy()]

        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES %%s" % (tabledata, cols)
        
        try:
            extras.execute_values(cursor, query, tuples)
            conn.commit()
            print("the dataframe is inserted")
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
    cursor.close()

def guardardatoscoordenadasCsv(json_object,userid,csvid,num,version):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])

    cursor = conn.cursor()
    step = 5

   

    # Del path obtenemos la banda 
    # Ejemplo del path
    # 
    #/app/files/src_data_safe/appcsvfiles/0/<webapp userid>/<webapp csv id >/tiff/<s2l1c o s2l2a >/12/482d49845b24396d0700e225b35619b8/response.tiff
    #appfilessrc_data_safeappsharedfiles0lucas20180tiffs2l1c3176221412482d49845b24396d0700e225b35619b8/response.tiff
    try:
        points = obtenerPuntosPathCsv(userid,csvid,num)
    except (Exception, psycopg2.Error) as error:
        print("guardardatoscoordenadasCsv: Error while fetching data from PostgreSQL", error,"; step :", step) 
    #recorremos los archivos para todas las bandas
    for x in points:
        # LOs campo del array son
        # x[0] index file tiff
        # x[1] full path tiff
        path = x[1]
        index = x[0]
        # la banda viene despues del id  pos + 1 y siempre 2 dígitos
        long = json_object['longitude']
        lat = json_object['latitude']
        date_str = json_object['date']
        soc =  json_object['soc']
        
        band =   path[path.find('band') + 4  + 1:path.find('band') + 4 + 3]
        print( 'guardardatoscoordenadasCsv, la banda es:' +band + ', para el path :' + path )
        # Create an empty DataFrame with column names
        # fuente will have userid
        df = pd.DataFrame(columns=['fuente','internalid','path', 'longitude', 'latitude','relectance','band','userid','linefile','index_tiff_file','soc'])
        #print('Tras crear Nº de filas del df:' )
        #print(len(df.index))
        tabledata = ''
        #eliminamos los datos de la tabla para el archivo
        if version == 0:
            tabledata = 'tbl_coord_tiff_reflectance'
        elif version == 1:
            tabledata = 'tbl_coord_tiff_reflectance_v1'
        elif version == 1:
            tabledata = 'tbl_coord_tiff_reflectance_v2'
        cursor.execute("DELETE FROM " + tabledata + " WHERE  userid = %s and internalid = %s and linefile = %s and band = %s", (str(userid),str(csvid), str(num), band))
        conn.commit()

        ds = gdal.Open(path)
        rb=ds.GetRasterBand(1)
        width = ds.RasterXSize
        height = ds.RasterYSize
        gt = ds.GetGeoTransform()
        gp = ds.GetProjection()
        #data = np.array(ds.ReadAsArray())

        point_srs = osr.SpatialReference()
        point_srs.ImportFromEPSG(4326) # hardcode for lon/lat

        # GDAL>=3: make sure it's x/y
        # see https://trac.osgeo.org/gdal/wiki/rfc73_proj6_wkt2_srsbarn
        point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)     

        file_srs = osr.SpatialReference()
        file_srs.ImportFromWkt(gp)
        num_dec_x = decimal(long)
        #print(num_dec_x)
        num_dec_y = decimal(lat)

        #Creating the coordinate transformation, and using it to convert the point from lon/lat 
        # to mapx/mapy coordinates (whatever projection it is) with:

        ct = osr.CoordinateTransformation(point_srs, file_srs)

        point_x = float(long) # lon
        point_y = float(lat)  # lat
        print(point_x)
        print(point_y)

        mapx, mapy, z = ct.TransformPoint(point_x, point_y)

        #To go from map coordinates to pixel coordinates, the geotransform needs to be inverted
        #  first. And can then be used to retrieve the pixel coordinates like:
        gt_inv = gdal.InvGeoTransform(gt)
        pixel_x, pixel_y = gdal.ApplyGeoTransform(gt_inv, mapx, mapy)
        # round to pixel
        pixel_x = round(pixel_x)
        pixel_y = round(pixel_y)

        # clip to file extent
        pixel_x = max(min(pixel_x, width-1), 0)
        pixel_y = max(min(pixel_y, height-1), 0)

        #pixel_data = data[pixel_y, pixel_x]
        print('pixel_x:pixel_y:data')
        print(pixel_x)
        print(pixel_y)
        try: #in case raster isnt full extent
            structval=rb.ReadRaster(pixel_x,pixel_y,1,1, buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
            #print(structval)
            intval = struct.unpack('f' , structval) #assume float
            val=intval[0]
            print ("Valor de la reflectancia")
            print(val)
            #Insertamos el valor en dl dataframe
            df.loc[len(df.index)] = ['csvfile',csvid,path, point_x, point_y, val,band,userid,num, index,soc]
            #Numero de filas del df
            #print('Nº de filas del df:')
            #print(len(df.index))
        except Exception as e:
            print(e)
            val=-9999 #or some value to indicate a fail
            #print ("Valor de la reflectancia KO")
            #print(val)
            
        #si se han obtenido datos los insertamos
        print('Antes de guardar Nº de filas del df:' )
        print(len(df.index))

            
        tuples = [tuple(x) for x in df.to_numpy()]

        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES %%s" % (tabledata, cols)
        
        try:
            extras.execute_values(cursor, query, tuples)
            conn.commit()
            print("the dataframe is inserted")
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
    cursor.close()


'''
def guardardatoscoordenadas(uuid, opt):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_coord_tiff_values'
    basename = ""
    productName = ""
    source = srvconf['PYSRV_SRC_ROOT_DATA_DIR' ]
    processgdal = srvconf['PYSRV_SRC_ROOT_DATA_DIR_PROCESS_GDAL' ]
    filename = uuid + '.zip'
    points=[]
    cursor = conn.cursor()
    step = 5
    if ( opt == 'test'):
        print("leemos los datos de test")
        points = [
        [-4.27254326,	42.08352779, 1],
        [-4.27217104,	42.08376982,2] ,
        [-4.2727401,	42.08221765,3] ,
        [-4.27296015,	42.08213388,4] ,
        [-4.27268713,	42.08182134,5],
        [-4.21574342,	42.44570320 ,6],
        [-3.68352864,   42.295119665,7]
        ]
    elif (opt == 'jcyl'):
        print("leemos los datos de la junta de castilla y leon, tabla tbl_datos_carga_JCyL")
        #En este caso hay que convertir las coordenadas
        #En este caso las coordenadas se usam tal cual vienen
        step = 10
        try:
            df = pd.DataFrame()
            table = 'tbl_datos_carga_JCyL'
            #Leemos los datos 
            query = "SELECT coor_x_etr , coor_y_etr, objectid FROM %s where origen = 'Ines' " % (table)
            cursor.execute(query) 
            rowd = cursor.fetchall()
            for row in rowd:
                coor_x_etr , coor_y_etr , objectid = row
                step = 20
                #points.append([coor_x_etr, coor_y_etr,objectid])
            
                #convertimos coordenadas 
                pointX = coor_x_etr
                pointY = coor_y_etr

                # Spatial Reference System
                inputEPSG = 3857
                outputEPSG = 4326

                # create a geometry from coordinates
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(pointX, pointY)

                # create coordinate transformation
                inSpatialRef = osr.SpatialReference()
                inSpatialRef.ImportFromEPSG(inputEPSG)

                outSpatialRef = osr.SpatialReference()
                outSpatialRef.ImportFromEPSG(outputEPSG)

                coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

                # transform point
                point.Transform(coordTransform)

                # print point in EPSG 4326
                points.append([point.GetX(), point.GetY(),objectid])
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step)    
    elif (opt == 'jc'):
        print("leemos los datos de Juan Carlos: tbl_datos_jc")
        #En este caso las coordenadas se usam tal cual vienen
        step = 80
        try:
            df = pd.DataFrame()
            table = 'tbl_datos_jc'
            #Leemos los datos 
            query = "SELECT longuitud, latitud , id FROM %s " % (table)
            cursor.execute(query) 
            rowd = cursor.fetchall() 
            for row in rowd:
                longuitud , latitud , id = row
                step = 110
                points.append([longuitud, latitud,id])
            print(points)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    elif (opt == 'lucas'):
        print("leemos los datos de Lucas: tbl_coord_lucasdb")
        #En este caso las coordenadas se usam tal cual vienen
        step = 80
        try:
            df = pd.DataFrame()
            table = 'tbl_coord_lucasdb'
            #Leemos los datos 
            query = "SELECT x_wgs84, y_wgs84 , index FROM %s " % (table)
            cursor.execute(query) 
            rowd = cursor.fetchall() 
            for row in rowd:
                x_wgs84 , y_wgs84 , index = row
                step = 110
                points.append([x_wgs84 , y_wgs84 , index])
            print(points)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step) 
    elif (opt == 'lucas2018'):
        print("leemos los datos de Lucas: tbl_coord_lucasdb_2018")
        #En este caso las coordenadas se usam tal cual vienen
        step = 80
        try:
            df = pd.DataFrame()
            table = 'tbl_coord_lucasdb_2018'
            #Leemos los datos 
            query = "SELECT x_wgs84, y_wgs84 , index  FROM %s " % (table)
            cursor.execute(query) 
            rowd = cursor.fetchall() 
            for row in rowd:
                x_wgs84 , y_wgs84 , index = row
                step = 110
                points.append([x_wgs84 , y_wgs84 , index])
            print(points)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step) 
    #Matriz de puntos
    print('Matriz de puntos')
    #print(points)
    # Create an empty DataFrame with column names
    df = pd.DataFrame(columns=['fuente','internalid','title', 'longitude', 'latitude','relectance','band','userid'])
    print('Tras crear Nº de filas del df:' )
    print(len(df.index))
    
    outputPathSubdirectory = processgdal+"/" + uuid + "_PROCESSED/IMAGE_DATA"
    #eliminamos los datos de la tabla para el archivo
    tabledata = 'tbl_coord_tiff_values'
    cursor.execute("DELETE FROM " + tabledata + " WHERE 'title' = %s and 'fuente' = %s", (uuid,opt,))
    conn.commit()

    for tiff_file in os.listdir(outputPathSubdirectory):
        # check only text files
        if tiff_file.endswith('.tiff'):
            print(uuid + '' + tiff_file)
            ds = gdal.Open(outputPathSubdirectory + "/" + tiff_file)
            rb=ds.GetRasterBand(1)
            width = ds.RasterXSize
            height = ds.RasterYSize
            gt = ds.GetGeoTransform()
            gp = ds.GetProjection()
            #data = np.array(ds.ReadAsArray())

            point_srs = osr.SpatialReference()
            point_srs.ImportFromEPSG(4326) # hardcode for lon/lat

            # GDAL>=3: make sure it's x/y
            # see https://trac.osgeo.org/gdal/wiki/rfc73_proj6_wkt2_srsbarn
            point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)     

            file_srs = osr.SpatialReference()
            file_srs.ImportFromWkt(gp)
            for x in points:
                #print('x(0)') 
                #print(x[0])
                num_dec_x = decimal(x[0])
                #print(num_dec_x)
                num_dec_y = decimal(x[1])
                #print('x(1)')
                #print(x[1])
                #Creating the coordinate transformation, and using it to convert the point from lon/lat 
                # to mapx/mapy coordinates (whatever projection it is) with:
                ct = osr.CoordinateTransformation(point_srs, file_srs)
                point_x = x[1] # lon
                point_y = x[0]  # lat
                mapx, mapy, z = ct.TransformPoint(point_x, point_y)
                #To go from map coordinates to pixel coordinates, the geotransform needs to be inverted
                #  first. And can then be used to retrieve the pixel coordinates like:
                gt_inv = gdal.InvGeoTransform(gt)
                pixel_x, pixel_y = gdal.ApplyGeoTransform(gt_inv, mapx, mapy)
                # round to pixel
                pixel_x = round(pixel_x)
                pixel_y = round(pixel_y)

                # clip to file extent
                pixel_x = max(min(pixel_x, width-1), 0)
                pixel_y = max(min(pixel_y, height-1), 0)

                #pixel_data = data[pixel_y, pixel_x]
                #print('pixel_x:pixel_y:data')
                #print(pixel_x)
                #print(pixel_y)
                #print(pixel_data)
                try: #in case raster isnt full extent
                    structval=rb.ReadRaster(pixel_x,pixel_y,1,1, buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
                    #print(structval)
                    intval = struct.unpack('f' , structval) #assume float
                    val=intval[0]
                    #print ("Valor de la reflectancia")
                    #print(val)
                    #Insertamos el valor en dl dataframe
                    df.loc[len(df.index)] = [opt,x[2],uuid, point_x, point_y, val,tiff_file]
                    #Numero de filas del df
                    #print('Nº de filas del df:')
                    #print(len(df.index))
                except Exception as e:
                    print(e)
                    val=-9999 #or some value to indicate a fail
                    #print ("Valor de la reflectancia KO")
                    #print(val)
                
    #si se han obtenido datos los insertamos
    print('Antes de guardar Nº de filas del df:' )
    print(len(df.index))

        
    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (tabledata, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
'''
def leercsvlucas2015info():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    data = srvconf['PYSRV_DATA_UPLOAD' ]
    file = data + '/2015/EU_2015_20200225.csv'
    table = 'tbl_datos_lucas_eu_2015_20200225'
    datos = pd.read_csv( file )
    # get metadata of DataFrame
    print("Info para :" + file)
    print(datos.info())
    # crearTablaSentinel creamos la tabla en postgres genero sql en el log luego comento
    #crearTablaSentinel(datos, table)
    #Cargamos los datos
    cursor = conn.cursor()
    tuples = [tuple(x) for x in datos.to_numpy()]

    cols = ','.join(list(datos.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    '''
    file = data + '/2015/LUCAS_Topsoil_2015_20200323.csv'
    table = 'tbl_datos_lucas_Topsoil_2015_20200323'
    datos1 = pd.read_csv(file   )
    print("Info para :" + file)
    # crearTablaSentinel creamos la tabla en postgres genero sql en el log luego comento
    #crearTablaSentinel(datos1, table)
    print(datos1.info())
    tuples = [tuple(x) for x in datos1.to_numpy()]

    cols = ','.join(list(datos.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    '''
    cursor.close()
def leercsvlucas2018OCinfo():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    data = srvconf['PYSRV_DATA_UPLOAD' ]
    file = data + '/2018/LUCAS-SOIL-2018-csv.csv' 
    table = 'tbl_datos_lucas_eu_2018'
    datos = pd.read_csv( file )
    # get metadata of DataFrame
    print("Info para :" + file)
    print(datos.info())
    # crearTablaSentinel creamos la tabla en postgres genero sql en el log luego comento
    #crearTablaSentinel(datos, table)
    #Cargamos los datos
    cursor = conn.cursor()
    tuples = [tuple(x) for x in datos.to_numpy()]

    cols = ','.join(list(datos.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    
    cursor.close()

def leercsvcyl():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    data = srvconf['PYSRV_COORDS_DATA' ]
    datoscyl = pd.read_csv(data + '/datosJCyL.csv'  )
    table = 'tbl_datos_carga_JCyL'
    # get metadata of DataFrame
    print(datoscyl.info())
    # crearTablaSentinel creamos la tabla en postgres genero sql en el log luego comento
    #crearTablaSentinel(datoscyl, table)
    cursor = conn.cursor()
    tuples = [tuple(x) for x in datoscyl.to_numpy()]

    cols = ','.join(list(datoscyl.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()

def leercoordLucas():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    data = srvconf['PYSRV_COORDS_DATA' ]
    datos = pd.read_csv(data + '/LUCAS-Master-Grid.csv'  )
    table = 'tbl_coord_lucasdb'
    # get metadata of DataFrame
    print(datos.info())
    # crearTablaSentinel creamos la tabla en postgres genero sql en el log luego comento
    #crearTablaSentinel(datos, table)
    
    cursor = conn.cursor()
    tuples = [tuple(x) for x in datos.to_numpy()]

    cols = ','.join(list(datos.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()

def leercoordLucas1():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    data = srvconf['PYSRV_COORDS_DATA' ]
    datos = pd.read_csv(data + '/EU_2018_20200213.CSV'  )
    table = 'tbl_coord_lucasdb_2018'
    # get metadata of DataFrame
    print(datos.info())
    # crearTablaSentinel creamos la tabla en postgres genero sql en el log luego comento
    #crearTablaSentinel(datos, table)
    
    cursor = conn.cursor()
    tuples = [tuple(x) for x in datos.to_numpy()]

    cols = ','.join(list(datos.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
    

def leercsvjuancarlos():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    data = srvconf['PYSRV_COORDS_DATA' ]
    datos = pd.read_csv(data + '/20230210_Datos Suelos.csv'  )
    table = 'tbl_datos_jc'
    # get metadata of DataFrame
    print(datos.info())
    # crearTablaSentinel creamos la tabla en postgres genero sql en el log luego comento
    #crearTablaSentinel(datos, table)
    
    cursor = conn.cursor()
    tuples = [tuple(x) for x in datos.to_numpy()]

    cols = ','.join(list(datos.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
def guardardatoscoordenadastifffiles(df,version):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos

    table='tbl_files_tiff_for_coord'
    if version == 1:
        table='tbl_files_tiff_for_coord_v1'
    elif version == 2:
        table='tbl_files_tiff_for_coord_v2'
    
    #si se han obtenido datos los insertamos
    print('Antes de guardar Nº de filas del df:' )
    print(len(df.index))

    cursor = conn.cursor()
    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
def checkPuntProcesado(point_id, version,tiffuserfolder):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_files_tiff_for_coord'
    if version == 1:
        table='tbl_files_tiff_for_coord_v1'
    elif version == 2:
        table='tbl_files_tiff_for_coord_v2'
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas:" +  table)
    encontrado = 0
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where id = ' + str(point_id) + '  and  path like \'' +  tiffuserfolder + '%\' ' 
        query = (   'select  count(*)  '
                    'FROM public.tbl_files_tiff_for_coord  a  ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        results = cursor.fetchone()
        encontrado = 0
        for r in results: 
            print("Tipo de dato da salida de result: " ,type(r))
            if int(r) > 0:
                encontrado = 1
    except (Exception, psycopg2.Error) as error:
        print("checkPuntProcesado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return encontrado
def checkPuntProcesado(point_id, version,tiffuserfolder,satellite):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_files_tiff_for_coord'
    if version == 1:
        table='tbl_files_tiff_for_coord_v1'
    elif version == 2:
        table='tbl_files_tiff_for_coord_v2'
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lucas:" +  table)
    encontrado = 0
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where id = ' + str(point_id) + '  and  path like \'' +  tiffuserfolder + '%\' ' + \
                     'and satellite = \'' + satellite + '\' '
        query = (   'select  count(*)  '
                    'FROM public.tbl_files_tiff_for_coord  a  ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        results = cursor.fetchone()
        encontrado = 0
        for r in results: 
            print("Tipo de dato da salida de result: " ,type(r))
            if int(r) > 0:
                encontrado = 1
    except (Exception, psycopg2.Error) as error:
        print("checkPuntProcesado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return encontrado
def checkCsvLineaProcesado(id,numline,band,userid, collection,version):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_files_tiff_for_coord'
    if version == 1:
        table='tbl_files_tiff_for_coord_v1'
    elif version == 2:
        table='tbl_files_tiff_for_coord_v2'
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lineas procesadas:" +  table)
    encontrado = 0
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where a.userid = ' + str(userid) + ' and a.linefile = ' + str(numline) + ' and a.id = ' + str(id)  + ' and band = \'' + band + '\' and  a.path like \'%' +  collection + '\' '

        query = (   'select  count(*) as num '
                    'FROM public.tbl_files_tiff_for_coord  a  ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            num  = row
            if int(num) > 0:
                encontrado = 1
    except (Exception, psycopg2.Error) as error:
        print("checkCsvLineaProcesado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return encontrado

def checkCsvLineaProcesado(id,numline,band,userid, collection,version,satellite):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_files_tiff_for_coord'
    if version == 1:
        table='tbl_files_tiff_for_coord_v1'
    elif version == 2:
        table='tbl_files_tiff_for_coord_v2'
    points=[]
    cursor = conn.cursor()
    print("leemos los datos de lineas procesadas:" +  table)
    encontrado = 0
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where a.userid = ' + str(userid) + ' and a.linefile = ' + \
                    str(numline) + ' and a.id = ' + str(id)  + ' and band = \'' + \
                    band + '\' and  a.path like \'%' +  collection + '\' ' + \
                    ' and a.satellite = \'' + satellite + '\' '

        query = (   'select  count(*) as num '
                    'FROM public.tbl_files_tiff_for_coord  a  ' + wherecond
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            num  = row
            if int(num) > 0:
                encontrado = 1
    except (Exception, psycopg2.Error) as error:
        print("checkCsvLineaProcesado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return encontrado

def puntoscsvusuario(userid, csvid):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    cursor = conn.cursor()
    df = pd.DataFrame()
    print("leemos los datos del csv procesados: tbl_coord_tiff_reflectance")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where a.path like \'%response.tiff\' and fuente = \'csvfile\' and  userid = ' + str(userid) + ' and internalid = ' + str(csvid)
        query = (   
            'select longitude, latitude, relectance ,  userid  , band , internalid , path , soc '
            'from public.tbl_coord_tiff_reflectance a  ' + wherecond
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longitud , latitud , relectance,userid , band , internalid , path ,soc = row
            step = 120
            new_row = pd.DataFrame({ 'longitud':longitud, 'latitud':latitud,'reflectance': relectance, 'userid': userid, 
                                    'band':band, 'id':internalid,'path':path,'soc':soc}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntoscsvusuario: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df

def puntosLucas2018Listado(minmax):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    cursor = conn.cursor()
    df = pd.DataFrame()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where a.path like \'%response.tiff\' and  reference = \'lucas2018\' and  b.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and b.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 
        orderby =  ' order by  b.point_id, a.band'
        query = (  
            'select distinct b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.path, r.relectance as reflectance, '
            'a.band, b.survey_date, c.coarse_mas, c.coarse_vol '
            'FROM public.tbl_files_tiff_for_coord  a   '
            'join public.tbl_coord_tiff_reflectance r on r.index_tiff_file = a.index ' 
            'join public.tbl_coord_lucasdb_2018 b on b.point_id = a.id  '
            'join public.datoslucasdb c on c.point_id = b.point_id  ' + wherecond + orderby
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longitud , latitud , id, path , reflectance , band , survey_date ,  coarse_mas, coarse_vol  = row
            step = 120
            new_row = pd.DataFrame({ 'longitud':longitud, 'latitud':latitud,'id':id,'path':path,'reflectance':reflectance,
                                    'band':band,'survey_date':survey_date,'coarse_mas':coarse_mas,'coarse_vol':coarse_vol}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018Listado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df

def puntosLucas2018ListadoOC(minmax,ref):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    cursor = conn.cursor()
    df = pd.DataFrame()
    print("leemos los datos de lucas: tbl_datos_lucas_eu_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        table_search = 'tbl_coord_tiff_reflectance'
        if (ref == 'lucas2018OC'):
            table_search = 'tbl_coord_tiff_reflectance'
        if (ref == 'lucas2018OCN'):
            table_search = 'tbl_coord_tiff_reflectance_v1'
        if (ref == 'lucas2018OCND'):
            table_search = 'tbl_coord_tiff_reflectance_v2'
        #Leemos los datos 
        wherecond = ' where a.path like \'%response.tiff\' and  reference = \''+ ref + \
                    '\' and  b.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  \
                    ' and b.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) + \
                    ' and r.relectance > 0'
        orderby =  ' order by  b.point_id, a.band'
        query = (  
            'select distinct b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.path, r.relectance as reflectance, '
            'a.band, b.survey_date, b.oc '
            'FROM public.tbl_files_tiff_for_coord  a   '
            'join public.' + table_search +' r on  r.internalid = a.id  and a.path = r.path ' 
            'join public.tbl_datos_lucas_eu_2018 b on b.point_id = a.id   ' + wherecond + orderby
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longitud , latitud , id, path , reflectance , band , survey_date ,  oc  = row
            step = 120
            new_row = pd.DataFrame({ 'longitud':longitud, 'latitud':latitud,'id':id,'path':path,'reflectance':reflectance,
                                    'band':band,'survey_date':survey_date,'oc':oc}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018Listado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df

def puntosLucas2018ListadoV1(minmax):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where a.path like \'%response.tiff\' and  reference = \'lucas2018\' and  b.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and b.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 

        query = (   
            'select b.th_long as longuitud, b.th_lat as  latitud , b.point_id as id , a.path, r.relectance as reflectance, '
            'a.band, b.survey_date, c.coarse_mas, c.coarse_vol '
            'FROM public.tbl_files_tiff_for_coord_v1  a   '
            'join public.tbl_coord_tiff_reflectance_v1 r on r.internalid = a.id ' 
            'join public.tbl_coord_lucasdb_2018 b on b.point_id = a.id  '
            'join public.datoslucasdb c on c.point_id = b.point_id  ' + wherecond
                    
                )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, path , reflectance , band , survey_date ,  coarse_mas, coarse_vol  = row
            step = 120
            new_row = pd.DataFrame({ 'longitud':longitud, 'latitud':latitud,'id':id,'path':path,'reflectance':reflectance,
                                    'band':band,'survey_date':survey_date,'coarse_mas':coarse_mas,'coarse_vol':coarse_vol}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018Listadov1: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
def puntosLucas2018ListadoV2(minmax, dateini, datefin):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    cursor = conn.cursor()
    print("leemos los datos de lucas: tbl_coord_lucasdb_2018")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where a.path like \'%response.tiff\' and  reference = \'lucas2018\' and  b.th_long BETWEEN ' + str(minmax[0]) + ' and ' + str(minmax[2]) +  ' and b.th_lat  BETWEEN ' + str(minmax[1]) + ' and ' +  str(minmax[3]) 

        query = (   
            'select b.th_long as longuitud, b.th_lat as  latitud , b.point_id as id , a.path, r.relectance as reflectance, '
            'a.band, b.survey_date, c.coarse_mas, c.coarse_vol '
            'FROM public.tbl_files_tiff_for_coord_v1  a   '
            'join public.tbl_coord_tiff_reflectance_v1 r on r.internalid = a.id ' 
            'join public.tbl_coord_lucasdb_2018 b on b.point_id = a.id  '
            'join public.datoslucasdb c on c.point_id = b.point_id  ' + wherecond
        )
                    
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longuitud , latitud , id, path , reflectance , band , survey_date ,  coarse_mas, coarse_vol  = row
            new_row = pd.DataFrame({ 'longitud':longitud, 'latitud':latitud,'id':id,'path':path,'reflectance':reflectance,
                                    'band':band,'survey_date':survey_date,'coarse_mas':coarse_mas,'coarse_vol':coarse_vol}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018ListadoV2: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()