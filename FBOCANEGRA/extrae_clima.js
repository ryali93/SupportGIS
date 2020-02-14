var clipimage = function(img){
  return img.clip(geometry)
};

var precipitacion = ee.ImageCollection('TRMM/3B43V7').
                      filter(ee.Filter.date('2015-01-01', '2020-01-31')).
                      select('precipitation').
                      map(clipimage);


var temperatura = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').
                      filter(ee.Filter.date('2015-01-01', '2020-01-31')).
                      select('tmmx').
                      map(clipimage);

var humedad = ee.ImageCollection('NOAA/CFSR').
                      filter(ee.Filter.date('2015-01-01', '2020-01-31')).
                      select('Relative_humidity_entire_atmosphere_single_layer').
                      map(clipimage);

Map.addLayer(precipitacion, {}, 'PRECIPITACION');
Map.addLayer(temperatura, {}, 'TEMP');
Map.addLayer(humedad, {}, 'HUMEDAD')