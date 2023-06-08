
import sys
import subprocess
sys.path.append('Scripts/')
import gdal_merge
from sentinelsat import SentinelAPI
from shapely.geometry import Polygon
import numpy as np
from geotiff import GeoTiff
from scipy.interpolate import RectBivariateSpline
import sys
import os
import glob
import pyproj
from osgeo import gdal,ogr
from shapely.ops import transform
from rasterio.io import MemoryFile
from optparse import OptionParser
import pathlib
import zipfile
from pykml import parser as parserkml
import pandas as pd
from xml.dom.minidom import parseString
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from osgeo import gdal,ogr,osr
from osgeo.gdalconst import *
import PIL
from PIL import Image
import rasterio
from rasterio.mask import mask
from rasterio import plot
from rasterio.plot import show
from rasterio.coords import BoundingBox
from rasterio import windows
from rasterio import warp
from rasterio import mask
import rasterio.plot as plot
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rasterio.plot import show_hist
import folium
import webbrowser
import numpy as np
import affine 

def get_tallinn_polygon(swap_coordinates=False):
    tln_points = [
        (59.455947169131946, 24.532626930520898),
        (59.47862155366181, 24.564212623880273),
        (59.49535595077547, 24.69810849790371),
        (59.51138530046753, 24.825137916849023),
        (59.459087606762346, 24.907535377786523),
        (59.4147455486766, 24.929508034036523),
        (59.39832075950073, 24.844363991067773),
        (59.37664183245853, 24.814151588724023),
        (59.35249898189222, 24.75304013852871),
        (59.32798867805195, 24.573825660989648)
    ]
    # Copernicus hub likes polygons in lng/lat format
    return Polygon([(y, x) if swap_coordinates else (x, y) for x, y in tln_points])

def get_tallinn_polygon_ge(swap_coordinates=False):
    print("polygon")
    src_root_kml_path = "../files/src_data_kml"
    filenamefullpath = src_root_kml_path + "/" + options.polygonfile
    i=0
    for p in readPoly(filenamefullpath):
        p,desc=p
        i=i+1
        print(p)
        #stats=polyStats(p)
        #desc.update(stats)
        #print ('Polygon #%i' % i)
        #for d,v in desc.iteritems():
        #    print ('%16s: %s' % (d,v))
        #print ('')
    # Copernicus hub likes polygons in lng/lat format
    return Polygon([(y, x) if swap_coordinates else (x, y) for x, y in p])

def plot(arr):
    x = np.array(range(arr.shape[0]))
    y = np.array(range(arr.shape[1]))
    z = arr
    fig, ax = plt.subplots(nrows=1, ncols=2, subplot_kw={'projection': '3d'})
    ax[0].plot_wireframe(x, y, z, color='k')
    for axes in ax:
        axes.set_zlim(-0.2,1)
        axes.set_axis_off()

    fig.tight_layout()
    plt.show()

def extrapolate(arr, target_dim):
    x = np.array(range(arr.shape[0]))
    y = np.array(range(arr.shape[1]))
    z = arr
    xx = np.linspace(x.min(), x.max(), target_dim[0])
    yy = np.linspace(y.min(), y.max(), target_dim[1])
    
    new_kernel = RectBivariateSpline(x, y, z, kx=2, ky=2)
    narr = new_kernel(xx, yy)
    x1 = np.array(range(narr.shape[0]))
    y1 = np.array(range(narr.shape[1]))
    fig, ax = plt.subplots(nrows=1, ncols=2, subplot_kw={'projection': '3d'})
    ax[0].plot_wireframe(x, y, z, color='k')

    ax[1].plot_wireframe(x1, y1, narr, color='k')
    for axes in ax:
        axes.set_zlim(-0.2,1)
        axes.set_axis_off()

    fig.tight_layout()
    plt.show()
    sys.exit()
    result = narr

def extrapolatedown(arr, target_dim):
    x = np.array(range(arr.shape[0]))
    y = np.array(range(arr.shape[1]))
    z = arr
    xx = np.linspace(x.min(), x.max(), target_dim[0])
    yy = np.linspace(y.min(), y.max(), target_dim[1])
    
    new_kernel = RectBivariateSpline(x, y, z, kx=2, ky=2)
    result = new_kernel(xx, yy)

    return result
def reproject(polygons, proj_from, proj_to):
    proj_from = pyproj.Proj(proj_from)
    proj_to = pyproj.Proj(proj_to)
    
    projection = pyproj.Transformer.from_proj(proj_from, proj_to)
    return [transform(projection.transform, p) for p in polygons]

#TRANS_32630_TO_4326 = pyproj.Transformer.from_crs("ESPG:32630","ESPG:4326")

def crop_memory_tiff_file(mem_file, polygons, crop):
    polygons = reproject(polygons, "EPSG:4326", mem_file.crs)
    result_image, result_transform = mask(mem_file, polygons, crop=crop)
    
    profile = mem_file.profile
    profile.update(width=result_image.shape[1], 
                   height=result_image.shape[2], 
                   transform=result_transform)

    result_f = MemoryFile().open(**profile)
    result_f.write(result_image)
    
    return result_f

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def openKMZ(filename):
    zip=ZipFile(filename)
    for z in zip.filelist:
        if z.filename[-4:] == '.kml':
            fstring=zip.read(z)
            break
    else:
        raise Exception("Could not find kml file in %s" % filename)
    return fstring

def openKML(filename):
    try:
        fstring=openKMZ(filename)
    except Exception:
        fstring=open(filename,'r').read()
    return parseString(fstring)


def readPoly(filename):
    def parseData(d):
        dlines=d.split()
        poly=[]
        for l in dlines:
            l=l.strip()
            if l:
                point=[]
                for x in l.split(','):
                    point.append(float(x))
                poly.append(point[:2])
        return poly

    xml=openKML(filename)
    nodes=xml.getElementsByTagName('Placemark')
    desc={}
    for n in nodes:
        names=n.getElementsByTagName('name')
        try:
            desc['name']=names[0].childNodes[0].data.strip()
        except Exception:
            pass
        
        descriptions=n.getElementsByTagName('description')
        try:
            desc['description']=names[0].childNodes[0].data.strip()
        except Exception:
            pass

        times=n.getElementsByTagName('TimeSpan')
        try:
            desc['beginTime']=times[0].getElementsByTagName('begin')[0].childNodes[0].data.strip()
            desc['endTime'  ]=times[0].getElementsByTagName('end'  )[0].childNodes[0].data.strip()
        except Exception:
            pass

        times=n.getElementsByTagName('TimeStamp')
        try:
            desc['timeStamp']=times[0].getElementsByTagName('when')[0].childNodes[0].data.strip()
        except Exception:
            pass

            
        polys=n.getElementsByTagName('Polygon')
        for poly in polys:
            invalid=False
            c=n.getElementsByTagName('coordinates')
            if len(c) != 1:
                print ('invalid polygon found')
                continue
            if not invalid:
                c=c[0]
                d=c.childNodes[0].data.strip()
                data=parseData(d)
                yield (data,desc)

def latlon2meters(p):
    pi2=2.*math.pi
    reradius=1./6370000
    alat=0
    alon=0
    for i in p:
        alon=alon+i[0]
        alat=alat+i[1]
    lon_ctr=alon/len(p)
    lat_ctr=alat/len(p)
    unit_fxlat=pi2/(360. * reradius)
    unit_fxlon=math.cos(lat_ctr*pi2/360.) * unit_fxlat

    q=[]
    olon=p[0][0]
    olat=p[0][1]
    for i in p:
        q.append( ( (i[0] - olon) * unit_fxlon , \
                    (i[1] - olat) * unit_fxlat ) )
    return q

def polyStats(p):
    pm=Polygon(latlon2meters(p))
    area=pm.area()
    numpts=len(p)
    pl=Polygon(p)
    bbox=pl.boundingBox()
    center=pl.center()

    stat=\
            {'vertices':'%i' % numpts,
             'bounding box':'(%f , %f) - (%f , %f)' % (bbox[0],bbox[2],bbox[1],bbox[3]),
             'center':'(%f , %f)' % (center[0],center[1]),
             'area':'%f m^2' % (area) }
    return stat

def makepoly(p):
    return Polygon(p)

def intersect(p1,p2):
    q1=makepoly(p1)
    q2=makepoly(p2)

    q=q1 & q2

    return q

def get_area(p):
    q=makepoly(p)
    return p.area()

def write_poly(p,fname):
    if isinstance(fname,basestring):
        f=open(fname,'w')
    else:
        f=fname
    for i in p:
        f.write('%19.16f,%19.16f,0.\n' % (i[0],i[1]))
    f.flush()

def read_poly(fname):
    if isinstance(fname,basestring):
        f=open(fname,'r')
    else:
        f=fname
    s=f.readlines()
    p=[]
    for i in s:
        i=i.strip()
        j=i.split(',')
        p.append((float(j[0]),float(j[1])))
    return p

def poly2kmz(pp,fname):
    strs=[]
    i=0
    for p in pp:
        i=i+1
        f=StringIO()
        write_poly(p,f)
        strs.append(polystr % (i,f.getvalue()))
    s='\n'.join(strs)
    s=kmlstr % (fname,s)
    open(fname,'w').write(s)

def decimal(obj):
    is_point = False
    decimals = []
    for get_float in str(obj):
        if is_point:
            decimals.append(get_float)
        if get_float == ".":
            is_point = True
    return len(decimals)
def isclose1(a, b, rel_tol, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory,bands_and_resolutions):

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

    outPutTiff = '/'+granule[:-6]+'16Bit-AllBands.tiff'
    outPutVRT = '/'+granule[:-6]+'16Bit-AllBands.vrt'

    outPutFullPath = outputPathSubdirectory + "/IMAGE_DATA/TODAS" + outPutTiff
    outPutFullVrt = outputPathSubdirectory + "/IMAGE_DATA/TODAS" + outPutVRT
    inputPath = unprocessedBandPath #+ granuleBandTemplate

    for i, (band, resolution,band_resolutions) in enumerate(bands_and_resolutions, start=1):
        band_path = inputPath + resolution +"/" + granuleBandTemplate + band + "_" + band_resolutions + ".jp2"
        vrt_path = outputPathSubdirectory + "/IMAGE_DATA/" + band + ".vrt"
        tiff_path = outputPathSubdirectory + "/IMAGE_DATA/" + band + ".tiff"
        cmd_unitario = ['gdalbuildvrt', '-resolution', 'user', '-tr' ,'20', '20', '-separate',vrt_path,band_path]
        subprocess.call(cmd_unitario)
        cmd_unitario_1 = ['gdal_translate', '-of' ,'GTiff', vrt_path,tiff_path,]
        print('Archivo de salida:' + tiff_path )
        my_file = Path(tiff_path)
        if not my_file.is_file():
            # file exists
            subprocess.call(cmd_unitario_1)
    cmd = ['gdalbuildvrt', '-resolution', 'user', '-tr' ,'20', '20', '-separate' ,outPutFullVrt]
    for j, (band, resolution,band_resolutions) in enumerate(bands_and_resolutions, start=1):
        band_path = inputPath + resolution +"/"+ granuleBandTemplate + band + "_" + band_resolutions + ".jp2"
        cmd.append(band_path)
    print(cmd)

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

def reverse_coordinates(pol):
    """
    Reverse the coordinates in pol
    Receives list of coordinates: [[x1,y1],[x2,y2],...,[xN,yN]]
    Returns [[y1,x1],[y2,x2],...,[yN,xN]]
    """
    return [list(f[-1::-1]) for f in pol]

def to_index(wind_):
    """
    Generates a list of index (row,col): [[row1,col1],[row2,col2],[row3,col3],[row4,col4],[row1,col1]]
    """
    return [[wind_.row_off,wind_.col_off],
            [wind_.row_off,wind_.col_off+wind_.width],
            [wind_.row_off+wind_.height,wind_.col_off+wind_.width],
            [wind_.row_off+wind_.height,wind_.col_off],
            [wind_.row_off,wind_.col_off]]

def generate_polygon(bbox):
    """
    Generates a list of coordinates: [[x1,y1],[x2,y2],[x3,y3],[x4,y4],[x1,y1]]
    """
    return [[bbox[0],bbox[1]],
             [bbox[2],bbox[1]],
             [bbox[2],bbox[3]],
             [bbox[0],bbox[3]],
             [bbox[0],bbox[1]]]

def pol_to_np(pol):
    """
    Receives list of coordinates: [[x1,y1],[x2,y2],...,[xN,yN]]
    """
    return np.array([list(l) for l in pol])

def pol_to_bounding_box(pol):
    """
    Receives list of coordinates: [[x1,y1],[x2,y2],...,[xN,yN]]
    """
    arr = pol_to_np(pol)
    return BoundingBox(np.min(arr[:,0]),
                       np.min(arr[:,1]),
                       np.max(arr[:,0]),
                       np.max(arr[:,1]))

def sampleRaster(r,pts,band=1):
    """ 
    Providing a rasterio raster and numpy 2-D array of coordinates, returns
    the values at that point. Assumes CRS of raster and coordinates are the 
    same.
    Args:
        r: Rasterio raster 
        pts: Numpy array of dimensions (n,2)
        band: The raster band number to be evaluated, defaults to 1
    Example:
        r = rasterio.open("raster.tif")
        pts = np.genfromtxt("points.csv",delimiter=",",skip_header=1,usecols=(1,2))
        rasterVals = sampleRaster(r,pts)
    """
    ras = r.read(band)
    inPts = pts[np.where((pts[:, 0] >= r.bounds[0]) & (pts[:, 0] < r.bounds[2]) & (pts[:, 1] >= r.bounds[1]) & (pts[:, 1] < r.bounds[3]))]
    originX = r.bounds[0]
    originY = r.bounds[3]
    cellSize = r.transform[0]
    col = ((inPts[:, 0] - originX) / cellSize).astype(int)
    row = ((originY - inPts[:, 1]) / cellSize).astype(int)
    res = ras[row,col]
    return(inPts,res)

def main(options):
    print ("[DEBUG] sys.argv[1:] = {}\n".format(sys.argv[1:]))
    #usuario y password
    username = "jmafernandez"
    password = "EneasDuna2805.."
    #rutas internas
    src_root_data_dir = "../files/src_data"
    src_root_data_dir_proc = "../files/src_data_proc"
    src_root_data_dir_processs = "../files/src_data_process"
    src_root_data_dir_processs_gdal = "../files/src_data_process_gdal"
    src_root_data_safe = "../files/src_data_safe"


    if options.action:
        if options.action == "listar":
            hub = SentinelAPI(username, password, "https://scihub.copernicus.eu/dhus")
            if options.dateini and options.datefin:
                data_products = hub.query(
                    get_tallinn_polygon_ge(swap_coordinates=True),  # which area interests you
                    date=(options.dateini, options.datefin),
                    cloudcoverpercentage=(0, 10),  # we don't want clouds
                    platformname="Sentinel-2",
                    processinglevel="Level-2A"  # more processed, ready to use data
                )
                data_products = hub.to_geodataframe(data_products)
                if options.keyboard:
                    # we want to avoid downloading overlapping images, so selecting by this keyword
                    data_products = data_products[data_products["title"].str.contains(options.keyboard)]
                print(data_products)
            else:
                print("Datos mínimos para la busqueda fecha inicio y fecha fin")
                print("-a listar -i 20230101 -f 20230405 -k T34VFL")
        elif options.action == "descargar":
            if options.hub:
                #movemos todos los archivos antes de descargar
                source = src_root_data_dir 
                destination = src_root_data_dir_proc 
                zipfiles = [f for f in os.listdir(source) if '.zip' in f.lower()]

                for f in zipfiles:
                    old_path = source +'/' + f
                    new_path = destination +'/' + f
                    if not os.path.exists(new_path):
                        pathlib.Path(old_path).rename(new_path)
                #desargamos el nuevo zip
                hub = SentinelAPI(username, password, "https://scihub.copernicus.eu/dhus")
                hub.download(options.hub,src_root_data_dir)
            else:
                print("Informar la cadena de descarga")
        elif options.action == "descomprimir":
            #zip file with folder
            zipfilestr = "/"
            basename = "1"
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
                    
            if basename != 1:
                if os.path.isdir(src_root_data_safe + "/" + basename[:-3] + "SAFE") :
                    print('Already extracted')
                else:
                    zipf = zipfile.ZipFile(zipfilestr)
                    zipf.extractall(src_root_data_safe)
                    print("Extracting Done")
        elif options.action == "procesar_stiky":
            zipfilestr = "/"
            basename = "1"
            productName = ""
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            #valores iniciales para descargas
            bands = ["B02", "B03", "B04","B05","B06","B07", "B08", "B8A", "B11", "B12"]
            resolutions = ["R10m", "R10m", "R10m","R20m","R20m","R20m","R10m", "R20m", "R20m", "R20m"]
            bands_and_resolutions = list(zip(bands, resolutions))
            target_dim = (10980, 10980)
            #target_dim = (5490, 5490)
            #variables para los directorios
            directoryName = src_root_data_safe +"/" + basename[:-3] + "SAFE/GRANULE"

            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs+"/" + productName + "_PROCESSED"

            if not os.path.exists(outputPathSubdirectory):
                os.makedirs(outputPathSubdirectory)

            subDirectorys = get_immediate_subdirectories(directoryName)

            src_data_dirs = []
            unprocessedBandPath = ""
            tiff_image_dir = ""
            outPutFullPath = ""
            outPutFullVrt = ""
            inputPath = ""
            for granule in subDirectorys:
                unprocessedBandPath = src_root_data_safe +"/"+ productName + ".SAFE/GRANULE/" + granule + "/" + "IMG_DATA/"
                #variables para gestión de tiff
                granuleBandTemplate =  granule[:-6]
                granpart_1 = unprocessedBandPath.split(".SAFE")[0][-22:-16]
                granule_2 = unprocessedBandPath.split(".SAFE")[0][-49:-34]

                granuleBandTemplate = granpart_1 + "_" + granule_2 + "_"
                #sys.exit()
                tiff_image_dir = outputPathSubdirectory+ "/IMAGE_DATA"
                outputPathSubdirectory = outputPathSubdirectory
                if not os.path.exists(outputPathSubdirectory+ "/IMAGE_DATA"):
                    os.makedirs(outputPathSubdirectory+ "/IMAGE_DATA")
                    
                if not os.path.exists(outputPathSubdirectory+ "/IMAGE_DATA/TODAS"):
                    os.makedirs(outputPathSubdirectory+ "/IMAGE_DATA/TODAS")
                print(unprocessedBandPath)
                
                #+ granuleBandTemplate
            #Combinamos imágenes den tiff
            for x in os.listdir(unprocessedBandPath):
                src_data_dir = glob.glob(os.path.join(unprocessedBandPath, x))[0]
                src_data_dirs.append(src_data_dir)
                print(src_data_dir)
            src_data_dirs = sorted(src_data_dirs, key=lambda x: x[0])
            for src_data_dir in src_data_dirs:
                tiff_file = os.path.join(tiff_image_dir,"TODAS" ,  granule[:-6] + "_all.tiff")
                print(tiff_file)
                if os.path.exists(tiff_file):
                    continue

                tiff_f = None

                for i, (band, resolution) in enumerate(bands_and_resolutions, start=1):
                    band_file = glob.glob(os.path.join(unprocessedBandPath, resolution, "*_" + band + "_*.jp2"))[0]
                    band_f = rasterio.open(band_file, driver="JP2OpenJPEG")
                    band_data = band_f.read(1)

                    #Caracteristicas de las imagenes
                    print("Datos para la banda antes:" +band)
                    x = np.array(range(band_data.shape[0]))
                    y = np.array(range(band_data.shape[1]))
                    z = band_data

                    if band_data.shape[0] < target_dim[0] and band_data.shape[1] < target_dim[1]:
                        print("Extrapolating", band_data.shape, "to", target_dim)
                        band_data = extrapolate(band_data, target_dim).astype(band_f.dtypes[0])
                        print("Datos para la banda despues:" +band)
                    else:
                        print("Grafico para la banda:" +band)
                        plot(band_data)

                    #if band_data.shape[0] > target_dim[0] and band_data.shape[1] >  target_dim[1]:
                    #    print("Extrapolating", band_data.shape, "to", target_dim)
                    #    band_data = extrapolate(band_data, target_dim).astype(band_f.dtypes[0])    

                    if tiff_f is None:  
                        profile = band_f.profile
                        profile.update(driver="Gtiff", count=len(bands_and_resolutions))
                        tiff_f = MemoryFile().open(**profile)
                        
                    print("Writing band {} ".format(band))
                    tiff_f.write(band_data, i)

                    
                    band_f.close()
                print("Antes del tiff_f_cropped")
                tiff_f_cropped = crop_memory_tiff_file(tiff_f, [get_tallinn_polygon_ge()], crop=True)
                print("Despues del tiff_f_cropped")
                tiff_f.close()
                tiff_f = None

                with rasterio.open(tiff_file, "w", **tiff_f_cropped.profile) as f:
                    f.write(tiff_f_cropped.read())
                    
                tiff_f_cropped.close()
        elif options.action == "procesar_gdal":
            basename = ""
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            
            #valores iniciales para descargas
            bands = ["B02", "B03", "B04","B05","B06","B07", "B08", "B8A", "B11", "B12"]
            band_resolutions = ["10m", "10m", "10m","20m","20m","20m","10m", "20m", "20m", "20m"]
            resolutions = ["R10m", "R10m", "R10m","R20m","R20m","R20m","R10m", "R20m", "R20m", "R20m"]
            bands_and_resolutions = list(zip(bands, resolutions,band_resolutions))
            
            #variables para los directorios
            directoryName = src_root_data_safe +"/" + basename[:-3] + "SAFE/GRANULE"

            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED"
            subDirectorys = get_immediate_subdirectories(directoryName)
            results = []
            for granule in subDirectorys:
                unprocessedBandPath = src_root_data_safe +"/"+ productName + ".SAFE/GRANULE/" + granule + "/" + "IMG_DATA/"
                #print(unprocessedBandPath)
                results.append(generate_all_bands(unprocessedBandPath, granule, outputPathSubdirectory,bands_and_resolutions))
            #gdal_merge.py -n 0 -a_nodata 0 -of GTiff -o /home/daire/Desktop/merged.tif /home/daire/Desktop/aa.tif /home/daire/Desktop/rgbTiff-16Bit-AllBands.tif
            merged = outputPathSubdirectory + "/merged.tif"
            params = ['',"-of", "GTiff", "-o", merged]

            for granule in results:
                params.append(granule)

            gdal_merge.main(params)
        elif options.action == "shpfile":
            basename = ""
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            rast = outputPathSubdirectory + "/" + tiff_file
            fc = ""
            #open vector layer
            drv=ogr.GetDriverByName('ESRI Shapefile') #assuming shapefile?
            ds=drv.Open(fc,True) #open for editing
            lyr=ds.GetLayer(0)

            #open raster layer
            src_ds=gdal.Open(rast) 
            gt=src_ds.GetGeoTransform()
            rb=src_ds.GetRasterBand(1)
            gdal.UseExceptions() #so it doesn't print to screen everytime point is outside grid

            for feat in lyr:
                geom=feat.GetGeometryRef()
                mx=geom.Centroid().GetX()
                my=geom.Centroid().GetY()

                px = int((mx - gt[0]) / gt[1]) #x pixel
                py = int((my - gt[3]) / gt[5]) #y pixel
                try: #in case raster isnt full extent
                    structval=rb.ReadRaster(px,py,1,1,buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
                    intval = struct.unpack('f' , structval) #assume float
                    val=intval[0]
                except:
                    val=-9999 #or some value to indicate a fail

            feat.SetField('YOURFIELD',val)
            lyr.SetFeature(feat)

        elif options.action == "coord_values_map":
            #https://opensourceoptions.com/blog/gdal-python-tutorial-reading-and-writing-raster-datasets/?utm_content=cmp-true
            basename = ""
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            for tiff_file in os.listdir(outputPathSubdirectory):
                # check only text files
                if tiff_file.endswith('.tiff'):
                    print(tiff_file)
                    geo_tiff = GeoTiff(outputPathSubdirectory + "/" + tiff_file)
                    # Open the raster and store metadata
                    src = rasterio.open(outputPathSubdirectory + "/" + tiff_file)
                    r = src.read()
                    print(r)
                    print ( "Min y max")
                    print (np.min(r))
                    print (np.max(r))
                    print ("r.shape")
                    print(r.shape)


                    #open raster layer
                    driver = gdal.GetDriverByName('GTiff')
                    src_ds=gdal.Open(outputPathSubdirectory + "/" + tiff_file)
                    #Get espg from tiff
                    proj = osr.SpatialReference(src_ds.GetProjection())
                    print("SpatialReference")
                    print(proj.GetAttrValue('AUTHORITY',1))

                    gt=src_ds.GetGeoTransform()
                    print("gt=src_ds.GetGeoTransform()")
                    print(gt)
                    Band =src_ds.GetRasterBand(1)


                    NoData = Band.GetNoDataValue()  # this might be important later

                    nBands = src_ds.RasterCount      # how many bands, to help you loop
                    nRows  = src_ds.RasterYSize      # how many rows
                    nCols  = src_ds.RasterXSize      # how many columns
                    dType  = Band.DataType          # the datatype for this band
                    print("Projection: ", src_ds.GetProjection())  # get projection
                    print("Columns:", src_ds.RasterXSize)  # number of columns
                    print("Rows:", src_ds.RasterYSize)  # number of rows
                    print("Band count:", src_ds.RasterCount)  # number of bands
                    print("Band dtype:", dType)  # number of bands

                    transform = src_ds.GetGeoTransform()
                    xOrigin = transform[0]
                    yOrigin = transform[3]
                    pixelWidth = transform[1]
                    pixelHeight = -transform[5]
                    #Read raster data
                    data_array = src_ds.GetRasterBand(1).ReadAsArray(0,0,nCols,nRows)

                    print("data_array.shape:", data_array.shape)
                    print("data_array[0]", data_array[0])

                    #Geting no data values
                    ndv = data_array = src_ds.GetRasterBand(1).GetNoDataValue()
                    print('No data value:', ndv)

                    data_array = src_ds.GetRasterBand(1).ReadAsArray()  # read band data from the existing raster
                    #data_nan = np.where(data_array == ndv, np.nan, data_array)  # set all the no data values to np.nan so we can easily calculate the minimum elevation
                    #data_min = np.min(data_nan)  # get the minimum elevation value (excluding nan)
                    #data_stretch = np.where(data_array == ndv, ndv, (data_array - data_min) * 1.5)  # now apply the strech algorithm
                    #print('Min:', np.min(data_nan))
                    #print('Max:', np.min(data_nan))


                    print("test de trans")
                    wgs_proj = pyproj.CRS("EPSG:4326")
                    utm_proj = pyproj.CRS("EPSG:32630")
                    print(pyproj.transform(utm_proj,wgs_proj,399960,4700040))

                    #leemos el csv con los datos
                    datos_coords = pd.read_csv('./csv/test1.csv', usecols= ['Longuitud','Latitud','Materiaorganica'])
                    #print(datos_coords)
                    for ind  in datos_coords.index:
                        long = datos_coords['Longuitud'][ind]
                        lat = datos_coords['Latitud'][ind]
                        value = datos_coords['Materiaorganica'][ind]
                 
                        print ('long,lat')
                        print (long,lat)
                        point = pyproj.transform(wgs_proj,utm_proj,lat,long)
                        print ('point[0],xOrigin')
                        print (point[0],xOrigin)
                        print ('yOrigin,point[1]')
                        print (yOrigin,point[1])
                        col = int((point[0] - xOrigin) / pixelWidth)
                        row = int((yOrigin - point[1] ) / pixelHeight)
                        
                        print ('row,col')
                        print (row,col)
                        print ( "Encntrado")
                        print ('data_array[row][col], value')
                        print ( data_array[row][col], value)

                    sys.exit()
        elif options.action == "coord_values":
            #https://opensourceoptions.com/blog/gdal-python-tutorial-reading-and-writing-raster-datasets/?utm_content=cmp-true
            basename = ""
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            for tiff_file in os.listdir(outputPathSubdirectory):
                # check only text files
                if tiff_file.endswith('.tiff'):
                    print(tiff_file)
                    geo_tiff = GeoTiff(outputPathSubdirectory + "/" + tiff_file)
                    # Open the raster and store metadata
                    src = rasterio.open(outputPathSubdirectory + "/" + tiff_file)
                    r = src.read()
                    print(r)
                    print ( "Min y max")
                    print (np.min(r))
                    print (np.max(r))
                    print ("r.shape")
                    print(r.shape)


                    #open raster layer
                    src_ds=gdal.Open(outputPathSubdirectory + "/" + tiff_file)
                    #Get espg from tiff
                    proj = osr.SpatialReference(src_ds.GetProjection())
                    print("SpatialReference")
                    print(proj.GetAttrValue('AUTHORITY',1))

                    gt=src_ds.GetGeoTransform()
                    print("gt=src_ds.GetGeoTransform()")
                    print(gt)
                    Band =src_ds.GetRasterBand(1)


                    NoData = Band.GetNoDataValue()  # this might be important later

                    nBands = src_ds.RasterCount      # how many bands, to help you loop
                    nRows  = src_ds.RasterYSize      # how many rows
                    nCols  = src_ds.RasterXSize      # how many columns
                    dType  = Band.DataType          # the datatype for this band
                    print("Projection: ", src_ds.GetProjection())  # get projection
                    print("Columns:", src_ds.RasterXSize)  # number of columns
                    print("Rows:", src_ds.RasterYSize)  # number of rows
                    print("Band count:", src_ds.RasterCount)  # number of bands
                    print("Band dtype:", dType)  # number of bands

                    #Read raster data
                    data_array = src_ds.GetRasterBand(1).ReadAsArray()
                    print("data_array.shape:", data_array.shape)
                    print("data_array[0]", data_array[0])

                    #Geting no data values
                    ndv = data_array = src_ds.GetRasterBand(1).GetNoDataValue()
                    print('No data value:', ndv)

                    data_array = src_ds.GetRasterBand(1).ReadAsArray()  # read band data from the existing raster
                    #data_nan = np.where(data_array == ndv, np.nan, data_array)  # set all the no data values to np.nan so we can easily calculate the minimum elevation
                    #data_min = np.min(data_nan)  # get the minimum elevation value (excluding nan)
                    #data_stretch = np.where(data_array == ndv, ndv, (data_array - data_min) * 1.5)  # now apply the strech algorithm
                    #print('Min:', np.min(data_nan))
                    #print('Max:', np.min(data_nan))
                 


                    
                    RowRange = range(nRows)
                    for ThisRow in RowRange:
                        # read a single line from this band
                        ThisLine = Band.ReadRaster(0,ThisRow,nCols,1,nCols,1,dType)
                        
                        

                        if ThisRow % 100 == 0: # report every 100 lines
                            print ("Scanning %d of %d" % (ThisRow,nRows))
                            #print (ThisLine)

                        for Val in ThisLine: # some simple test on the values
                            if Val == 65535:
                                print ('Bad value')
                        

                    Image = None # close the raster


                    gdal.UseExceptions() #so it doesn
                    '''
                    Rescaling
                    Rescaling and calculating indices (see Calculating indices) are examples of operations that are applied on each pixel, separately, to compose a new raster with the results. This type of operations are collectively known as raster algebra.

                    For example, the Sentinel-2 images are stored as uint16, for conserving storage space, but they need to be reslaced by dividing each pixel value by 10000 to get the true reflectance values. This is a common “compression” technique when storing satellite images.

                    To get the reflectance values, we need to rescale all values dividing the entire array by 10000:
                    '''
                    r = r / 10000
                    print(r)

                    # the original crs code
                    print ("geo_tiff.crs_code: ")
                    print (geo_tiff.crs_code)
                    # the current crs code
                    print ("geo_tiff.as_crs: ")
                    print( geo_tiff.as_crs)
                    # the shape of the tiff
                    print ("geo_tiff.tif_shape: ")
                    print(geo_tiff.tif_shape)
                    # the bounding box in the as_crs CRS
                    print ("geo_tiff.tif_bBox: ")
                    print(geo_tiff.tif_bBox)
                    # the bounding box as WGS 84
                    print ("geo_tiff.tif_bBox_wgs_84: ")
                    print(geo_tiff.tif_bBox_wgs_84)
                    print("valores de las primeras 20 coordenadas")
                    '''
                    test de transformacion
                    '''
                    #print("test de trans")
                    #wgs_proj = pyproj.CRS("EPSG:4326")
                    #utm_proj = pyproj.CRS("EPSG:32630")
                    #print(pyproj.transform(utm_proj,wgs_proj,399960,4700040))
                    #transformer_1 = pyproj.Transformer.from_crs(32630, 4326)
                    #transformer_2 = pyproj.Transformer.from_crs(4326,32630)
                    
                    #print("fin test de trans")
                    points = [
                    #[-4.27254326,	42.08352779],
                    #[-4.27217104,	42.08376982] ,
                    #[-4.2727401,	42.08221765] ,
                    #[-4.27296015,	42.08213388] ,
                    #[-4.27268713,	42.08182134],
                    [-4.21574342,	42.44570320 ]
                    ]
                    #pt_val = [(-4.21574342,	42.44570320 )]
                    #for pt in transformer_1.itransform(pt_val): 
                    #    print('{:.3f} {:.3f}'.format(*pt))
                   
                    #print("fin test de trans transformer_1")

                    nparr_points = np.array(points)
                    for x in points:
                        print("Coordenadas de referencia")
                        print(x[0])
                        num_dec_x = decimal(x[0])
                        print(num_dec_x)
                        num_dec_y = decimal(x[1])
                        print(x[1])
                        x_transf = x[0]
                        y_transf = x[1]
                        #print("test de trans")
                        

                        #print(pyproj.transform(wgs_proj,utm_proj,x[1],x[0]))
                        #x_transf = pyproj.transform(wgs_proj,utm_proj,x[1],x[0])[0]
                        #y_transf = pyproj.transform(wgs_proj,utm_proj,x[1],x[0])[1]
                        #print("fin test de trans")
                        xr = 0
                        while xr < 5:
                            yr = 0
                            while yr < 5:
                                print (geo_tiff.get_coords(xr, yr))

                                if isclose1(x_transf,geo_tiff.get_coords(xr, yr)[0],1e-08) and  isclose1(y_transf,geo_tiff.get_coords(xr, yr)[1],1e-08):
                                    print ("Coordenadas encontradas")
                                    print(geo_tiff.get_coords(xr, yr))
                                    print(sampleRaster(src,nparr_points))
                                    try: #in case raster isnt full extent
                                        print(rb)
                                        structval=rb.ReadRaster(x_transf,y_transf,1,1,buf_type=gdal.GDT_Float16) #Assumes 32 bit int- 'float'
                                        intval = struct.unpack('f' , structval) #assume float
                                        val=intval[0]
                                        print ("Valor de la reflectancia")
                                        print(val)
                                    except:
                                        val=-9999 #or some value to indicate a fail
                                        print ("Valor de la reflectancia KO")
                                        print(val)
                                yr += 1

                            xr += 1
                sys.exit()

                        




        elif options.action == "coord":
            basename = ""
            print(src_root_data_dir)
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            for tiff_file in os.listdir(outputPathSubdirectory):
                # check only text files
                if tiff_file.endswith('.tiff'):
                    print(tiff_file)
                    geo_tiff = GeoTiff(outputPathSubdirectory + "/" + tiff_file)
                    # the original crs code
                    print ("geo_tiff.crs_code: ")
                    print (geo_tiff.crs_code)
                    # the current crs code
                    print ("geo_tiff.as_crs: ")
                    print( geo_tiff.as_crs)
                    # the shape of the tiff
                    print ("geo_tiff.tif_shape: ")
                    print(geo_tiff.tif_shape)
                    # the bounding box in the as_crs CRS
                    print ("geo_tiff.tif_bBox: ")
                    print(geo_tiff.tif_bBox)
                    # the bounding box as WGS 84
                    print ("geo_tiff.tif_bBox_wgs_84: ")
                    print(geo_tiff.tif_bBox_wgs_84)
                    i=5
                    j=6
                    # in the as_crs coords
                    print("geo_tiff.get_coords(i, j)")
                    print(geo_tiff.get_coords(i, j))
                    # in WGS 84 coords
                    print("geo_tiff.get_wgs_84_coords(i, j)")
                    print(geo_tiff.get_wgs_84_coords(i, j))
                    #Leamos el .tiff
                    im = Image.open(outputPathSubdirectory + "/" + tiff_file)
                    print(im)
                    
                    print("im.getpixel((0,0))")
                    print(im.getpixel((i,j)))
                    im2 = im.convert('I')
                    print("im2.getpixel((0,0))")
                    print(im2.getpixel((i,j)))
                    im3 = im2.convert('I;16')
                    print("im3.getpixel((0,0))")
                    print(im3.getpixel((i,j)))            
                    print("sacamos la grafica")
                    #Leamos la informacion con rasterio
                    #https://www.uv.es/gonmagar/blog/2018/11/11/RasterioExample
                    print("Caracteristicas del archivo")
                    src = rasterio.open(outputPathSubdirectory + "/" + tiff_file)
                    print(src.height,src.width)
                    print("src.transform")
                    print(src.transform)
                    print("src.crs")
                    print(src.crs)
                    print("check the crs of the data")
                    print(src.crs)
                    print("check the bounding-box of the data")
                    print(src.bounds)
                    print("check size")
                    print(src.read().shape)
                    z = src.read()[0]
                    #Read a Window of data
                    print("Read a Window of data")
                    slice_ = (slice(2000,src.height),slice(0,2500))
                    window_slice = windows.Window.from_slices(*slice_)
                    print(window_slice)
                    #veamos la ventana
                    datos_b1 = src.read(1)
                    plt.imshow(datos_b1)
                    ax = plt.gca()
                    ax.add_patch(Rectangle((window_slice.col_off,window_slice.row_off),
                                        width=window_slice.width,
                                        height=window_slice.height,fill=True,alpha=.2,
                                    color="red"))
                    plt.show()
                    #Read a Window from the raster object
                    # find specific transform, necessary to show the coordinates appropiately
                    transform_window = windows.transform(window_slice,src.transform)

                    # Read img and convert to rgb
                    img = np.stack(src.read(1, window=window_slice),
                                axis=-1)
                    img = np.clip(img,0,2200)/2200

                    print(img.shape)
                    plt.imshow(src.read(1, window=window_slice))
                    plt.title = "band 4"
                    plt.show()


                    print("Window to list of index (row,col)")
                    pol_index = to_index(window_slice)
                    print(pol_index)

                    print("Convert list of index (row,col) to list of coordinates")
                    print("[list(src.transform*p) for p in reverse_coordinates(pol_index)]")
                    print([list(src.transform*p) for p in reverse_coordinates(pol_index)])
                    
                    print("[list(src.xy(*p,offset=\"center\")) for p in pol_index]")
                    print([list(src.xy(*p,offset="center")) for p in pol_index])

                    print("[list(src.xy(*p,offset=\"ul\")) for p in pol_index]")
                    print([list(src.xy(*p,offset="ul")) for p in pol_index])

                    print("Convert Window to BoundingBox")
                    bbox = windows.bounds(window_slice,src.transform)
                    print(bbox)

                    print("Convert BoundingBox to Window")
                    window_same = windows.from_bounds(*bbox,src.transform)
                    print(window_same)

                    print("BoundingBox to list of coordinates (closed)")
                    pol = generate_polygon(bbox)
                    print(pol)
                    
                    print("list of coordinates to BoundingBox")
                    pol_to_bounding_box(pol)
                    print(pol_to_bounding_box(pol))

                    '''Change of Refence System (CRS) using rasterio.warp
                    We will change the reference system from the different types of objects we have generated so far. 
                    The source reference system of our raster is UTM epsg:32630. The target reference system we will 
                    use is epsg:4326 which corresponds to standard (longitude,latitude) coordinates. 
                    Transformations are done using the rasterio.warp module. There are different functions depending 
                    on the objects we want to transform to.'''

                    print("transform list of coordinates")
                    pol_np = np.array(pol)
                    coords_transformed = warp.transform(src.crs,{'init': 'epsg:4326'},pol_np[:,0],pol_np[:,1])
                    coords_transformed = [[r,c] for r,c in zip(coords_transformed[0],coords_transformed[1])]
                    print(coords_transformed)

                    print("transform BoundingBox")
                    bounds_trans = warp.transform_bounds(src.crs,{'init': 'epsg:4326'},*bbox)
                    print(bounds_trans)
                    pol_bounds_trans = generate_polygon(bounds_trans)
                    print(pol_bounds_trans)

                    ''' transform GeoJSON like dictionary
                    A GeoJSON like dictionary in its simplest form is a dictionary with 
                    a a field type set to Polygon and a field coordinates as a list of 
                    list of coordinates. The function warp.transform_geom use this structure
                    to transform geometries between different coordinate reference systems (CRS).
                    '''
                    print("transform GeoJSON like dictionary")
                    pol_trans = warp.transform_geom(src.crs,{'init': 'epsg:4326'},
                                {"type":"Polygon","coordinates":[pol]})
                    print(pol_trans)
                    print("pol_to_bounding_box(pol_trans[\"coordinates\"][0])")
                    print(pol_to_bounding_box(pol_trans["coordinates"][0]))

                    '''Show polygons with folium
                    Now we will show all the polygons we have defined using folium.
                    In particular we will show the bounds of the original image, 
                    the polygons of the transformed coordinates (and we will see they are both the same)
                    and the bounds of the transformed window. With the functions folium.Polygon and 
                    folium.Polyline we can easily plot in an OpenStreetMap map our list of coordinates. 
                    However we should reverse the coordinates in such lists because
                    folium works with (lat,lng) coordinates instead of (lng,lat).'''

                    # original bounds of the image
                    bounds_trans_original = warp.transform_bounds(src.crs,{'init': 'epsg:4326'},
                                                                *src.bounds)
                    polygon_trans_original = generate_polygon(bounds_trans_original)

                    polyline_polygon_trans_original = folium.PolyLine(reverse_coordinates(polygon_trans_original),
                                                                    popup="polygon_trans_original",
                                                                    color="#2ca02c")

                    polyline_pol_trans = folium.Polygon(reverse_coordinates(pol_trans["coordinates"][0]),
                                                        popup="pol_trans",color="red",fill=True)

                    polyline_coords_transformed = folium.PolyLine(reverse_coordinates(coords_transformed),
                                                                popup="coords_transformed")

                    # transformed bounds which should be different than the previous two
                    polyline_pol_bounds_trans = folium.PolyLine(reverse_coordinates(pol_bounds_trans),
                                                                popup="pol_bounds_trans",color="orange")

                    mean_lat = (bounds_trans[1] + bounds_trans[3]) / 2.0
                    mean_lng = (bounds_trans[0] + bounds_trans[2]) / 2.0
                    map_bb = folium.Map(location=[mean_lat,mean_lng],
                                    zoom_start=6)
                    map_bb.add_child(polyline_pol_trans)
                    map_bb.add_child(polyline_coords_transformed)
                    map_bb.add_child(polyline_pol_bounds_trans)
                    map_bb.add_child(polyline_polygon_trans_original)
                    map_bb
                    sys.exit()

        elif options.action == "coord_todas":
            basename = ""
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            for tiff_file in os.listdir(outputPathSubdirectory + "/TODAS/"  ):
                # check only text files
                if tiff_file.endswith('.tiff'):
                    print(tiff_file)
                    geo_tiff = GeoTiff(outputPathSubdirectory + "/TODAS/" + tiff_file)
                    # the original crs code
                    print ("geo_tiff.crs_code: ")
                    print (geo_tiff.crs_code)
                    # the current crs code
                    print ("geo_tiff.as_crs: ")
                    print( geo_tiff.as_crs)
                    # the shape of the tiff
                    print ("geo_tiff.tif_shape: ")
                    print(geo_tiff.tif_shape)
                    # the bounding box in the as_crs CRS
                    print ("geo_tiff.tif_bBox: ")
                    print(geo_tiff.tif_bBox)
                    # the bounding box as WGS 84
                    print ("geo_tiff.tif_bBox_wgs_84: ")
                    print(geo_tiff.tif_bBox_wgs_84)
        elif options.action == "coord_folium":
            basename = ""
            print("coord_folium")
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            for tiff_file in os.listdir(outputPathSubdirectory):
                # check only text files
                if tiff_file.endswith('.tiff'):
                    print("Show polygons with folium")
                    print(tiff_file)
                    
                    #Leamos la informacion con rasterio
                    #https://www.uv.es/gonmagar/blog/2018/11/11/RasterioExample
                    print("Caracteristicas del archivo")
                    src = rasterio.open(outputPathSubdirectory + "/" + tiff_file)
                    slice_ = (slice(2000,src.height),slice(0,2500))
                    window_slice = windows.Window.from_slices(*slice_)
                    bbox = windows.bounds(window_slice,src.transform)
                    pol = generate_polygon(bbox)
                    pol_trans = warp.transform_geom(src.crs,{'init': 'epsg:4326'},
                                {"type":"Polygon","coordinates":[pol]})
                    print("transform list of coordinates")
                    pol_np = np.array(pol)
                    coords_transformed = warp.transform(src.crs,{'init': 'epsg:4326'},pol_np[:,0],pol_np[:,1])
                    coords_transformed = [[r,c] for r,c in zip(coords_transformed[0],coords_transformed[1])]
                    print("transform BoundingBox")
                    bounds_trans = warp.transform_bounds(src.crs,{'init': 'epsg:4326'},*bbox)
                    print(bounds_trans)
                    pol_bounds_trans = generate_polygon(bounds_trans)
                    '''Show polygons with folium
                    Now we will show all the polygons we have defined using folium.
                    In particular we will show the bounds of the original image, 
                    the polygons of the transformed coordinates (and we will see they are both the same)
                    and the bounds of the transformed window. With the functions folium.Polygon and 
                    folium.Polyline we can easily plot in an OpenStreetMap map our list of coordinates. 
                    However we should reverse the coordinates in such lists because
                    folium works with (lat,lng) coordinates instead of (lng,lat).'''

                    # original bounds of the image
                    bounds_trans_original = warp.transform_bounds(src.crs,{'init': 'epsg:4326'},
                                                                *src.bounds)
                    polygon_trans_original = generate_polygon(bounds_trans_original)

                    polyline_polygon_trans_original = folium.PolyLine(reverse_coordinates(polygon_trans_original),
                                                                    popup="polygon_trans_original",
                                                                    color="#2ca02c")

                    polyline_pol_trans = folium.Polygon(reverse_coordinates(pol_trans["coordinates"][0]),
                                                        popup="pol_trans",color="red",fill=True)

                    polyline_coords_transformed = folium.PolyLine(reverse_coordinates(coords_transformed),
                                                                popup="coords_transformed")

                    # transformed bounds which should be different than the previous two
                    polyline_pol_bounds_trans = folium.PolyLine(reverse_coordinates(pol_bounds_trans),
                                                                popup="pol_bounds_trans",color="orange")

                    mean_lat = (bounds_trans[1] + bounds_trans[3]) / 2.0
                    mean_lng = (bounds_trans[0] + bounds_trans[2]) / 2.0
                    map_bb = folium.Map(location=[mean_lat,mean_lng],
                                    zoom_start=6)
                    map_bb.add_child(polyline_pol_trans)
                    map_bb.add_child(polyline_coords_transformed)
                    map_bb.add_child(polyline_pol_bounds_trans)
                    map_bb.add_child(polyline_polygon_trans_original)
                    #mostramos el mapa
                    map_bb.save("map.html")
                    webbrowser.open("map.html")
                    
                    sys.exit()
        elif options.action == "coord_polygon":
            basename = ""
            print("coord_folium")
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            for tiff_file in os.listdir(outputPathSubdirectory):
                # check only text files
                if tiff_file.endswith('.tiff'):
                    print("Show polygons with folium")
                    print(tiff_file)
                    
                    #Leamos la informacion con rasterio
                    #https://www.uv.es/gonmagar/blog/2018/11/11/RasterioExample
                    print("Caracteristicas del archivo")
                    src = rasterio.open(outputPathSubdirectory + "/" + tiff_file)
                    slice_ = (slice(2000,src.height),slice(0,2500))
                    window_slice = windows.Window.from_slices(*slice_)
                    bbox = windows.bounds(window_slice,src.transform)
                    pol = generate_polygon(bbox)
                    pol_trans = warp.transform_geom(src.crs,{'init': 'epsg:4326'},
                                {"type":"Polygon","coordinates":[pol]})
                    print("transform list of coordinates")
                    pol_np = np.array(pol)
                    coords_transformed = warp.transform(src.crs,{'init': 'epsg:4326'},pol_np[:,0],pol_np[:,1])
                    coords_transformed = [[r,c] for r,c in zip(coords_transformed[0],coords_transformed[1])]
                    print("transform BoundingBox")
                    bounds_trans = warp.transform_bounds(src.crs,{'init': 'epsg:4326'},*bbox)
                    print(bounds_trans)
                    pol_bounds_trans = generate_polygon(bounds_trans)
                    '''Show polygons with folium
                    Now we will show all the polygons we have defined using folium.
                    In particular we will show the bounds of the original image, 
                    the polygons of the transformed coordinates (and we will see they are both the same)
                    and the bounds of the transformed window. With the functions folium.Polygon and 
                    folium.Polyline we can easily plot in an OpenStreetMap map our list of coordinates. 
                    However we should reverse the coordinates in such lists because
                    folium works with (lat,lng) coordinates instead of (lng,lat).'''

                    # original bounds of the image
                    bounds_trans_original = warp.transform_bounds(src.crs,{'init': 'epsg:4326'},
                                                                *src.bounds)
                    polygon_trans_original = generate_polygon(bounds_trans_original)

                    polyline_polygon_trans_original = folium.PolyLine(reverse_coordinates(polygon_trans_original),
                                                                    popup="polygon_trans_original",
                                                                    color="#2ca02c")

                    polyline_pol_trans = folium.Polygon(reverse_coordinates(pol_trans["coordinates"][0]),
                                                        popup="pol_trans",color="red",fill=True)

                    polyline_coords_transformed = folium.PolyLine(reverse_coordinates(coords_transformed),
                                                                popup="coords_transformed")

                    # transformed bounds which should be different than the previous two
                    polyline_pol_bounds_trans = folium.PolyLine(reverse_coordinates(pol_bounds_trans),
                                                                popup="pol_bounds_trans",color="orange")

                    mean_lat = (bounds_trans[1] + bounds_trans[3]) / 2.0
                    mean_lng = (bounds_trans[0] + bounds_trans[2]) / 2.0
                    map_bb = folium.Map(location=[mean_lat,mean_lng],
                                    zoom_start=6)
                    map_bb.add_child(polyline_pol_trans)
                    map_bb.add_child(polyline_coords_transformed)
                    map_bb.add_child(polyline_pol_bounds_trans)
                    map_bb.add_child(polyline_polygon_trans_original)
                    #mostramos el mapa
                    map_bb.save("map.html")
                    webbrowser.open("map.html")
                    
                    sys.exit()
        elif options.action == "exprlore":
            #https://hatarilabs.com/ih-en/sentinel2-images-explotarion-and-processing-with-python-and-rasterio
            print("explore")
        elif options.action == "coord1":
            #https://rasterio.readthedocs.io/en/stable/topics/plotting.html
            basename = ""
            for file in os.listdir(src_root_data_dir):
                if os.path.isfile(os.path.join(src_root_data_dir, file)):
                    zipfilestr = src_root_data_dir + "/" +  file
                    basename =  os.path.basename( zipfilestr)
            productName = os.path.basename(zipfilestr)[:-4]
            outputPathSubdirectory = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA"
            outputPathSubdirectoryfile02 = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/B02.tiff"
            outputPathSubdirectoryfile03 = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/B03.tiff"
            outputPathSubdirectoryfile04 = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/B04.tiff"
            outputPathSubdirectoryfile05 = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/B05.tiff"
            outputPathSubdirectoryfile06 = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/B06.tiff"
            outputPathSubdirectoryfile07 = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/B07.tiff"
            outputPathSubdirectoryfile08 = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/B08.tiff"
            outputPathSubdirectoryfiletodas = src_root_data_dir_processs_gdal+"/" + productName + "_PROCESSED/IMAGE_DATA/TODAS/L2A_T30TVM_A040031_20230220T16Bit-AllBands.tiff"
            '''
            #generate histogram
            src02 = rasterio.open(outputPathSubdirectoryfile02)
            plt.imshow(src02.read(1), cmap='pink')
            plt.title = "band 2"
            plt.show()
            #generate histogram
            src03 = rasterio.open(outputPathSubdirectoryfile03)
            plt.imshow(src03.read(1), cmap='pink')
            plt.title = "band 3"
            plt.show()
            #generate histogram
            src04 = rasterio.open(outputPathSubdirectoryfile04)
            plt.imshow(src04.read(1), cmap='pink')
            plt.title = "band 4"
            plt.show()

            #generate histogram
            src05 = rasterio.open(outputPathSubdirectoryfile05)
            plt.imshow(src05.read(1), cmap='pink')
            plt.title = "band 5"
            plt.show()
            '''
            #generate histogram
            src = rasterio.open(outputPathSubdirectoryfiletodas)
            #Histograma
            print("Grafico 1")
            show_hist(
                src, bins=50, lw=0.0, stacked=False, alpha=0.3,
                histtype='stepfilled', title="Histogram")
            print("Grafico 2")
            fig, (axrgb, axhist) = plt.subplots(1, 2, figsize=(14,7))
            show(src, ax=axrgb)
            show_hist(src, bins=50, histtype='stepfilled',
                lw=0.0, stacked=False, alpha=0.3, ax=axhist)
            plt.show()
            #generate histogram
            src06 = rasterio.open(outputPathSubdirectoryfile06)
            plt.imshow(src06.read(1), cmap='pink')
            plt.title = "band 6"
            plt.show()
            #For single-band rasters, there is also an option to generate contours.
            fig, ax = plt.subplots(1, figsize=(12, 12))
            show((src06, 1), cmap='Greys_r', interpolation='none', ax=ax)
            show((src06, 1), contour=True, ax=ax)
            plt.show()


    else:
        print ("Choose an action")

if __name__ == "__main__":
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option(
                    "-i",
                    "--dateini",
                    type="string",
                    dest="dateini",
                    help="from date", 
                    metavar="FROM_DATE")
    parser.add_option(
                    "-f",
                    "--datefin",
                    type="string",
                    dest="datefin",
                    help="to date", 
                    metavar="TO_DATE")
    parser.add_option(
                    "-a",
                    "--action",
                    type="string",
                    dest="action",
                    help="actio to launch :listar,descargar,procesar", 
                    metavar="ACTION")
    parser.add_option(
                    "-k",
                    "--keyboard",
                    type="string",
                    dest="keyboard",
                    help="keyboard to for searching ", 
                    metavar="KEYBOARD")
    parser.add_option(
                    "-d",
                    "--desarga",
                    type="string",
                    dest="hub",
                    help="hub cadena para descarca del archivo ", 
                    metavar="HUB")
    parser.add_option(
                    "-s",
                    "--safedir",
                    type="string",
                    dest="safedir",
                    help="directorio del zip descomprimido ", 
                    metavar="SAFEDIR")
    parser.add_option(
                    "-p",
                    "--polygonfile",
                    type="string",
                    dest="polygonfile",
                    help="archivo klm  de google earth", 
                    metavar="POLYFILE")
    (options, args) = parser.parse_args()
    
    print ("[DEBUG] sys.argv[1:] = {}\n".format(sys.argv[1:]))
    print(options)
    main(options)


