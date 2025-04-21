import requests
from pyproj import Transformer
import base64
import xarray as xr
import rioxarray
from rasterio.io import MemoryFile
from shapely.geometry import Polygon, mapping
import json
 
# Define the geometry
geometry_json = '''{ "type": "Polygon", "coordinates": [ [ [ 150.1126865, -29.2255068 ], [ 150.1039762, -29.2243777 ], [ 150.103701199999989, -29.2245019 ], [ 150.1035071, -29.2245142 ], [ 150.0918797, -29.2230173 ], [ 150.0917524, -29.222976 ], [ 150.091697399999987, -29.2229369 ], [ 150.0916207, -29.2228069 ], [ 150.0916454, -29.2225624 ], [ 150.0934881, -29.2114467 ], [ 150.0936721, -29.2104342 ], [ 150.0937548, -29.2102981 ], [ 150.0939214, -29.2102237 ], [ 150.094009699999987, -29.2102251 ], [ 150.0941322, -29.2102609 ], [ 150.0947937, -29.2108058 ], [ 150.0948923, -29.2109237 ], [ 150.094995899999986, -29.2110963 ], [ 150.0950344, -29.2111974 ], [ 150.095121299999988, -29.2117 ], [ 150.0951761, -29.2118721 ], [ 150.0953447, -29.2122385 ], [ 150.095551300000011, -29.2125781 ], [ 150.0959033, -29.2130318 ], [ 150.0962366, -29.2134046 ], [ 150.096890800000011, -29.2139772 ], [ 150.0971956, -29.2141825 ], [ 150.0974879, -29.214272 ], [ 150.0977446, -29.2142941 ], [ 150.0979903, -29.214285 ], [ 150.098398800000012, -29.2141977 ], [ 150.0990562, -29.2139084 ], [ 150.099899, -29.2138841 ], [ 150.100123700000012, -29.2138351 ], [ 150.100327600000014, -29.2137415 ], [ 150.1012307, -29.2135528 ], [ 150.1015282, -29.2136282 ], [ 150.101817399999987, -29.2137781 ], [ 150.1025439, -29.214377 ], [ 150.102902199999988, -29.214617 ], [ 150.1031384, -29.2147156 ], [ 150.103347, -29.2147458 ], [ 150.103499199999987, -29.2147401 ], [ 150.1037307, -29.21469 ], [ 150.1044364, -29.2144067 ], [ 150.105561, -29.2141905 ], [ 150.105702900000011, -29.2142384 ], [ 150.1058581, -29.2143345 ], [ 150.1065556, -29.2149181 ], [ 150.106759899999986, -29.2149985 ], [ 150.1069929, -29.2150357 ], [ 150.1071355, -29.2150346 ], [ 150.107311399999986, -29.214998 ], [ 150.1081442, -29.2146057 ], [ 150.1083688, -29.2145261 ], [ 150.108617, -29.214474 ], [ 150.10909620000001, -29.2144519 ], [ 150.1107245, -29.2144974 ], [ 150.1113245, -29.2144695 ], [ 150.111787099999987, -29.2143629 ], [ 150.1127861, -29.2139822 ], [ 150.1131816, -29.2139067 ], [ 150.1134385, -29.2139007 ], [ 150.1136579, -29.2139268 ], [ 150.1138369, -29.2139933 ], [ 150.1139475, -29.2140779 ], [ 150.114047699999986, -29.2142552 ], [ 150.1140412, -29.2145935 ], [ 150.1138338, -29.2162949 ], [ 150.113470299999989, -29.2186687 ], [ 150.1135133, -29.2187373 ], [ 150.1137865, -29.2188267 ], [ 150.1139101, -29.2189072 ], [ 150.113972, -29.2189902 ], [ 150.1140024, -29.2191226 ], [ 150.113, -29.2252668 ], [ 150.112932, -29.2254101 ], [ 150.1128458, -29.2254765 ], [ 150.1126865, -29.2255068 ] ] ] }'''
geometry = json.loads(geometry_json)
 
# Define bounding box in WGS84
bbox_wgs = [150.0916207, -29.2255068, 150.1140477, -29.2102237]
 
# Transformation from WGS84 to UTM
transformer = Transformer.from_crs(4326, 32756)
bbox_utm = list(transformer.transform(
    bbox_wgs[1], bbox_wgs[0])) + list(transformer.transform(bbox_wgs[3], bbox_wgs[2]))
 
# Round all values in bbox_utm to nearest 30m
bbox_utm = [round(x / 30) * 30 for x in bbox_utm]
 
# Expand bbox by 30m in each direction
bbox_utm = [bbox_utm[0] - 30, bbox_utm[1] -
            30, bbox_utm[2] + 30, bbox_utm[3] + 30]
 
# Convert geometry from WGS84 to UTM
coords_wgs84 = geometry['coordinates'][0]
coords_utm = [list(transformer.transform(coord[1], coord[0]))
              for coord in coords_wgs84]
geom_utm = {"type": "Polygon", "coordinates": [coords_utm]}
 
# Create a shapely polygon with a negative buffer of 30 m
polygon = Polygon(coords_utm)
polygon = polygon.buffer(-30)
geom_utm = mapping(polygon)
 
# Sentinel Hub instance ID
instance_id = 'af099e61-1a8f-4e8e-8b0f-a89a35b586f2'
 
# Define WFS parameters
feature_offset = 0
bbox = str(bbox_utm)[1:-1]
date_start = '2022-06-01'
date_finish = '2022-07-01'
wfs_url = f'https://services.sentinel-hub.com/ogc/wfs/{instance_id}?REQUEST=GetFeature&FEATURE_OFFSET={feature_offset}&srsName=EPSG:32756&TYPENAMES=DSS21&BBOX={bbox}&TIME={date_start}/{date_finish}&OUTPUTFORMAT=application/json'
# Fetch WFS data
more_data = True
dates = []
 
while more_data:
    response = requests.get(wfs_url).json()
    features = response['features']
 
    for feature in features:
        dates.append({
            'date': feature['properties']['date'],
            'crs': feature['properties']['crs'],
            'cloud': feature['properties']['cloudCoverPercentage'],
            'id': feature['properties']['id']
        })
 
    if len(features) < 100:
        more_data = False
    else:
        feature_offset += 100
 
    wfs_url = f'https://services.sentinel-hub.com/ogc/wfs/{instance_id}?REQUEST=GetFeature&FEATURE_OFFSET={feature_offset}&srsName=EPSG:3857&TYPENAMES=DSS21&BBOX={bbox}&TIME={date_start}/{date_finish}&OUTPUTFORMAT=application/json'
 
print(dates[0])
 
# Define bands and metadata
bands = [
    {'name': 'Blue', 'factor': 0.001, 'constellation': 'both', 'id': 0},
    {'name': 'Green', 'factor': 0.001, 'constellation': 'both', 'id': 1},
    {'name': 'Red', 'factor': 0.001, 'constellation': 'both', 'id': 2},
    {'name': 'RedEdge1', 'factor': 0.0025, 'constellation': 'sentinel', 'id': 3},
    {'name': 'RedEdge2', 'factor': 0.0025, 'constellation': 'sentinel', 'id': 4},
    {'name': 'RedEdge3', 'factor': 0.0025, 'constellation': 'sentinel', 'id': 5},
    {'name': 'NIR_Narrow', 'factor': 0.0025, 'constellation': 'both', 'id': 6},
    {'name': 'SWIR1', 'factor': 0.0025, 'constellation': 'both', 'id': 7},
    {'name': 'SWIR2', 'factor': 0.0025, 'constellation': 'both', 'id': 8},
    {'name': 'ThermalInfrared1', 'factor': 0.1,
        'constellation': 'landsat', 'id': 9},
    {'name': 'ThermalInfrared2', 'factor': 0.1,
        'constellation': 'landsat', 'id': 10},
]
 
metadata = {
    'width': None,
    'height': None,
    'bounds': None,
    'crs': 'EPSG:32756',
    'transform': None,
    'count': None,
}
 
xds = xr.Dataset({}, coords={'x': [], 'y': [], 'time': []})
 
# Loop through dates and bands to fetch and process data
for date_info in dates[:10]:
    # Check QA band first to determine cloud cover before downloading other bands
    evalscript = '''//VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["QA", "dataMask"],
            }],
            output: { bands: 1, sampleType: "INT8" }
        }
    }
    function rs(num, bits) {
    var divisor = Math.pow(2, bits);
    var result = Math.floor(num / divisor);
    return result;
    }
    function evaluatePixel(sample) {
        var cloud = (rs(sample.QA, 1) & 1) 
        var adj_cld_shadow = (rs(sample.QA, 2) & 1)
        var cloud_shadow = (rs(sample.QA, 3) & 1)
        var snow_ice = (rs(sample.QA, 4) & 1)
        var water = (rs(sample.QA,5) & 1)
        if (sample.dataMask == 0) {
            return [1]
        }
        if (cloud == 1) {
            return [1]
        } else if (cloud_shadow == 1) {
            return [1]
        } else if (adj_cld_shadow == 1) {
            return [1]
        } else if (snow_ice == 1) {
            return [2]
        } else if (water == 1) {
            return [2]
        } else {
            return [2]
        }
    }'''
 
    evalscript = base64.b64encode(evalscript.encode('ascii')).decode('ascii')
 
    wcs_url = f'https://services-uswest2.sentinel-hub.com/ogc/wcs/{instance_id}?SERVICE=WCS&REQUEST=GetCoverage&VERSION=1.1.2&COVERAGE=HLS&CRS=EPSG:32756&STYLES=&RESX=30.0&RESY=30.0&FORMAT=image/tiff&TIME={date_info["date"]}/{date_info["date"]}&BBOX={bbox}&EVALSCRIPT={evalscript}&SHOWLOGO=false'
 
    # Download data using requests
    response = requests.get(wcs_url)
 
    # If status is 400, print error message
    if response.status_code == 400:
        print(response.text)
 
    with MemoryFile(response.content) as memfile:
        with memfile.open() as dataset:
            if metadata['width'] is None:
                metadata['width'] = dataset.width
                metadata['height'] = dataset.height
                metadata['bounds'] = dataset.bounds
                metadata['transform'] = dataset.transform
 
            data = dataset.read()
            temp_array = rioxarray.open_rasterio(
                dataset, engine='rasterio',  masked=True)
            clipped = temp_array.rio.clip([geom_utm], all_touched=False)
 
            array = xr.DataArray(clipped[0], dims=['y', 'x'], name='QA')
            array.rio.write_crs('EPSG:32756', inplace=True)
            array.attrs['id'] = date_info['id']
            array = array.expand_dims('time')
            array['time'] = [date_info['date']]
            xds = xr.merge([xds, array])
 
            good_pixels = int(clipped.where(
                clipped == 2).count(dim=['x', 'y'])[0])
            bad_pixels = int(clipped.where(
                clipped == 1).count(dim=['x', 'y'])[0])
            good_percent = round(
                (good_pixels / (good_pixels + bad_pixels)) * 100, 2)
 
            # If good percent is less than 97%, then skip
            if good_percent < 97:
                print('Skipping')
                continue
 
            for band_info in bands:
                evalscript_band = f'''
                //VERSION=3
                let f = {band_info['factor']};
                function setup() {{
                    return {{
                        input: [{{
                            bands: ["{band_info['name']}"],
                        }}],
                        output: {{
                            bands: 1,
                            sampleType: "UINT8"
                        }}
                    }};
                }}
                function evaluatePixel(sample) {{
                    return [sample.{band_info['name']} / f]; 
                }}
                '''
 
                # Check constellation
                constellation = 'landsat' if date_info['id'].split(
                    '.')[1] == 'L30' else 'sentinel'
 
                if band_info['constellation'] == 'both':
                    evalscript_band = base64.b64encode(
                        evalscript_band.encode('ascii')).decode('ascii')
 
                    wcs_url_band = f'https://services-uswest2.sentinel-hub.com/ogc/wcs/{instance_id}?SERVICE=WCS&REQUEST=GetCoverage&VERSION=1.1.2&COVERAGE=HLS&CRS=EPSG:32756&STYLES=&RESX=30.0&RESY=30.0&FORMAT=image/tiff&TIME={date_info["date"]}/{date_info["date"]}&BBOX={bbox}&EVALSCRIPT={evalscript_band}&SHOWLOGO=false'
 
                    # Download data using requests
                    response_band = requests.get(wcs_url_band)
 
                    # If status is 400, print error message
                    if response_band.status_code == 400:
                        print(response_band.text)
 
                    with MemoryFile(response_band.content) as memfile_band:
                        with memfile_band.open() as dataset_band:
                            data_band = dataset_band.read()
                            temp_array_band = rioxarray.open_rasterio(
                                dataset_band, engine='rasterio', masked=True)
                            clipped_band = temp_array_band.rio.clip(
                                [geom_utm], all_touched=False)
 
                            array_band = xr.DataArray(clipped_band[0], dims=[
                                                      'y', 'x'], name=band_info['name'])
                            array_band.rio.write_crs(
                                'EPSG:32756', inplace=True)
                            array_band.attrs['id'] = date_info['id']
                            array_band = array_band.expand_dims('time')
                            array_band['time'] = [date_info['date']]
                            xds = xr.merge([xds, array_band])
 
# Export with preserved projection
 
 
def export_to_netcdf(dataset, filename, encoding=None):
    if encoding is not None:
        dataset = dataset.copy()
        for var_name, var in dataset.data_vars.items():
            if var_name in encoding:
                var.encoding = encoding[var_name]
 
    # Write CRS
    dataset.rio.write_crs("EPSG:32756", inplace=True)
 
    # Write to a NetCDF file
    dataset.to_netcdf(filename)
 
 
# Define encoding for NetCDF
encoding_netcdf = {
    'QA': {'dtype': 'uint8', 'zlib': True, 'complevel': 9, '_FillValue': 0},
    'Blue': {'dtype': 'uint8', 'zlib': True, 'complevel': 9, '_FillValue': 0},
    'Green': {'dtype': 'uint8', 'zlib': True, 'complevel': 9, '_FillValue': 0},
    'Red': {'dtype': 'uint8', 'zlib': True, 'complevel': 9, '_FillValue': 0},
    'NIR_Narrow': {'dtype': 'uint8', 'zlib': True, 'complevel': 9, '_FillValue': 0},
    'SWIR1': {'dtype': 'uint8', 'zlib': True, 'complevel': 9, '_FillValue': 0},
    'SWIR2': {'dtype': 'uint8', 'zlib': True, 'complevel': 9, '_FillValue': 0}
}
 
# Export to NetCDF files
export_to_netcdf(xds, 'processed_data.nc', encoding=encoding_netcdf)