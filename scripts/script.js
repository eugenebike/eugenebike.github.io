//Base Map
L.mapbox.accessToken = 'pk.eyJ1Ijoibmhob3JuZXIiLCJhIjoiaE5kZE5KTSJ9.FBXIBLr6wC0wdsGq_qBsVA';
var bounds = L.latLngBounds(L.latLng(43.97, -123.279136), L.latLng(44.173753, -122.839683)); // (Southwest, Northeast)
var map = L.mapbox.map('map', 'rdc.5ae54ca4', {maxBounds: bounds, maxZoom: 16, minZoom: 13, infoControl: false, attributionControl: true}).setView([44.058460, -123.073983], 14);
map.attributionControl.addAttribution('Data from: <a href="https://www.eugene-or.gov/" style="color: #4682B4;">City of Eugene</a> and <a href="http://www.lcog.org/" style="color: #4682B4;">Lane Council of Governments</a>');

//Data
var load_data = function() {
    $.ajax({
        type: 'GET',
        url: "./data/BikeFacilty_June24d.json",
        success: function(data) {
            //Style key
            var style_color = {"Confident and Enthused":"#fee08b", "Kids with Training":"#1a9850", "Most Adults":"#91cf60", "Strong and Fearless":"#af8dc3"}

            //Adjust data
            for (var i in data.features) {
                for (var points in data.features[i].geometry.coordinates) {
                    data.features[i].geometry.coordinates[points][0] = data.features[i].geometry.coordinates[points][0] - 0.002899 //Long
                    data.features[i].geometry.coordinates[points][1] = data.features[i].geometry.coordinates[points][1] - 0.007195 // Lat
                }
                console.log(data.features[i].properties.bikefac, data.feature[i].properties.condition);
                data.features[i].properties.stroke = style_color[data.features[i].properties.condition];
                data.features[i].properties['stroke-width'] = 3;
                // if (data.feature[i].properties.condition == "Kids with Training") {
                //     data.features[i].properties['stroke-width'] = 4;
                // }
            }

            var featureLayer = L.mapbox.featureLayer(data).addTo(map);

            var faciltyDictionary = {"rmup":"Multi-Use Path", "bike lanes":"Bike Lanes"}

            featureLayer.eachLayer(function(layer) {
                var content = '<span style="font-weight:bold; font-size:120%;">' + layer.feature.properties.str_name2 + ' ' + layer.feature.properties.eval + '/10 <\span><br>Condition: ' + layer.feature.properties.condition + '<br>Speed: ' + layer.feature.properties.Speed + '<br>Estimated Traffic Volume: ' + layer.feature.properties.est_vol + '<br>Bike Facilty: ' + faciltyDictionary[layer.feature.properties.bikefac];
                layer.bindPopup(content);
            });

            featureLayer.on('mouseover', function(e) {
                e.layer.openPopup();
            });
            featureLayer.on('mouseout', function(e) {
                e.layer.closePopup();
            });
        }
    });
}
$( document ).ready(load_data());