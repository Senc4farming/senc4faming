import sys
import subprocess
sys.path.append('Scripts/')
import gdal_merge
import zipfile
import os
import time
import readline, glob
from pathlib import Path
import rasterio as rs
from osgeo import gdal,ogr
import os 
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def generate_geotiffs(inputProductPath, outputPath):

    basename =  os.path.basename(inputProductPath)
    if os.path.isdir(outputPath + basename[:-3] + "SAFE") :
        print('Already extracted')
    else:
        zip = zipfile.ZipFile(inputProductPath)
        zip.extractall(outputPath)
        print("Extracting Done")


    directoryName = outputPath + basename[:-3] + "SAFE/GRANULE"

    productName = os.path.basename(inputProductPath)[:-4]
    outputPathSubdirectory = outputPath + productName + "_PROCESSED"

    if not os.path.exists(outputPathSubdirectory):
        os.makedirs(outputPathSubdirectory)

    subDirectorys = get_immediate_subdirectories(directoryName)

    results = []

    for granule in subDirectorys:
        unprocessedBandPath = outputPath + productName + ".SAFE/GRANULE/" + granule + "/" + "IMG_DATA/"
        #print(unprocessedBandPath)
        results.append(generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory))

    #gdal_merge.py -n 0 -a_nodata 0 -of GTiff -o /home/daire/Desktop/merged.tif /home/daire/Desktop/aa.tif /home/daire/Desktop/rgbTiff-16Bit-AllBands.tif
    merged = outputPathSubdirectory + "/merged.tif"
    params = ['',"-of", "GTiff", "-o", merged]

    for granule in results:
        params.append(granule)

    gdal_merge.main(params)

def training_points(raster, shp):
    lsx=[]
    lsy=[]
    lsz=[]
    src_ds=gdal.Open(raster) 
    gt=src_ds.GetGeoTransform()
    rb=src_ds.GetRasterBand(1)
    print('gt[0]) / gt[1]')
    format_float = "{:.2f}".format(gt[0])
    print(format_float)
    format_float1 = "{:.2f}".format(gt[1])
    print(format_float1)
    format_float = "{:.2f}".format(gt[0])
    print(format_float)
    format_float1 = "{:.2f}".format(gt[1])
    print(format_float1)
    ds=ogr.Open(shp)
    lyr=ds.GetLayer()
    for feat in lyr:
        geom = feat.GetGeometryRef()
        mx,my=geom.GetX(), geom.GetY()  #coord in map units

        #Convert from map to pixel coordinates.
        #Only works for geotransforms with no rotation.
        px = int((mx - gt[0]) / gt[1]) #x pixel
        py = int((my - gt[3]) / gt[5]) #y pixel

        intval=rb.ReadAsArray(px,py,1,1)

        value = float(intval[0]) #### this is the value of the pixel, forcing it to a float
        x = float(mx)
        y = float(my)
        lsz.append(value)
        lsx.append(x)
        lsy.append(y)
		
    return lsx, lsy, lsz

def generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory):

    granuleBandTemplate =  granule[:-6]
    granpart_1 = unprocessedBandPath.split(".SAFE")[0][-22:-16]
    granule_2 = unprocessedBandPath.split(".SAFE")[0][-49:-34]

    granuleBandTemplate = granpart_1 + "_" + granule_2 + "_"
    #sys.exit()
    global tiff_image
    tiff_image = outputPathSubdirectory+ "/IMAGE_DATA"
    outputPathSubdirectory = outputPathSubdirectory
    if not os.path.exists(outputPathSubdirectory+ "/IMAGE_DATA"):
        os.makedirs(outputPathSubdirectory+ "/IMAGE_DATA")
        
    if not os.path.exists(outputPathSubdirectory+ "/IMAGE_DATA/TODAS"):
        os.makedirs(outputPathSubdirectory+ "/IMAGE_DATA/TODAS")

    outPutTiff = '/'+granule[:-6]+'16Bit-AllBands.tif'
    outPutVRT = '/'+granule[:-6]+'16Bit-AllBands.vrt'

    outPutFullPath = outputPathSubdirectory + "/IMAGE_DATA/TODAS" + outPutTiff
    outPutFullVrt = outputPathSubdirectory + "/IMAGE_DATA/TODAS" + outPutVRT
    inputPath = unprocessedBandPath #+ granuleBandTemplate

    #print("\n\t" + inputPath)

    
    bands = {
        "02" :  inputPath + "R10m/" + granuleBandTemplate +  "B02_10m.jp2",
        "03" :  inputPath + "R10m/" + granuleBandTemplate +  "B03_10m.jp2",
        "04" :  inputPath + "R10m/" + granuleBandTemplate +  "B04_10m.jp2",
        "05" :  inputPath + "R20m/" + granuleBandTemplate +  "B05_20m.jp2",
        "06" :  inputPath + "R20m/" + granuleBandTemplate +  "B06_20m.jp2",
        "07" :  inputPath + "R20m/" + granuleBandTemplate +  "B07_20m.jp2",
        "08" :  inputPath + "R10m/" + granuleBandTemplate +  "B08_10m.jp2",
        "8A" :  inputPath + "R20m/" + granuleBandTemplate +  "B8A_20m.jp2",
        "11" :  inputPath + "R20m/" + granuleBandTemplate +  "B11_20m.jp2",
        "12" :  inputPath + "R20m/" + granuleBandTemplate +  "B12_20m.jp2"}
    tiffs = {
        "02" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B02.tif",
        "03" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B03.tif",
        "04" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B04.tif",
        "05" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B05.tif",
        "06" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B06.tif",
        "07" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B07.tif",
        "08" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B08.tif",
        "8A" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B8A.tif",
        "11" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B11.tif",
        "12" :  outputPathSubdirectory + "/IMAGE_DATA/" + "B12.tif"}
	
    vrt = {
        "02" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B02.vrt",
        "03" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B03.vrt",
        "04" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B04.vrt",
        "05" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B05.vrt",
        "06" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B06.vrt",
        "07" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B07.vrt",
        "08" :  outputPathSubdirectory + "/IMAGE_DATA/" +   "B08.vrt",
        "8A" :  outputPathSubdirectory + "/IMAGE_DATA/" + "B8A.vrt",
        "11" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B11.vrt",
        "12" :  outputPathSubdirectory + "/IMAGE_DATA/" +  "B12.vrt"}

    
    


    for i in bands:
        cmd_unitario = ['gdalbuildvrt', '-resolution', 'user', '-tr' ,'20', '20', '-separate',vrt[i],bands[i] ]
        subprocess.call(cmd_unitario)
        cmd_unitario_1 = ['gdal_translate', '-of' ,'GTiff', vrt[i], tiffs[i]]
        print('Archivo de salida:' +  tiffs[i] )
        my_file = Path(tiffs[i])
        if not my_file.is_file():
            # file exists
            subprocess.call(cmd_unitario_1)
    cmd = ['gdalbuildvrt', '-resolution', 'user', '-tr' ,'20', '20', '-separate' ,outPutFullVrt]
    for band in sorted(bands.values()):
        cmd.append(band)

    my_file = Path(outPutFullVrt)
    if not my_file.is_file():
        # file exists
        subprocess.call(cmd)

    #, '-a_srs', 'EPSG:3857'
    cmd = ['gdal_translate', '-of' ,'GTiff', outPutFullVrt, outPutFullPath]
    print('Archivo de salida:' +  outPutTiff );
    my_file = Path(outPutTiff)
    if not my_file.is_file():
        # file exists
        subprocess.call(cmd)



    #params = ['', '-o', outPutFullPath, '-separate', band_02, band_03, band_04, band_05, band_06, band_07, band_08, band_8A, band_10, band_11, band_12]

    #gdal_merge.main(params)

    return(outPutFullPath)


outputPath = './Output/'
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)
inputPath = input("Input Path? ")

start_time = time.time()

generate_geotiffs(inputPath, outputPath)

print("--- %s seconds ---" % (time.time() - start_time))

print("Procesando puntos")
##merge with all bands to 20 m
inputPath = tiff_image
#folder for coords inmput
shppath = './Inputs/prov_cyl_recintos/'
## My points
shpfile = 'prov_cyl_recintos.shp'
shp = shppath + shpfile
## create a 3dplot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
## lable axis
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('reflectance') 

## Using 6 bands so I need 6 colours
colours = ['blue', 'green', 'yellow', 'purple', 'brown', 'orange']
## count to control colours
count = 0
## loop through my source directory
for root, dirs, filenames in os.walk(tiff_image):
    for file in filenames:
    ## looking for tiles ending with TIF
        if file.endswith('tif'):
            raster = os.path.join(tiff_image, file)
            lsx, lsy, lsz = training_points(raster, shp)
            ax.scatter(lsx, lsy, lsz, s=500, c=colours[count])
            count +=1
## I am cheating a bit here I know that the bands are in this order
plt.legend(["Band 2", "Band 3", "Band 4", "Band 5", "Band 6", "Band 7"])

## show my plot
plt.show()
