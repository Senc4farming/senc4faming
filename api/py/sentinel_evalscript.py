import logging
import pandas as pd
import numpy as np
import os
from senfarming import  checkCsvLineaProcesado
from sentinelhub import (
    DataCollection,
    SentinelHubRequest,
    MosaickingOrder,
    BBox,
    Band,
    Unit, 
    bbox_to_dimensions,
    CRS,
    MimeType
)
log = logging.getLogger("api_senfarming")

sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
sh_base_url = "https://sh.dataspace.copernicus.eu"

evalscript_gen = """
//VERSION=3
function setup() {
return {
    input: ["B02", "B03", "B04"],
    output: { bands: 3 },
}
}

function evaluatePixel(sample) {
return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02]
}
"""
request_gen = {
    "input": {
        "bounds": {
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/32633"},
            "bbox": [
                408553.58,
                5078145.48,
                466081.02,
                5126576.61,
            ],
        },
        "data": [
            {
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2022-10-01T00:00:00Z",
                        "to": "2022-10-31T00:00:00Z",
                    }
                },
            }
        ],
    },
    
    "output": {
        "resx": 100,
        "resy": 100,
    },
    "evalscript": evalscript_gen,
}
evalscript = """
//VERSION=3
function setup() {
    return {
        input: ["B04"],
        output: { bands: 1 },
    }
    output: {
    id: "default",
    bands: 1,
    sampleType: SampleType.UINT16,
    },
}

function evaluatePixel(sample) {
return [sample.B04]
}
"""

request = {
    "input": {
        "bounds": {
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/32633"},
            "bbox": [
                408553.58,
                5078145.48,
                466081.02,
                5126576.61,
            ],
        },
        "data": [
            {
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2022-10-01T00:00:00Z",
                        "to": "2022-10-31T00:00:00Z",
                    }
                },
            }
        ],
    },
    
    "output": {
        "resx": 100,
        "resy": 100,
    },
    "evalscript": evalscript,
}
evalscript_true_color = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: ["B02", "B03", "B04"]
        }],
        output: {
            bands: 3
        }
    };
}

function evaluatePixel(sample) {
    return [sample.B04, sample.B03, sample.B02];
}
"""
evalscript_01 = """
//VERSION=3
function setup() {
return {
    input: [
    {
        bands: [
        "B01"
        ],
        units: "DN",
    },
    ],
    output: {
    id: "default",
    bands: 1,
    sampleType: SampleType.UINT16,
    },
}
}

function evaluatePixel(sample) {
return [
    sample.B01
]
}
"""
evalscript_02 = """
//VERSION=3
function setup() {
return {
    input: [
    {
        bands: [
        "B02"
        ],
        units: "DN",
    },
    ],
    output: {
    id: "default",
    bands: 1,
    sampleType: SampleType.UINT16,
    },
}
}

function evaluatePixel(sample) {
return [
    sample.B02
]
}
"""

evalscript_03 = """
//VERSION=3
function setup() {
return {
    input: [
    {
        bands: [
        "B03"
        ],
        units: "DN",
    },
    ],
    output: {
    id: "default",
    bands: 1,
    sampleType: SampleType.UINT16,
    },
}
}

function evaluatePixel(sample) {
return [
    sample.B03
]
}
"""
request_03 = {
    "input": {
        "bounds": {
            "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -94.04798984527588,
                            41.7930725281021,
                        ],
                        [
                            -94.04803276062012,
                            41.805773608962866,
                        ],
                        [
                            -94.06738758087158,
                            41.805901566741305,
                        ],
                        [
                            -94.06734466552734,
                            41.7967199475024,
                        ],
                        [
                            -94.06223773956299,
                            41.79144072064381,
                        ],
                        [
                            -94.0504789352417,
                            41.791376727347966,
                        ],
                        [
                            -94.05039310455322,
                            41.7930725281021,
                        ],
                        [
                            -94.04798984527588,
                            41.7930725281021,
                        ],
                    ]
                ],
            },
        },
        "data": [
            {
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2023-10-01T00:00:00Z",
                        "to": "2023dataspace -10-31T00:00:00Z",
                    }
                },
                "processing": {"harmonizeValues": "false"},
            }
        ],
    },
    "output": {
        "responses": [
            {
                "identifier": "default",
                "format": {"type": "image/tiff"},
            }
        ],
    },
    "evalscript": evalscript_03,
}
evalscript = """
//VERSION=3
function setup() {
return {
    input: [
    {
        bands: [
        "B01",
        "B02",
        "B03",
        "B04",
        "B05",
        "B06",
        "B07",
        "B08",
        "B8A",
        "B09",
        "B11",
        "B12",
        ],
        units: "DN",
    },
    ],
    output: {
    id: "default",
    bands: 12,
    sampleType: SampleType.UINT16,
    },
}
}

function evaluatePixel(sample) {
return [
    sample.B01,
    sample.B02,
    sample.B03,
    sample.B04,
    sample.B05,
    sample.B06,
    sample.B07,
    sample.B08,
    sample.B8A,
    sample.B09,
    sample.B11,
    sample.B12,
]
}
"""

request = {
    "input": {
        "bounds": {
            "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -94.04798984527588,
                            41.7930725281021,
                        ],
                        [
                            -94.04803276062012,
                            41.805773608962866,
                        ],
                        [
                            -94.06738758087158,
                            41.805901566741305,
                        ],
                        [
                            -94.06734466552734,
                            41.7967199475024,
                        ],
                        [
                            -94.06223773956299,
                            41.79144072064381,
                        ],
                        [
                            -94.0504789352417,
                            41.791376727347966,
                        ],
                        [
                            -94.05039310455322,
                            41.7930725281021,
                        ],
                        [
                            -94.04798984527588,
                            41.7930725281021,
                        ],
                    ]
                ],
            },
        },
        "data": [
            {
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2022-10-01T00:00:00Z",
                        "to": "2022-10-31T00:00:00Z",
                    }
                },
                "processing": {"harmonizeValues": "false"},
            }
        ],
    },
    "output": {
        "width": 512,
        "height": 512,
        "responses": [
            {
                "identifier": "default",
                "format": {"type": "image/tiff"},
            }
        ],
    },
    "evalscript": evalscript,
}


evalscript_XXX_band = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["XXX"],
            units: "REFLECTANCE"
        }],
        output: {
            bands: 1,
            sampleType: "AUTO"
        }
    };
}

function evaluatePixel(sample) {    
    return [sample.XXX];
}
"""

evalscript_XXX_band_16 = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["XXX"],
            units: "REFLECTANCE"
        }],
        output: {
            bands: 1,
            sampleType: "INT16"
        }
    };
}

function evaluatePixel(sample) {    
    return [sample.XXX];
}
"""

evalscript_XXX_band_DN = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["XXX"],
            units: "DN"
        }],
        output: {
            bands: 1,
            sampleType: "INT16"
        }
    };
}

function evaluatePixel(sample) {    
    return [sample.XXX];
}
"""
evalscript_XXX_band_Reflectance = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["XXX"],
            units: "reflectance"
        }], 
        output: {
            bands: 1,
            sampleType: "YYY"
        }
    };
}

function evaluatePixel(sample) {    
    return [sample.XXX];
}
"""
evalscript_XXX_band_Reflectance_CORR = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["XXX"],
            units: "reflectance"
        }], 
        output: {
            bands: 1,
            sampleType: "YYY"
        }
    };
}

function evaluatePixel(sample) {    
    return [sample.ZZZ];
}
"""
evalscript_11_band_Reflectance = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"],
            units: "reflectance"
        }], 
        output: {
            bands: 11,
            sampleType: SampleType.UINT16
        }
    };
}

function evaluatePixel(sample) {    
    return [  sample.B02, sample.B03, sample.B04, sample.B05, sample.B06, sample.B07, sample.B08, sample.B8A, sample.B09, sample.B11, sample.B12]
}
"""
evalscript_GNDVI  = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["B08","B03" ],
            units: "FLOAT32"
        }], 
        output: {
        bands: 1,
        sampleType: SampleType.FLOAT32
        },
        mosaicking: Mosaicking.ORBIT
    };
}

function evaluatePixel(sample) {    
    let index = (sample.B08 - sample.B03) / (sample.B08 + sample.B03);
    return[index]
}
"""

evalscript_NDMI  = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["B8A", "B11" ],
            units: "FLOAT32"
        }], 
        output: {
        bands: 1,
        sampleType: SampleType.FLOAT32
        },
        mosaicking: Mosaicking.ORBIT
    };
}

function evaluatePixel(sample) {    
    let index = (sample.B08 - sample.B11) / (sample.B08 + sample.B11);
    return[index]
}
"""

def saveBandTiff(band, evalscriptin,tiffuserfolder, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue):
    tiffuserfolderband=tiffuserfolder + '/' + band
    print("en saveBandTiff 10: ")
    dffiles = pd.DataFrame()
    if str_datacollection_type ==  's2l2a':
        request_all_bands = SentinelHubRequest(
        data_folder=tiffuserfolderband,
        evalscript=evalscriptin,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    str_datacollection_type, service_url=config.sh_base_url
                ),
                time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                maxcc=maxccvalue
            )
        ],
        

        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=switchBandResolutionbbox(band,offset,minmax),
        size=switchBandResolutionsize(band,offset,minmax),
        config=config,
        )
        all_bands_img = request_all_bands.get_data(save_data=True)
        print(
        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
        )

        for folder, _, filenames in os.walk(request_all_bands.data_folder):
            for filename in filenames:
                file = os.path.join(folder, filename)
                print(file)
                #add file ref fo pandas dataframe
                new_row = pd.DataFrame({'Band':band, 'Path':file}, index=[0])
                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)

    print("en saveBandTiff 20: ")
    if str_datacollection_type ==  's2l1c':
        request_all_bands = SentinelHubRequest(
        data_folder=tiffuserfolderband,
        evalscript=evalscriptin,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C.define_from(
                    str_datacollection_type, service_url=config.sh_base_url
                ),
                time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                maxcc=maxccvalue,
            )
        ],

        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=switchBandResolutionbbox(band,offset,minmax),
        size=switchBandResolutionsize(band,offset,minmax),
        config=config,
        )
        all_bands_img = request_all_bands.get_data(save_data=True)
        print(
        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
        )

        for folder, _, filenames in os.walk(request_all_bands.data_folder):
            for filename in filenames:
                file = os.path.join(folder, filename)
                print(file)
                #add file ref fo pandas dataframe
                new_row = pd.DataFrame({'Band':band, 'Path':file}, index=[0])
                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)

    return dffiles

def saveAllBandsTiffCheckSize( offset,minmax):
    print("en saveAllBandsTiffCheckSize 10: " + offset)
    str_list = ["01","02","03","04","05","06","07","08","8A","09","11","12"]
    for x in range(len(str_list)):
        band = str_list[x]
        size=switchBandResolutionsize(band,float(offset),minmax)
        print("Size:")
        print(size)
        height = size[0]
        print("height:")
        print(height)
        width = size[1]
        print("width:")
        print(width)
        message = "OK"
        if (height > 2500 ):
            message = "Height greater than 2500, change polygon"
            return message
        if (width > 2500 ):
            message = "Height greater than 2500, change polygon"
            return message
    return message

def saveAllBandsTiff( unit,dffiles,tiffuserfolder, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue,token,id,reference):

    print("en saveBandTiff 10: ")
    idpunto = int(id)
    str_list = ["01","02","03","04","05","06","07","08","8A","09","11","12"]
    #str_list = ["01","02"]
    for x in range(len(str_list)):
        band = str_list[x]
        bandletter = "B" + band
        tiffuserfolderband=tiffuserfolder + '/' + band
        '''
        INT8 - signed 8-bit integer (values should range from -128 to 127)
        UINT8 - unsigned 8-bit integer (values should range from 0 to 255)
        INT16 - signed 16-bit integer (values should range from -32768 to 32767)
        UINT16 - unsigned 16-bit integer (values should range from 0 to 65535)
        FLOAT32 - 32-bit floating point (values have effectively no limits)
        AUTO (default) - values should range from 0-1, which will then automatically be stretched 
        from the interval [0, 1] to [0, 255] and written into an UINT8 raster. Values below 0 and above 
        1 will be clamped to 0 and 255, respectively. This is the default if sampleType is not set in the output object.
        '''
        evalscriptin = evalscript_XXX_band_Reflectance_CORR.replace("XXX",bandletter)
        evalscriptin = evalscriptin.replace("YYY",unit)
        evalscriptin = evalscriptin.replace("ZZZ",bandletter)
        #evalscriptin = evalscriptin.replace("FFF"," ")
        if unit == 'UINT8':
            evalscriptin = evalscriptin.replace("ZZZ",bandletter + " * 255")
            #evalscriptin = evalscriptin.replace("FFF",bandletter + "2.5 * ")
        if unit == 'UINT16':
            evalscriptin = evalscriptin.replace("ZZZ",bandletter + " * 65535")
            #evalscriptin = evalscriptin.replace("FFF",bandletter + "2.5 * ")

        if str_datacollection_type ==  's2l2a':
            request_all_bands = SentinelHubRequest(
            data_folder=tiffuserfolderband,
            evalscript=evalscriptin,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A.define_from(
                        str_datacollection_type, service_url=config.sh_base_url
                    ),
                    time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                    maxcc=maxccvalue
                )
            ],
            

            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=switchBandResolutionbbox(band,offset,minmax),
            size=switchBandResolutionsize(band,offset,minmax),
            config=config,
            )
            all_bands_img = request_all_bands.get_data(save_data=True)
            print(
            "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
            )

            for folder, _, filenames in os.walk(request_all_bands.data_folder):
                for filename in filenames:
                    file = os.path.join(folder, filename)
                    print(file)
                    #add file ref to pandas dataframe
                    if idpunto > 0:
                        new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference}, index=[0])
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                    else :
                        new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)

        print("en saveBandTiff 20: ")
        if str_datacollection_type ==  's2l1c':
            request_all_bands = SentinelHubRequest(
            data_folder=tiffuserfolderband,
            evalscript=evalscriptin,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L1C.define_from(
                        str_datacollection_type, service_url=config.sh_base_url
                    ),
                    time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                    maxcc=maxccvalue
                )
            ],

            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=switchBandResolutionbbox(band,offset,minmax),
            size=switchBandResolutionsize(band,offset,minmax),
            config=config,
            )
            all_bands_img = request_all_bands.get_data(save_data=True)
            print(
            "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
            )

            for folder, _, filenames in os.walk(request_all_bands.data_folder):
                for filename in filenames:
                    file = os.path.join(folder, filename)
                    print(file)
                    #add file ref fo pandas dataframe
                    if idpunto > 0:
                        new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference}, index=[0])
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                    else :
                        new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)

    return dffiles
def saveAllBandsTiffReflectance(unit , tiffuserfolder, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue,token,id,numline,reference,userid,mosaicking_order):

    print("en saveBandTiff 10: ")
    idpunto = int(id)
    dffiles = pd.DataFrame()
    str_list = ["02","03","04","05","06","07","08","8A","09","11","12"]
    for x in range(len(str_list)):
        band = str_list[x]
        # Comportamiento por defecto
        bandletter = "B" + band
        '''
        INT8 - signed 8-bit integer (values should range from -128 to 127)
        UINT8 - unsigned 8-bit integer (values should range from 0 to 255)
        INT16 - signed 16-bit integer (values should range from -32768 to 32767)
        UINT16 - unsigned 16-bit integer (values should range from 0 to 65535)
        FLOAT32 - 32-bit floating point (values have effectively no limits)
        AUTO (default) - values should range from 0-1, which will then automatically be stretched 
        from the interval [0, 1] to [0, 255] and written into an UINT8 raster. Values below 0 and above 
        1 will be clamped to 0 and 255, respectively. This is the default if sampleType is not set in the output object.
        '''
        tiffuserfolderband=tiffuserfolder + '/' + band
        evalscriptin = evalscript_XXX_band_Reflectance.replace("XXX",bandletter)
        evalscriptin = evalscriptin.replace("YYY",unit)
        if band == "GNDVI":
            evalscriptin = evalscript_GNDVI
            bandletter = band
        elif band == "NDMI":
            evalscriptin = evalscript_NDMI
            bandletter = band
        
        controldatosdescargados = 0
        print("en saveBandTiff 20: ")
        if str_datacollection_type ==  's2l1c':
            if maxccvalue > 0:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L1C.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            maxcc=maxccvalue,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
            else:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L1C.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            mosaicking_order=MosaickingOrder.LEAST_CC,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
        if str_datacollection_type ==  's2l2a':
            if maxccvalue > 0:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L2A.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            maxcc=maxccvalue,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
            else:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L2A.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            mosaicking_order=MosaickingOrder.LEAST_CC,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
    return dffiles

def saveAllBandsTiffReflectance(unit , tiffuserfolder, str_datacollection_type ,offset,minmax,dateread,
                                enddate,config,maxccvalue,token,id,numline,reference,satellite,userid,mosaicking_order):

    print("en saveBandTiff 10: ")
    idpunto = int(id)
    dffiles = pd.DataFrame()
    if satellite == 'sentinel':
        str_list = ["02","03","04","05","06","07","08","8A","09","11","12"]
        for x in range(len(str_list)):
            band = str_list[x]
            # Comportamiento por defecto
            bandletter = "B" + band
            '''
            INT8 - signed 8-bit integer (values should range from -128 to 127)
            UINT8 - unsigned 8-bit integer (values should range from 0 to 255)
            INT16 - signed 16-bit integer (values should range from -32768 to 32767)
            UINT16 - unsigned 16-bit integer (values should range from 0 to 65535)
            FLOAT32 - 32-bit floating point (values have effectively no limits)
            AUTO (default) - values should range from 0-1, which will then automatically be stretched 
            from the interval [0, 1] to [0, 255] and written into an UINT8 raster. Values below 0 and above 
            1 will be clamped to 0 and 255, respectively. This is the default if sampleType is not set in the output object.
            '''
            tiffuserfolderband=tiffuserfolder + '/' + band
            evalscriptin = evalscript_XXX_band_Reflectance.replace("XXX",bandletter)
            evalscriptin = evalscriptin.replace("YYY",unit)
            if band == "GNDVI":
                evalscriptin = evalscript_GNDVI
                bandletter = band
            elif band == "NDMI":
                evalscriptin = evalscript_NDMI
                bandletter = band
            
            controldatosdescargados = 0
            print("en saveBandTiff 20: ")
            if str_datacollection_type ==  's2l1c':
                if maxccvalue > 0:
                    #no ejecutar si ya exise del registro en la bbdd y es csvfile
                    if reference == 'csvfile':
                        controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0,satellite)
                    else:
                        controldatosdescargados = 0
                    if controldatosdescargados == 0:
                        request_all_bands = SentinelHubRequest(
                        data_folder=tiffuserfolderband,
                        evalscript=evalscriptin,
                        input_data=[
                            SentinelHubRequest.input_data(
                                data_collection=DataCollection.SENTINEL2_L1C.define_from(
                                    str_datacollection_type, service_url=config.sh_base_url
                                ),
                                time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                                maxcc=maxccvalue,
                            )
                        ],

                        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                        bbox=switchBandResolutionbbox(band,offset,minmax),
                        size=switchBandResolutionsize(band,offset,minmax),
                        config=config,
                        )
                        all_bands_img = request_all_bands.get_data(save_data=True)
                        print(
                        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                        )

                        for folder, _, filenames in os.walk(request_all_bands.data_folder):
                            for filename in filenames:
                                file = os.path.join(folder, filename)
                                print(file)
                                #add file ref fo pandas dataframe
                                if idpunto > 0:
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                                else :
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                else:
                    #no ejecutar si ya exise del registro en la bbdd y es csvfile
                    if reference == 'csvfile':
                        controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0,satellite)
                    else:
                        controldatosdescargados = 0
                    if controldatosdescargados == 0:
                        request_all_bands = SentinelHubRequest(
                        data_folder=tiffuserfolderband,
                        evalscript=evalscriptin,
                        input_data=[
                            SentinelHubRequest.input_data(
                                data_collection=DataCollection.SENTINEL2_L1C.define_from(
                                    str_datacollection_type, service_url=config.sh_base_url
                                ),
                                time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                                mosaicking_order=MosaickingOrder.LEAST_CC,
                            )
                        ],

                        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                        bbox=switchBandResolutionbbox(band,offset,minmax),
                        size=switchBandResolutionsize(band,offset,minmax),
                        config=config,
                        )
                        all_bands_img = request_all_bands.get_data(save_data=True)
                        print(
                        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                        )

                        for folder, _, filenames in os.walk(request_all_bands.data_folder):
                            for filename in filenames:
                                file = os.path.join(folder, filename)
                                print(file)
                                #add file ref fo pandas dataframe
                                if idpunto > 0:
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                                else :
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
            if str_datacollection_type ==  's2l2a':
                if maxccvalue > 0:
                    #no ejecutar si ya exise del registro en la bbdd y es csvfile
                    if reference == 'csvfile':
                        controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0,satellite)
                    else:
                        controldatosdescargados = 0
                    if controldatosdescargados == 0:
                        request_all_bands = SentinelHubRequest(
                        data_folder=tiffuserfolderband,
                        evalscript=evalscriptin,
                        input_data=[
                            SentinelHubRequest.input_data(
                                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                                    str_datacollection_type, service_url=config.sh_base_url
                                ),
                                time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                                maxcc=maxccvalue,
                            )
                        ],

                        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                        bbox=switchBandResolutionbbox(band,offset,minmax),
                        size=switchBandResolutionsize(band,offset,minmax),
                        config=config,
                        )
                        all_bands_img = request_all_bands.get_data(save_data=True)
                        print(
                        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                        )

                        for folder, _, filenames in os.walk(request_all_bands.data_folder):
                            for filename in filenames:
                                file = os.path.join(folder, filename)
                                print(file)
                                #add file ref fo pandas dataframe
                                if idpunto > 0:
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                                else :
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                else:
                    #no ejecutar si ya exise del registro en la bbdd y es csvfile
                    if reference == 'csvfile':
                        controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0,satellite)
                    else:
                        controldatosdescargados = 0
                    if controldatosdescargados == 0:
                        request_all_bands = SentinelHubRequest(
                        data_folder=tiffuserfolderband,
                        evalscript=evalscriptin,
                        input_data=[
                            SentinelHubRequest.input_data(
                                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                                    str_datacollection_type, service_url=config.sh_base_url
                                ),
                                time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                                mosaicking_order=MosaickingOrder.LEAST_CC,
                            )
                        ],

                        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                        bbox=switchBandResolutionbbox(band,offset,minmax),
                        size=switchBandResolutionsize(band,offset,minmax),
                        config=config,
                        )
                        all_bands_img = request_all_bands.get_data(save_data=True)
                        print(
                        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                        )

                        for folder, _, filenames in os.walk(request_all_bands.data_folder):
                            for filename in filenames:
                                file = os.path.join(folder, filename)
                                print(file)
                                #add file ref fo pandas dataframe
                                if idpunto > 0:
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                                else :
                                    new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                    dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
    if satellite == 'landsat':
        str_list = ["01","02","03","04","05","06","07","08","09","10","11"]
        #https://docs.sentinel-hub.com/api/latest/data/landsat-8-l2/
        for x in range(len(str_list)):
            band = str_list[x]
            # Comportamiento por defecto
            bandletter = "B" + band
            '''
            INT8 - signed 8-bit integer (values should range from -128 to 127)
            UINT8 - unsigned 8-bit integer (values should range from 0 to 255)
            INT16 - signed 16-bit integer (values should range from -32768 to 32767)
            UINT16 - unsigned 16-bit integer (values should range from 0 to 65535)
            FLOAT32 - 32-bit floating point (values have effectively no limits)
            AUTO (default) - values should range from 0-1, which will then automatically be stretched 
            from the interval [0, 1] to [0, 255] and written into an UINT8 raster. Values below 0 and above 
            1 will be clamped to 0 and 255, respectively. This is the default if sampleType is not set in the output object.
            '''
            tiffuserfolderband=tiffuserfolder + '/' + band
            evalscriptin = evalscript_XXX_band_Reflectance.replace("XXX",bandletter)
            evalscriptin = evalscriptin.replace("YYY",unit)
            if band == "GNDVI":
                evalscriptin = evalscript_GNDVI
                bandletter = band
            elif band == "NDMI":
                evalscriptin = evalscript_NDMI
                bandletter = band
            
            controldatosdescargados = 0
            print("en saveBandTiff 220: ")
            if maxccvalue > 0:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0,satellite)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.LANDSAT_OT_L1,
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            maxcc=maxccvalue,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
            else:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0,satellite)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.LANDSAT_OT_L2,
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            mosaicking_order=MosaickingOrder.LEAST_CC,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)

    return dffiles

def saveAllBandsTiffReflectance11( tiffuserfolder, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue,id,numline,reference,satellite,userid,mosaicking_order):

    print("en saveBandTiff 10: ")
    idpunto = int(id)
    dffiles = pd.DataFrame()
    str_list = ["all"]
    for x in range(len(str_list)):
        band = str_list[x]
        # Comportamiento por defecto
        bandletter = "B" + band
        '''
        INT8 - signed 8-bit integer (values should range from -128 to 127)
        UINT8 - unsigned 8-bit integer (values should range from 0 to 255)
        INT16 - signed 16-bit integer (values should range from -32768 to 32767)
        UINT16 - unsigned 16-bit integer (values should range from 0 to 65535)
        FLOAT32 - 32-bit floating point (values have effectively no limits)
        AUTO (default) - values should range from 0-1, which will then automatically be stretched 
        from the interval [0, 1] to [0, 255] and written into an UINT8 raster. Values below 0 and above 
        1 will be clamped to 0 and 255, respectively. This is the default if sampleType is not set in the output object.
        '''
        tiffuserfolderband=tiffuserfolder + '/' + band
        if band == "all":
            evalscriptin = evalscript_11_band_Reflectance
            bandletter = band
        controldatosdescargados = 0
        print("en saveBandTiff 20: ")
        if str_datacollection_type ==  's2l1c':
            if maxccvalue > 0:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L1C.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            maxcc=maxccvalue,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
            else:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L1C.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            mosaicking_order=MosaickingOrder.LEAST_CC,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
        if str_datacollection_type ==  's2l2a':
            if maxccvalue > 0:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L2A.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            maxcc=maxccvalue,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
            else:
                #no ejecutar si ya exise del registro en la bbdd y es csvfile
                if reference == 'csvfile':
                    controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
                else:
                    controldatosdescargados = 0
                if controldatosdescargados == 0:
                    request_all_bands = SentinelHubRequest(
                    data_folder=tiffuserfolderband,
                    evalscript=evalscriptin,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L2A.define_from(
                                str_datacollection_type, service_url=config.sh_base_url
                            ),
                            time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                            mosaicking_order=MosaickingOrder.LEAST_CC,
                        )
                    ],

                    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                    bbox=switchBandResolutionbbox(band,offset,minmax),
                    size=switchBandResolutionsize(band,offset,minmax),
                    config=config,
                    )
                    all_bands_img = request_all_bands.get_data(save_data=True)
                    print(
                    "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                    )

                    for folder, _, filenames in os.walk(request_all_bands.data_folder):
                        for filename in filenames:
                            file = os.path.join(folder, filename)
                            print(file)
                            #add file ref fo pandas dataframe
                            if idpunto > 0:
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                            else :
                                new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
    return dffiles

def saveAllBandsTiffReflectanceHSL(unit , tiffuserfolder, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue,token,id,numline,reference,satellite,userid,mosaicking_order):

    print("en saveAllBandsTiffReflectanceHSL 10: ")
    optical_bands = tuple(
    Band(name, (Unit.REFLECTANCE), (np.float32))
    for name in [ "Blue", "Green", "Red", "RedEdge1", "RedEdge2", 
                 "RedEdge3", "NIR_Broad", "NIR_Narrow", "SWIR1", "SWIR2", "WaterVapor"]
    )
    bands = optical_bands
    hsl_collection = DataCollection.define(
    name="Harmonized LandSat Sentinel",
    api_id="hls",
    catalog_id="hls",
    collection_type="HLS",
    service_url="https://services-uswest2.sentinel-hub.com",
    bands=bands
    )
    idpunto = int(id)
    dffiles = pd.DataFrame()
    str_list = ["Blue", "Green", "Red", "RedEdge1", "RedEdge2", 
                 "RedEdge3", "NIR_Broad", "NIR_Narrow", "SWIR1", "SWIR2", "WaterVapor"]
    for x in range(len(str_list)):
        band = str_list[x]
        bandletter = band
        '''
        INT8 - signed 8-bit integer (values should range from -128 to 127)
        UINT8 - unsigned 8-bit integer (values should range from 0 to 255)
        INT16 - signed 16-bit integer (values should range from -32768 to 32767)
        UINT16 - unsigned 16-bit integer (values should range from 0 to 65535)
        FLOAT32 - 32-bit floating point (values have effectively no limits)
        AUTO (default) - values should range from 0-1, which will then automatically be stretched 
        from the interval [0, 1] to [0, 255] and written into an UINT8 raster. Values below 0 and above 
        1 will be clamped to 0 and 255, respectively. This is the default if sampleType is not set in the output object.
        '''
        tiffuserfolderband=tiffuserfolder + '/' + band
        evalscriptin = evalscript_XXX_band_Reflectance.replace("XXX",bandletter)
        evalscriptin = evalscriptin.replace("YYY",unit)
        controldatosdescargados = 0
        print("en saveBandTiff 20: ")
        #no ejecutar si ya exise del registro en la bbdd y es csvfile
        if reference == 'csvfile':
            controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
        else:
            controldatosdescargados = 0
        if controldatosdescargados == 0:
            request_all_bands = SentinelHubRequest(
            data_folder=tiffuserfolderband,
            evalscript=evalscriptin,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=hsl_collection,
                    time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                    maxcc=maxccvalue,
                )
            ],

            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=switchBandResolutionbbox(band,offset,minmax),
            size=switchBandResolutionsize(band,offset,minmax),
            config=config,
            )
            all_bands_img = request_all_bands.get_data(save_data=True)
            print(
            "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
            )

            for folder, _, filenames in os.walk(request_all_bands.data_folder):
                for filename in filenames:
                    file = os.path.join(folder, filename)
                    print(file)
                    #add file ref fo pandas dataframe
                    if idpunto > 0:
                        new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid,'satellite':satellite}, index=[0])
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                    else :
                        new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                        dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
    return dffiles


def saveAllBandsTiffDN( tiffuserfolder, str_datacollection_type ,offset,minmax,dateread,enddate,config,maxccvalue,token,id,numline,reference,userid):

    print("en saveBandTiff 10: ")
    idpunto = int(id)
    dffiles = pd.DataFrame()
    str_list = ["01","02","03","04","05","06","07","08","8A","09","11","12"]
    for x in range(len(str_list)):
        band = str_list[x]
        bandletter = "B" + band
        tiffuserfolderband=tiffuserfolder + '/' + band
        evalscriptin = evalscript_XXX_band_DN.replace("XXX",bandletter)
        controldatosdescargados = 0
        print("en saveBandTiff 20: ")
        if str_datacollection_type ==  's2l1c':
            #no ejecutar si ya exise del registro en la bbdd y es csvfile
            if reference == 'csvfile':
                controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
            else:
                controldatosdescargados = 0
            if controldatosdescargados == 0:
                request_all_bands = SentinelHubRequest(
                data_folder=tiffuserfolderband,
                evalscript=evalscriptin,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L1C.define_from(
                            str_datacollection_type, service_url=config.sh_base_url
                        ),
                        time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                        mosaicking_order=MosaickingOrder.LEAST_CC
                    )
                ],

                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=switchBandResolutionbbox(band,offset,minmax),
                size=switchBandResolutionsize(band,offset,minmax),
                config=config,
                )
                all_bands_img = request_all_bands.get_data(save_data=True)
                print(
                "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                )

                for folder, _, filenames in os.walk(request_all_bands.data_folder):
                    for filename in filenames:
                        file = os.path.join(folder, filename)
                        print(file)
                        #add file ref fo pandas dataframe
                        if idpunto > 0:
                            new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid}, index=[0])
                            dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        else :
                            new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                            dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
        if str_datacollection_type ==  's2l2a':
            #no ejecutar si ya exise del registro en la bbdd y es csvfile
            if reference == 'csvfile':
                controldatosdescargados =  checkCsvLineaProcesado(id,numline,bandletter,userid, str_datacollection_type,0)
            else:
                controldatosdescargados = 0
            if controldatosdescargados == 0:
                request_all_bands = SentinelHubRequest(
                data_folder=tiffuserfolderband,
                evalscript=evalscriptin,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A.define_from(
                            str_datacollection_type, service_url=config.sh_base_url
                        ),
                        time_interval=(dateread.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")),
                        mosaicking_order=MosaickingOrder.LEAST_CC
                    )
                ],

                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=switchBandResolutionbbox(band,offset,minmax),
                size=switchBandResolutionsize(band,offset,minmax),
                config=config,
                )
                all_bands_img = request_all_bands.get_data(save_data=True)
                print(
                "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
                )

                for folder, _, filenames in os.walk(request_all_bands.data_folder):
                    for filename in filenames:
                        file = os.path.join(folder, filename)
                        print(file)
                        #add file ref fo pandas dataframe
                        if idpunto > 0:
                            new_row = pd.DataFrame({'Band':bandletter, 'Path':file,'id':id,'reference':reference,'linefile':numline, 'userid':userid}, index=[0])
                            dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
                        else :
                            new_row = pd.DataFrame({'Band':bandletter, 'Path':file}, index=[0])
                            dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
    return dffiles



def saveEvalScripTiff(tiffuserfolder, str_datacollection_type ,offset,minmax,dateini, datefin,config,maxccvalue,script ,resolution,token):
    dffiles = pd.DataFrame()
    if str_datacollection_type ==  's2l2a':
        request_all_bands = SentinelHubRequest(
        data_folder=tiffuserfolder,
        evalscript=script,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    str_datacollection_type, service_url=config.sh_base_url
                ),
                time_interval=(dateini,datefin),
                maxcc=maxccvalue
            )
        ],
        

        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=Resolutionbbox(offset,minmax),
        size=Resolutionsize(offset,minmax,resolution),
        config=config,
        )
        all_bands_img = request_all_bands.get_data(save_data=True)
        print(
        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
        )

        for folder, _, filenames in os.walk(request_all_bands.data_folder):
            for filename in filenames:
                file = os.path.join(folder, filename)
                print(file)
                #add file ref fo pandas dataframe
                new_row = pd.DataFrame({ 'Path':file}, index=[0])
                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)
        print(dffiles)
    if str_datacollection_type ==  's2l1c':
        request_all_bands = SentinelHubRequest(
        data_folder=tiffuserfolder,
        evalscript=script,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C.define_from(
                    str_datacollection_type, service_url=config.sh_base_url
                ),
                time_interval=(dateini,datefin),
                maxcc=maxccvalue
            )
        ],

        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=Resolutionbbox(offset,minmax),
        size=Resolutionsize(offset,minmax,resolution),
        config=config,
        )
        all_bands_img = request_all_bands.get_data(save_data=True)
        print(
        "The output directory has been created and a tiff file with all 13 bands was saved into the following structure:\n"
        )

        for folder, _, filenames in os.walk(request_all_bands.data_folder):
            for filename in filenames:
                file = os.path.join(folder, filename)
                print(file)
                #add file ref fo pandas dataframe
                new_row = pd.DataFrame({'Path':file}, index=[0])
                dffiles = pd.concat([new_row,dffiles.loc[:]]).reset_index(drop=True)

    return dffiles

def switchBandResolutionbbox(band,offset,minmax):
    #set up box
    return  BBox(((minmax[0]-offset,minmax[1]-offset), (minmax[2]+offset,minmax[3]+offset)), crs=CRS('4326'))
def switchBandResolutionsize(band,offset,minmax):
    print("switchBandResolutionsize, band: ",band)
    if band == "01":
        resolution = 60
    if band == "02":
        resolution = 10
    if band == "03":
        resolution = 10
    if band == "04":
        resolution = 10
    if band == "05":
        resolution = 20
    if band == "06":
        resolution = 20
    if band == "07":
        resolution = 20
    if band == "08":
        resolution = 10
    if band == "8A":
        resolution = 20
    if band == "09":
        resolution = 60
    if band == "11":
        resolution = 20
    if band == "12":
        resolution = 20
    if band == "Blue":
        resolution = 60    
    if band == "Green":
        resolution = 20    
    if band == "Red":
        resolution = 20    
    if band == "RedEdge1":
        resolution = 20    
    if band == "RedEdge2":
        resolution = 20    
    if band == "RedEdge3":
        resolution = 20    
    if band == "NIR_Broad":
        resolution = 20    
    if band == "NIR_Narrow":
        resolution = 10    
    if band == "SWIR1":
        resolution = 20  
    if band == "SWIR2":
        resolution = 20  
    if band == "WaterVapor":
        resolution = 60
    if band == "GNDVI":
        resolution = 20
    if band == "NDMI":
        resolution = 20
    if band == "all":
        resolution = 10


    #set up box
    bbox = BBox(((minmax[0]-offset,minmax[1]-offset), (minmax[2]+offset,minmax[3]+offset)), crs=CRS('4326'))
    #print("switchBandResolutionsize:Box size = ")
    #print(bbox_to_dimensions(bbox, resolution=resolution))
    return bbox_to_dimensions(bbox, resolution=resolution)

def Resolutionbbox(offset,minmax):
    #set up box
    return  BBox(((minmax[0]-offset,minmax[1]-offset), (minmax[2]+offset,minmax[3]+offset)), crs=CRS('4326'))
def Resolutionsize(offset,minmax,resolution):
    #set up box
    bbox = BBox(((minmax[0]-offset,minmax[1]-offset), (minmax[2]+offset,minmax[3]+offset)), crs=CRS('4326'))
    print("Resolutionsize: Box size = ")
    print(bbox_to_dimensions(bbox, resolution=resolution))
    return bbox_to_dimensions(bbox, resolution=resolution)