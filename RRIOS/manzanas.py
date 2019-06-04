manzanas = "Manzanas_Project"
lineas = 'lineas_Project'

arcpy.DeleteRows_management(lineas)

mz = arcpy.MakeFeatureLayer_management(manzanas, "manzanas", "INGR_1 = '0'")
centroids = arcpy.FeatureToPoint_management(mz, "in_memory\\points")
buff = arcpy.Buffer_analysis(centroids, "in_memory\\buffer", "80 meters", "FULL", "ROUND", "NONE")

idmzs = [x[0] for x in arcpy.da.SearchCursor(centroids, ["ID_MZ"])]

for idmz in idmzs:
    sql = "ID_MZ = '%s'"%idmz
    xy = [x[0] for x in arcpy.da.SearchCursor(centroids, ["SHAPE@XY"], sql)][0]

    a = 80
    tamBuffer = []
    tamBuffer.append([xy[0] + a, xy[1]])
    tamBuffer.append([xy[0], xy[1] + a])
    tamBuffer.append([xy[0] - a, xy[1]])
    tamBuffer.append([xy[0], xy[1] - a])

    for i in tamBuffer:
        cursor = arcpy.da.InsertCursor(lineas, ["SHAPE@"])
        array = arcpy.Array([arcpy.Point(xy[0], xy[1]), arcpy.Point(i[0], i[1])])
        polyline = arcpy.Polyline(array)
        cursor.insertRow([polyline])

acont = arcpy.SelectLayerByLocation_management(manzanas, 'INTERSECT', lineas, '#', 'NEW_SELECTION', 'NOT_INVERT')