#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for hgmd
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca

from flask import request, jsonify, g
from playhouse.shortcuts import dict_to_model, update_model_from_dict
from senfarming_util import get_tallinn_polygon_ge , create_polygon_for_point
from senfarming import  guardardatosbusquedaSentinel ,listarDatosSentinel, \
                        crearTablaSentinel,descargarzip,generateallbands, \
                        descomprimirzip,eliminarresultadosintermedios, \
                        guardardatoscoordenadas ,leercsvcyl,leercsvjuancarlos, \
                        obtenerPuntos,moverdatosaproc,borrardatosbusquedaSentinel ,\
                        leercoordLucas
import webutil
import json
from io import BytesIO
import os
from webutil import app, login_required, get_myself

import logging
from sentinelsat import SentinelAPI
import pandas as pd

# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))

log = logging.getLogger("api.senfarming")

@app.route('/api/test/', methods = ['GET'])
def test():
     return webutil.warn_reply("Has llamado al api de test")

@app.route('/api/test1/', methods = ['GET'])
def test1():
    input = request.args
    reference = input.get('reference')
    leercoordLucas()
    return "test 1 ejecutado",200

@app.route('/api/generarlista2A/', methods = ['GET'])
def generarlista():
    """Save list of files in sentinel web"""

    input = request.args
    hub = SentinelAPI(srvconf['PYSRV_USERNAME'], srvconf['PYSRV_PASSWORD'], "https://scihub.copernicus.eu/dhus")
    reference = input.get('reference')
    dateini = input.get('dateini')
    datefin = input.get('datefin')
    keyboard = input.get('keyboard') 
    polygonxml = input.get('polygon')
    if dateini and datefin:
        data_products = hub.query(
            get_tallinn_polygon_ge(polygonxml,swap_coordinates=True),  # which area interests you
            date=(dateini, datefin),
            cloudcoverpercentage=(0, 10),  # we don't want clouds
            platformname="Sentinel-2",
            processinglevel="Level-2A"  # more processed, ready to use data
        )
        data_products = hub.to_geodataframe(data_products)
        if keyboard:
            # we want to avoid downloading overlapping images, so selecting by this keyword
            data_products = data_products[data_products["title"].str.contains(keyboard)]
        print(data_products)
        # then for the conversion, I drop the last column (geometry) and specify the column names for the new df
        df1 = pd.DataFrame(data_products.iloc[:,:-1].values, columns = list(data_products.columns.values)[:-1] )
        guardardatosbusquedaSentinel(df1,'tbl_lista_archivos_sentinel',reference)
        return df1.to_json(), 200
    else:
        print("Datos mínimos para la busqueda fecha inicio y fecha fin")
        print("-a listar -i 20230101 -f 20230405 -k T34VFL")
        return "Datos mínimos para la busqueda fecha inicio y fecha fin",400
    
@app.route('/api/generarlistaRef/', methods = ['GET'])
def generarlistaRef():
    """Save list of files in sentinel web"""

    input = request.args
    hub = SentinelAPI(srvconf['PYSRV_USERNAME'], srvconf['PYSRV_PASSWORD'], "https://scihub.copernicus.eu/dhus")
    #reference valores test , jcyl, y jc
    refpuntos = input.get('refpuntos')
    reference = input.get('reference')
    dateini = input.get('dateini')
    datefin = input.get('datefin')
    keyboard = input.get('keyboard')
    #texto a añadir en el where
    dbfilter = input.get('filter')
    df1 = pd.DataFrame()
    if dateini and datefin:
        #Obtenemos un polígono por cadapunto a estudiar
        points = obtenerPuntos(refpuntos,dbfilter)
        borrardatosbusquedaSentinel('tbl_lista_archivos_sentinel_proc',reference)
        for x in points:
            data_products = hub.query(
            create_polygon_for_point(x[0],x[1],swap_coordinates=True),  # which area interests you
            date=(dateini, datefin),
            cloudcoverpercentage=(0, 10),  # we don't want clouds
            platformname="Sentinel-2",
            processinglevel="Level-2A"  # more processed, ready to use data
            )
            data_products = hub.to_geodataframe(data_products)
            if keyboard:
                # we want to avoid downloading overlapping images, so selecting by this keyword
                data_products = data_products[data_products["title"].str.contains(keyboard)]
            print('data_products')
            print(data_products)
            # then for the conversion, I drop the last column (geometry) and specify the column names for the new df
            df1 = pd.DataFrame(data_products.iloc[:,:-1].values, columns = list(data_products.columns.values)[:-1] )
            guardardatosbusquedaSentinel(df1,'tbl_lista_archivos_sentinel_proc',reference)
        moverdatosaproc(reference)
        return df1.to_json(), 200
    else:
        print("Datos mínimos para la busqueda referencia")
        print("-reference T34VFL")
        return "Datos mínimos para procesar referencia",400
    '''
       
        
    else:
        print("Datos mínimos para la busqueda fecha inicio y fecha fin")
        print("-a listar -i 20230101 -f 20230405 -k T34VFL")
        return "Datos mínimos para la busqueda fecha inicio y fecha fin",400
    '''
@app.route('/api/procesarlista2A/', methods = ['GET'])
def procesarlista(): 
    """Proccess list of files in sentinel web"""
    input = request.args
    reference = input.get('reference')
    optguardado = input.get('origen')
    if reference:
        df = listarDatosSentinel('tbl_lista_archivos_sentinel',reference)
        print(df[40])
        #Recorremos la lista de archivos y procesamos los archivos
        for ind in df.index:
            #Descargamos un zip por cada archivo y lo descomprimimos
            dict_descarga= descargarzip(df.at[df.index[ind],40])
            #Generemos los .tiff
            productname = generateallbands(df.at[df.index[ind],1])
            #Obtenemos los valores para un conjunto de coordenadas
            print('Guardando valores para coordenadas, procesando: ' + productname )
            #Guardamos los datos para las coordenadas
            print('Guardando valores para coordenadas, procesando: ' + df.at[df.index[ind],1] )
            guardardatoscoordenadas(df.at[df.index[ind],1],optguardado) 
            #Eliminamos resultados intermedios
            eliminarresultadosintermedios()


        return df.to_json(), 200
    else:
        print("Datos mínimos para la busqueda referencia")
        print("-reference T34VFL")
        return "Datos mínimos para procesar referencia",400

@app.route('/api/listar/', methods = ['GET'])
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
        

@app.route('/api/procesarlistapasos/', methods = ['GET'])
def procesarlistapasos():
    """Proccess list of files in sentinel web"""
    input = request.args
    reference = input.get('reference')
    optguardado = input.get('origen')
    if reference:
        df = listarDatosSentinel('tbl_lista_archivos_sentinel',reference)
        print(df[1])
        #Recorremos la lista de archivos y procesamos los archivos
        for ind in df.index:
            #Descargamos un zip por cada archivo y lo descomprimimos
            #dict_descarga= descargarzip(df.at[df.index[ind],40])
            descomprimirzip(df.at[df.index[ind],1]) 
            #Generemos los .tiff
            productname = generateallbands(df.at[df.index[ind],1])
            #Obtenemos los valores para un conjunto de coordenadas
            print('Guardando valores para coordenadas, procesando: ' + productname )
            #Guardamos los datos para las coordenadas
            print('Guardando valores para coordenadas, procesando: ' + df.at[df.index[ind],1] )
            guardardatoscoordenadas(df.at[df.index[ind],1],optguardado) 
            #Eliminamos resultados intermedios
            eliminarresultadosintermedios()
            
            


        return df.to_json(), 200
    else:
        print("Datos mínimos para la busqueda referencia")
        print("-reference T34VFL")
        return "Datos mínimos para procesar referencia",400

@app.route('/api/guardardatoscoordenadas/', methods = ['GET'])
def guardardatos():
    """Proccess list of files in sentinel web"""
    input = request.args
    reference = input.get('reference')
    optguardado = input.get('origen')
    if reference:
        df = listarDatosSentinel('tbl_lista_archivos_sentinel',reference)
        print(df[1])
        #Recorremos la lista de archivos y procesamos los archivos
        for ind in df.index:
            #Guardamos los datos para las coordenadas
            print('Guardando valores para coordenadas, procesando: ' + df.at[df.index[ind],1] )
            guardardatoscoordenadas(df.at[df.index[ind],1],optguardado) 
        return df.to_json(), 200
    else:
        print("Datos mínimos para la busqueda referencia")
        print("-reference T34VFL")
        return "Datos mínimos para procesar referencia",400
    



@app.route('/api/liberarespacio/', methods = ['GET'])
def liberarespacio():
    eliminarresultadosintermedios()
    return 200
'''
@app.route('/api/cargardatosarchivo/', methods = ['GET'])
def cargardatosarchivo():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

@app.route('/api/descargar/', methods = ['GET'])
def descargar():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

@app.route('/api/descomprimir/', methods = ['GET'])
def descomprimir():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

@app.route('/api/procesar_stiky/', methods = ['GET'])
def procesar_stiky():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

@app.route('/api/procesar_gdal/', methods = ['GET'])
def procesar_gdal():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

@app.route('/api/shpfile/', methods = ['GET'])
def shpfile():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200


@app.route('/api/coord_values/', methods = ['GET'])
def coord_values():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200


@app.route('/api/hist/', methods = ['GET'])
def hist():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

@app.route('/api/coord_todas/', methods = ['GET'])
def coord_todas():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

@app.route('/api/coord_polygon/', methods = ['GET'])
def coord_polygon():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200

'''