import {Map, View, DragAndDrop, Feature} from './ol/index.js';
import {OSM, Vector as VectorSource} from './ol/source.js';
import {Draw, Modify, Snap} from './ol/interaction.js';
import {Tile as TileLayer, Vector as VectorLayer, WebGLTile} from './ol/layer.js';
import {
    defaults as defaultInteractions,
} from './ol/interaction.js';
import {GPX, GeoJSON, IGC, KML, TopoJSON} from './ol/format.js';
import {Point, Polygon} from "./ol/geom.js";

// Create functions to extract KML and icons from KMZ array buffer,
// which must be done synchronously.

const zip = new JSZip();


//valores por defecto para el centrado
var v_lat = 42.29511966573258
var v_long=-3.683528642004319
//const v_lat = parseFloat( myArray_Polygon_center[1])
//const v_long = parseFloat(myArray_Polygon_center[0])


//kml files
const iniurl = "http://localhost:8092/"

var file_k = ""
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





const raster = new TileLayer({
    source: new OSM(),
});
const source = new VectorSource();
const vector = new VectorLayer({
    source: source,
});


function getKMLData(buffer) {
    let kmlData;
    zip.load(buffer);
    const kmlFile = zip.file(/\.kml$/i)[0];
    if (kmlFile) {
        kmlData = kmlFile.asText();
    }
    return kmlData;
}

function getKMLImage(href) {
    const index = window.location.href.lastIndexOf('/');
    if (index !== -1) {
        const kmlFile = zip.file(href.slice(index + 1));
        if (kmlFile) {
            return URL.createObjectURL(new Blob([kmlFile.asArrayBuffer()]));
        }
    }
    return href;
}

// Define a KMZ format class by subclassing ol/format/KML

class KMZ extends KML {
    constructor(opt_options) {
        const options = opt_options || {};
        options.iconUrlFunction = getKMLImage;
        super(options);
    }

    getType() {
        return 'arraybuffer';
    }

    readFeature(source, options) {
        const kmlData = getKMLData(source);
        return super.readFeature(kmlData, options);
    }

    readFeatures(source, options) {
        const kmlData = getKMLData(source);
        return super.readFeatures(kmlData, options);
    }
}

// Set up map with Drag and Drop interaction

const dragAndDropInteraction = new DragAndDrop({
    formatConstructors: [KMZ, GPX, GeoJSON, IGC, KML, TopoJSON],
});

const map = new Map({
    interactions: defaultInteractions().extend([dragAndDropInteraction]),
    layers: [
        vector,
        raster,
    ],
    target: 'map',
    view: new View({
        center: [v_long, v_lat],
        projection: 'EPSG:4326',
        zoom: 10
    }),
});



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
function addpoints()  {
    //remove app from file
    let path = document.getElementById("path").value;
    let filename = document.getElementById("filename").value;
    let path_final = path.replace("/app/","");
    const file =iniurl + path_final + "/" + filename
    file_k = file
    console.log(file)
    const vector = new VectorLayer({
        source: new VectorSource({
            url: file,
            format: new KML(),
        }),
    });

    map.addLayer(vector)
};


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

addpoints();
addInteraction();

dragAndDropInteraction.on('addfeatures', function (event) {
    const vectorSource = new VectorSource({
        features: event.features,
    });
    map.addLayer(
        new VectorLayer({
            source: vectorSource,
        }),
    );
    map.getView().fit(vectorSource.getExtent());
});

const displayFeatureInfo = function (pixel) {
    const features = [];
    map.forEachFeatureAtPixel(pixel, function (feature) {
        features.push(feature);
    });
    if (features.length > 0) {
        const info = [];
        let i, ii;
        for (i = 0, ii = features.length; i < ii; ++i) {
            const description =
                features[i].get('description') ||
                features[i].get('name') ||
                features[i].get('_name') ||
                features[i].get('layer');
            if (description) {
                info.push(description);
            }
        }
        document.getElementById('info').innerHTML = info.join('<br/>') || '&nbsp';
    } else {
        document.getElementById('info').innerHTML = '&nbsp;';
    }
};

map.on('pointermove', function (evt) {
    if (evt.dragging) {
        return;
    }
    const pixel = map.getEventPixel(evt.originalEvent);
    displayFeatureInfo(pixel);
});

map.on('click', function (evt) {
    displayFeatureInfo(evt.pixel);
});

// Sample data download

const link = document.getElementById('download');

function download(fullpath, filename) {
    fetch(fullpath)
        .then(function (response) {
            return response.blob();
        })
        .then(function (blob) {
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
        });
}


map.on('pointermove', function(evt) {
    //Same code as in click event
    //console.log(evt)
    var point = map.getCoordinateFromPixel(evt.pixel)
    //console.log("point="+point);
    var lat = point[1];
    var lon = point[0];
    var locTxt =  " Longitude: " + lon + "Latitude: " + lat ;
    // coords is a div in HTML below the map to display
    document.getElementById('coords').innerHTML = locTxt;
});



document.getElementById('download-kmz').addEventListener('click', function () {
    download(file_k, 'kmz_download.kmz');
});


document.getElementById('showpolygon').addEventListener('click', function () {
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
document.getElementById('clearcanvas').addEventListener('click', function () {
    map.getLayers().forEach(function (layer) {
        map.removeLayer(layer);
    });
    //for some crazy reason I need to do it twice.
    map.getLayers().forEach(function (layer) {
        map.removeLayer(layer);
    });

    map.addLayer(raster)
});
