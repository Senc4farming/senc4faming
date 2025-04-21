import sys
import subprocess
#sys.path.append('Scripts/')
#import gdal_merge
from shapely.geometry import Polygon
import numpy as np
from geotiff import GeoTiff
from scipy.interpolate import RectBivariateSpline
import sys
import os
import glob
import pyproj
from  pyproj import Transformer
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
from osgeo.gdalconst import *
from rasterio.mask import mask
from rasterio import plot
from rasterio.plot import show
from rasterio.coords import BoundingBox
from rasterio import windows
from rasterio import warp
from rasterio import mask
import rasterio.plot as plot
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rasterio.plot import show_hist
import numpy as np
import affine 
import json
from io import BytesIO
import os
import requests

def get_access_token(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
        }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Access token creation failed. Reponse from the server was: {r.json()}"
            )
    return r.json()["access_token"]

def get_access_token_openid(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
        }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Access token creation failed. Reponse from the server was: {r.json()}"
            )
    return r.json()["access_token"]

def get_tallinn_polygon_from_coord(swap_coordinates=False):
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

def create_polygon_for_point(long,lat,swap_coordinates=False):
    print("create_polygon_for_point polygon")
    offset = 0.02
    tln_points = [
        [long - offset, lat - offset],
        [long + offset, lat - offset],
        [long + offset, lat + offset],
        [long - offset, lat + offset],
        [long - offset, lat - offset]
    ]
    print('En  create_polygon_for_point tln_points')
    print(tln_points)
    # Copernicus hub likes polygons in lng/lat format
    return Polygon([(y, x) if swap_coordinates else (x, y) for x, y in tln_points])
def create_polygon_for_point_offset(long,lat,offset,swap_coordinates=False):
    print("create_polygon_for_point polygon")
    num_offset = float(offset)
    tln_points = [
        [long - num_offset, lat - num_offset],
        [long + num_offset, lat - num_offset],
        [long + num_offset, lat + num_offset],
        [long - num_offset, lat + num_offset],
        [long - num_offset, lat - num_offset]
    ]
    print('En  create_polygon_for_point tln_points')
    print(tln_points)
    # Copernicus hub likes polygons in lng/lat format
    return Polygon([(y, x) if swap_coordinates else (x, y) for x, y in tln_points])
def get_tallinn_polygon_ge(strfilename,swap_coordinates=False):
    print("polygon")
    # first load config from a json file,
    srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))
    src_root_kml_path = "/app/files/src_data_kml"
    filenamefullpath = src_root_kml_path + '/' + strfilename
    i=0
    for p in readPoly(filenamefullpath):
        p,desc=p
        i=i+1
        print('En readpoly p:')
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
def retrieve_pixel_value(x,y, data_source):
    '''
    https://gis.stackexchange.com/questions/221292/retrieve-pixel-value-with-geographic-coordinate-as-input-with-gdal
    Here is the function I came up with, using a function I found in another stack post 
    (that I unfortunately cannot remember the title of). It was originally written to be 
    used with a point vector file instead of manually inputting the points like I am doing.
      Below is the simplified function, using affine and gdal, where data_source is an 
      opened gdal object of a GeoTIFF and coord is a tuple of a geo-coordinate. 
      This tuple must be in the same coordinate system as the GeoTIFF
    '''
    """Return floating-point value that corresponds to given point."""
    forward_transform =  \
        affine.Affine.from_gdal(*data_source.GetGeoTransform())
    reverse_transform = ~forward_transform
    px, py = reverse_transform * (x, y)
    px, py = int(px + 0.5), int(py + 0.5)
    pixel_coord = px, py

    data_array = np.array(data_source.GetRasterBand(1).ReadAsArray())
    val = 0
    try:
        val = data_array[pixel_coord[0]][pixel_coord[1]]
    except IndexError as e:
        val = -1
    except:
        raise
    return val