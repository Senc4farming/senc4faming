#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for senc4farming
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from flask import request, jsonify,render_template, send_from_directory, redirect
from PIL import Image,ImageSequence
from playhouse.shortcuts import dict_to_model, update_model_from_dict
from senfarming_util import  get_access_token , get_access_token_openid,create_polygon_for_point,\
                        create_polygon_for_point_offset
from senfarming import  guardardatoscoordenadastifffiles ,\
                        listarDatosSentinel, \
                        crearTablaSentinel,descargarzip,generateallbands, \
                        descomprimirzip,eliminarresultadosintermedios, \
                        obtenerPuntos,checkPuntProcesado,\
                        listarDatosSentinelNew ,guardardatoscoordenadasSent, \
                        CSVDatosSentinel,obtenerPuntosLucasPoligono,contarPuntosLucasPoligono, \
                        guardardatoscoordenadasCsv,contarPuntosLucasPoligono2015 ,\
                        obtenerPuntosLucasPoligono2015,contarPuntosLucasPoligonoOC ,\
                        obtenerPuntosLucasPoligonoOC,guardardatoscoordenadasSentOC, \
                        contarPuntosLucasPoligonoOCImproved
import sentinel_evalscript
from dateutil import parser
import json
from io import BytesIO
import os
from webutil import app, login_required, get_myself
from shapely.geometry import Polygon, mapping, shape
import logging
from sentinelsat import SentinelAPI
import pandas as pd
import json
import shutil
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import date , datetime, timedelta
from sentinelhub import (
    SHConfig,
    DataCollection,
    SentinelHubCatalog,
    SentinelHubRequest,
    BBox,
    bbox_to_dimensions,
    CRS,
    MimeType,
    Geometry,
)
import tifffile
import csv
CWD = os.getcwd()

# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))

log = logging.getLogger("api.senfarmingproc")
def sentinelhub_compliance_hook(response):
    response.raise_for_status()
    return response

def gettokenInt(client_id,client_secret):
    print('gettokenInt')
    # Create a session
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    print('antes de llaman')
    # Get token for the session
    token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                            client_secret=client_secret)

   
    print("token")
    print(token)
    return token 

@app.route('/api/proc/test/', methods = ['GET'])
def testproc():
     webutil.warn_reply("Has llamado al api de test sen4farmingproc ")
     return "Has llamado al api de test",200
@app.route('/api/proc/generarlistaRefFechasIntegradasLucas2015General/', methods = ['GET'])
def generarlistaRefFechasIntegradasGeneral2015(): 
    """Save list of files in sentinel web"""
    print('generarlistaRefFechasIntegradas')
    content = request.json
    #leemos los parámetros de entrada
    polygoncoords = content['polygon']
    offset = content['offset']
    dirstr = content['dirstr']
    cloudcover = content['cloudcover']
    mosaicking_order = content['mosaicking_order']
    sentsecret = content['sentsecret']
    #Valores posibles s2l2a , s2l1c, all
    execution_mode = content['mode']
    #Valores posibles auto , uint32, all
    prec = content['prec']
    maxccvalue = float(cloudcover)/100
    #reference valores test , jcyl, lucas2018, lucas2022, jc
    reference = 'lucas2015'
    satellite = 'sentinel'
    # config = SHConfig("Senc4farming1")
    config = SHConfig()
    if sentsecret == 'general':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET']
    elif sentsecret == 'juan':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_JUAN']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_JUAN']
    elif sentsecret == 'ubu':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_UBU']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_UBU']

    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")
    #obrtenemos el token
    token = gettokenInt(config.sh_client_id,config.sh_client_secret )

    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/appsharedfiles/' + dirstr
    tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff'

     #Del polígono sacamos el nínimo y máximo de longotud y latitud
    coords = polygoncoords.split(",")
    parts, tupla = [] , []
    j= 0
    for i in range(0,len(coords) ):
        val_coord = coords[i]
        #get lat and long
        val_coord_lst = [float(val) for val in val_coord.split(" ")]
        parts.append(val_coord_lst)
    print(parts)
    polygon = Polygon(parts)
    print(polygon.bounds)
    minmax= polygon.bounds 
    #Comprobamos que hay coordenadas de lucas 2015
    puntospordia =  contarPuntosLucasPoligono2015(minmax)
    for fila in puntospordia:
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = fila[0]
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
        #fecha con formato YYYY-MM-DD se usa el día de la muestra +-3
        dateini_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days=-3)
        datefin_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days= 3)

        df1 = pd.DataFrame()
        points = obtenerPuntosLucasPoligono2015(minmax, fecha_formato_lucas)
        for x in points:
            polygon_for_point = create_polygon_for_point_offset(x[0],x[1],offset,swap_coordinates=True)
            minmax_for_point= polygon_for_point.bounds  
            #Check if tiff files has been downloaded for the point 
            #Validate if l1c or l2a
            #Descarga de imagen con sentinel 1c
            if execution_mode == 's2l1c' or execution_mode == 'all':
                str_datacollection_type = 's2l1c'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l1c)
                    if buscarpunto == 0:
                        
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)

                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 1c
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l1c)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)

                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
            #Descarga de imagen con sentinel 2a
            if execution_mode == 's2l2a' or execution_mode == 'all':
                str_datacollection_type = 's2l2a'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l2a)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 2a
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l2a)
                    if buscarpunto == 0:
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )

    return 'Elementos procesados ',200

@app.route('/api/proc/generarlistaRefFechasIntegradasLucas2018General/', methods = ['GET'])
def generarlistaRefFechasIntegradasGeneral(): 
    """Save list of files in sentinel web"""
    print('generarlistaRefFechasIntegradas')
    content = request.json
    #leemos los parámetros de entrada
    polygoncoords = content['polygon']
    offset = content['offset']
    dirstr = content['dirstr']
    cloudcover = content['cloudcover']
    mosaicking_order = content['mosaicking_order']
    sentsecret = content['sentsecret']
    #Valores posibles s2l2a , s2l1c, all
    execution_mode = content['mode']
    #Valores posibles auto , uint32, all
    prec = content['prec']
    maxccvalue = float(cloudcover)/100
    #reference valores test , jcyl, lucas2018, lucas2022, jc
    reference = 'lucas2018'
    satellite = 'sentinel'
    # config = SHConfig("Senc4farming1")
    config = SHConfig()
    if sentsecret == 'general':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET']
    elif sentsecret == 'juan':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_JUAN']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_JUAN']
    elif sentsecret == 'ubu':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_UBU']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_UBU']

    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")
    #obrtenemos el token
    token = gettokenInt(config.sh_client_id,config.sh_client_secret )

    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/appsharedfiles/' + dirstr
    tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff'

     #Del polígono sacamos el nínimo y máximo de longotud y latitud
    coords = polygoncoords.split(",")
    parts, tupla = [] , []
    j= 0
    for i in range(0,len(coords) ):
        val_coord = coords[i]
        #get lat and long
        val_coord_lst = [float(val) for val in val_coord.split(" ")]
        parts.append(val_coord_lst)
    print(parts)
    polygon = Polygon(parts)
    print(polygon.bounds)
    minmax= polygon.bounds 
    #Comprobamos que hay coordenadas de lucas 2018 
    puntospordia =  contarPuntosLucasPoligono(minmax)
    for fila in puntospordia:
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = fila[0]
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
        #fecha con formato YYYY-MM-DD se usa el día de la muestra +-3
        dateini_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days=-3)
        datefin_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days= 3)

        df1 = pd.DataFrame()
        points = obtenerPuntosLucasPoligono(minmax, fecha_formato_lucas)
        for x in points:
            polygon_for_point = create_polygon_for_point_offset(x[0],x[1],offset,swap_coordinates=True)
            minmax_for_point= polygon_for_point.bounds  
            #Check if tiff files has been downloaded for the point 
            #Validate if l1c or l2a
            #Descarga de imagen con sentinel 1c
            if execution_mode == 's2l1c' or execution_mode == 'all':
                str_datacollection_type = 's2l1c'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l1c)
                    if buscarpunto == 0:
                        
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)

                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 1c
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l1c)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)

                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
            #Descarga de imagen con sentinel 2a
            if execution_mode == 's2l2a' or execution_mode == 'all':
                str_datacollection_type = 's2l2a'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l2a)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 2a
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l2a)
                    if buscarpunto == 0:
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )

    return 'Elementos procesados ',200

@app.route('/api/proc/generarlistaRefFechasIntegradasLucas2018GeneralOC/', methods = ['GET'])
def generarlistaRefFechasIntegradasGeneralOC(): 
    """Save list of files in sentinel web"""
    print('generarlistaRefFechasIntegradasGeneralOC')
    content = request.json
    #leemos los parámetros de entrada
    polygoncoords = content['polygon']
    offset = content['offset']
    dirstr = content['dirstr']
    cloudcover = content['cloudcover']
    mosaicking_order = content['mosaicking_order']
    sentsecret = content['sentsecret']
    #Valores posibles s2l2a , s2l1c, all
    execution_mode = content['mode']
    #Valores posibles auto , uint32, all
    prec = content['prec']
    maxccvalue = float(cloudcover)/100
    #reference valores test , jcyl, lucas2018, lucas2022, jc
    reference = content['reference']
    satellite = content['satellite']
    #periodo valores 0 -> todos los días; num -> num días sobre la fecha inicial
    numdias = content['numdias']
    numdiasint = int(numdias)
    # config = SHConfig("Senc4farming1") 
    config = SHConfig()
    if sentsecret == 'general':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET']
    elif sentsecret == 'juan':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_JUAN']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_JUAN']
    elif sentsecret == 'ubu':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_UBU']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_UBU']
    elif sentsecret == 'app':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_APP']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_APP']
    elif sentsecret == 'app1':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_APP1']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_APP1']
    
    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")
    #obrtenemos el token
    token = gettokenInt(config.sh_client_id,config.sh_client_secret )

    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/appsharedfiles/' + dirstr
    tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff'

     #Del polígono sacamos el nínimo y máximo de longotud y latitud
    coords = polygoncoords.split(",")
    parts, tupla = [] , []
    j= 0
    for i in range(0,len(coords) ):
        val_coord = coords[i]
        #get lat and long
        val_coord_lst = [float(val) for val in val_coord.split(" ")]
        parts.append(val_coord_lst)
    print(parts)
    polygon = Polygon(parts)
    print(polygon.bounds)
    minmax= polygon.bounds 
    #Comprobamos que hay coordenadas de lucas 2018 
    puntospordia =  contarPuntosLucasPoligonoOC(minmax)
    for fila in puntospordia:
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = fila[0]
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
        #fecha con formato YYYY-MM-DD se usa el día de la muestra +-3
        #dateini_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days=-3)
        #datefin_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days= 3)

        df1 = pd.DataFrame()
        points = obtenerPuntosLucasPoligonoOC(minmax, fecha_formato_lucas)
        for x in points:
            dateini_formato_sentinel = datetime.strptime(x[4],'%d/%m/%y' )
            datefin_formato_sentinel = datetime.strptime(x[5],'%d/%m/%y' )
            if numdiasint > 0:
                dateini_formato_sentinel = dateini_formato_sentinel + timedelta(days=numdiasint)
                datefin_formato_sentinel= dateini_formato_sentinel + timedelta(days=numdiasint+1)
            polygon_for_point = create_polygon_for_point_offset(x[0],x[1],offset,swap_coordinates=True)
            minmax_for_point= polygon_for_point.bounds  
            #Check if tiff files has been downloaded for the point 
            #Validate if l1c or l2a
            #Descarga de imagen con sentinel 1c
            if execution_mode == 's2l1c' or execution_mode == 'all':
                str_datacollection_type = 's2l1c'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l1c)
                    if buscarpunto == 0:
                        
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)

                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 1c
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l1c)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)

                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
            #Descarga de imagen con sentinel 2a
            if execution_mode == 's2l2a' or execution_mode == 'all':
                str_datacollection_type = 's2l2a'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l2a)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 2a
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(x[2])
                    buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l2a)
                    if buscarpunto == 0:
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,x[2],0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )

    return 'Elementos procesados ',200

@app.route('/api/proc/generarlistaRefFechasIntegradasLucas2018General11/', methods = ['GET'])
def generarlistaRefFechasIntegradasGeneral11(): 
    """Save list of files in sentinel web"""
    print('generarlistaRefFechasIntegradasGeneral11')
    content = request.json
    #leemos los parámetros de entrada
    polygoncoords = content['polygon']
    offset = content['offset']
    dirstr = content['dirstr']
    cloudcover = content['cloudcover']
    mosaicking_order = content['mosaicking_order']
    sentsecret = content['sentsecret']
    #Valores posibles s2l2a , s2l1c, all
    execution_mode = content['mode']
    #Valores posibles auto , uint32, all
    prec = content['prec']
    maxccvalue = float(cloudcover)/100
    #reference valores test , jcyl, lucas2018, lucas2022, jc
    reference = 'lucas2018OC'
    satellite = 'sentinel'
    # config = SHConfig("Senc4farming1")
    config = SHConfig()
    if sentsecret == 'general':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET']
    elif sentsecret == 'juan':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_JUAN']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_JUAN']
    elif sentsecret == 'ubu':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_UBU']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_UBU']
    elif sentsecret == 'app':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_APP']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_APP']
    elif sentsecret == 'app1':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_APP1']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_APP1']

    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")
    #obrtenemos el token
    token = gettokenInt(config.sh_client_id,config.sh_client_secret )

    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/appsharedfiles/' + dirstr
    tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff'

     #Del polígono sacamos el nínimo y máximo de longotud y latitud
    coords = polygoncoords.split(",")
    parts, tupla = [] , []
    j= 0
    for i in range(0,len(coords) ):
        val_coord = coords[i]
        #get lat and long
        val_coord_lst = [float(val) for val in val_coord.split(" ")]
        parts.append(val_coord_lst)
    print(parts)
    polygon = Polygon(parts)
    print(polygon.bounds)
    minmax= polygon.bounds 
    #Comprobamos que hay coordenadas de lucas 2018 
    puntospordia =  contarPuntosLucasPoligonoOCImproved(minmax, 2)
    for fila in puntospordia:
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = fila[0]
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
        #fecha con formato YYYY-MM-DD se usa el día de la muestra +-3
        #dateini_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days=-3)
        #datefin_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days= 3)

        df1 = pd.DataFrame()
        points = obtenerPuntosLucasPoligonoOC(minmax, fecha_formato_lucas)
        for x in points:
            dateini_formato_sentinel = datetime.strptime(x[4],'%d/%m/%y' )
            datefin_formato_sentinel = datetime.strptime(x[5],'%d/%m/%y' )
            polygon_for_point = create_polygon_for_point_offset(x[0],x[1],offset,swap_coordinates=True)
            minmax_for_point= polygon_for_point.bounds  
            #Check if tiff files has been downloaded for the point 
            #Validate if l1c or l2a
            #Descarga de imagen con sentinel 1c
            if execution_mode == 's2l1c' or execution_mode == 'all':
                str_datacollection_type = 's2l1c'
               
                tiffuserfolders2l1c = tiffuserfolder + '/all/' + str_datacollection_type + '/int16/' + str(x[2])
                buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l1c)
                if buscarpunto == 0:
                    
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolders2l1c):
                        os.makedirs(tiffuserfolders2l1c)
                    
                    dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance11(tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,x[2],0,reference,satellite,0,mosaicking_order)

                    #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                    guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                    #de inicializan lod df
                    dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                else:
                    print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
            #Descarga de imagen con sentinel 2a
            if execution_mode == 's2l2a' or execution_mode == 'all':
                str_datacollection_type = 's2l2a'
                tiffuserfolders2l2a = tiffuserfolder + '/all/' + str_datacollection_type +  '/int16/'  + str(x[2])
                buscarpunto = checkPuntProcesado(x[2],0, tiffuserfolders2l2a)
                if buscarpunto == 0:
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolders2l2a):
                        os.makedirs(tiffuserfolders2l2a)
                    dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance11(tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,x[2],0,reference,satellite,0,mosaicking_order)
                    #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                    guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
            
                    #de inicializan lod df
                    dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                else:
                    print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )
    return 'Elementos procesados ',200

@app.route('/api/proc/descomponertiffbandas/', methods = ['GET'])
def descomponertiffbandas():
    print('descomponertiffbandas')
    content = request.json
    dirstr = content['dirstr']
    reference = content['reference']
    pathfinal = content['pathfinal']
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/appsharedfiles/' + dirstr
    tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff' + '/' + pathfinal
    tifffile = tiffuserfolder + '/response.tiff'
    print('tifffile:' + tifffile )
    im = Image.open(tifffile)

    for i, page in enumerate(ImageSequence.Iterator(im)):
        tiffuserfolderpng = tiffuserfolder + '/png/'
        page.save(tiffuserfolderpng + "page%d.png" % i)
    return 'Elementos procesados ',200

@app.route('/api/proc/getreflecancecsvcoords/', methods = ['POST'])
def getreflecancecsvcoords():
    """Save list of files in sentinel web"""
    print('getreflecancecsvcoords')
    content = request.json
    #leemos los parámetros de entrada
    userid = content['userid']
    csvid = content['csvid']
    numlines = content['numlines']
    
    reference = 'csvfile'
    # config = SHConfig("Senc4farming1")
    config = SHConfig()
    config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID']
    config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET']
    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")
    #obrtenemos el token
    token = gettokenInt(config.sh_client_id,config.sh_client_secret )

    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/appcsvfiles/' + '0' 
    tiffuserfolder = userfolder + '/' + str(userid) + '/' + str(csvid) +  '/tiff'

    print(tiffuserfolder)
    num = 1
    while num <= numlines:
        coordvalues = content['linea' + str(num)]
        #convert string to  object
        #json_object = json.loads(coordvalues)
        json_object = coordvalues
        long = coordvalues['longitude']
        lat = coordvalues['latitude']
        date_str = coordvalues['date']
        soc = coordvalues['soc']

        print('coordvalues')
        print(coordvalues)
        print (long)
        #get dates for searching info
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = date_str
        print('date_str: ' + date_str)
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%Y' )
        #fecha con formato YYYY-MM-DD se usa el día de la muestra +-3
        dateini_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days=-3)
        datefin_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days= 3)
        #Save tiff file
        polygon_for_point = create_polygon_for_point(float(long),float(lat),swap_coordinates=True)
        minmax_for_point= polygon_for_point.bounds
        maxccvalue = 0.1
        #-----------------------s2l1c---------------------------
        #Descarga de imagen con sentinel 1c
        str_datacollection_type = 's2l1c'
        #create tiff folder if does not exists
        tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/band'
        if not os.path.exists(tiffuserfolders2l1c):
            os.makedirs(tiffuserfolders2l1c)
        
        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffDN(tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,csvid,num,reference,userid)
        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
        #de inicializan lod df
        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
        #-----------------------s2l2a---------------------------
        #create tiff folder if does not exists
        str_datacollection_type = 's2l2a'
        tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type   + '/band'
        if not os.path.exists(tiffuserfolders2l2a):
            os.makedirs(tiffuserfolders2l2a)
        
        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffDN(tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,csvid,num,reference,userid)
        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
        #de inicializan lod df
        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
        #Read tiff file and save reflectance
        guardardatoscoordenadasCsv(json_object,userid,csvid,num,0)
        num += 1
    return 'Elementos procesados ',200

@app.route('/api/proc/guardarReflectanciasRefFechasIntegradasLucas2018/', methods = ['GET'])
def guardarReflectanciasRefFechasIntegradas():
    """Save list of files in sentinel web """
    print('guardarReflectanciasRefFechasIntegradas')
    content = request.json
    #leemos los parámetros de entrada
    reference = content['reference']
    guardardatoscoordenadasSent(reference,0)
    return 'Elementos guardados ',200

@app.route('/api/proc/guardarReflectanciasRefFechasIntegradasLucas2018OC/', methods = ['GET'])
def guardarReflectanciasRefFechasIntegradasOC():
    """Save list of files in sentinel web"""
    print('guardarReflectanciasRefFechasIntegradasOC')
    content = request.json
    #leemos los parámetros de entrada
    reference = content['reference']
    version = content['version']
    guardardatoscoordenadasSentOC(reference,version)
    return 'Elementos guardados ',200



@app.route('/api/proc/listar/', methods = ['GET'])
def listar():
    """Returns list of files in sentinel web"""

    input = request.args
    reference = input.get('reference')
    if reference:
        df = listarDatosSentinel('tbl_lista_archivos_sentinel',reference)
        return df.to_json(), 200
    else:
        print("Datos mínimos para la busqueda referencia")
        print("-reference T34VFL")
        return "Datos mínimos para la busqueda referencia",400
        
@app.route('/api/proc/listarnew/', methods = ['GET'])
def listarnew():
    """Returns list of files in sentinel web"""
    input = request.args
    reference = input.get('reference')
    userid = input.get('userid')
    if reference:
        df = listarDatosSentinelNew('tbl_lista_archivos_sentinel_new',reference,userid)
        return df.to_json(), 200
    else:
        print("Datos mínimos para la busqueda referencia")
        print("-reference T34VFL")
        return "Datos mínimos para la busqueda referencia",400


@app.route('/api/copsh/proc/download/csv/', methods = ['POST'])
def downloadcsvcopsh(): 
    """Save list of files in sentinel web"""
    print('generarlistaRefFechasIntegradasGeneralOC copsh')
    content = request.json
    #parametros obligatorios
    user_id = content['user_id']
    dirstr = content['dirstr']
    offset = content['offset']
    num_offset= float(offset)
    num_cloud = content['cloudcover']
    maxccvalue = float(num_cloud)/100
    satellite = content['satellite']
    reference = content['reference']
    pathcsv = content['path']
   
    mosaicking_order = content['mosaickingorder']
    sentsecret = content['sentsecret']
    #Valores posibles s2l2a , s2l1c, all
    execution_mode = content['mode']
    #Valores posibles auto , uint32, all
    prec = content['prec']
    #reference valores test , jcyl, lucas2018, lucas2022, jc
    reference = content['reference']
    #periodo valores 0 -> todos los días; num -> num días sobre la fecha inicial
    numdias = content['numdias']
    numdiasint = int(numdias)
    # config = SHConfig("Senc4farming1") 
    config = SHConfig()
    
    if sentsecret == 'general':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET']
    elif sentsecret == 'juan':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_JUAN']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_JUAN']
    elif sentsecret == 'ubu':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_UBU']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_UBU']
    elif sentsecret == 'app':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_APP']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_APP']
    elif sentsecret == 'app1':
        config.sh_client_id = srvconf['PYSRV_SENTINEL_CLIENT_ID_APP1']
        config.sh_client_secret =  srvconf['PYSRV_SENTINEL_SECRET_APP1']
    
    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")
    #obrtenemos el token
    token = gettokenInt(config.sh_client_id,config.sh_client_secret )

    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/appsharedfiles/' + str(dirstr)
    tiffuserfolder = userfolder + '/' + str(reference) + '/' + '0' +  '/tiff'

    # Create an empty DataFrame with column names to read csv
    df = pd.DataFrame(columns=['depth','point_id','ph_cacl2','ph_h2o','ec',
                               'oc','caco3','n','k','th_lat',
                               'th_long','survey_date','elev','lc','lu',
                               'lc0_desc','lc1_desc','lu1_desc','date_ini_search','date_end_search',
                               'path'])
    
    #Leemos el CSV en un data frame
    # Open file 
    file = open(pathcsv, "r")
    data = list(csv.reader(file, delimiter=";"))
    file.close()
    for i in range(1,len(data)):
        
        print(data[i][0])
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = data[i][5]
        print("fecha_formato_lucas" +  fecha_formato_lucas)
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%Y' )
        print('Comienza el dia  : '+ fecha_formato_lucas)

        dateini_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days=-numdiasint)
        datefin_formato_sentinel = datetime_fecha_formato_lucas + timedelta(days=numdiasint)


        #Insertamos el valor en dl dataframe
        df.loc[len(df.index)] = [data[i][0],data[i][1],-1,-1,-1,
                                 data[i][2],-1,-1,-1,float(data[i][3]),
                                 float(data[i][4]), data[i][5], data[i][6],'N/A','N/A',
                                 data[i][7],data[i][8],data[i][9],dateini_formato_sentinel, datefin_formato_sentinel,
                                 pathcsv]

        long = float(data[i][4])
        lat = float(data[i][3])
        point_id =data[i][1]

        df1 = pd.DataFrame()
        polygon_for_point = create_polygon_for_point_offset(long,lat,offset,swap_coordinates=True)
        minmax_for_point= polygon_for_point.bounds  
        #Sentinel o landstat
        if satellite == 'sentinel':
            #Check if tiff files has been downloaded for the point 
            #Validate if l1c or l2a
            #Descarga de imagen con sentinel 1c
            if execution_mode == 's2l1c' or execution_mode == 'all':
                str_datacollection_type = 's2l1c'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(point_id)
                    buscarpunto = checkPuntProcesado(point_id,0, tiffuserfolders2l1c,satellite)
                    if buscarpunto == 0:
                        
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,point_id,0,reference,satellite,0,mosaicking_order)

                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 1c
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l1c = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/' + str(point_id)
                    buscarpunto = checkPuntProcesado(point_id,0, tiffuserfolders2l1c)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l1c):
                            os.makedirs(tiffuserfolders2l1c)
                        
                        dffiles_str_l1c = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l1c, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,point_id,0,reference,satellite,0,mosaicking_order)
                        #Se almadena el valor guardado para buscar el vector de reflectancia
                        df1 = dffiles_str_l1c.copy()
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l1c,0)
                        #de inicializan lod df
                        dffiles_str_l1c = pd.DataFrame(columns=dffiles_str_l1c.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l1c +  '-- ya está procesado.' )
            #Descarga de imagen con sentinel 2a
            if execution_mode == 's2l2a' or execution_mode == 'all':
                str_datacollection_type = 's2l2a'
                if prec == 'auto' or prec == 'all':
                    str_unit = 'AUTO'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(point_id)
                    buscarpunto = checkPuntProcesado(point_id,0, tiffuserfolders2l2a,satellite)
                    if buscarpunto == 0:
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,point_id,0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )
                #Descarga de imagen con sentinel 2a
                if prec == 'uint32' or prec == 'all':
                    str_unit = 'FLOAT32'
                    tiffuserfolders2l2a = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(point_id)
                    buscarpunto = checkPuntProcesado(point_id,0, tiffuserfolders2l2a,satellite)
                    if buscarpunto == 0:
                        if not os.path.exists(tiffuserfolders2l2a):
                            os.makedirs(tiffuserfolders2l2a)
                        dffiles_str_l2a = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders2l2a, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,point_id,0,reference,satellite,0,mosaicking_order)
                        #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                        guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                        #Se almadena el valor guardado para buscar el vector de reflectancia
                        df1 = dffiles_str_l2a.copy()
                        #de inicializan lod df
                        dffiles_str_l2a = pd.DataFrame(columns=dffiles_str_l2a.columns)
                    else:
                        print('El punto para el path :'+tiffuserfolders2l2a +  '-- ya está procesado.' )
        if satellite == 'landsat':
            str_datacollection_type = 'landsat'
            if prec == 'auto' or prec == 'all':
                str_unit = 'AUTO'
                tiffuserfolders = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(point_id)
                buscarpunto = checkPuntProcesado(point_id,0,tiffuserfolders ,satellite)
                if buscarpunto == 0:
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolders):
                        os.makedirs(tiffuserfolders)
                    dffiles_str_landsat = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,point_id,0,reference,satellite,0,mosaicking_order)
                    #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                    guardardatoscoordenadastifffiles(dffiles_str_landsat,0)
            
                    #de inicializan lod df
                    dffiles_str_landsat = pd.DataFrame(columns=dffiles_str_landsat.columns)
                else:
                    print('El punto para el path :'+tiffuserfolders +  '-- ya está procesado.' )
            #Descarga de imagen con sentinel 2a
            if prec == 'uint32' or prec == 'all':
                str_unit = 'FLOAT32'
                tiffuserfolders = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit + '/'  + str(point_id)
                buscarpunto = checkPuntProcesado(point_id,0, tiffuserfolders,satellite)
                if buscarpunto == 0:
                    if not os.path.exists(tiffuserfolders):
                        os.makedirs(tiffuserfolders)
                    dffiles_str_landsat = sentinel_evalscript.saveAllBandsTiffReflectance(str_unit,tiffuserfolders, str_datacollection_type ,0,minmax_for_point,dateini_formato_sentinel,datefin_formato_sentinel,config,maxccvalue ,token,point_id,0,reference,satellite,0,mosaicking_order)
                    #Guardamos los datos en la bbdd asociados a los puntos para buscar mas tarde replectancias
                    guardardatoscoordenadastifffiles(dffiles_str_l2a,0)
                    #Se almadena el valor guardado para buscar el vector de reflectancia
                    df1 = dffiles_str_landsat.copy()
                    #de inicializan lod df
                    dffiles_str_landsat = pd.DataFrame(columns=dffiles_str_landsat.columns)
                else:
                    print('El punto para el path :'+tiffuserfolders +  '-- ya está procesado.' )

        #Read tiff file and save reflectance
        #guardardatoscoordenadasSentOC(reference,version)
    return 'Elementos procesados ',200


@app.route('/api/proc/liberarespacio/', methods = ['GET'])
def liberarespacio():
    eliminarresultadosintermedios()
    return 200
