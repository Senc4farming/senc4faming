(function ($) {
    "use strict";
    console.log("Inico main_ol_jquwry")
/*
    // Create functions to extract KML and icons from KMZ array buffer,
    // which must be done synchronously.
    const zip = new JSZip();

    const lat = document.getElementById("minlatval").value
    const long = document.getElementById("minlongval").value
    const  polygon = document.getElementById("coordinates").value

    console.log("poligono")
    console.log(polygon)
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
            const options = opt_options || {};º
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
        layers: [raster, vector,
            new TileLayer({
                source: new OSM(),
            }),
        ],
        target: 'map',
        view: new View({
            projection: 'EPSG:4326',
            center: ol.proj.fromLonLat([long, lat ]) ,
            zoom: 3,
        }),
    });

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
        console.log("displayFeatureInfo")
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
        console.log("pointermove")
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
        console.log("download")
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

    document.getElementById('download-kmz').addEventListener('click', function () {
        download('data/kmz/iceland.kmz', 'iceland.kmz');
    });




    const raster = new TileLayer({
        source: new OSM(),
    });

    const source = new VectorSource({wrapX: false});

    const vector = new VectorLayer({
        source: source,
    });


    const typeSelect = document.getElementById('type');

    let draw; // global so we can remove it later
    function addInteraction() {
        console.log("addInteraction")
        const value = typeSelect.value;
        if (value !== 'None') {
            draw = new Draw({
                source: source,
                type: typeSelect.value,
            });
            map.addInteraction(draw);
        }
    }

    /**
     * Handle change event.
     */
    /*
    typeSelect.onchange = function () {
        map.removeInteraction(draw);
        addInteraction();
    };

    document.getElementById('undo').addEventListener('click', function () {
        draw.removeLastPoint();
    });

    addInteraction();
*/
})(jQuery);

