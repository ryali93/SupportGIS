import arcpy, os
import math

arcpy.env.overwriteOutput = True

SCRATCH = arcpy.env.scratchGDB
CCPP = r'E:\SupportGIS\ABARJA\Datos_barja_py\gpo_ccpp.shp' # Cambiar por la ruta de ccpp
CAPITAL = r'E:\SupportGIS\ABARJA\Datos_barja_py\gpo_capitales.shp' # Cambiar por la ruta de capitales
PUNTOS_TMP = r'E:\SupportGIS\ABARJA\Datos_barja_py\puntos_tmp.shp' # Cambiar por cualquier ruta
SALIDA = r'E:\SupportGIS\ABARJA\Datos_barja_py\salida.shp' # Cambiar por shp de salida

CODIGO = 'UBIGEO' # CAMBIAR
WEIGHT = 'n_hogar' # CAMBIAR
FIELD_SDW = 'SDW' # Valor de sdw
PERCENT = 'PERCENT' # Nombre del campo porcentaje

print(arcpy.Describe(CCPP))
cod_unico = list(set([x for x in arcpy.da.SearchCursor(CCPP, [CODIGO])]))
puntos_tmp = arcpy.Copy_management(CAPITAL, PUNTOS_TMP)
arcpy.AddField_management(puntos_tmp, FIELD_SDW, "DOUBLE")
arcpy.AddField_management(puntos_tmp, PERCENT, "DOUBLE")

lista_error = []
for cod in cod_unico:
    try:
        print("CODIGO: {}".format(cod[0]))
        query = "{} = '{}'".format(CODIGO, cod[0])
        fields = ['SHAPE@X', 'SHAPE@Y',  WEIGHT] # agregar 'SHAPE@Z'
        datos = [x for x in arcpy.da.SearchCursor(CCPP, fields, query)]
        n = len(datos)
        print("n: {}".format(n))
        # xmean = sum([x[0] for x in datos])/n
        # ymean = sum([x[1] for x in datos])/n
        # zmean = sum([x[2] for x in datos])/n
        centroide = [x for x in arcpy.da.SearchCursor(CAPITAL, ['SHAPE@X', 'SHAPE@Y'], query)][0]
        print(centroide)

        # Calculando distancia standar
        sumatoria_x = 0 # X
        sumatoria_y = 0 # Y
        sumatoria_z = 0 # Z
        sumatoria_pesos = sum([x[2] for x in datos])
        for i in datos:
            sumatoria_x += i[2] * (i[0] - centroide[0]) ** 2
            sumatoria_y += i[2] * (i[1] - centroide[1]) ** 2
            # sumatoria_z += i[2] * (i[2] - centroide[2]) ** 2

        sdw = math.sqrt((sumatoria_x / sumatoria_pesos) + (sumatoria_y / sumatoria_pesos))
        print('SDW: {}'.format(sdw))

        mfl_ccpp = arcpy.MakeFeatureLayer_management(CCPP, "mfl_ccpp", query)
        mfl_capital = arcpy.MakeFeatureLayer_management(CAPITAL, "mfl_capital", query)

        # tabla_near = arcpy.PointDistance_analysis(mfl_ccpp, mfl_capital, "in_memory\\tb_near", sdw)
        tabla_near = arcpy.Near_analysis(mfl_ccpp, mfl_capital, '{} Meters'.format(sdw), 'NO_LOCATION', 'NO_ANGLE', 'PLANAR')
        print([x[0] for x in arcpy.da.SearchCursor(tabla_near, ["NEAR_DIST"])])

        cantidad_cercanos = len([x[0] for x in arcpy.da.SearchCursor(tabla_near, ["NEAR_DIST"]) if x[0] != -1])
        print('cantidad_cercanos: {}'.format(cantidad_cercanos))
        percent_cercanos = round(cantidad_cercanos * 100 / n, 2)
        print('percent_cercanos: {}'.format(percent_cercanos))

        with arcpy.da.UpdateCursor(puntos_tmp, [FIELD_SDW, PERCENT], query) as cursor:
            for x in cursor:
                x[0] = sdw
                x[1] = percent_cercanos
                cursor.updateRow(x)
    except:
        lista_error.append(cod)

arcpy.Buffer_analysis(puntos_tmp, SALIDA, FIELD_SDW)
print(lista_error)
