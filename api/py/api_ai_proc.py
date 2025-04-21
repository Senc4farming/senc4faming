#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for senc4farming
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from webutil import app, login_required, get_myself,warn_reply
import pandas as pd
import os
from senfarming_ai_utils import display_func ,display_func_val,clean_outliers,procesamiento_basico_pivot_valores_medios_sin_fechas,\
             eval_r2,draw_scatter,perform_cross_validation,obtenerModelos,readmodelbyref,draw_scatter_tit

from flask import request
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
import numpy as np
from datetime import date , datetime, timedelta

import json
import ee
from gee_util import mask_s2_clouds, functn_scale_bands , functn_Clip, functn_ResemapleSentinel2,puntosUploadCsvAiModel

import requests
import io
import joblib


filesnamesarray = [
                    'files/definitivos/gee_data_v1.csv',
                    'files/definitivos/gee_data_v2_ndvi_02_04.csv',
                     'files/definitivos/gee_data_v3_msavi_menos1_02.csv',
                     'files/definitivos/gee_data_v3_msavi_menos1_02_v1.csv',
                     'files/definitivos/gee_data_v3_msavi_menos1_02_v7.csv',
                     'files/definitivos/gee_data_v5_min_ndvi_v5.csv',
                     'files/definitivos/gee_data_v3_msavi_menos1_02_v4.csv',
                     'files/definitivos/gee_data_v3_min_ndvi_cc_menor_1.csv',
                     'files/definitivos/gee_data_v6_min_ndvi_cc_menor_05.csv',
                     'files/definitivos/gee_data_v8_min_ndvi_cc_menor_005.csv',
                     'files/definitivos/gee_data_v9_min_ndvi_cc_menor_005.csv',
                     'files/definitivos/gee_data_v2_min_ndvi_cc_menor_007.csv',
                    'files/definitivos/point_proc.csv',
                  ]


corrfilesnamesarray = ['matriz_oc_bandas_10_02_v3.csv',
                       'matriz_oc_bandas_15_02_v3.csv',
    'matriz_oc_bandas_30d_min_ndvi_oc_1_v3.csv',
 'matriz_oc_bandas_45d_min_ndvi_oc_005_v8.csv',
 'matriz_oc_bandas_60d_min_ndvi_oc_005_v9.csv',
 'matriz_oc_bandas_fullrange_min_ndvi_oc_007_v2.csv']
corrfilestitlearray = ['Correlacion 10 dias ',
                        'Correlacion 15 dias ',
                       'Correlacion 30 dias ',
                      'Correlacion 45 dias ',
 'Correlacion 60 dias',
 'Correlacion todos dias']


#cv value
cv_param=11
#select csv item
#elem = 11
elem_corr = [5]
#Bands to use 1 all 2 rgb
opt_band = 1
#AI items to run
exec_rf = 0
exec_knn = 1
exec_svr = 1
#outliers
min_outl = 0 
max_outl = 20
outliers = 0
#csv predict val
elem_val_pred = 12




CWD = os.getcwd()
'''
https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
https://gis.stackexchange.com/questions/457847/downloading-sentinel-2-float32-image-as-npy-array-in-gee-python-api
'''
# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))

band_array_min_ndiv_30d = ['04','07','08','08A','NDVI']
band_array_min_ndiv_45d = ['NDVI']
band_array_min_ndiv_60d = ['08','12','NDVI']
band_array_min_ndiv_todosd = ['01','02','03','04','05','06','07','08','09','11','12','8A','NDVI']
band_array_min_ndiv_rgb_d = ['02','03','04']
band_array_min_ndiv_grp1d = ['02','03','04','NDVI']

descdf_all = "Use full df"
descdf_mean = "Use mean values for df"
descdf_median = "Use median values for df"

if opt_band == 1:
    band_array_usar = band_array_min_ndiv_todosd 
elif opt_band == 2:
    band_array_usar = band_array_min_ndiv_rgb_d 
elif opt_band == 3:
    band_array_usar = band_array_min_ndiv_grp1d 

@app.route('/api/ai/test/', methods = ['GET'])
def testaipred():
     warn_reply("Has llamado al api de test /api/ai/test/  ")
     cwd = os.getcwd()
     arr = os.listdir()

     print(arr)

     return "Has llamado al api de test",200



@app.route('/api/ai/pred/knn', methods = ['POST'])
def getPredValueknn():
    """Get files and data from Google Earth Engine """
    print('en /api/ai/pred/knn ')
    content = request.json 
    #Gee credentials
    service_account = 'walgreen@ee-josemanuelarocafernandez.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account,  srvconf['PYSRV_GEE_CONFIG_FILE'])
    ee.Initialize(credentials)
   
    content = request.json
    elem = content['elem']
    point_id = content['pointid']
    fechaIni = content['fechaIni']
    fechaFin = content['fechaFin']
    longitude = content['longitude']
    latitude = content['latitude']
    offset = content['offset']
    num_offset = float(offset)
    cloudcover = content['cloudcover']
    num_cloud = float(cloudcover)
    numberOfGeeImages = content['numberOfGeeImages']
    reference = content['reference']
    #read model path from table
    df_model = readmodelbyref(reference, 'tbl_ai_model')
    fullmodelfilename = df_model.at[0,'modelnamepath']
    print("Path :" +fullmodelfilename )

    #read data from gee
    start = datetime.strptime(fechaIni,'%d/%m/%y' )
    end = datetime.strptime(fechaFin,'%d/%m/%y' )
    long = float(longitude)
    lat = float(latitude)


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
    
    if int(images.size().getInfo()) > 0:
        #Making a list of images so I can iterate over the number recived in call  images.
        num_items = 0
        if numberOfGeeImages  <= int(images.size().getInfo()):
            num_items = numberOfGeeImages
        else:
            num_items = images.size().getInfo()
        listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)

        print('listOfImages.size().getInfo()')
        print(listOfImages.size().getInfo())

        #As img are ordered by cloud we get the first img
        i = 0
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
        failedBands = []
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

        path = imageitm.getDownloadUrl({ 
        'scale': 10,  
        'crs': crs,
        'region': roi_point}) 

        new_row = pd.DataFrame({ 'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                'B11':-1.1, 'B12':-1.1
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

        data ={'point_id': [point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id],
            'fecha':[start,start,start,start,start,start,start,start,start,start,start,start],
            'band':['01','02','03','04','05','06','07','08','09','11','12','8A'],
            'longitude':[longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude],
            'latitude':[latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude],
            'readvalue':[0,0,0,0,0,0,0,0,0,0,0,0],
            'reflectance':[new_row.at[0,'B1'],new_row.at[0,'B2'],new_row.at[0,'B3'],new_row.at[0,'B4'],new_row.at[0,'B5'],new_row.at[0,'B6'],
                            new_row.at[0,'B7'],new_row.at[0,'B8'],new_row.at[0,'B8A'],new_row.at[0,'B9'],new_row.at[0,'B11'],new_row.at[0,'B12']],
            'ndvi':[0,0,0,0,0,0,0,0,0,0,0,0],
            'point_id-2':[0,0,0,0,0,0,0,0,0,0,0,0],
            'ndvi-2':[0,0,0,0,0,0,0,0,0,0,0,0]
        }
        display_func_val(0,'data',data)
        
        #read file with data
        df = pd.read_csv(filesnamesarray[elem])

        
        if outliers == 1:  
            #Quito los outliers despues de normalizar
            df_ini_sin_outliers = clean_outliers(min_outl,max_outl,df)
            df = df_ini_sin_outliers
        X,y= procesamiento_basico_pivot_valores_medios_sin_fechas(df,band_array_usar)
        display_func_val(0,'X', X.shape)
        display_func_val(0,'Y', y.shape)

        
        display_func(1,"Inicio KNN pred ")
        # load the model from disk
        knn = joblib.load(fullmodelfilename)
        knn.fit(X, y)
        df_pred_point_knn = pd.DataFrame(data)
        display_func(1,df_pred_point_knn.head(5))
        #para todos los valores
        X_a_pred_knn,Y_a_pred_knn = procesamiento_basico_pivot_valores_medios_sin_fechas(df_pred_point_knn,band_array_usar)
        display_func_val(1,'X', X_a_pred_knn)
        display_func_val(1,'Y', Y_a_pred_knn)
        pred_knn = knn.predict(X_a_pred_knn)
        display_func(0,pred_knn)
        return str(pred_knn[0]),200
    else:
        return "Punto no encontrado",200

@app.route('/api/ai/pred/svr', methods = ['POST'])
def getPredValuesvr():
    print('en /api/ai/pred/svr ')
    content = request.json 
    #Gee credentials
    service_account = 'walgreen@ee-josemanuelarocafernandez.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account,  srvconf['PYSRV_GEE_CONFIG_FILE'])
    ee.Initialize(credentials)
   
    content = request.json
    elem = content['elem']
    point_id = content['pointid']
    fechaIni = content['fechaIni']
    fechaFin = content['fechaFin']
    longitude = content['longitude']
    latitude = content['latitude']
    offset = content['offset']
    num_offset = float(offset)
    cloudcover = content['cloudcover']
    num_cloud = float(cloudcover)
    numberOfGeeImages = content['numberOfGeeImages']
    reference = content['reference']
    #read model path from table
    df_model = readmodelbyref(reference, 'tbl_ai_model')
    print(df_model.head())
    fullmodelfilename = df_model.at[0,'modelnamepath']
    print("Path :" +fullmodelfilename )


    #read data from gee
    start = datetime.strptime(fechaIni,'%d/%m/%y' )
    end = datetime.strptime(fechaFin,'%d/%m/%y' )
    long = float(longitude)
    lat = float(latitude)


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
    
    if int(images.size().getInfo()) > 0:
        #Making a list of images so I can iterate over the number recived in call  images.
        num_items = 0
        if numberOfGeeImages  <= int(images.size().getInfo()):
            num_items = numberOfGeeImages
        else:
            num_items = images.size().getInfo()
        listOfImages = images.sort('CLOUDY_PIXEL_PERCENTAGE',True).toList(num_items)

        print('listOfImages.size().getInfo()')
        print(listOfImages.size().getInfo())

        #As img are ordered by cloud we get the first img
        i = 0
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
        failedBands = []
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

        path = imageitm.getDownloadUrl({ 
        'scale': 10,  
        'crs': crs,
        'region': roi_point}) 

        new_row = pd.DataFrame({ 'B1':-1.1, 'B2':-1.1, 'B3':-1.1, 'B4':-1.1, 'B5':-1.1, 'B6':-1.1, 'B7':-1.1, 'B8':-1.1, 'B8A':-1.1, 'B9':-1.1,
                                'B11':-1.1, 'B12':-1.1
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

        data ={'point_id': [point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id,point_id],
            'fecha':[start,start,start,start,start,start,start,start,start,start,start,start],
            'band':['01','02','03','04','05','06','07','08','09','11','12','8A'],
            'longitude':[longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude,longitude],
            'latitude':[latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude,latitude],
            'readvalue':[0,0,0,0,0,0,0,0,0,0,0,0],
            'reflectance':[new_row.at[0,'B1'],new_row.at[0,'B2'],new_row.at[0,'B3'],new_row.at[0,'B4'],new_row.at[0,'B5'],new_row.at[0,'B6'],
                            new_row.at[0,'B7'],new_row.at[0,'B8'],new_row.at[0,'B8A'],new_row.at[0,'B9'],new_row.at[0,'B11'],new_row.at[0,'B12']],
            'ndvi':[0,0,0,0,0,0,0,0,0,0,0,0],
            'point_id-2':[0,0,0,0,0,0,0,0,0,0,0,0],
            'ndvi-2':[0,0,0,0,0,0,0,0,0,0,0,0]
        }
        display_func_val(0,'data',data)

        parameters=[ {'C':np.logspace(-3,3,20   )
                        ,'gamma':np.logspace(-3,3,20   ),
        'kernel':['rbf']} ]
        #read file with data
        df = pd.read_csv(filesnamesarray[elem])

        
        if outliers == 1:  
            #Quito los outliers despues de normalizar
            df_ini_sin_outliers = clean_outliers(min_outl,max_outl,df)
            df = df_ini_sin_outliers
        X,y= procesamiento_basico_pivot_valores_medios_sin_fechas(df,band_array_usar)
        display_func_val(0,'X', X.shape)
        display_func_val(0,'Y', y.shape)
        # load the model from disk
        grid_GBC = joblib.load(fullmodelfilename)

        grid_GBC.fit(X, y)
        print(" Results from Grid Search " )
        print("\n The best estimator across ALL searched params:\n",grid_GBC.best_estimator_)
        print("\n The best score across ALL searched params:\n",grid_GBC.best_score_)
        print("\n The best parameters across ALL searched params:\n",grid_GBC.best_params_)
        
        df_pred_point = pd.DataFrame(data)
        display_func(0,df_pred_point.head(5))
        
        #para todos los valores
        X_a_pred,Y_a_pred = procesamiento_basico_pivot_valores_medios_sin_fechas(df_pred_point,band_array_usar)
        display_func_val(1,'X', X_a_pred)
        display_func_val(1,'X', Y_a_pred)
        pred = grid_GBC.predict(X_a_pred)
        display_func(0,pred)
        return str(pred[0]),200
    else:
        return "Punto no encontrado",200
    

@app.route('/api/ai/pred/csv/knn', methods = ['POST'])
def getPredValueCsvknn():
    print('en /api/ai/pred/csv/knn')
   
    content = request.json
    user_id = content['user_id']
    reference = content['reference']
    path = content['path']
    title = 'KNN ai model for ' + str(reference)
    fullimagefilename = 'files/definitivos/scatter_knn' + str(user_id) + str(reference)
    fullmodelfilename = 'files/definitivos/model/knn'  + str(user_id) + str(reference) + '.sav'
    

    


    #para todos los valores
    display_func(1,"Inicio KNN ") 
    #read data from db
    df = puntosUploadCsvAiModel(user_id,path)
    
    if outliers == 1:  
        #Quito los outliers despues de normalizar
        df_ini_sin_outliers = clean_outliers(min_outl,max_outl,df)
        df = df_ini_sin_outliers
    X,y= procesamiento_basico_pivot_valores_medios_sin_fechas(df,band_array_usar)
    display_func_val(0,'X', X.shape)
    display_func_val(0,'Y', y.shape)

    knn = KNeighborsRegressor(n_neighbors=15)
    display_func(0,"KNN run perform_cross_validation")
    knn_output = perform_cross_validation(knn, X, y, cv_param)
    scores = eval_r2(knn_output)       
    display_func(1,"Values for  r2 per fold")
    display_func(1,scores)
    display_func(1,"Mid value  of r2")
    display_func(1,scores.mean())
    draw_scatter_tit(knn_output,'knn',descdf_all,reference,fullimagefilename,fullmodelfilename,title )
    #save model to file
    joblib.dump(knn, fullmodelfilename)
    return "evalregressionknn :" ,200

@app.route('/api/ai/pred/csv/svr', methods = ['POST'])
def getPredValueCsvSvr():
    print('en /api/ai/pred/csv/knn')
   
    content = request.json
    user_id = content['user_id']
    reference = content['reference']
    path = content['path']
    title = 'KNN ai model for ' + str(reference)
    fullimagefilename = 'files/definitivos/scatter_svr' + str(user_id) + str(reference)
    fullmodelfilename = 'files/definitivos/model/svr' + str(user_id) + str(reference) + '.sav'
    
    #para todos los valores
    display_func(1,"Inicio SVR ") 
    #read data from db
    df = puntosUploadCsvAiModel(user_id,path)
    
    if outliers == 1:  
        #Quito los outliers despues de normalizar
        df_ini_sin_outliers = clean_outliers(min_outl,max_outl,df)
        df = df_ini_sin_outliers
    X,y= procesamiento_basico_pivot_valores_medios_sin_fechas(df,band_array_usar)
    display_func_val(0,'X', X.shape)
    display_func_val(0,'Y', y.shape)

    knn = KNeighborsRegressor(n_neighbors=15)
    display_func(0,"KNN run perform_cross_validation")
    knn_output = perform_cross_validation(knn, X, y, cv_param)
    scores = eval_r2(knn_output)       
    display_func(1,"Values for  r2 per fold")
    display_func(1,scores)
    display_func(1,"Mid value  of r2")
    display_func(1,scores.mean())
    draw_scatter_tit(knn_output,'knn',descdf_all,reference,fullimagefilename,fullmodelfilename,title )
    #save model to file
    joblib.dump(knn, fullmodelfilename)
    return "evalregressionsvr :" ,200
    

@app.route('/api/ai/regr/knn', methods = ['GET'])
def evalregressionknn(): 
    print('en /api/ai/regr/knn  ')
    content = request.json
    elem = content['elem']
    reference = content['reference']
    filename = content['filename']
    fullimagefilename = 'files/definitivos/' + filename
    modelfilename = content['modelfilename']
    fullmodelfilename = 'files/definitivos/model/'  + modelfilename
    

    #para todos los valores
    display_func(1,"Inicio SVR")
    #read file with data
    df = pd.read_csv(filesnamesarray[elem])
    
    if outliers == 1:  
        #Quito los outliers despues de normalizar
        df_ini_sin_outliers = clean_outliers(min_outl,max_outl,df)
        df = df_ini_sin_outliers
    X,y= procesamiento_basico_pivot_valores_medios_sin_fechas(df,band_array_usar)
    display_func_val(0,'X', X.shape)
    display_func_val(0,'Y', y.shape)

    parameters=[ {'C':np.logspace(-3,3,20   )
                      ,'gamma':np.logspace(-3,3,20   ),
       'kernel':['rbf']} ]

    svr_opt=GridSearchCV(estimator=SVR(),
                             param_grid=parameters,
                             cv=5,
                             n_jobs=1,scoring="r2")
    display_func(0,"SVR run perform_cross_validation")
    svr_opt_output = perform_cross_validation(svr_opt, X, y, cv_param)
    scores = eval_r2(svr_opt_output)     
    display_func(1,"Values for  r2 per fold")
    display_func(1,scores)
    display_func(1,"Mid value  of r2")
    display_func(1,scores.mean())
    draw_scatter(svr_opt_output,'svr',descdf_all,reference,fullimagefilename,fullmodelfilename,elem )
    #save model to file
    joblib.dump(svr_opt, fullmodelfilename)

    return "evalregressionsvr :" ,200

@app.route('/api/ai/regr/svr', methods = ['GET'])
def evalregressionsvr():
    print('en /api/ai/regr/svr ')
    content = request.json
    elem = content['elem']
    reference = content['reference']
    filename = content['filename']
    fullimagefilename = 'files/definitivos/' + filename
    modelfilename = content['modelfilename']
    fullmodelfilename = 'files/definitivos/model/'  + modelfilename

    #para todos los valores
    display_func(1,"Inicio SVR ")
    #read file with data
    df = pd.read_csv(filesnamesarray[elem])
    
    if outliers == 1:  
        #Quito los outliers despues de normalizar
        df_ini_sin_outliers = clean_outliers(min_outl,max_outl,df)
        df = df_ini_sin_outliers
    X,y= procesamiento_basico_pivot_valores_medios_sin_fechas(df,band_array_usar)
    display_func_val(0,'X', X.shape)
    display_func_val(0,'Y', y.shape)

    parameters=[ {'C':np.logspace(-3,3,20   )
                      ,'gamma':np.logspace(-3,3,20   ),
       'kernel':['rbf']} ]

    svr_opt=GridSearchCV(estimator=SVR(),
                             param_grid=parameters,
                             cv=5,
                             n_jobs=1,scoring="r2")
    display_func(0,"SVR run perform_cross_validation")
    svr_opt_output = perform_cross_validation(svr_opt, X, y, cv_param)
    scores = eval_r2(svr_opt_output)     
    display_func(1,"Values for  r2 per fold")
    display_func(1,scores)
    display_func(1,"Mid value  of r2")
    display_func(1,scores.mean())
    draw_scatter(svr_opt_output,'svr',descdf_all,reference,fullimagefilename,fullmodelfilename,elem )
    #save model to file
    joblib.dump(svr_opt, fullmodelfilename)

    return "evalregressionsvr :" ,200


# retrieve file from 'static/images' directory
@app.route('/api/ai/models', methods = ['POST'])
def obtenermodelosai():
    print('obtenermodelosai')
    content = request.json
    userid = content['userid']
    dfdata = obtenerModelos()
    return dfdata.to_json(),200