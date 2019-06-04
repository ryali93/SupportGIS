import os, fnmatch
import arcpy

path = arcpy.GetParameterAsText(0)
shp = arcpy.GetParameterAsText(1)

# path = r'D:\RYali\AYUDADGR'
# shp = "Export_Output_2.shp"

arcpy.env.overwriteOutput = True

lista = fnmatch.filter(os.listdir(path), "*.tif")

namesLista = [x[:3] for x in lista]
for x in range(len(namesLista)):
    raster = arcpy.Raster(os.path.join(path,lista[x]))
    spr = raster.spatialReference

    if spr.name == u'WGS_1984_UTM_Zone_17S':
        spn = arcpy.SpatialReference(32717)
    elif spr.name == u'WGS_1984_UTM_Zone_18S':
        spn = arcpy.SpatialReference(32718)
    elif spr.name == u'WGS_1984_UTM_Zone_19S':
        spn = arcpy.SpatialReference(32719)
    else:
        spn = arcpy.SpatialReference(4326)

    areaHoja = arcpy.MakeFeatureLayer_management(shp, "in_memory\ghp", "COD_100 = '{}'".format(namesLista[x]))
    areaHojaN = arcpy.Project_management(areaHoja, os.path.join(path, "temp.shp"), spn)

    pathRaster = '{}'.format(''.join([namesLista[x], ".tif"]))
    pathRaster2 = os.path.join(path, 'RASTER', pathRaster)

    dsc = arcpy.Describe(areaHojaN)
    Rectangle = dsc.Extent.__str__().replace('NaN', '')

    arcpy.Clip_management(raster, Rectangle, pathRaster2)