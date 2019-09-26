from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode
from arcgis.geometry import Point

import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import fiona

gis = GIS()

class findAdress(object):
    def __init__(self, *args):
        self.pathFilename = args[0]
        self.fieldIndice = args[1]
        self.fieldAddress = args[2]
        self.ubicacion = args[3]
        self.output = args[4]
        self.rango = args[5]

    def assignFieldsDF(self):
        df = pd.read_csv(self.pathFilename, sep=";", encoding="cp1252")
        df["ADDRESS"] = df[self.fieldAddress]
        df["x"], df["y"] = 0, 0
        df["Match_addr"] = ""
        df["Score"] = ""
        return df

    def extractAddress(self, df, indice):
        zona_extent = geocode(self.ubicacion)[0]
        geocode_result = geocode(address = df.iloc[indice][self.fieldAddress],
                                as_featureset=True,
                                max_locations=1,
                                search_extent=zona_extent["extent"])
        for x in geocode_result.features:
            gdpoint = x.as_dict["geometry"]
            attr = x.as_dict["attributes"]
            df = df.append(
                pd.Series([df.iloc[indice][self.fieldIndice],
                    gdpoint["x"],
                    gdpoint["y"],
                    df.iloc[indice][self.fieldAddress],
                    attr["Match_addr"],
                    attr["Score"]],
                    index=[self.fieldIndice, "x", "y", self.fieldAddress,"Match_addr", "Score"] ), ignore_index=True)
        return df

    def main(self):
        self.df = self.assignFieldsDF()
        for n in range(self.rango[0], self.rango[1]):
            if n%10 == 0: print(n)
            self.df = self.extractAddress(self.df, n)

        data = self.df[self.df["x"] != 0]
        list_cli = list(set(data[self.fieldIndice]))
        data = self.df[self.df[self.fieldIndice].isin(list_cli)]

        data = data[data["x"]!=0]

        data = data[[self.fieldIndice, self.fieldAddress, 'x', 'y']]

        geometry = [Point(xy) for xy in zip(data.x, data.y)]
        crs = {'init': 'epsg:4326'}
        geo_df = GeoDataFrame(data, crs=crs, geometry=geometry)

        geo_df.to_file(driver='ESRI Shapefile', filename=self.output)

if __name__ == '__main__':
    try:
        pathFilename = 'direcciones.csv'
        fieldIndice = 'CLIENTE'
        fieldAddress = 'DIRECCION'
        ubicacion = 'Juliaca, PER'
        output = 'data3.shp'
        rango = [0, 21]

        poo = findAdress(pathFilename, fieldIndice, fieldAddress, ubicacion, output, rango)
        poo.main()

        import webbrowser
        # webbrowser.open('https://ryali93.github.io/blog')

    except Exception as e:
        print(e.message)