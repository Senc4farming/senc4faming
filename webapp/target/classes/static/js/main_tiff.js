import {Map,View,Feature} from './ol/index.js';
import {OSM, Vector as VectorSource} from './ol/source.js';
import {defaults as defaultInteractions, Draw, Modify, Select, Snap} from './ol/interaction.js';
import {Tile as TileLayer, Vector as VectorLayer, WebGLTile as WebGLTile} from './ol/layer.js';
import {Polygon,Point} from "./ol/geom.js";
import {GeoTIFF} from './ol/geotiff/geotiff.js';




//valores por defecto para el centrado
var v_lat = 42.29511966573258
var v_long=-3.683528642004319

function getpolygontext(){
    var  polygon = document.getElementById("coordinates")
    console.log(polygon.value.length)
    if (polygon.value.length < 10){
        return ""
    }
    else{
        try{
            var polygonstr = polygon.value
            var myArray_Polygon = polygonstr.split(",");

            var  myArray_Polygon_center = myArray_Polygon[0].split(" ")
            v_lat = parseFloat( myArray_Polygon_center[1])
            v_long = parseFloat(myArray_Polygon_center[0])


            let i = 0;
            var polyCoords_l = ""
            while (i < myArray_Polygon.length) {
                var myArray_Polygon_center_l = myArray_Polygon[i].split(" ")
                var long_l = parseFloat( myArray_Polygon_center_l[0])
                var lat_l = parseFloat( myArray_Polygon_center_l[1])
                if (i == 0){
                    polyCoords_l = '['+ long_l + ', '+ lat_l + ']'
                } else {
                    polyCoords_l += ',['+ long_l + ', '+ lat_l + ']'
                }
                i++;
            }
            if ( i== 1){
                return "Format error"
            }else{

                return polyCoords_l
            }
        }catch{
            return "Format error"
        }
    }
}

const polyCoords = getpolygontext();
//const polyCoords = '[-3.683528642004319, 42.29511966573258],[-3.679380123297809, 42.301402752089],[-3.680710612979148, 42.30127347013828],[-3.683280108931597 ,42.30023457260301],[-3.683528642004319 ,42.29511966573258]';
//console.log("polyCoords:" + polyCoords)
const pointCoords = '[' + v_long + ',' + v_lat + ']';

const polygonFeatureT = new Feature(new Polygon(JSON.parse('[[' + polyCoords + ']]')));
const pointFeatureK = new Feature(new Point(JSON.parse(pointCoords)));

const source_poly = new VectorSource({
    features: [polygonFeatureT, pointFeatureK]
})
const source_tiff = new GeoTIFF({
    sources: [
        {
            url: 'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/36/Q/WD/2020/7/S2A_36QWD_20200701_0_L2A/TCI.tif',
        },
    ],
});
const layer_source_poly = new  VectorLayer({
    source: source_poly,
});

const raster = new TileLayer({
    source: new OSM(),
});

const source = new VectorSource();

const vector = new VectorLayer({
    source: source,
});
const select = new Select({
    wrapX: false,
});

const modify = new Modify({
    features: select.getFeatures(),
});

// Limit multi-world panning to one world east and west of the real world.
// Geometry coordinates have to be within that range.
/*
const map = new Map({
    interactions: defaultInteractions().extend([select, modify]),
    layers: [
        raster,
        vector,
        layer_source_poly
    ],
    target: 'map',
    view: new View({
        center: [v_long, v_lat],
        projection: 'EPSG:4326',
        zoom: 15
    }),
});
*/

const map = new Map({
    target: 'map',
    layers: [new TileLayer({source})],
    view: new View({
        center: [0, 0],
        zoom: 12,
    }),
});
//map.addLayer(geoTiffLayer);
const typeSelect = document.getElementById('type');

let draw; // global so we can remove it later
function addInteraction() {
    const value = typeSelect.value;
    if (value !== 'None') {
        draw = new Draw({
            source: source,
            type: typeSelect.value,
        });
        map.removeInteraction(map);
        map.addInteraction(draw);
    }
}


var deleteFeature = function(evt){
    if(evt.keyCode == 46) {
        var selectCollection = select.getFeatures();
        if (selectCollection.getLength() > 0) {
            vector.getSource().removeFeature(selectCollection.item(0));
        }
    };
};
document.addEventListener('keydown', deleteFeature, false);

map.on('pointermove', function(evt) {
    //Same code as in click event
    //console.log(evt)
    console.log(polygon)
    var point = map.getCoordinateFromPixel(evt.pixel)
    //console.log("point="+point);
    var lat = point[1];
    var lon = point[0];
    var locTxt =  " Longitude: " + lon + "Latitude: " + lat ;
    // coords is a div in HTML below the map to display
    document.getElementById('coords').innerHTML = locTxt;
});


/**
 * Handle change event.
 */
typeSelect.onchange = function () {
    map.removeInteraction(draw);
    addInteraction();
};

document.getElementById('undo').addEventListener('click', function () {
    draw.removeLastPoint();
});
document.getElementById('clearcanvas').addEventListener('click', function () {
    location.reload()
});

document.getElementById('addpolygon').addEventListener('click', function () {
    const polyCoords = getpolygontext();
    //const polyCoords = '[-3.683528642004319, 42.29511966573258],[-3.679380123297809, 42.301402752089],[-3.680710612979148, 42.30127347013828],[-3.683280108931597 ,42.30023457260301],[-3.683528642004319 ,42.29511966573258]';
    console.log("polyCoords:" + polyCoords)
    if (polyCoords == "Format error"){
        document.getElementById("coordinates").value = polyCoords
    } else
    {
        if (polyCoords.length >= 10){
            const pointCoords = '[' + v_long + ',' + v_lat + ']';

            const polygonFeatureT = new Feature(new Polygon(JSON.parse('[[' + polyCoords + ']]')));
            const pointFeatureK = new Feature(new Point(JSON.parse(pointCoords)));

            const source_poly = new VectorSource({
                features: [polygonFeatureT, pointFeatureK]
            })

            const layer_source_poly = new  VectorLayer({
                source: source_poly,
            });

            map.addLayer(layer_source_poly)
        }
        else{
            document.getElementById("coordinates").value = "Add polygon"
        }
    }
});


addInteraction();