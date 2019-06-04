import arcpy

arcpy.env.overwriteOutput = True

troba = arcpy.GetParameterAsText(0)
output = arcpy.GetParameterAsText(1)
field = arcpy.GetParameterAsText(2)
tap = arcpy.GetParameterAsText(3)
vias = arcpy.GetParameterAsText(4)
#   excel = arcpy.GetParameterAsText(5)


oids = [x[0] for x in arcpy.da.SearchCursor(troba, "OID@")][:5]
tapt = arcpy.MakeFeatureLayer_management(tap, "tap")
vias_mfl = arcpy.MakeFeatureLayer_management(vias, "vias_mfl")
longitud = [x[0] for x in arcpy.da.SearchCursor(output, [field])]
if len(longitud)==0:
    identificador = int()
else:
    identificador = max(longitud)

def optimizacion_cobertura(oid):
    global troba, tapt, identificador, vias_mfl

    query = "OBJECTID = %s" % oid
    troba_mfl = arcpy.MakeFeatureLayer_management(troba, "troba", query)


    pol_tmp = arcpy.FeatureToPolygon_management([troba_mfl, vias_mfl],  r'D:\TEMP\hora.shp')
    for m in arcpy.da.SearchCursor(pol_tmp, ['OID@', 'SHAPE@']):


        identificador += 1
        arcpy.AddMessage(identificador)
        pol = arcpy.MakeFeatureLayer_management(pol_tmp, 'pol_tmp_mfl', 'FID = {}'.format(m[0]))

        arcpy.SelectLayerByLocation_management(vias_mfl, "INTERSECT", troba_mfl, "#", 'NEW_SELECTION')

        arcpy.SelectLayerByLocation_management(tapt, "INTERSECT", pol, "#", 'NEW_SELECTION')

        if arcpy.GetCount_management(vias_mfl).__str__() == '0':
            arcpy.AddMessage("Tiene vias")

            pol = arcpy.FeatureToPolygon_management([pol, vias_mfl], "in_memory//thiessenVias")

        arcpy.env.extent = pol

        taps_thiessen = arcpy.CreateThiessenPolygons_analysis(tapt, "in_memory//taptemp")
        pol = arcpy.Clip_analysis(taps_thiessen, m[1], "in_memory//clipThiessen")

        #if pol:
          arcpy.Append_management(pol, output, 'NO_TEST')

        with arcpy.da.UpdateCursor(output, [field], "%s is null" % field) as cursor:
            for i in cursor:
                i[0] = identificador
                cursor.updateRow(i)
        del cursor

        arcpy.SelectLayerByAttribute_management(tapt, 'CLEAR_SELECTION')
        arcpy.SelectLayerByAttribute_management(vias_mfl, 'CLEAR_SELECTION')


if __name__ == '__main__':
    map(optimizacion_cobertura, oids)