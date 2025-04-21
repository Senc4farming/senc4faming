#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for senc4farming
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from flask import request
from PIL import Image,ImageSequence
from senfarming import  contarPuntosLucasPoligonoOC ,\
                        obtenerPuntosLucasPoligonoOC ,\
                        obtenerPuntosLucasPoint
import sentinel_evalscript
from dateutil import parser
import json
from io import BytesIO
import os
from webutil import app, login_required, get_myself,warn_reply
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
import tifffile
import ee
import os
import requests
import pandas as pd
from gee_util import mask_s2_clouds, functn_scale_bands , functn_Clip, functn_ResemapleSentinel2,\
        cloudMaskingBasedonSCL,guardardatoscoordenadasGeeTifffiles,checkPuntGeeProcesado,guardardatoscsvpoints,\
        puntosUploadCsvOC,deletePuntGeeProcesado,getPuntGeeLandsatProcesados,getPuntGeeSentinelProcesados
import random
import time 
import io
import csv
from pykalman import KalmanFilter
from scipy.interpolate import interp1d

CWD = os.getcwd()
'''
https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
https://gis.stackexchange.com/questions/457847/downloading-sentinel-2-float32-image-as-npy-array-in-gee-python-api
'''
# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))
gee_credentials = "."

@app.route('/api/gee/proc/test/', methods = ['GET'])
def testprocgee():
     warn_reply("Has llamado al api de test /api/gee/proc/test ")
     return "Has llamado al api de test",200
@app.route('/api/gee/token/', methods = ['GET'])
def testgeetoken():
    warn_reply("Has llamado al api de test /api/gee/token ")
    #Gee credentials
    service_account = 'walgreen@ee-josemanuelarocafernandez.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account,  srvconf['PYSRV_GEE_CONFIG_FILE'])
    ee.Initialize(credentials)
    return 'Credenciales conseguidas de Gee',200
@app.route('/api/gee/proc/download/', methods = ['GET'])
def geedownload(): 
    """Get files and data from Google Earth Engine """
    print('geedownload')
    content = request.json 
    #Gee credentials
    service_account = 'walgreen@ee-josemanuelarocafernandez.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account,  srvconf['PYSRV_GEE_CONFIG_FILE'])
    ee.Initialize(credentials)
    #read input parameters
    user_id = content['user_id']
    polygoncoords = content['polygon']
    offset = content['offset']
    num_offset = float(offset)
    cloudcover = content['cloudcover']
    num_cloud = float(cloudcover)
    numberOfGeeImages = content['numberOfGeeImages']
    dirstr = content['dirstr']
    reference = content['reference']
    satellite = content['satellite']

    
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
        dffiles = pd.DataFrame()
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = fila[0]
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
        print('Comienza el dia  : '+ fecha_formato_lucas)
        points = obtenerPuntosLucasPoligonoOC(minmax, fecha_formato_lucas)
        for x in points:
            print('point:'+ str(x[2]))
            print('dateini  : '+ x[4])
            print('datefin  : '+ x[5])

                
            
            dateini = datetime.strptime(x[4],'%d/%m/%y' )
            datefin = datetime.strptime(x[5],'%d/%m/%y' )
            start = datetime.strptime(x[4],'%d/%m/%y' )
            end = datetime.strptime(x[5],'%d/%m/%y' )
            #Si la fecha de 01/01/2017 usamos la fecha de la lectura
            if x[4] == '01/01/17' and x[4] == '01/01/17':
                start = datetime_fecha_formato_lucas + timedelta(days=-15)
                end = datetime_fecha_formato_lucas + timedelta(days=15)
            long = x[0]
            lat = x[1]
            point_id =x[2]
            #check in point has alredy values
            buscarpunto = checkPuntGeeProcesado(point_id,user_id,satellite,-1) 
            if buscarpunto == 0:
                
                sleepsecp = random.randint(10,20) 
                print('Esperando punto:' + str(sleepsecp) + ', segundos')
                time.sleep(sleepsecp)
                
                print('Long:' + str(long))
                print('lat:' + str(lat))
                print('point_id:' + str(point_id))
                print(start)
                print(end)
                roi_point = ee.Geometry.Point(long,lat)
                region = ee.Geometry.BBox(long - num_offset , lat - num_offset, long + num_offset , lat + num_offset)

                images = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filterBounds(roi_point) \
                    .filterDate(start, end) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud)) \
                    .map(mask_s2_clouds)
                
                
                print("Total Sentinel2 SR Image Retrieved for data: ",images.size().getInfo())
                num_images = int(images.size().getInfo())
                #double validation change date filter if image not found
                if num_images == 0:
                    print("Change date filter ")
                    start = datetime_fecha_formato_lucas + timedelta(days=-90)
                    end = datetime_fecha_formato_lucas + timedelta(days=90)
                    images = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filterBounds(roi_point) \
                    .filterDate(start, end) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud)) \
                    .map(mask_s2_clouds)
                    print("Total Sentinel2 SR Image Retrieved for data after Change date filter: ",images.size().getInfo())
                    num_images = int(images.size().getInfo())
                
                if num_images > 0:
                    #Get bands for the better image  and save to dir
                    bestCloudImage = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).first() # Sorting the image on cloudcover and taking the best image
                    #CloudMasking
                    print('Applying cloud mask')
                    bestCloudImageCloudMasked = cloudMaskingBasedonSCL(bestCloudImage) # applying the cloud mask
                    print('Applying cloud mask done')

                    #check if user forder exists
                    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
                    userfolder = data_safe + '/appsharedfiles/' + dirstr
                    tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff/gee/' + str(point_id) + '/zip'
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolder):
                        os.makedirs(tiffuserfolder)
                    # Multi-band GeoTIFF file wrapped in a zip file.
                    url = bestCloudImage.getDownloadUrl({
                        'name': 'single_band',
                        'bands':  ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'],
                        'region': region
                    })
                    #get date for zip files
                    print('get date for zip files')
                    timeStamp_zip_file = ee.Date(bestCloudImage.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                    timeStamp_zip_file = ee.String('Date: ').cat(ee.String(timeStamp_zip_file)); #convert time stamp to string 
                    timeStamp_zip_file_txt = timeStamp_zip_file.getInfo()
                    
                    response = requests.get(url)
                    
                    filename = tiffuserfolder + '/multi_band.zip'
                    with open(filename, 'wb') as fd:
                        fd.write(response.content)
                    
                    #Save bands info into database
                    print('Save bands info into database')
                    #Making a list of images so I can iterate over the number recived in call  images.
                    num_items = 0
                    if numberOfGeeImages  <= int(images.size().getInfo()):
                        num_items = numberOfGeeImages
                    else:
                        num_items = images.size().getInfo()
                    listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)
                    print('listOfImages.size().getInfo()')
                    print(listOfImages.size().getInfo())
                    failedBands = []
                    selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                    #LOOP OVER IMAGES
                    for i in range(listOfImages.size().getInfo()):
                        img = listOfImages.get(i)
                        imageitm = ee.Image(img)
                        cloud_cover =  ee.Image(img).get('CLOUDY_PIXEL_PERCENTAGE').getInfo() 
                        print('Cloud cover:')
                        print(cloud_cover)
                        timeStamp_itm_file = ee.Date(imageitm.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                        timeStamp_itm_file = ee.String('Date: ').cat(ee.String(timeStamp_itm_file)); #convert time stamp to string 
                        timeStamp_itm_file_txt = timeStamp_itm_file.getInfo()
                        bestCloudImageCloudMasked = imageitm 
                        print('Detalles de la imagen  :')
                        #inicio codigo prueba 
                        bandnames = bestCloudImageCloudMasked.bandNames() # Retrieving the bandnames 
                        #Scaling the selected bands
                        selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                        # scale_factor = 1 # Define the scale factor
                        scale_factor = 0.0001 # Define the scale factor
                        print('Scaling the bands',selectedbands, 'by factor', scale_factor)
                        bestCloudImageCloudMaskedScaled = functn_scale_bands(bestCloudImageCloudMasked, selectedbands, scale_factor) # Scaling the selected layers of cloudmasked image
                        print('Scaling done')

                        print('Resampling the masked and scaled image') 
                        bestCloudImageCloudMaskedScaledResampled = functn_ResemapleSentinel2(bestCloudImageCloudMaskedScaled) #reseampled to 10m 
                        print('Resampling done')

                        print('Clipping the image') 
                        bestCloudImageCloudMaskedScaledResampledClipped = functn_Clip(bestCloudImageCloudMaskedScaledResampled,roi_point) #clipped to aoi
                        print('clipping done.')

                        selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                        bestCloudImageCloudMaskedScaledResampledClipped_SB = bestCloudImageCloudMaskedScaledResampledClipped.select(selectedbands)

                        bestCloudImageCloudMaskedScaledResampledClipped_SB_f=bestCloudImageCloudMaskedScaledResampledClipped_SB.toFloat()

                        #Some meta info of the image that will be useful for later calculatiosn
                        projection =  bestCloudImageCloudMaskedScaled.select('B8').projection()
                        crs = projection.crs()
                        transform_image = projection.transform()

                        path = imageitm.getDownloadUrl({ 
                        'scale': 10,  
                        'crs': crs,
                        'region': roi_point}) 
                        #print('path')
                        #print(path)
                        new_row = pd.DataFrame({'point_id':point_id, 'gee_path':path,'internal_path': tiffuserfolder, 'imageid':str(i),
                                                    'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                                    'B11':-1.1, 'B12':-1.1,'datetime_zip_file':timeStamp_zip_file_txt,'datetime_itm_file':timeStamp_itm_file_txt,'cloud_cover':cloud_cover,
                                                    'user_id':user_id,'csvpath':'N/A','B10':-1.1,'satellite':satellite,'iter':-1
                                                    }, index=[0])
                        for band in selectedbands:
                            print(band)
                            thisBand = bestCloudImageCloudMaskedScaledResampledClipped_SB_f.select(band)   
                            try:
                                urlNumpy = thisBand.getDownloadUrl({
                                    'scale': 10,
                                    'crs': crs,
                                    'region': roi_point,
                                    'format': 'NPY'
                                })
                                responseNumpy= requests.get(urlNumpy)
                                dataNumpy = np.load(io.BytesIO(responseNumpy.content), encoding='bytes').astype(np.float64)
                                val = float(dataNumpy[0])
                                new_row.at[0,band] = val
                                #print(bandsData)
                            except Exception as e:
                                failedBands.append(thisBand)
                                print("An exception occurred while downloading band:", band)
                                print(str(e))
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        print(dffiles)
                    #insert data frame into database
                    if len(dffiles) > 0:
                        guardardatoscoordenadasGeeTifffiles(dffiles,0)  
                        print(dffiles)
                        dffiles.drop(dffiles.index,inplace=True)
                    else:
                        print('Datos no encontrados')
                else:
                    print('No se han encontrado imagenes para el punto')

    return 'Elementos procesados ',200
@app.route('/api/gee/proc/download/kalman', methods = ['GET'])
def geedownloadkalman(): 
    """Get data from Google Earth Engine """
    print('geedownloadkalman')
    content = request.json 
    #Gee credentials
    service_account = 'walgreen@ee-josemanuelarocafernandez.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account,  srvconf['PYSRV_GEE_CONFIG_FILE'])
    ee.Initialize(credentials)
    #read input parameters
    user_id = content['user_id']
    polygoncoords = content['polygon']
    offset = content['offset']
    num_offset = float(offset)
    cloudcover = content['cloudcover']
    num_cloud = float(cloudcover)
    numberOfGeeImages = content['numberOfGeeImages']
    dirstr = content['dirstr']
    reference = content['reference']
    num_days_serie = 140
    satellite = content['satellite']
    
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
        dffiles = pd.DataFrame()
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = fila[0]
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
        print('Comienza el dia  : '+ fecha_formato_lucas)
        points = obtenerPuntosLucasPoligonoOC(minmax, fecha_formato_lucas)
        for x in points:
            print('point:'+ str(x[2]))
            print('survey date  : '+ x[3])
            datetimesurveydate = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
            #loop over 150 days 75 after and 75 before
            num = 0
            while num < num_days_serie:
                num_control = num_days_serie/2 + num
                print("num_control")
                print(num_control)
                start = datetimesurveydate  - timedelta(days=-num_control) 
                end =  datetimesurveydate  - timedelta(days=-num_control -1)
                print("start")
                print(start)
                print("end")
                print(end)
                long = x[0]
                lat = x[1]
                point_id =x[2]
                #check in point has alredy values
                buscarpunto = checkPuntGeeProcesado(point_id,user_id,satellite,num) 
                if buscarpunto == 0:
                    
                    sleepsecp = random.randint(3,5) 
                    print('Esperando punto:' + str(sleepsecp) + ', segundos')
                    time.sleep(sleepsecp)
                    
                    print('Long:' + str(long))
                    print('lat:' + str(lat))
                    print('point_id:' + str(point_id))
                    print(start)
                    print(end)
                    roi_point = ee.Geometry.Point(long,lat)
                    region = ee.Geometry.BBox(long - num_offset , lat - num_offset, long + num_offset , lat + num_offset)

                    images = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                        .filterBounds(roi_point) \
                        .filterDate(start, end) \
                        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud)) \
                        .map(mask_s2_clouds)
                    
                    
                    print("Total Sentinel2 SR Image Retrieved for data: ",images.size().getInfo())
                    num_images = int(images.size().getInfo())
                    #double validation change date filter if image not found
                    if num_images == 0:
                        print("Change date filter ")
                        start = datetime_fecha_formato_lucas + timedelta(days=-90)
                        end = datetime_fecha_formato_lucas + timedelta(days=90)
                        images = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                        .filterBounds(roi_point) \
                        .filterDate(start, end) \
                        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud)) \
                        .map(mask_s2_clouds)
                        print("Total Sentinel2 SR Image Retrieved for data after Change date filter: ",images.size().getInfo())
                        num_images = int(images.size().getInfo())
                    
                    if num_images > 0:
                        #Get bands for the better image  and save to dir
                        bestCloudImage = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).first() # Sorting the image on cloudcover and taking the best image
                        #CloudMasking
                        print('Applying cloud mask')
                        bestCloudImageCloudMasked = cloudMaskingBasedonSCL(bestCloudImage) # applying the cloud mask
                        print('Applying cloud mask done')

                        #check if user forder exists
                        data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
                        userfolder = data_safe + '/appsharedfiles/' + dirstr
                        tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff/gee/' + str(point_id) + '/zip'
                        #create tiff folder if does not exists
                        if not os.path.exists(tiffuserfolder):
                            os.makedirs(tiffuserfolder)
                        # Multi-band GeoTIFF file wrapped in a zip file.
                        url = bestCloudImage.getDownloadUrl({
                            'name': 'single_band',
                            'bands':  ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'],
                            'region': region
                        })
                        #get date for zip files
                        print('get date for zip files')
                        timeStamp_zip_file = ee.Date(bestCloudImage.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                        timeStamp_zip_file = ee.String('Date: ').cat(ee.String(timeStamp_zip_file)); #convert time stamp to string 
                        timeStamp_zip_file_txt = timeStamp_zip_file.getInfo()
                        
                        response = requests.get(url)
                        
                        filename = tiffuserfolder + '/multi_band.zip'
                        with open(filename, 'wb') as fd:
                            fd.write(response.content)
                        
                        #Save bands info into database
                        print('Save bands info into database')
                        #Making a list of images so I can iterate over the number recived in call  images.
                        num_items = 0
                        if numberOfGeeImages  <= int(images.size().getInfo()):
                            num_items = numberOfGeeImages
                        else:
                            num_items = images.size().getInfo()
                        listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)
                        print('listOfImages.size().getInfo()')
                        print(listOfImages.size().getInfo())
                        failedBands = []
                        selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                        #LOOP OVER IMAGES
                        for i in range(listOfImages.size().getInfo()):
                            img = listOfImages.get(i)
                            imageitm = ee.Image(img)
                            cloud_cover =  ee.Image(img).get('CLOUDY_PIXEL_PERCENTAGE').getInfo() 
                            print('Cloud cover:')
                            print(cloud_cover)
                            timeStamp_itm_file = ee.Date(imageitm.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                            timeStamp_itm_file = ee.String('Date: ').cat(ee.String(timeStamp_itm_file)); #convert time stamp to string 
                            timeStamp_itm_file_txt = timeStamp_itm_file.getInfo()
                            bestCloudImageCloudMasked = imageitm 
                            print('Detalles de la imagen  :')
                            #inicio codigo prueba 
                            #bandnames = bestCloudImageCloudMasked.bandNames() # Retrieving the bandnames 
                            #Scaling the selected bands
                            selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                            # scale_factor = 1 # Define the scale factor
                            scale_factor = 0.0001 # Define the scale factor
                            print('Scaling the bands',selectedbands, 'by factor', scale_factor)
                            bestCloudImageCloudMaskedScaled = functn_scale_bands(bestCloudImageCloudMasked, selectedbands, scale_factor) # Scaling the selected layers of cloudmasked image
                            print('Scaling done')

                            print('Resampling the masked and scaled image') 
                            bestCloudImageCloudMaskedScaledResampled = functn_ResemapleSentinel2(bestCloudImageCloudMaskedScaled) #reseampled to 10m 
                            print('Resampling done')

                            print('Clipping the image') 
                            bestCloudImageCloudMaskedScaledResampledClipped = functn_Clip(bestCloudImageCloudMaskedScaledResampled,roi_point) #clipped to aoi
                            print('clipping done.')

                            selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                            bestCloudImageCloudMaskedScaledResampledClipped_SB = bestCloudImageCloudMaskedScaledResampledClipped.select(selectedbands)

                            bestCloudImageCloudMaskedScaledResampledClipped_SB_f=bestCloudImageCloudMaskedScaledResampledClipped_SB.toFloat()

                            #Some meta info of the image that will be useful for later calculatiosn
                            projection =  bestCloudImageCloudMaskedScaled.select('B8').projection()
                            crs = projection.crs()
                            #transform_image = projection.transform()

                            path = imageitm.getDownloadUrl({ 
                            'scale': 10,  
                            'crs': crs,
                            'region': roi_point}) 
                            #print('path')
                            #print(path)
                            new_row = pd.DataFrame({'point_id':point_id, 'gee_path':path,'internal_path': tiffuserfolder, 'imageid':str(i),
                                                        'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                                        'B11':-1.1, 'B12':-1.1,'datetime_zip_file':timeStamp_zip_file_txt,'datetime_itm_file':timeStamp_itm_file_txt,'cloud_cover':cloud_cover,
                                                        'user_id':user_id,'csvpath':'N/A','B10':-1.1,'satellite':satellite,'iter':num
                                                        }, index=[0])
                            for band in selectedbands:
                                print(band)
                                thisBand = bestCloudImageCloudMaskedScaledResampledClipped_SB_f.select(band)   
                                try:
                                    urlNumpy = thisBand.getDownloadUrl({
                                        'scale': 10,
                                        'crs': crs,
                                        'region': roi_point,
                                        'format': 'NPY'
                                    })
                                    responseNumpy= requests.get(urlNumpy)
                                    dataNumpy = np.load(io.BytesIO(responseNumpy.content), encoding='bytes').astype(np.float64)
                                    val = float(dataNumpy[0])
                                    new_row.at[0,band] = val
                                    #print(bandsData)
                                except Exception as e:
                                    failedBands.append(thisBand)
                                    print("An exception occurred while downloading band:", band)
                                    print(str(e))
                            dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            print(dffiles)
                        #insert data frame into database
                        if len(dffiles) > 0:
                            guardardatoscoordenadasGeeTifffiles(dffiles,0)  
                            print(dffiles)
                            dffiles.drop(dffiles.index,inplace=True)
                        else:
                            print('Datos no encontrados')
                    else:
                        print('No se han encontrado imagenes para el punto')
                num += 1
    return 'Elementos procesados ',200

@app.route('/api/gee/proc/download/csv/', methods = ['POST'])
def geedownloadcsv(): 
    """Get files and data from Google Earth Engine """
    print('geedownload')
    content = request.json 
    #Gee credentials
    service_account = 'walgreen@ee-josemanuelarocafernandez.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account,  srvconf['PYSRV_GEE_CONFIG_FILE'])
    ee.Initialize(credentials)
    #read input parameters
    user_id = content['user_id']
    dirstr = content['dirstr']
    offset = content['offset']
    num_offset= float(offset)
    maxccvalue = content['cloudcover']
    num_cloud = float(maxccvalue)
    numberOfGeeImages = content['numberOfGeeImages']

    reference = content['reference']
    satellite = content['satellite']
    
    pathcsv = content['path']

    # Create an empty DataFrame with column names
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
        dffiles = pd.DataFrame()
        #fecha con formato DD-MM-YY
        fecha_formato_lucas = data[i][5]
        datetime_fecha_formato_lucas = datetime.strptime(fecha_formato_lucas,'%d/%m/%Y' )
        print('Comienza el dia  : '+ fecha_formato_lucas + ' ' + satellite)
        

        start = datetime_fecha_formato_lucas + timedelta(days=-15)
        end = datetime_fecha_formato_lucas + timedelta(days=15)


        #Insertamos el valor en dl dataframe
        df.loc[len(df.index)] = [data[i][0],data[i][1],-1,-1,-1,
                                 data[i][2],-1,-1,-1,float(data[i][3]),
                                 float(data[i][4]), data[i][5], data[i][6],'N/A','N/A',
                                 data[i][7],data[i][8],data[i][9],start, end,
                                 pathcsv]

        long = float(data[i][4])
        lat = float(data[i][3])
        point_id =data[i][1]
        #check in point has alredy values
        buscarpunto = checkPuntGeeProcesado(point_id,user_id,satellite,-1) 
        if buscarpunto == 0:
            sleepsecp = random.randint(5,10) 
            print('Esperando punto:' + str(sleepsecp) + ', segundos' + ',' + satellite)
            time.sleep(sleepsecp)
            
            print('Long:' + str(long))
            print('lat:' + str(lat))
            print('point_id:' + str(point_id))
            print(start)
            print(end)
            roi_point = ee.Geometry.Point(long,lat)
            region = ee.Geometry.BBox(long - num_offset , lat - num_offset, long + num_offset , lat + num_offset)
            
            if (satellite == 'sentinel'):

                images = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filterBounds(roi_point) \
                    .filterDate(start, end) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud)) \
                    .map(mask_s2_clouds)
                
                
                print("Total Sentinel2 SR Image Retrieved for data: ",images.size().getInfo())
            
                if int(images.size().getInfo()) > 0:
                    #Get bands for the better image  and save to dir
                    bestCloudImage = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).first() # Sorting the image on cloudcover and taking the best image
                    #CloudMasking
                    print('Applying cloud mask')
                    bestCloudImageCloudMasked = cloudMaskingBasedonSCL(bestCloudImage) # applying the cloud mask
                    print('Applying cloud mask done')

                    #check if user forder exists
                    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
                    userfolder = data_safe + '/appsharedfiles/' + str(dirstr)
                    tiffuserfolder = userfolder + '/' + str(reference) + '/' + '0' +  '/tiff/gee/' + str(point_id) + '/zip'
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolder):
                        os.makedirs(tiffuserfolder)
                    # Multi-band GeoTIFF file wrapped in a zip file.
                    url = bestCloudImage.getDownloadUrl({
                        'name': 'single_band',
                        'bands':  ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'],
                        'region': region
                    })
                    #get date for zip files
                    print('get date for zip files')
                    timeStamp_zip_file = ee.Date(bestCloudImage.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                    timeStamp_zip_file = ee.String('Date: ').cat(ee.String(timeStamp_zip_file)); #convert time stamp to string 
                    timeStamp_zip_file_txt = timeStamp_zip_file.getInfo()
                    
                    response = requests.get(url)
                    
                    filename = tiffuserfolder + '/multi_band.zip'
                    with open(filename, 'wb') as fd:
                        fd.write(response.content)
                    
                    #Save bands info into database
                    print('Save bands info into database')
                    #Making a list of images so I can iterate over the number recived in call  images.
                    num_items = 0
                    if numberOfGeeImages  <= int(images.size().getInfo()):
                        num_items = numberOfGeeImages
                    else:
                        num_items = images.size().getInfo()
                    listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)
                    print('listOfImages.size().getInfo()')
                    print(listOfImages.size().getInfo())
                    failedBands = []
                    selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                    #LOOP OVER IMAGES
                    for i in range(listOfImages.size().getInfo()):
                        img = listOfImages.get(i)
                        imageitm = ee.Image(img)
                        cloud_cover =  ee.Image(img).get('CLOUDY_PIXEL_PERCENTAGE').getInfo() 
                        print('Cloud cover:')
                        print(cloud_cover)
                        timeStamp_itm_file = ee.Date(imageitm.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                        timeStamp_itm_file = ee.String('Date: ').cat(ee.String(timeStamp_itm_file)); #convert time stamp to string 
                        timeStamp_itm_file_txt = timeStamp_itm_file.getInfo()
                        bestCloudImageCloudMasked = imageitm 
                        print('Detalles de la imagen  :')
                        #inicio codigo prueba 
                        bandnames = bestCloudImageCloudMasked.bandNames() # Retrieving the bandnames 
                        #Scaling the selected bands
                        selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                        # scale_factor = 1 # Define the scale factor
                        scale_factor = 0.0001 # Define the scale factor
                        print('Scaling the bands',selectedbands, 'by factor', scale_factor)
                        bestCloudImageCloudMaskedScaled = functn_scale_bands(bestCloudImageCloudMasked, selectedbands, scale_factor) # Scaling the selected layers of cloudmasked image
                        print('Scaling done')

                        print('Resampling the masked and scaled image') 
                        bestCloudImageCloudMaskedScaledResampled = functn_ResemapleSentinel2(bestCloudImageCloudMaskedScaled) #reseampled to 10m 
                        print('Resampling done')

                        print('Clipping the image') 
                        bestCloudImageCloudMaskedScaledResampledClipped = functn_Clip(bestCloudImageCloudMaskedScaledResampled,roi_point) #clipped to aoi
                        print('clipping done.')

                        selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                        bestCloudImageCloudMaskedScaledResampledClipped_SB = bestCloudImageCloudMaskedScaledResampledClipped.select(selectedbands)

                        bestCloudImageCloudMaskedScaledResampledClipped_SB_f=bestCloudImageCloudMaskedScaledResampledClipped_SB.toFloat()

                        #Some meta info of the image that will be useful for later calculatiosn
                        projection =  bestCloudImageCloudMaskedScaled.select('B8').projection()
                        crs = projection.crs()
                        transform_image = projection.transform()

                        path = imageitm.getDownloadUrl({ 
                        'scale': 10,  
                        'crs': crs,
                        'region': roi_point}) 
                        #print('path')
                        #print(path)
                        new_row = pd.DataFrame({'point_id':point_id, 'gee_path':path,'internal_path': tiffuserfolder, 'imageid':str(i),
                                                    'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                                    'B11':-1.1, 'B12':-1.1,'datetime_zip_file':timeStamp_zip_file_txt,'datetime_itm_file':timeStamp_itm_file_txt,'cloud_cover':cloud_cover,
                                                    'user_id':user_id,'csvpath':pathcsv,'B10':-1.1,'satellite':satellite,'iter':-1
                                                    }, index=[0])
                        for band in selectedbands:
                            print(band)
                            thisBand = bestCloudImageCloudMaskedScaledResampledClipped_SB_f.select(band)   
                            try:
                                urlNumpy = thisBand.getDownloadUrl({
                                    'scale': 10,
                                    'crs': crs,
                                    'region': roi_point,
                                    'format': 'NPY'
                                })
                                responseNumpy= requests.get(urlNumpy)
                                dataNumpy = np.load(io.BytesIO(responseNumpy.content), encoding='bytes').astype(np.float64)
                                val = float(dataNumpy[0])
                                new_row.at[0,band] = val
                                #print(bandsData)
                            except Exception as e:
                                failedBands.append(thisBand)
                                print("An exception occurred while downloading band:", band)
                                print(str(e))
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        print(dffiles)
                    #insert data frame into database
                    if len(dffiles) > 0:
                        guardardatoscoordenadasGeeTifffiles(dffiles,0)
                        print(dffiles)
                        dffiles.drop(dffiles.index,inplace=True)
                    else:
                        print('Datos no encontrados')
                else:
                    print('No se han encontrado imagenes para el punto')
            if (satellite == 'landsat'):
                print("empezando landsat")
                images = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                    .filterBounds(roi_point) \
                    .filterDate(start, end) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud))
                
                
                print("Total landsat SR Image Retrieved for data: ",images.size().getInfo())
            
                if int(images.size().getInfo()) > 0:
                    #Get bands for the better image  and save to dir
                    bestCloudImage = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).first() # Sorting the image on cloudcover and taking the best image
                    #CloudMasking
                    print('Applying cloud mask')
                    bestCloudImageCloudMasked = cloudMaskingBasedonSCL(bestCloudImage) # applying the cloud mask
                    print('Applying cloud mask done')

                    #check if user forder exists
                    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
                    userfolder = data_safe + '/appsharedfiles/' + str(dirstr)
                    tiffuserfolder = userfolder + '/' + str(reference) + '/' + '0' +  '/tiff/gee/' + str(point_id) + '/zip'
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolder):
                        os.makedirs(tiffuserfolder)
                    # Multi-band GeoTIFF file wrapped in a zip file.
                    url = bestCloudImage.getDownloadUrl({
                        'name': 'single_band',
                        'bands':  ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11'],
                        'region': region
                    })
                    #get date for zip files
                    print('get date for zip files')
                    timeStamp_zip_file = ee.Date(bestCloudImage.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                    timeStamp_zip_file = ee.String('Date: ').cat(ee.String(timeStamp_zip_file)); #convert time stamp to string 
                    timeStamp_zip_file_txt = timeStamp_zip_file.getInfo()
                    
                    response = requests.get(url)
                    
                    filename = tiffuserfolder + '/multi_band.zip'
                    with open(filename, 'wb') as fd:
                        fd.write(response.content)
                    
                    #Save bands info into database
                    print('Save bands info into database')
                    #Making a list of images so I can iterate over the number recived in call  images.
                    num_items = 0
                    if numberOfGeeImages  <= int(images.size().getInfo()):
                        num_items = numberOfGeeImages
                    else:
                        num_items = images.size().getInfo()
                    listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)
                    print('listOfImages.size().getInfo()')
                    print(listOfImages.size().getInfo())
                    failedBands = []
                    selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
                    #LOOP OVER IMAGES
                    for i in range(listOfImages.size().getInfo()):
                        img = listOfImages.get(i)
                        imageitm = ee.Image(img)
                        cloud_cover =  ee.Image(img).get('CLOUDY_PIXEL_PERCENTAGE').getInfo() 
                        print('Cloud cover:')
                        print(cloud_cover)
                        timeStamp_itm_file = ee.Date(imageitm.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                        timeStamp_itm_file = ee.String('Date: ').cat(ee.String(timeStamp_itm_file)); #convert time stamp to string 
                        timeStamp_itm_file_txt = timeStamp_itm_file.getInfo()
                        bestCloudImageCloudMasked = imageitm 
                        print('Detalles de la imagen  :')
                        #inicio codigo prueba 
                        bandnames = bestCloudImageCloudMasked.bandNames() # Retrieving the bandnames 
                        #Scaling the selected bands
                        selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
                        # scale_factor = 1 # Define the scale factor
                        scale_factor = 0.0001 # Define the scale factor
                        print('Scaling the bands',selectedbands, 'by factor', scale_factor)
                        bestCloudImageCloudMaskedScaled = functn_scale_bands(bestCloudImageCloudMasked, selectedbands, scale_factor) # Scaling the selected layers of cloudmasked image
                        print('Scaling done')

                        print('Resampling the masked and scaled image') 
                        bestCloudImageCloudMaskedScaledResampled = functn_ResemapleSentinel2(bestCloudImageCloudMaskedScaled) #reseampled to 10m 
                        print('Resampling done')

                        print('Clipping the image') 
                        bestCloudImageCloudMaskedScaledResampledClipped = functn_Clip(bestCloudImageCloudMaskedScaledResampled,roi_point) #clipped to aoi
                        print('clipping done.')

                        selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
                        bestCloudImageCloudMaskedScaledResampledClipped_SB = bestCloudImageCloudMaskedScaledResampledClipped.select(selectedbands)

                        bestCloudImageCloudMaskedScaledResampledClipped_SB_f=bestCloudImageCloudMaskedScaledResampledClipped_SB.toFloat()

                        #Some meta info of the image that will be useful for later calculatiosn
                        projection =  bestCloudImageCloudMaskedScaled.select('B5').projection()
                        crs = projection.crs()
                        transform_image = projection.transform()

                        path = imageitm.getDownloadUrl({ 
                        'scale': 10,  
                        'crs': crs,
                        'region': roi_point}) 
                        #print('path')
                        #print(path)
                        new_row = pd.DataFrame({'point_id':point_id, 'gee_path':path,'internal_path': tiffuserfolder, 'imageid':str(i),
                                                    'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                                    'B11':-1.1, 'B12':-1.1,'datetime_zip_file':timeStamp_zip_file_txt,'datetime_itm_file':timeStamp_itm_file_txt,'cloud_cover':cloud_cover,
                                                    'user_id':user_id,'csvpath':pathcsv,'B10':-1.1,'satellite':satellite,'iter':-1
                                                    }, index=[0])
                        for band in selectedbands:
                            print(band)
                            thisBand = bestCloudImageCloudMaskedScaledResampledClipped_SB_f.select(band)   
                            try:
                                urlNumpy = thisBand.getDownloadUrl({
                                    'scale': 10,
                                    'crs': crs,
                                    'region': roi_point,
                                    'format': 'NPY'
                                })
                                responseNumpy= requests.get(urlNumpy)
                                dataNumpy = np.load(io.BytesIO(responseNumpy.content), encoding='bytes').astype(np.float64)
                                val = float(dataNumpy[0])
                                new_row.at[0,band] = val
                                #print(bandsData)
                            except Exception as e:
                                failedBands.append(thisBand)
                                print("An exception occurred while downloading band:", band)
                                print(str(e))
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        print(dffiles)
                    #insert data frame into database
                    if len(dffiles) > 0:
                        guardardatoscoordenadasGeeTifffiles(dffiles,0)
                        print(dffiles)
                        dffiles.drop(dffiles.index,inplace=True)
                    else:
                        print('Datos no encontrados')
                else:
                    print('No se han encontrado imagenes para el punto')
    if len(df) > 0:
        guardardatoscsvpoints(df,0) 

    return 'Elementos procesados ',200


# retrieve file from 'static/images' directory
@app.route('/api/obtenercsvproc/reflvector/gee/', methods = ['POST'])
def obtenercsvprocreflvector():
    print('obtenercsvprocreflvector')
    content = request.json
    #leemos los parámetros de entrada
    userid = content['userid']
    path = content['path']
    print('path:' + path)


    #Obtenemos los parametros minimo y max del poligono
    dfdata = puntosUploadCsvOC(userid,path )
    return dfdata.to_json(),200



@app.route('/api/gee/proc/download/kalman/point/', methods = ['post'])
def geedownloadkalmanPoint(): 
    """Get data from Google Earth Engine """
    print('geedownloadkalman')
    content = request.json 
    #Gee credentials
    service_account = 'walgreen@ee-josemanuelarocafernandez.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account,  srvconf['PYSRV_GEE_CONFIG_FILE'])
    ee.Initialize(credentials)
    #read input parameters
    content_point_id = content['pointid']
    offset = content['offset']
    num_offset = float(offset)
    cloudcover = content['cloudcover']
    num_cloud = float(cloudcover)
    numberOfGeeImages = content['numberOfGeeImages']
    reference = content['reference']
    user_id = content['user_id']
    num_days_serie_str = content['num_days_serie']
    num_days_serie = num_days_serie_str
    satellite = content['satellite']
    kalmanpred = content['kalmanpred']
    dirstr = content['dirstr']
    origin = content['origin']
    pathcsv = content['path']

    print('pathcsv:' + pathcsv)

    dffiles = pd.DataFrame()
    dffkalman =  pd.DataFrame()
    #initialize values
    fecha_formato_lucas =  ''
    long = 0.1
    lat = 0.1
    point_id = 0
    datetimesurveydate = date.today()
    #default path value
    pathdef = 'N/A'
    #check if is lucas or is a csv file
    if (origin == 'csv'):
        #read cvs file and look for point id
        # Create an empty DataFrame with column names
        df = pd.DataFrame(columns=['depth','POINTID','OC','TH_LAT','TH_LONG',
                               'SURVEY_DATE','Elev',
                               'lc0_desc','lc1_desc','lu1_desc'])
    
        #Leemos el CSV en un data frame
        # Open file 
        file = open(pathcsv, "r")
        data = list(csv.reader(file, delimiter=";"))
        file.close()
        for i in range(1,len(data)):
            print(data[i][0])
            dffiles = pd.DataFrame()
            #fecha con formato DD-MM-YYYY
            fecha_formato_lucas = data[i][5]
            long =  float(data[i][4])
            lat =  float(data[i][3])
            point_id = int(data[i][1])
            datetimesurveydate = datetime.strptime(fecha_formato_lucas,'%d/%m/%Y' )
            pathdef = pathcsv
            print('point_id :content_point_id ; ' + str(point_id) + ':' + str(content_point_id) )
            if point_id == content_point_id:
                break
    else:
        points = obtenerPuntosLucasPoint(content_point_id)
        x= points[0]
        print(x)
        print('point:'+ str(x[2]))
        print('survey date  : '+ x[3])
        fecha_formato_lucas =  x[3]
        long = x[0]
        lat = x[1]
        point_id =x[2]
        datetimesurveydate = datetime.strptime(fecha_formato_lucas,'%d/%m/%y' )
    #loop over number of days divided by 2
    num = 0
    while num < num_days_serie:
        num_control = num_days_serie/2 - num
        print("num")
        print(num) 
        print("num_control") 
        print(num_control)
        start = datetimesurveydate  - timedelta(days=num_control) 
        end =  datetimesurveydate  - timedelta(days=num_control -1)
        print("datetimesurveydate")
        print(datetimesurveydate)
        print("start")
        print(start)
        print("end")
        print(end)

        #check in point has alredy values
        #buscarpunto = deletePuntGeeProcesado(point_id,user_id,satellite,num,pathdef) 
        buscarpunto = checkPuntGeeProcesado(point_id,user_id,satellite,num)
        if buscarpunto == 1:
            sleepsecp = random.randint(3,6) 
            print('Esperando punto:' + str(sleepsecp) + ', segundos')
            time.sleep(sleepsecp)
            
            print('Long:' + str(long))
            print('lat:' + str(lat))
            print('point_id:' + str(point_id))
            print(start)
            print(end)
            roi_point = ee.Geometry.Point(long,lat)
            region = ee.Geometry.BBox(long - num_offset , lat - num_offset, long + num_offset , lat + num_offset)
            if (satellite == 'sentinel'):
                images = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filterBounds(roi_point) \
                    .filterDate(start, end) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud)) \
                    .map(mask_s2_clouds)
                

                print("Total Sentinel2 SR Image Retrieved for data: ",images.size().getInfo())
                num_images = int(images.size().getInfo())
                #double validation change date filter if image not found
                
                if num_images > 0:
                    #Get bands for the better image  and save to dir
                    bestCloudImage = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).first() # Sorting the image on cloudcover and taking the best image
                    #CloudMasking
                    print('Applying cloud mask')
                    bestCloudImageCloudMasked = cloudMaskingBasedonSCL(bestCloudImage) # applying the cloud mask
                    print('Applying cloud mask done')

                    #check if user forder exists
                    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
                    userfolder = data_safe + '/appsharedfiles/' + dirstr
                    tiffuserfolder = userfolder + '/' + reference + '/' + '0' +  '/tiff/gee/' + str(point_id) + '/zip'
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolder):
                        os.makedirs(tiffuserfolder)
                    # Multi-band GeoTIFF file wrapped in a zip file.
                    url = bestCloudImage.getDownloadUrl({
                        'name': 'single_band',
                        'bands':  ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'],
                        'region': region
                    })
                    #get date for zip files
                    print('get date for zip files')
                    timeStamp_zip_file = ee.Date(bestCloudImage.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                    timeStamp_zip_file = ee.String('Date: ').cat(ee.String(timeStamp_zip_file)); #convert time stamp to string 
                    timeStamp_zip_file_txt = timeStamp_zip_file.getInfo()
                    
                    response = requests.get(url)
                    
                    filename = tiffuserfolder + '/multi_band.zip'
                    with open(filename, 'wb') as fd:
                        fd.write(response.content)
                    
                    #Save bands info into database
                    print('Save bands info into database')
                    #Making a list of images so I can iterate over the number recived in call  images.
                    num_items = 0
                    if numberOfGeeImages  <= int(images.size().getInfo()):
                        num_items = numberOfGeeImages
                    else:
                        num_items = images.size().getInfo()
                    listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)
                    print('listOfImages.size().getInfo()')
                    print(listOfImages.size().getInfo())
                    failedBands = []
                    selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                    #LOOP OVER IMAGES
                    for i in range(listOfImages.size().getInfo()):
                        img = listOfImages.get(i)
                        imageitm = ee.Image(img)
                        cloud_cover =  ee.Image(img).get('CLOUDY_PIXEL_PERCENTAGE').getInfo() 
                        print('Cloud cover:')
                        print(cloud_cover)
                        timeStamp_itm_file = ee.Date(imageitm.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                        #timeStamp_itm_file = ee.String('Date: ').cat(ee.String(timeStamp_itm_file)); #convert time stamp to string 
                        timeStamp_itm_file = ee.String(timeStamp_itm_file)
                        timeStamp_itm_file_txt = timeStamp_itm_file.getInfo()
                        bestCloudImageCloudMasked = imageitm 
                        print('Detalles de la imagen  :')
                        #inicio codigo prueba 
                        #bandnames = bestCloudImageCloudMasked.bandNames() # Retrieving the bandnames 
                        #Scaling the selected bands
                        selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                        # scale_factor = 1 # Define the scale factor
                        scale_factor = 0.0001 # Define the scale factor
                        print('Scaling the bands',selectedbands, 'by factor', scale_factor)
                        bestCloudImageCloudMaskedScaled = functn_scale_bands(bestCloudImageCloudMasked, selectedbands, scale_factor) # Scaling the selected layers of cloudmasked image
                        print('Scaling done')

                        print('Resampling the masked and scaled image') 
                        bestCloudImageCloudMaskedScaledResampled = functn_ResemapleSentinel2(bestCloudImageCloudMaskedScaled) #reseampled to 10m 
                        print('Resampling done')

                        print('Clipping the image') 
                        bestCloudImageCloudMaskedScaledResampledClipped = functn_Clip(bestCloudImageCloudMaskedScaledResampled,roi_point) #clipped to aoi
                        print('clipping done.')

                        selectedbands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
                        bestCloudImageCloudMaskedScaledResampledClipped_SB = bestCloudImageCloudMaskedScaledResampledClipped.select(selectedbands)

                        bestCloudImageCloudMaskedScaledResampledClipped_SB_f=bestCloudImageCloudMaskedScaledResampledClipped_SB.toFloat()

                        #Some meta info of the image that will be useful for later calculatiosn
                        projection =  bestCloudImageCloudMaskedScaled.select('B8').projection()
                        crs = projection.crs()
                        #transform_image = projection.transform()

                        path = imageitm.getDownloadUrl({ 
                        'scale': 10,  
                        'crs': crs,
                        'region': roi_point}) 
                        #print('path')
                        #print(path)
                        new_row = pd.DataFrame({'point_id':point_id, 'gee_path':path,'internal_path': tiffuserfolder, 'imageid':str(i),
                                                    'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                                    'B11':-1.1, 'B12':-1.1,'datetime_zip_file':timeStamp_itm_file_txt,'datetime_itm_file':timeStamp_itm_file_txt,'cloud_cover':cloud_cover,
                                                    'user_id':user_id,'csvpath':pathdef,'B10':-1.1,'satellite':satellite,'iter':num
                                                    }, index=[0])
                        for band in selectedbands:
                            print(band)
                            thisBand = bestCloudImageCloudMaskedScaledResampledClipped_SB_f.select(band)   
                            try:
                                urlNumpy = thisBand.getDownloadUrl({
                                    'scale': 10,
                                    'crs': crs,
                                    'region': roi_point,
                                    'format': 'NPY'
                                })
                                responseNumpy= requests.get(urlNumpy)
                                dataNumpy = np.load(io.BytesIO(responseNumpy.content), encoding='bytes').astype(np.float64)
                                val = float(dataNumpy[0])
                                new_row.at[0,band] = val
                                #print(bandsData)
                            except Exception as e:
                                failedBands.append(thisBand)
                                print("An exception occurred while downloading band:", band)
                                print(str(e))
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        dffkalman = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        print(dffiles)
                    #insert data frame into database
                    if len(dffiles) > 0:
                        guardardatoscoordenadasGeeTifffiles(dffiles,0)  
                        print(dffiles)
                        dffiles.drop(dffiles.index,inplace=True)
                    else:
                        print('Datos no encontrados')
                else:
                    print('No se han encontrado imagenes para el punto')
            if (satellite == 'landsat'):
                print("empezando landsat")
                images = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                    .filterBounds(roi_point) \
                    .filterDate(start, end) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', num_cloud))
                
                
                print("Total landsat SR Image Retrieved for data: ",images.size().getInfo())
            
                if int(images.size().getInfo()) > 0:
                    #Get bands for the better image  and save to dir
                    bestCloudImage = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).first() # Sorting the image on cloudcover and taking the best image
                    #CloudMasking
                    print('Applying cloud mask')
                    bestCloudImageCloudMasked = cloudMaskingBasedonSCL(bestCloudImage) # applying the cloud mask
                    print('Applying cloud mask done')

                    #check if user forder exists
                    data_safe = srvconf['PYSRV_SRC_ROOT_DATA_SAFE' ]
                    userfolder = data_safe + '/appsharedfiles/' + str(dirstr)
                    tiffuserfolder = userfolder + '/' + str(reference) + '/' + '0' +  '/tiff/gee/' + str(point_id) + '/zip'
                    #create tiff folder if does not exists
                    if not os.path.exists(tiffuserfolder):
                        os.makedirs(tiffuserfolder)
                    # Multi-band GeoTIFF file wrapped in a zip file.
                    url = bestCloudImage.getDownloadUrl({
                        'name': 'single_band',
                        'bands':  ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11'],
                        'region': region
                    })
                    #get date for zip files
                    print('get date for zip files')
                    timeStamp_zip_file = ee.Date(bestCloudImage.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                    timeStamp_zip_file = ee.String('Date: ').cat(ee.String(timeStamp_zip_file)); #convert time stamp to string 
                    timeStamp_zip_file_txt = timeStamp_zip_file.getInfo()
                    
                    response = requests.get(url)
                    
                    filename = tiffuserfolder + '/multi_band.zip'
                    with open(filename, 'wb') as fd:
                        fd.write(response.content)
                    
                    #Save bands info into database
                    print('Save bands info into database')
                    #Making a list of images so I can iterate over the number recived in call  images.
                    num_items = 0
                    if numberOfGeeImages  <= int(images.size().getInfo()):
                        num_items = numberOfGeeImages
                    else:
                        num_items = images.size().getInfo()
                    listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)
                    print('listOfImages.size().getInfo()')
                    print(listOfImages.size().getInfo())
                    failedBands = []
                    selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
                    #LOOP OVER IMAGES
                    for i in range(listOfImages.size().getInfo()):
                        img = listOfImages.get(i)
                        imageitm = ee.Image(img)
                        cloud_cover =  ee.Image(img).get('CLOUDY_PIXEL_PERCENTAGE').getInfo() 
                        print('Cloud cover:')
                        print(cloud_cover)
                        timeStamp_itm_file = ee.Date(imageitm.get('system:time_start')).format().slice(0,10); # get the time stamp of each frame. This can be any string. Date, Years, Hours, etc.
                        timeStamp_itm_file = ee.String('Date: ').cat(ee.String(timeStamp_itm_file)); #convert time stamp to string 
                        timeStamp_itm_file_txt = timeStamp_itm_file.getInfo()
                        bestCloudImageCloudMasked = imageitm 
                        print('Detalles de la imagen  :')
                        #inicio codigo prueba 
                        bandnames = bestCloudImageCloudMasked.bandNames() # Retrieving the bandnames 
                        #Scaling the selected bands
                        selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
                        # scale_factor = 1 # Define the scale factor
                        scale_factor = 0.0001 # Define the scale factor
                        print('Scaling the bands',selectedbands, 'by factor', scale_factor)
                        bestCloudImageCloudMaskedScaled = functn_scale_bands(bestCloudImageCloudMasked, selectedbands, scale_factor) # Scaling the selected layers of cloudmasked image
                        print('Scaling done')

                        print('Resampling the masked and scaled image') 
                        bestCloudImageCloudMaskedScaledResampled = functn_ResemapleSentinel2(bestCloudImageCloudMaskedScaled) #reseampled to 10m 
                        print('Resampling done')

                        print('Clipping the image') 
                        bestCloudImageCloudMaskedScaledResampledClipped = functn_Clip(bestCloudImageCloudMaskedScaledResampled,roi_point) #clipped to aoi
                        print('clipping done.')

                        selectedbands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
                        bestCloudImageCloudMaskedScaledResampledClipped_SB = bestCloudImageCloudMaskedScaledResampledClipped.select(selectedbands)

                        bestCloudImageCloudMaskedScaledResampledClipped_SB_f=bestCloudImageCloudMaskedScaledResampledClipped_SB.toFloat()

                        #Some meta info of the image that will be useful for later calculatiosn
                        projection =  bestCloudImageCloudMaskedScaled.select('B5').projection()
                        crs = projection.crs()
                        transform_image = projection.transform()

                        path = imageitm.getDownloadUrl({ 
                        'scale': 10,  
                        'crs': crs,
                        'region': roi_point}) 
                        #print('path')
                        #print(path)
                        new_row = pd.DataFrame({'point_id':point_id, 'gee_path':path,'internal_path': tiffuserfolder, 'imageid':str(i),
                                                    'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                                    'B11':-1.1, 'B12':-1.1,'datetime_zip_file':timeStamp_zip_file_txt,'datetime_itm_file':timeStamp_itm_file_txt,'cloud_cover':cloud_cover,
                                                    'user_id':user_id,'csvpath':pathdef,'B10':-1.1,'satellite':satellite,'iter':-1
                                                    }, index=[0])
                        for band in selectedbands:
                            print(band)
                            thisBand = bestCloudImageCloudMaskedScaledResampledClipped_SB_f.select(band)   
                            try:
                                urlNumpy = thisBand.getDownloadUrl({
                                    'scale': 10,
                                    'crs': crs,
                                    'region': roi_point,
                                    'format': 'NPY'
                                })
                                responseNumpy= requests.get(urlNumpy)
                                dataNumpy = np.load(io.BytesIO(responseNumpy.content), encoding='bytes').astype(np.float64)
                                val = float(dataNumpy[0])
                                new_row.at[0,band] = val
                                #print(bandsData)
                            except Exception as e:
                                failedBands.append(thisBand)
                                print("An exception occurred while downloading band:", band)
                                print(str(e))
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        dffkalman = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        print(dffiles)
                    #insert data frame into database
                    if len(dffiles) > 0:
                        guardardatoscoordenadasGeeTifffiles(dffiles,0)
                        print(dffiles)
                        dffiles.drop(dffiles.index,inplace=True)
                    else:
                        print('Datos no encontrados')
                else:
                    print('No se han encontrado imagenes para el punto')
        num += 1
    # get pd data frames
    dffkalmanproc = pd.DataFrame()
    band_array_literal  = ['B01','B02','B03','B04','B05','B06','B07','B08','B8A','B09','B11','B12']
    num_bands = 12
    if (satellite == 'sentinel'):
        dffkalmanproc = getPuntGeeSentinelProcesados(point_id,user_id,satellite,pathdef) 
        print('dffkalmanproc sentinel')
        print(dffkalmanproc)
    if (satellite == 'landsat'):
        dffkalmanproc = getPuntGeeLandsatProcesados(point_id,user_id,satellite,pathdef) 
        num_bands = 11
        band_array_literal  = ['B01','B02','B03','B04','B05','B06','B07','B08','B09','B10','B11']
        print('dffkalmanproc landsat')
        print(dffkalmanproc)
    
    #Seleciono el df a usar y  
    #Obtengo la matriz con solo datos de reflectancia
    df = dffkalmanproc.drop('datetime_itm_file',axis= 1)
    print('df')
    print(df)


    df_dates_str = dffkalmanproc.loc[:,'datetime_itm_file']
    print('df_dates_str')

    df_dates =  pd.to_datetime(df_dates_str)
    #initial dates series
    df_dates_ini =  pd.to_datetime(df_dates_str)
    df_dates_nan =  pd.to_datetime(df_dates_str)
    
    #Traspose df
    dft = df.T
    #band position
    band_pos = 0
    while band_pos < num_bands:
        #prepare path for saving first figure
        pltpath = pathdef.replace('.csv','/kanlman/images/' + str(content_point_id)  )
        
        
        #create directory in not exists
        if not os.path.exists(pltpath):
            os.makedirs(pltpath)

        #Prepare intermediate variables
        start_pred_date = datetimesurveydate - timedelta(days=-1) 

        new_dates_point = pd.date_range(start_pred_date, periods=1, freq='1D')

        # get dataset with reflectance values for a selected band
        observed_reflectance_ini = dft.iloc[band_pos]

        #se index for observed_reflectance_nan
        observed_reflectance_nan1 = observed_reflectance_ini.set_axis(df_dates_ini)
        df_dates_nan1 = df_dates_nan.set_axis(df_dates_ini)
        df_dates_ini1 = df_dates_nan.set_axis(df_dates_ini)

        #get min datetime
        min_date = df_dates_ini.min()
        #list of missing dates 
        new_dates = pd.date_range(start=min_date - timedelta(days=4) , periods=80, freq='1D')
        s = pd.Series(new_dates)

        #create series with nan values
        for val in s:
            #check if index exists
            if not val in observed_reflectance_nan1.index:
                # Get next index number
                next_index = val
                # Insert at end
                df_dates_nan1[next_index] = val
                #create holes in observed_reflectance
                observed_reflectance_nan1[next_index] = np.nan
        #Add new_dates_point to df_dates_ini
        #create series with nan values
        s1 = pd.Series(new_dates_point)
        for val1 in s1:
            #check if index exists
            if not val1 in df_dates_ini1.index:
                # Get next index number
                next_index = val1
                # Insert at end
                df_dates_ini1[next_index] = val1
        #set index for observed_reflectance_nan
        df_dates_nan_ord = df_dates_nan1.sort_index()
        df_dates_ini1_ord = df_dates_ini1.sort_index()
        #Predicted values for week of survey date
        # Aplicación del filtro de Kalman
        kf_p = KalmanFilter(initial_state_mean=observed_reflectance_ini[0], 
                        n_dim_obs=1)
        
        
        

        smoothed_reflectance, _ = kf_p.smooth(observed_reflectance_ini)

        # Interpolación usando Kalman
        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
        interp_func = interp1d(df_dates_ini.astype(np.int64), smoothed_reflectance.flatten(), kind='slinear', fill_value='extrapolate')
        interpolated_values = interp_func(df_dates_nan_ord.astype(np.int64))
        interpolated_values_date = interp_func(new_dates_point.astype(np.int64))

        # Gráfica de los datos
        frames = [df_dates,new_dates]

        plt_pred = plt

        plt_pred.figure(figsize=(14, 12))
        plt_pred.plot(df_dates_ini, observed_reflectance_ini, label='Real reflectance values',marker='D',linestyle='dotted')
        plt_pred.plot(df_dates_ini, smoothed_reflectance, 'bo-', label='Smoothed reflectance values')
        plt_pred.plot(df_dates_nan_ord, interpolated_values,  color='red',marker='.', label='Interpolated values with Kalman')
        plt_pred.plot(new_dates_point, interpolated_values_date,  color='orange',marker='P', label='Interpolated reflactance for point and date')
        plt.title('Reflectance values interpolated for ' +band_array_literal[band_pos]+' using kalman smoothing,\n Real  , Smoothed , and interpolated  reflectance values',fontsize=16)
        plt_pred.xlabel('Date',fontsize=14)
        plt_pred.xticks(rotation=90)
        plt_pred.xticks(df_dates_ini1_ord)
        plt_pred.ylabel('Reflectance',fontsize=14)
        plt_pred.legend() 

        plt_pred.show()

        plt_pred.savefig(pltpath+'/kalmanpredictionsmoothed'+band_array_literal[band_pos]+'.png')



        #Predicted values for week of survey date
        # Aplicación del filtro de Kalman
        kf_filter = KalmanFilter(initial_state_mean=observed_reflectance_ini[0], 
                        n_dim_obs=1)

        # Fit the Kalman filter with the estimated parameters
        filtered_state_means, filtered_state_covariances = kf_filter.filter(observed_reflectance_ini)

        # Interpolación usando Kalman
        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
        interp_func = interp1d(df_dates_ini.astype(np.int64), filtered_state_means.flatten(), kind='slinear', fill_value='extrapolate')
        interpolated_values = interp_func(df_dates_nan_ord.astype(np.int64))
        interpolated_values_date = interp_func(new_dates_point.astype(np.int64))


        # Gráfica de los datos
        frames = [df_dates,new_dates]

        plt_pred = plt

        plt_pred.figure(figsize=(14, 12))
        plt_pred.plot(df_dates_ini, observed_reflectance_ini, label='Real reflectance values',marker='D',linestyle='dotted')
        plt_pred.plot(df_dates_ini, filtered_state_means, 'bo-', label='Filter reflectance values')
        plt_pred.plot(df_dates_nan_ord, interpolated_values,  color='red',marker='.', label='Interpolated values with Kalman')
        plt_pred.plot(new_dates_point, interpolated_values_date,  color='orange',marker='P', label='Interpolated reflactance for point and date')
        plt.title('Reflectance values interpolated for ' +band_array_literal[band_pos]+' using EM algorithm,\n Real  , Filtered, and interpolated  reflectance values',fontsize=16)
        plt_pred.xlabel('Date',fontsize=14)
        plt_pred.xticks(rotation=90)
        plt_pred.xticks(df_dates_ini1_ord)
        plt_pred.ylabel('Reflectance',fontsize=14)
        plt_pred.legend() 

        plt_pred.show()
        plt_pred.savefig(pltpath+'/kalmanpredictionfilter'+band_array_literal[band_pos]+'.png')
        band_pos += 1
    
    return 'Elementos procesados ',200