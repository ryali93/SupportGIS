#!/usr/bin/env python
# coding: utf-8

import os
import arcpy
import time
from collections import Counter
arcpy.env.overwriteOutput = True

workspace = r"C:\CLUSTERS"
nameGdb = "clusters"
ws = os.path.dirname(__file__) 
TB_COTIZADOS = os.path.join(ws, "COTIZADOS_6m.csv")
TB_PENDIENTES = os.path.join(ws, "PENDIENTES_xCOTIZAR.csv")
Y = "LATITUD"
X = "LONGITUD"
CODIGO = "CODIGO"
DISTANCIA = "DISTANCIA"

if os.path.exists(workspace)==False:
    os.mkdir(workspace)

def createGdb(carpeta):
    list_fc = []
    fecha = time.strftime('%d%b%y')
    hora = time.strftime('%H%M%S')
    nameFile = "Proceso-{}-{}".format(fecha, hora)
    FOLDER = arcpy.CreateFolder_management(carpeta, nameFile)
    GDB = arcpy.CreateFileGDB_management(FOLDER, nameGdb, "10.0")
    return os.path.join(carpeta, nameFile, nameGdb + ".gdb")

pathgdb = createGdb(workspace)

def modifyCoords(tabla):
    arcpy.AddField_management(tabla, "X", "DOUBLE")
    arcpy.AddField_management(tabla, "Y", "DOUBLE")
    arcpy.CalculateField_management(tabla, "X", '!{}!'.format(X), "PYTHON_9.3")
    arcpy.CalculateField_management(tabla, "Y", '!{}!'.format(Y), "PYTHON_9.3")

def leerCsv(tabla):
    nameTb = tabla.split("\\")[-1].split("_")[0]
    tb = arcpy.TableToTable_conversion(tabla, pathgdb, "TB_"+nameTb)
    modifyCoords(tb)
    xyTmp = arcpy.MakeXYEventLayer_management(tb, "X", "Y", os.path.join(pathgdb, "TB_"+nameTb), arcpy.SpatialReference(4326))
    copy = arcpy.CopyFeatures_management(xyTmp, os.path.join(pathgdb, nameTb))
    return copy

def buffer(feature, tamano, nombre):
    bufferXY = arcpy.Buffer_analysis(feature, os.path.join(pathgdb, "BF_"+nombre), '{} Meters'.format(tamano))
    return bufferXY

def spatialAnalysis(pendienteBuffer, pendientePunto, cotizado, longBuffer):
    cantidadCotizados = 10
    campos = 'ORIG_FID "ORIG_FID" true true false 4 Long 0 0 ,First,#,multipart,ORIG_FID,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,multipart,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0 ,First,#,multipart,Shape_Area,-1,-1;CODIGO "CODIGO" true true false 8000 Text 0 0 ,Join,#,PENDIENTES,CODIGO,-1,-1;CLIENTE "CLIENTE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,CLIENTE,-1,-1;TIPO_REQUERIMIENTO "TIPO REQUERIMIENTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,TIPO_REQUERIMIENTO,-1,-1;ALIAS "ALIAS" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ALIAS,-1,-1;RESPONSABLE_VU "RESPONSABLE VU" true true false 8000 Text 0 0 ,First,#,PENDIENTES,RESPONSABLE_VU,-1,-1;SALESFORCE "SALESFORCE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,SALESFORCE,-1,-1;PROYECTO "PROYECTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PROYECTO,-1,-1;REGISTRO "REGISTRO" true true false 8 Date 0 0 ,First,#,PENDIENTES,REGISTRO,-1,-1;SEGMENTO "SEGMENTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,SEGMENTO,-1,-1;DEPARTAMENTO "DEPARTAMENTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,DEPARTAMENTO,-1,-1;PROVINCIA "PROVINCIA" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PROVINCIA,-1,-1;DISTRITO "DISTRITO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,DISTRITO,-1,-1;DIRECCION "DIRECCION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,DIRECCION,-1,-1;NUMERO "NUMERO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,NUMERO,-1,-1;ACCESO "ACCESO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ACCESO,-1,-1;TENDIDO_EXTERNO "TENDIDO EXTERNO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,TENDIDO_EXTERNO,-1,-1;TIPO_SEDE "TIPO SEDE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,TIPO_SEDE,-1,-1;NRO_PISOS "NRO PISOS" true true false 4 Long 0 0 ,First,#,PENDIENTES,NRO_PISOS,-1,-1;ZONAL "ZONAL" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ZONAL,-1,-1;RESPONSABLE "RESPONSABLE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,RESPONSABLE,-1,-1;REGION "REGION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,REGION,-1,-1;ENLACE "ENLACE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ENLACE,-1,-1;LATITUD "LATITUD" true true false 8 Double 0 0 ,First,#,PENDIENTES,LATITUD,-1,-1;LONGITUD "LONGITUD" true true false 8 Double 0 0 ,First,#,PENDIENTES,LONGITUD,-1,-1;UNIDAD_DE_NEGOCIO "UNIDAD DE NEGOCIO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,UNIDAD_DE_NEGOCIO,-1,-1;ESTUDIO "ESTUDIO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ESTUDIO,-1,-1;NODO "NODO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,NODO,-1,-1;DIAS "DIAS" true true false 4 Long 0 0 ,First,#,PENDIENTES,DIAS,-1,-1;PEP "PEP" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PEP,-1,-1;PEP2 "PEP2" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PEP2,-1,-1;GRAFO "GRAFO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,GRAFO,-1,-1;TOTAL_SOLES "TOTAL SOLES" true true false 8 Double 0 0 ,First,#,PENDIENTES,TOTAL_SOLES,-1,-1;TOTAL_DOLARES "TOTAL DOLARES" true true false 4 Long 0 0 ,First,#,PENDIENTES,TOTAL_DOLARES,-1,-1;ESTADO_ESTUDIO "ESTADO ESTUDIO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ESTADO_ESTUDIO,-1,-1;COTIZACION_SOLES "COTIZACION SOLES" true true false 4 Long 0 0 ,First,#,PENDIENTES,COTIZACION_SOLES,-1,-1;COTIZACION_DOLARES "COTIZACION DOLARES" true true false 4 Long 0 0 ,First,#,PENDIENTES,COTIZACION_DOLARES,-1,-1;FECHA_ENVIO "FECHA ENVIO" true true false 8 Date 0 0 ,First,#,PENDIENTES,FECHA_ENVIO,-1,-1;INICIO_ESTUDIO "INICIO ESTUDIO" true true false 8 Date 0 0 ,First,#,PENDIENTES,INICIO_ESTUDIO,-1,-1;FIN_ESTUDIO "FIN ESTUDIO" true true false 8 Date 0 0 ,First,#,PENDIENTES,FIN_ESTUDIO,-1,-1;FIN_CONSOLIDACION "FIN CONSOLIDACION" true true false 8 Date 0 0 ,First,#,PENDIENTES,FIN_CONSOLIDACION,-1,-1;INICIO_EJECUCION "INICIO EJECUCION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,INICIO_EJECUCION,-1,-1;INICIO_IMPLEMENTACION "INICIO IMPLEMENTACION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,INICIO_IMPLEMENTACION,-1,-1;ESTADO "ESTADO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ESTADO,-1,-1;X "X" true true false 8 Double 0 0 ,First,#,PENDIENTES,X,-1,-1;Y "Y" true true false 8 Double 0 0 ,First,#,PENDIENTES,Y,-1,-1'
    dissol1 = arcpy.Dissolve_management(pendienteBuffer, "in_memory\\dissolve1", '#', '#', 'MULTI_PART', 'DISSOLVE_LINES')
    multipart = arcpy.MultipartToSinglepart_management(dissol1, os.path.join(pathgdb, "multipart"))
    sp_pendiente = arcpy.SpatialJoin_analysis(multipart, pendientePunto, os.path.join(pathgdb, "sp_pendiente"), 'JOIN_ONE_TO_ONE', 'KEEP_ALL', campos, 'INTERSECT', '#', '#')
    featurePoint = arcpy.FeatureToPoint_management(sp_pendiente, os.path.join(pathgdb, "featurePoint"), 'INSIDE')
    # OJO buffer de 500???????
    bufferPoint = arcpy.Buffer_analysis(featurePoint, os.path.join(pathgdb, "BF_Pendiente_N"), '{} Meters'.format(longBuffer))
    tb_near = arcpy.GenerateNearTable_analysis(bufferPoint, cotizado, os.path.join(pathgdb, "TB_resumen"), '{} Meters'.format(longBuffer), 'NO_LOCATION', 'NO_ANGLE', 'ALL', cantidadCotizados, 'GEODESIC')
    codigoCotizado = {x[0]:x[1] for x in arcpy.da.SearchCursor(cotizado, ["OBJECTID", CODIGO])}
    codigoPendiente = {x[0]:x[1] for x in arcpy.da.SearchCursor(bufferPoint, ["OBJECTID", CODIGO])}

    arcpy.AddField_management(tb_near, "DISTANCIA", "DOUBLE")
    arcpy.AddField_management(tb_near, "CODIGO_PENDIENTE", "TEXT", "#", "#", 100)
    arcpy.AddField_management(tb_near, "CODIGO_COTIZADO", "TEXT", "#", "#", 100)
    arcpy.AddField_management(tb_near, "CODIGO_N", "TEXT", "#", "#", 100)

    with arcpy.da.UpdateCursor(tb_near, ["IN_FID", "NEAR_FID", "NEAR_DIST", "CODIGO_COTIZADO", "CODIGO_PENDIENTE", "DISTANCIA", "CODIGO_N"]) as cursor:
        for x in cursor:
            x[3] = codigoCotizado.get(x[1])
            x[4] = codigoPendiente.get(x[0])
            x[5] = x[2]
            cursor.updateRow(x)
    

def spatialJoin(tablaIn, tablaJoin):
    lista1cluster = []
    listaNcluster = []
    codes = [x[0] for x in arcpy.da.SearchCursor(tablaJoin, [CODIGO])]
    for code in codes:
        sql = "{} = '{}'".format(CODIGO, code)
        mfl_buffer = arcpy.MakeFeatureLayer_management(tablaJoin, "mfl_buffer", sql)
        spJoin = arcpy.SpatialJoin_analysis(tablaIn, mfl_buffer, "in_memory\\buffer_{}".format(code), "JOIN_ONE_TO_MANY")
        arcpy.SelectLayerByLocation_management(spJoin, tablaIn, "")


    nameFieldsTbIn = [x.name for x in arcpy.ListFields(tablaIn)] + [CODIGO+"_1", DISTANCIA, "X_1", "Y_1"]
    spJoin = arcpy.SpatialJoin_analysis(tablaIn, tablaJoin, os.path.join(pathgdb, "SJ_PENDIENTE"), "JOIN_ONE_TO_MANY")
    nameFieldsSpJn = [x.name for x in arcpy.ListFields(spJoin)]
    extraerDistancia(spJoin)
    codigos = Counter([x[1] for x in arcpy.da.SearchCursor(spJoin, [CODIGO, CODIGO + "_1"])])

    CODIGO_N = CODIGO + "_N"
    arcpy.AddField_management(spJoin, CODIGO_N, "TEXT", "#", "#", 100)
    for x in codigos.items():
        if x[1]==1:
            ejecutar1cluster(spJoin, x[0])
            lista1cluster.append(x)
        elif x[1]>1:
            ejecutarNcluster(spJoin, x[0], spJoin)
            listaNcluster.append(x)

    print("1cluster")
    print(lista1cluster)
    print("\n")
    print("Ncluster")
    print(listaNcluster)
    print("\n")
    
    nameFieldsRm = [x for x in nameFieldsSpJn if x not in nameFieldsTbIn]
    arcpy.DeleteField_management(spJoin, nameFieldsRm)

    return spJoin

def extraerDistancia(tabla):
    arcpy.AddField_management(tabla, DISTANCIA, "DOUBLE")
    with arcpy.da.UpdateCursor(tabla, ["X", "Y", "X_1", "Y_1", DISTANCIA]) as cursor:
        for m in cursor:
            try:
                m[4] = round(math.sqrt((pow(m[0] - m[2], 2) + pow(m[1] - m[3], 2))) * 111110, 1)
                cursor.updateRow(m)
            except:
                pass

def ejecutar1cluster(tabla, codigoUnico):
    CODIGO_N = CODIGO + "_N"
    sql = "{} = '{}'".format(CODIGO, codigoUnico)
    with arcpy.da.UpdateCursor(tabla, [CODIGO, CODIGO_N], sql) as cursor:
        for n in cursor:
            n[1] = "Cluster_Simple_{}".format(n[0])
            cursor.updateRow(n)

def ejecutarNcluster(tabla, codigoUnico, tablaJoin):
    pass
    # CODIGO_N = CODIGO + "_N"
    # sql = "{} = '{}'".format(CODIGO, codigoUnico)
    # mfl = arcpy.MakeFeatureLayer_management(tabla, "mfl", sql)
    # acont = arcpy.SelectLayerByLocation_management(tablaJoin, 'INTERSECT', mfl, '#', 'NEW_SELECTION', 'NOT_INVERT')
    # arcpy.


def main():
    cotizados = leerCsv(TB_COTIZADOS)
    pendientes = leerCsv(TB_PENDIENTES)
    bufferCotizado = buffer(cotizados, 500, "cotizado")
    bufferPendiente = buffer(pendientes, 500, "pendiente")
    # spatialJoin(cotizados, bufferPendiente)
    spatialAnalysis(bufferPendiente, pendientes, cotizados, 500)

if __name__ == '__main__':
    main()
