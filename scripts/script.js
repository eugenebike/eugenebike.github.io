//Base Map
L.mapbox.accessToken = 'pk.eyJ1Ijoibmhob3JuZXIiLCJhIjoiaE5kZE5KTSJ9.FBXIBLr6wC0wdsGq_qBsVA';
var bounds = L.latLngBounds(L.latLng(43.979395, -123.279136), L.latLng(44.173753, -122.839683)); // (Southwest, Northeast)
var map = L.mapbox.map('map', 'rdc.5ae54ca4', {
    maxBounds: bounds,
    maxZoom: 15,
    minZoom: 11
}).setView([44.058460, -123.073983], 13);

//Data
var load_data = function() {
    $.ajax({
        type: 'GET',
        url: "./data/BikeFacilty_June24d.json",
        success: function(data) {

            ////Test
            //console.log(data.features[0]);

            //Style key
            var style_color = {"Confident and Enthused":"#fee08b", "Kids with Training":"#1a9850", "Most Adults":"#91cf60", "Strong and Fearless":"#af8dc3"}

            //Adjust data
            for (var i in data.features) {
                for (var points in data.features[i].geometry.coordinates) {
                    data.features[i].geometry.coordinates[points][0] = data.features[i].geometry.coordinates[points][0] - 0.002899 //Long
                    data.features[i].geometry.coordinates[points][1] = data.features[i].geometry.coordinates[points][1] - 0.007195 // Lat
                }
                data.features[i].properties.stroke = style_color[data.features[i].properties.condition];
                data.features[i].properties['stroke-width'] = 3;
            }

            var featureLayer = L.mapbox.featureLayer(data).addTo(map);

            featureLayer.eachLayer(function(layer) {
                var content = '<span style="font-weight:bold; font-size:120%;">' + layer.feature.properties.str_name2 + '<\/span><br \/>Speed: ' + layer.feature.properties.Speed + '<br \/>Condition: ' + layer.feature.properties.condition + '<br \/>Estimated Traffic Volume: ' + layer.feature.properties.est_vol;
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

// //Change line weight based on zoom level
// map.on('zoomend', function() {
//     if (map.getZoom() > 13) {
//         $("svg > g > path").css("stroke-width", "1");
//     } else {
//         $("svg > g > path").css("stroke-width", "2");
//     }
// });
}
$( document ).ready(load_data());