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
    df.to_sql(table,engine, schema='Staging')

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
        print('Moviendo datos : ' + ref)
        query = "SELECT fnc_copy_unique_values('%s')" % (ref)
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
            print(points)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    
    cursor.close()
    #Matriz de puntos
    print('Matriz de puntos')
    print(points)
    return points
   
    


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
    

    #Matriz de puntos
    print('Matriz de puntos')
    #print(points)
    # Create an empty DataFrame with column names
    df = pd.DataFrame(columns=['fuente','internalid','title', 'longitude', 'latitude','relectance','band'])
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
    