import os
import arcpy

arcpy.env.overwriteOutput = True
scratch = arcpy.env.scratchGDB
scratchFolder = arcpy.env.scratchFolder


trobaInicial = r'E:\2019\GUSTAVO\COBERTURA\COBERTURA.gdb\TROBAS'
output = r'E:\2019\GUSTAVO\COBERTURA\COBERTURA.gdb\AREAS_IN'
field = 'increm'
tablaXY = r'E:\2019\GUSTAVO\COBERTURA\COBERTURA.gdb\TablaXY'
vias = r'E:\2019\GUSTAVO\COBERTURA\COBERTURA.gdb\VIAS'
zona = '18S'

zonasUTM = {'17S': 32717, '18S': 32718, '19S': 32719}

arcpy.DeleteRows_management(output)

def extents(fc):
    extent = arcpy.Describe(fc).extent
    west = extent.XMin
    south = extent.YMin
    east = extent.XMax
    north = extent.YMax
    width = extent.width
    height = extent.height
    return west, south, east, north, width, height


xyTmp = arcpy.MakeXYEventLayer_management(tablaXY, "X", "Y", "in_memory\\tbxy", arcpy.SpatialReference(4326))
xybuffer8 = arcpy.Buffer_analysis(xyTmp, "in_memory\\xybuffer8", '8 Meters', 'FULL', 'ROUND', 'ALL', '#', 'PLANAR')
xybuffer70 = arcpy.Buffer_analysis(xyTmp, "in_memory\\xybuffer70", '70 Meters', 'FULL', 'ROUND', 'ALL', '#', 'PLANAR')
xymts = arcpy.MultipartToSinglepart_management(xybuffer8, "in_memory\\xymts")
xyftp = arcpy.FeatureToPoint_management(xymts, "in_memory\\xyftp", 'INSIDE')
xyproj = arcpy.Project_management(xyftp, os.path.join(scratch, "xyproj"), arcpy.SpatialReference(zonasUTM[zona]))

xypolbuffer70 = arcpy.SimplifyPolygon_cartography(xybuffer70, "in_memory\\xypolbuffer70", 'BEND_SIMPLIFY', '40 Meters', '0 Unknown', 'RESOLVE_ERRORS', 'KEEP_COLLAPSED_POINTS', '#')
xyintertroba = arcpy.Intersect_analysis([xypolbuffer70, trobaInicial], os.path.join(scratch, "xyintertroba"), 'ALL', '#', 'INPUT')

xyintertroba_SJ = arcpy.SpatialJoin_analysis(xyintertroba, xyTmp, "in_memory\\xyintertroba_SJ", 'JOIN_ONE_TO_ONE', 'KEEP_ALL', '#', 'COMPLETELY_CONTAINS', '#', '#')

# vias = arcpy.Project_management(vias, os.path.join(scratch, "vias"), arcpy.SpatialReference(zonasUTM[zona]))
# ntroba = arcpy.Project_management(xyintertroba_SJ, os.path.join(scratch, "ntrobaN"), arcpy.SpatialReference(zonasUTM[zona]))
# output = arcpy.Project_management(output, os.path.join(scratch, "output"), arcpy.SpatialReference(zonasUTM[zona]))

querytroba = "Join_Count<>0"
ntroba = arcpy.MakeFeatureLayer_management(xyintertroba_SJ, "ntroba", querytroba)

oids = [x[0] for x in arcpy.da.SearchCursor(ntroba, "OID@")][:5]
tapt = arcpy.MakeFeatureLayer_management(xyftp, "tap")
vias_mfl = arcpy.MakeFeatureLayer_management(vias, "vias_mfl")
longitud = [x[0] for x in arcpy.da.SearchCursor(output, [field])]
if len(longitud)==0:
    identificador = int()
else:
    identificador = max(longitud)


for oid in oids:
    query = "OBJECTID = %s" % oid
    troba_mfl = arcpy.MakeFeatureLayer_management(ntroba, "ntroba", query)
    arcpy.SelectLayerByLocation_management(vias_mfl, "INTERSECT", troba_mfl, "#", 'NEW_SELECTION')
    print query, arcpy.GetCount_management(vias_mfl).__str__()
    if arcpy.GetCount_management(vias_mfl).__str__() != '0':
        troba_mfl = arcpy.FeatureToPolygon_management([troba_mfl, vias_mfl], "in_memory//troba_mfl")
    print query, arcpy.GetCount_management(vias_mfl).__str__()
    arcpy.SelectLayerByAttribute_management(vias_mfl, 'CLEAR_SELECTION')

    with arcpy.da.SearchCursor(troba_mfl, ['OID@', 'SHAPE@']) as cursor:
        for m in cursor:
            identificador += 1
            arcpy.AddMessage(identificador)
            nuevotroba = arcpy.MakeFeatureLayer_management(troba_mfl, 'troba_tmp_mfl', 'OBJECTID = {}'.format(m[0]))

            arcpy.SelectLayerByLocation_management(tapt, "INTERSECT", nuevotroba, "#", 'NEW_SELECTION')

            extentArea = extents(nuevotroba)
            arcpy.env.extent = "%s %s %s %s" % (extentArea[0], extentArea[1], extentArea[2], extentArea[3])
            
            taps_thiessen = arcpy.CreateThiessenPolygons_analysis(tapt, "in_memory//taptemp")
            trobaNuevo = arcpy.Clip_analysis(taps_thiessen, m[1], "in_memory//clipThiessen")

            arcpy.Append_management(trobaNuevo, output, 'NO_TEST')

            with arcpy.da.UpdateCursor(output, [field], "%s is null" % field) as cursor:
                for i in cursor:
                    i[0] = identificador
                    cursor.updateRow(i)
            del cursor

            arcpy.SelectLayerByAttribute_management(tapt, 'CLEAR_SELECTION')   
