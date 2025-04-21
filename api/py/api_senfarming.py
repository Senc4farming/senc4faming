#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for senc4farming
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from flask import request, jsonify,render_template, send_from_directory, redirect
from PIL import Image
from playhouse.shortcuts import dict_to_model, update_model_from_dict
from senfarming import  guardardatosbusquedaSentinel ,listarDatosSentinel, \
                        crearTablaSentinel, leercsvlucas2015info,puntosLucas2018ListadoOC ,\
                        leercsvlucas2018OCinfo,puntoscsvusuario
from dateutil import parser
import sentinel_evalscript
import webutil
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
import datetime
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import date
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

CWD = os.getcwd()

# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))

log = logging.getLogger("api.senfarming")


   
   

@app.route('/api/test/', methods = ['GET'])
def test():
     webutil.warn_reply("Has llamado al api de test")
     return "Has llamado al api de test",200

@app.route('/api/cargamanualtablascript/', methods = ['GET'])
def cargacript():
     #leercsvlucas2015info()
     leercsvlucas2018OCinfo()
     return "Has llamado al api de test",200

@app.route('/api/generarcreate/', methods = ['GET'])
def generacreate():
    json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((12.655118166047592 47.44667197521409,21.39065656328509 48.347694733853245,28.334291357162826 41.877123516783655,17.47086198383573 40.35854475076158,12.655118166047592 47.44667197521409))') and ContentDate/Start gt 2022-05-20T00:00:00.000Z and ContentDate/Start lt 2022-05-21T00:00:00.000Z").json()
    df = pd.DataFrame.from_dict(json['value'])
    crearTablaSentinel(df,'tbl_lista_archivos_sentinel')
    return "Create table generated check logs",200

@app.route('/api/generarlista2ANew/', methods = ['POST'])
def generarlistaNew():
    #read access token
    #access_token = get_access_token(srvconf['PYSRV_SENTINEL_USERNAME'],  srvconf['PYSRV_SENTINEL_PASSWORD'])
    """Save list of files in sentinel web
    json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((12.655118166047592 47.44667197521409,21.39065656328509 48.347694733853245,28.334291357162826 41.877123516783655,17.47086198383573 40.35854475076158,12.655118166047592 47.44667197521409))') and ContentDate/Start gt 2022-05-20T00:00:00.000Z and ContentDate/Start lt 2022-05-21T00:00:00.000Z").json()
    df = pd.DataFrame.from_dict(json['value'])

    json = requests.get("https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?cloudCover=[0,10]&startDate=2021-06-21T00:00:00Z&completionDate=2021-09-22T23:59:59Z&lon=21.01&lat=52.22").json()
    pd.DataFrame.from_dict(json['features']).head(3)

    # Print only specific columns
    columns_to_print = ['Id', 'Name','S3Path','ModificationDate','Online','OriginDate','PublicationDate']  
    df[columns_to_print].head(3)"""
    #input = request.args
         
    print('en api/generarlista2ANew ')
    content = request.json

    


    reference = content['reference']
    userid = content['userid']
    groupid = content['groupid']
    dateini = content['dateini']
    datefin = content['datefin']
    polygoncoords = content['polygon']
    cloudcover = content['cloudcover']
    
    if dateini and datefin:
        requestText = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter="
        #item for dates
        requestText +=  "ContentDate/Start gt " + dateini + "T00:00:00.000Z "
        requestText +=  " and ContentDate/Start lt " + datefin + "T00:00:00.000Z "
        #item for polygon
        requestText +=  " and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON(("+polygoncoords + "))')"
        #filter for sentinel2 
        requestText +=  " and contains(Name,'S2A')"
        #filter for cloudcover 
        requestText +=  " and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le "+ str(cloudcover) +")"
        print("la url es: " + requestText)
        try:
            response = requests.get(requestText)
            print('status_code:'+ str(response.status_code))
            columns_to_print = ['Id', 'Name','S3Path','ModificationDate','Online','OriginDate','PublicationDate','Footprint','GeoFootprint']  
            jsonrequest = response.json()
        
            dftodo = pd.DataFrame.from_dict(jsonrequest['value'])
            df=dftodo[columns_to_print]
            guardardatosbusquedaSentinel(df,'tbl_lista_archivos_sentinel_new',reference,userid, groupid)
            print("generarlista2ANew datos guardados: " + requestText)
            response.raise_for_status()
            return df.to_json(), 200
        except requests.JSONDecodeError:
            return "Error en llamada a copernicus jsondecode:" + str(response.reason) + ';' + str(response.status_code),400
        except requests.exceptions.HTTPError as errh: 
            print("HTTP Error") 
            print(errh.args[0]) 
            return "Error en llamada a copernicus:" + "HTTP Error",400 
        except requests.exceptions.ReadTimeout as errrt: 
            print("Time out") 
            return "Error en llamada a copernicus:" + "Time out",400
        except requests.exceptions.ConnectionError as conerr: 
            print("Connection error") 
            return "Error en llamada a copernicus:" + "Connection error",400
        except requests.exceptions.RequestException as errex: 
            print("Exception request") 
            return "Error en llamada a copernicus:" + "Exception request",400
        except Exception as e:
            try:
                error_json = response.json()
                print(error_json)
                return error_json,400
            except:
                return "Error en llamada a copernicus:" + str(response.text),400
    else:
        print("Datos mínimos para la busqueda fecha inicio y fecha fin")
        print("-a listar -i 20230101 -f 20230405 -k T34VFL")
        return "Datos mínimos para la busqueda fecha inicio y fecha fin",400


@app.route('/api/sentinel/checkpolygosize/', methods = ['POST'])
def checkpolygosize():
    print('checkpolygosize')
    content = request.json
    #leemos los parámetros de entrada
    reference = content['reference']
    userid = content['userid']
    queryid = content['queryid']
    datejson = content['date']
    polygoncoords = content['polygon']
    #geofootprint= content['geofootprint']
    cloudcover = content['cloudcover']
    sentinelfilename = content['sentinelfilename']
    sentinelfileid = content['sentinelfileid']
    offset = content['offset']
    clienteid = content['clienteid']
    secret = content['secret']
    token = content['token']
        
    
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
  
    result = sentinel_evalscript.saveAllBandsTiffCheckSize(offset,minmax)
    
    return result,200

@app.route('/api/sentinel/decargartiffbandas/', methods = ['POST'])
def decargartiffbandas():
    print('decargartiffbandas')
    content = request.json
    #leemos los parámetros de entrada
    reference = content['reference']
    userid = content['userid']
    queryid = content['queryid']
    datejson = content['date']
    polygoncoords = content['polygon']
    #geofootprint= content['geofootprint']
    cloudcover = content['cloudcover']
    sentinelfilename = content['sentinelfilename']
    sentinelfileid = content['sentinelfileid']
    offset = content['offset']
    clienteid = content['clienteid']
    secret = content['secret']
    token = content['token']
        
    #set up date from and date to
    # 2023-09-25T19:11:34.138Z
    dateread = parser.parse(datejson)
    dateread = dateread.replace(hour=0, minute=0, second=0, microsecond=0) 
    print(dateread)
    enddate = dateread + datetime.timedelta(days=1)
    print(enddate)
    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/userfiles/' + str(userid)
    tiffuserfolder = userfolder + '/' + reference + '/' + str(queryid) +  '/tiff'
    jp2userfolder = userfolder + '/' + reference + '/' + str(queryid) +  '/jp2'
    # config = SHConfig("Senc4farming1")
    config = SHConfig()
    config.sh_client_id = clienteid
    config.sh_client_secret =  secret
    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")

    print('decargartiffbandas 10')

    dffiles_final = pd.DataFrame()
    dffiles = pd.DataFrame()
    dffiles02 = pd.DataFrame()
    #polygon handling 
    #create shp from coords
    #split over coods
    #-3.683528642004319 42.29511966573258,-3.679380123297809 42.301402752089,-3.680710612979148 42.30127347013828,-3.683280108931597 42.30023457260301,-3.683528642004319 42.29511966573258

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

    #Validate if l1c or l2a
    str_l1c='MSIL1C'
    str_l2a='MSIL2A'
    maxccvalue = float(cloudcover)/100
    #Descarga de imagen con sentinel 1c
    if str_l1c in sentinelfilename:
        str_datacollection_type = 's2l1c'
    #Descarga de imagen con sentinel 2a
    if str_l2a in sentinelfilename:
        str_datacollection_type = 's2l2a'
    #create tiff folder if does not exists
    dffiles = pd.DataFrame()
    str_unit = 'AUTO'
    tiffuserfolder1 = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit 
    if not os.path.exists(tiffuserfolder1):
        os.makedirs(tiffuserfolder1)
    else:
        shutil.rmtree(tiffuserfolder1, ignore_errors=True)
        os.makedirs(tiffuserfolder1)
        
    dffilesauto = sentinel_evalscript.saveAllBandsTiff(str_unit,dffiles,tiffuserfolder1, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue ,token,0,'')
    
    dffiles = dffilesauto
    str_unit = 'UINT16'
    tiffuserfolder1 = tiffuserfolder + '/' + str_datacollection_type + '/' + str_unit 
    if not os.path.exists(tiffuserfolder1):
        os.makedirs(tiffuserfolder1)
    else:
        shutil.rmtree(tiffuserfolder1, ignore_errors=True)
        os.makedirs(tiffuserfolder1)
        
    dffilesfloat32 = sentinel_evalscript.saveAllBandsTiff(str_unit,dffiles,tiffuserfolder1, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue ,token,0,'')

    return dffilesfloat32.to_json(),200

def raise_on_error(response):
    response.raise_for_status()
    return response

@app.route('/api/sentinel/gettoken/', methods = ['POST'])
def gettoken():
    print('gettoken')
    content = request.json

    # Your client credentials
    client_id = content["client_id"]
    client_secret = content["client_secret"]
    # Create a session
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.register_compliance_hook('access_token_response', raise_on_error)
    print('antes de llamar para credenciales')
    try:
    # Get token for the session
        token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                            client_secret=client_secret)
        print("Evaluando la respuesta")
        print(token)
        return token,200
    except requests.exceptions.HTTPError as errh:
        print ("*********Http Error:",errh)
        errtxt = errh.response.text
        print ("*********Http Error text:",errtxt)
        if errtxt.find('Invalid client or Invalid client credentials',0,len(errtxt)) == -1:
            raise SystemExit(errh)
        else:
            return 'Invalid client or Invalid client credentials',401
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        raise SystemExit(errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        raise SystemExit(errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        print(err.response)
        raise SystemExit(err)




@app.route('/api/sentinel/executeevalscript/', methods = ['POST'])
def executeevalscript():
    print('executeevalscript')
    content = request.json
    #leemos los parámetros de entrada
    userid = content['userid']
    queryid = content['queryid']
    offset = content['offset']
    dateini = content['dateini']
    datefin = content['datefin']
    polygoncoords = content['polygon']
    collection = content['collection']
    clienteid = content['clienteid']
    secret = content['secret']
    token = content['token']
    maxcloudcoverage = content['maxcloudcoverage']
    script = content['script']
    resolution = content['resolution']

    
    print("clienteid:" +  clienteid)
    print("secret:" + secret)
    #check if user forder exists
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    userfolder = data_safe + '/userfiles/evalscript/' + str(userid)
    tiffuserfolder = userfolder + '/' + str(queryid) +  '/tiff'
    

    # config = SHConfig("Senc4farming1")
    config = SHConfig()
    #config.sh_client_id = 'sh-1ce7644d-d691-4679-9237-b66038cb0906'
    #config.sh_client_secret =  'vMcH8mHR1nh3MVB9JrAQu6TGIYeB4ct1'
    config.sh_client_id = clienteid 
    config.sh_client_secret = secret
    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    #config.save("Senc4farming1")
    #adaptamos el mac cloud coverage
    maxccvalue = float(maxcloudcoverage)/100

    print('executeevalscript 10')

    
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

    str_datacollection_type = collection
    #create tiff folder if does not exists
    tiffuserfolder = tiffuserfolder + '/' + str_datacollection_type
    if not os.path.exists(tiffuserfolder):
        os.makedirs(tiffuserfolder)
    else:
        shutil.rmtree(tiffuserfolder, ignore_errors=True)
        os.makedirs(tiffuserfolder)
        
    dffiles = sentinel_evalscript.saveEvalScripTiff(tiffuserfolder, str_datacollection_type ,offset,minmax,dateini, datefin,config,maxccvalue,script,resolution, token)
    return dffiles.to_json(),200

@app.route('/api/obtenerreflectancia/', methods = ['GET'])
def obtenerreflectancia():
    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    # Your client credentials
    client_id = 'sh-1ce7644d-d691-4679-9237-b66038cb0906'
    client_secret = 'vMcH8mHR1nh3MVB9JrAQu6TGIYeB4ct1'

    # Create a session
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    # Get token for the session
    token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                            client_secret=client_secret)


    
    print("antes de la url")
    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    print(url)
    response = oauth.post(url, json=sentinel_evalscript.request)
    if response.status_code == 200:
        
        target_path=data_safe + '/descargatest.png'
        with open(target_path, 'wb') as f:
            f.write(response.content)
        return "Llamada correcta", 200
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return f"Error: {response.status_code}", 400
    
# retrieve file from 'static/images' directory
@app.route('/api/obtenerlucas2018proc/', methods = ['POST'])
def obtenerlucas2018proc():
    print('obtenerlucas2018proc')
    content = request.json
    #leemos los parámetros de entrada
    userid = content['userid']
    polygoncoords = content['polygon']
    ref = content['ref']

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


    #Obtenemos los parametros minimo y max del poligono
    dfdata = puntosLucas2018ListadoOC(minmax,ref )
    return dfdata.to_json(),200


# retrieve file from 'static/images' directory
@app.route('/api/obtenerreflectancecsv/', methods = ['POST'])
def obtenerreflectancecsv():
    print('obtenerreflectancecsv')
    content = request.json
    #leemos los parámetros de entrada
    userid = content['userid']
    csvid = content['csvid']
    
    dfdata = puntoscsvusuario(userid,csvid   )
    return dfdata.to_json(),200
    
# retrieve file from 'static/images' directory


@app.route('/api/tiff/<path:path>')
def send_report(path):
    return send_from_directory('/app/files/src_data_safe/userfiles', path)


@app.route('/api/sentinel/descargartiff/', methods = ['GET'])
def descarcartiffsentinel():
    config = SHConfig("Senc4farming1")
    '''config = SHConfig()
    config.sh_client_id = 'sh-1ce7644d-d691-4679-9237-b66038cb0906'
    config.sh_client_secret =  'vMcH8mHR1nh3MVB9JrAQu6TGIYeB4ct1'
    config.sh_token_url = sentinel_evalscript.sh_token_url
    config.sh_base_url = sentinel_evalscript.sh_base_url
    config.save("Senc4farming1")'''
    betsiboka_coords_wgs84 = (46.16, -16.15, 46.51, -15.58)
    resolution = 60
    betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
    betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)


    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
    request_true_color = SentinelHubRequest(
        evalscript=sentinel_evalscript.evalscript_true_color,
        data_folder=data_safe,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C.define_from(
                    "s2l1c", service_url=config.sh_base_url
                ),
                time_interval=("2020-06-12", "2020-06-13"),
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=betsiboka_bbox,
        size=betsiboka_size,
        config=config,
    )
    true_color_imgs = request_true_color.get_data()
    print(
        f"Returned data is of type = {type(true_color_imgs)} and length {len(true_color_imgs)}."
    )
    print(
        f"Single element in the list is of type {type(true_color_imgs[-1])} and has shape {true_color_imgs[-1].shape}"
    )
    image = true_color_imgs[0]
    print(f"Image type: {image.dtype}")
    return "Datos mínimos para la busqueda fecha inicio y fecha fin",400



#a partir de este punto apis antiguas

