import os
import arcpy

arcpy.env.overwriteOutput = True
path = r'D:\temp' # Cambiar lo que esta entre comillas por tu carpeta
BASE_DIR = os.path.join(path)
listpaths = [os.path.join(BASE_DIR, x) for x in os.listdir(BASE_DIR) if x.split(".")[-1] == "shp"]
for x in listpaths:
    print x
    mfl = arcpy.MakeFeatureLayer_management(x, "mfl")
    arcpy.LayerToKML_conversion(mfl, x.split(".")[-2] + ".kmz")