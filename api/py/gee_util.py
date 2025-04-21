import pandas as pd
import psycopg2
from psycopg2 import connect
import json
import os
import psycopg2.extras as extras

# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))
'''
 * Function to mask clouds using the Sentinel-2 QA band
 * @param {ee.Image} image Sentinel-2 image
 * @return {ee.Image} cloud masked Sentinel-2 image
 */
 '''
def mask_s2_clouds(image):
  '''Masks clouds in a Sentinel-2 image using the QA band.

  Args:
      image (ee.Image): A Sentinel-2 image.

  Returns:
      ee.Image: A cloud-masked Sentinel-2 image.
  '''
  qa = image.select('QA60')

  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloud_bit_mask = 1 << 10
  cirrus_bit_mask = 1 << 11

  # Both flags should be set to zero, indicating clear conditions.
  mask = (
      qa.bitwiseAnd(cloud_bit_mask)
      .eq(0)
      .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
  )
  #if divide == 0:
  return image.updateMask(mask)
  #else:
  #  return image.updateMask(mask).divide(10000)
  
def functn_scale_bands(image, bandstoscale, scalefactor):
    
    scaledbands = image.select(bandstoscale).multiply(scalefactor)
    
    return image.addBands(scaledbands, overwrite=True)

def functn_ResemapleSentinel2(img):
    'Function to resample the sentinel bands from there native scale to 10 meter scale. Takes the image as iput, return the resampled image'
    crs =  img.select('B1').projection().crs()
    img = img.resample('bilinear').reproject(crs=crs, scale=10)
    return img


def functn_Clip(img, aoi_ee):
    'Cliping the bands of the image to the area of interest. Takes the image and aoi feature as input and returns the clipped image.'
    clipped_img = img.clip(aoi_ee)
    return clipped_img

# Functions
def cloudMaskingBasedonSCL(img_cloudy):
    scl = img_cloudy.select('SCL')
    #Selecting Cloudy Mask
    img_cloudy_shadow = img_cloudy.select('SCL').eq([3])
    img_cloudy_low = img_cloudy.select('SCL').eq([7])
    img_cloudy_med = img_cloudy.select('SCL').eq([8])
    img_cloudy_high = img_cloudy.select('SCL').eq([9])
    img_cloudy_cirrus = img_cloudy.select('SCL').eq([10])
    
    
    cloud_mask = img_cloudy_shadow.add(img_cloudy_low).add(img_cloudy_med).add(img_cloudy_high).add(img_cloudy_cirrus) 
    

#     #Inverting the Mask
    invert_mask = cloud_mask.eq(0).selfMask() #invert mask will have the pixels with only no cloud
    cloud_mask_only = cloud_mask.eq(1).selfMask() #this will have only the pixels without cloud
        
    img_masked = img_cloudy.updateMask(invert_mask)
    img_unmasked = img_masked.unmask(-99999)
    img_cloudy_cloudless = img_unmasked
    
    return img_cloudy_cloudless

def print_full(x):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')


def guardardatoscoordenadasGeeTifffiles(df,version):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos

    table='tbl_gee_points_bands_reflectance'
    
    #si se han obtenido datos los insertamos
    print('Antes de guardar Nº de filas del df: ' )
    print(len(df.index))

    cursor = conn.cursor()
    tuples = [tuple(x) for x in df.to_numpy()]
    print_full(df)
    cols = ','.join(list(df.columns))
    print(cols)
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

def guardardatoscsvpoints(df,version):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos

    table='tbl_datos_archivos_csv'
    
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

def checkPuntGeeProcesado(point_id,user_id,satellite,iter):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_gee_points_bands_reflectance'
    cursor = conn.cursor()
    print("leemos los datos checkPuntGeeProcesado  satellite:" +  table)
    encontrado = 0
    step = 100
    try:

        #Leemos los datos 
        wherecond = ' where point_id = ' + str(point_id) + ' and user_id = ' + str(user_id) + \
                    ' and satellite =\'' + str(satellite) + '\' and iter =  ' + str(iter) 
        
        query = ( ' select count(1)  , max(cloud_cover_null)   '
            ' from '
            ' ( '
            ' select  point_id,CASE WHEN cloud_cover IS NULL '
            '            THEN -1 '
            '            ELSE cloud_cover '
            '    END AS cloud_cover_null'
            ' FROM public.tbl_gee_points_bands_reflectance a ' 
        )
        query  +=  wherecond 
        query  +=  ' ) t  '
        

        #print(query)
        step = 33
        cursor.execute(query) 
        results = cursor.fetchone()
        encontrado = 0
        num_points = results[0]
        max_cc = results[1]
        print(num_points)
        if num_points > 0:
            if max_cc == -1:
                print("Punto incompleto se reprocesa manteniendo el registro anterior que tiene el path de la imagen descargada")
            else:    
                encontrado = 1
    except (Exception, psycopg2.Error) as error:
        print("checkPuntProcesado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return encontrado

def getPuntGeeSentinelProcesados(point_id,user_id,satellite,path):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_gee_points_bands_reflectance'
    cursor = conn.cursor()
    df = pd.DataFrame()
    print("leemos los datos getPuntGeeSentinelProcesados  satellite:" +  table)
    encontrado = 0
    step = 100
    try:

        #Leemos los datos 
        
        
        query = ( ' select  distinct  b1, b2, b3,b4,b5,b6,b7,b8,b8a,b9,b11,b12 , cloud_cover,  t1.datetime_itm_file as  datetime_itm_file '
                   ' from public.tbl_gee_points_bands_reflectance  t1 '
                    'join ('
                    ' select point_id ,user_id, iter, satellite ,csvpath , min(cloud_cover) as mincc'
                    ' from tbl_gee_points_bands_reflectance ' )
        wherecond = (' where point_id = ' + str(point_id) + ' and user_id = ' + str(user_id) + \
                    ' and satellite =\'' + str(satellite) + '\' '  + \
                    ' and csvpath =\'' + path + '\'')
        groupby = ( ' group by point_id ,user_id, iter, satellite ,csvpath) t2 on (t1.iter = t2.iter and '
                       ' t1.point_id = t2.point_id and '
                       ' t1.user_id = t2.user_id and '
                       ' t1.satellite = t2.satellite and '
                       ' t1.csvpath = t2.csvpath and '
                       ' t1.cloud_cover = t2.mincc)  order by  t1.datetime_itm_file asc '
                            ) 
        query  +=  wherecond 
        query  +=  groupby
        
        #print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            b1, b2, b3,b4,b5,b6,b7,b8,b8a,b9,b11,b12 , cloud_cover, datetime_itm_file= row
            step = 120
            new_row = pd.DataFrame({ 'b1':b1, 'b2':b2, 'b3':b3, 'b4':b4, 'b5':b5, 
                                    'b6':b6, 'b7':b7, 'b8':b8, 'b8a':b8a, 'b9':b9, 
                                    'b11':b11, 'b12':b12 , 'cloud_cover': cloud_cover, 'datetime_itm_file':datetime_itm_file
                                    }, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018Listado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df

def getPuntGeeLandsatProcesados(point_id,user_id,satellite,path):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_gee_points_bands_reflectance'
    cursor = conn.cursor()
    df = pd.DataFrame()
    print("leemos los datos getPuntGeeLandsatProcesados  satellite:" +  table)
    encontrado = 0
    step = 100
    try:

        #Leemos los datos 
        
        
        query = ( ' select distinct b1, b2, b3,b4,b5,b6,b7,b8,b9,b10, b11 , cloud_cover,  t1.datetime_itm_file as  datetime_itm_file '
                   ' from public.tbl_gee_points_bands_reflectance  t1 '
                    'join ('
                    'select point_id ,user_id, iter, satellite ,csvpath , min(cloud_cover) as mincc'
                    ' from tbl_gee_points_bands_reflectance ' )
        wherecond = (' where point_id = ' + str(point_id) + ' and user_id = ' + str(user_id) + \
                    ' and satellite =\'' + str(satellite) + '\' ' + \
                    ' and csvpath =\'' + path + '\'')
        groupby = ( ' group by point_id ,user_id, iter, satellite ,csvpath) t2 on (t1.iter = t2.iter and '
                       ' t1.point_id = t2.point_id and '
                       ' t1.user_id = t2.user_id and '
                       ' t1.satellite = t2.satellite and '
                       ' t1.csvpath = t2.csvpath and '
                       ' t1.cloud_cover = t2.mincc)  order by  t1.datetime_itm_file asc '
                            )
        query  +=  wherecond 
        query  +=  groupby
        
        #print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            b1, b2, b3,b4,b5,b6,b7,b8,b9,b10,b11 , cloud_cover, datetime_itm_file= row
            step = 120
            new_row = pd.DataFrame({ 'b1':b1, 'b2':b2, 'b3':b3, 'b4':b4, 'b5':b5, 
                                    'b6':b6, 'b7':b7, 'b8':b8,  'b9':b9, 'b10':b10,
                                    'b11':b11,  'cloud_cover': cloud_cover, 'datetime_itm_file':datetime_itm_file
                                    }, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018Listado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df

def deletePuntGeeProcesado(point_id,user_id,satellite,iter,path):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table='tbl_gee_points_bands_reflectance'
    cursor = conn.cursor()
    print("leemos los datos checkPuntGeeProcesado  satellite:" +  table)
    encontrado = 0
    step = 100

    try:
        #Leemos los datos 
        wherecond = ' where point_id = ' + str(point_id) + ' and user_id = ' + str(user_id) + \
                    ' and satellite =\'' + str(satellite) + '\' and iter =  ' + str(iter) + \
                    ' and csvpath =\'' + path + '\''
        
        deletequery = "delete from %s " % ( table) + wherecond
        cursor.execute(deletequery) 
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
    return 1

def puntosUploadCsvOC(userid,path):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    cursor = conn.cursor()
    df = pd.DataFrame()
    print("leemos los datos de para los csv procesados: tbl_gee_points_bands_reflectance")
    table_search = 'tbl_coord_tiff_reflectance'
    step = 100
    try:
        #Leemos los datos 
        query =(
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b1 as reflectance,     '
                '            \'b1\'  as band, b.survey_date, b.oc , a.user_id                                                          '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b2 as reflectance,     '
                '            \'b2\'  as band, b.survey_date, b.oc , a.user_id                                                             '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b3 as reflectance,     '
                '            \'b3\'  as band, b.survey_date, b.oc , a.user_id                                                             '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b4 as reflectance,     '
                '            \'b4\'  as band, b.survey_date, b.oc , a.user_id                                                             '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b5 as reflectance,     '
                '            \'b5\'  as band, b.survey_date, b.oc  , a.user_id                                                            '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b6 as reflectance,     '
                '            \'b6\'  as band, b.survey_date, b.oc  , a.user_id                                                            '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b7 as reflectance,     '
                '            \'b7\'  as band, b.survey_date, b.oc , a.user_id                                                             '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b8 as reflectance,     '
                '            \'b8\'  as band, b.survey_date, b.oc , a.user_id                                                             '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b8a as reflectance,    '
                '            \'b8A\'  as band, b.survey_date, b.oc , a.user_id                                                            '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b9 as reflectance,     '
                '            \'b9\'  as band, b.survey_date, b.oc, a.user_id                                                              '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b11 as reflectance,    '
                '            \'b11\'  as band, b.survey_date, b.oc  , a.user_id                                                           '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.th_long as longitud, b.th_lat as  latitud , b.point_id as id , a.csvpath, a.b12 as reflectance,    '
                '            \'b12\'  as band, b.survey_date, b.oc , a.user_id                                                            '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
        )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            longitud , latitud , id, path , reflectance , band , survey_date ,  oc , user_id = row
            step = 120
            new_row = pd.DataFrame({ 'longitud':longitud, 'latitud':latitud,'id':id,'path':path,'reflectance':reflectance,
                                    'band':band,'survey_date':survey_date,'oc':oc,'user_id':user_id}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018Listado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df


def puntosUploadCsvAiModel(userid,path):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    cursor = conn.cursor()
    df = pd.DataFrame()
    print("leemos los datos de para los csv procesados: tbl_gee_points_bands_reflectance")
    table_search = 'tbl_coord_tiff_reflectance'
    step = 100
    try:
        #Leemos los datos 
        query =(
                'select   b.point_id , b.survey_date as fecha,  \'b1\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b1 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2  '                                             
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.point_id , b.survey_date as fecha,  \'b2\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b2 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2    '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select  b.point_id , b.survey_date as fecha,  \'b3\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b3 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2   '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select  b.point_id , b.survey_date as fecha,  \'b4\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b4 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2   '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select   b.point_id , b.survey_date as fecha,  \'b5\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b5 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2   '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select   b.point_id , b.survey_date as fecha,  \'b6\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b6 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2    '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select   b.point_id , b.survey_date as fecha,  \'b7\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b7 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2    '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select   b.point_id , b.survey_date as fecha,  \'b8\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b8 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2   '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select   b.point_id , b.survey_date as fecha,  \'b8a\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b8a as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2   '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.point_id , b.survey_date as fecha,  \'b9\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b8 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2  '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.point_id , b.survey_date as fecha,  \'b11\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b11 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2   '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
                'union                                                                                                       '
                'select b.point_id , b.survey_date as fecha,  \'b12\'  as band ,  b.th_long as longitude, b.th_lat as  latitude ,   '
                '           b.oc as readvalue , a.b12 as  reflectance, 0  as ndvi , b.point_id as point_id_2, 0 as ndvi_2 '
                'FROM public.tbl_gee_points_bands_reflectance a                                                              '
                'join public.tbl_datos_archivos_csv  b on a.point_id = b.point_id and a.csvpath = b.path                     '
                'where a.user_id = ' + str(userid) + ' and a.csvpath = \'' + path + '\'  '
        )
        print(query)
        step = 120
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            point_id, fecha, band , longitude , latitude, readvalue , reflectance , ndvi , point_id_2 ,  ndvi_2  = row
            step = 120
            new_row = pd.DataFrame({ 'point_id': point_id,'fecha':fecha,'band':band,  'longitude':longitude, 'latitude':latitude,'readvalue':readvalue,
                                    'reflectance':reflectance,'ndvi':ndvi,'point_id-2':point_id_2,'ndvi-2':ndvi_2 }, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("puntosLucas2018Listado: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df