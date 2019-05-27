#!/usr/bin/env python
# coding: utf-8

import os
import arcpy
import time
import csv
from collections import Counter
arcpy.env.overwriteOutput = True

workspace = r"C:\CLUSTERS"
nameGdb = "clusters"
ws = os.path.dirname(__file__)
# TB_COTIZADOS = arcpy.GetParameterAsText(0)
# TB_PENDIENTES = arcpy.GetParameterAsText(1)
# ws = arcpy.GetParameterAsText(2)
TB_COTIZADOS  = os.path.join(ws, "COTIZADOS_6m.csv")
TB_PENDIENTES = os.path.join(ws, "PENDIENTES_xCOTIZAR.csv")
GDB_DIR       = os.path.join(ws, "CLUSTERS.gdb")

COBERTURA_P2P = os.path.join(GDB_DIR, "COBERTURA_P2P_MIXTA")
URA           = os.path.join(GDB_DIR, "URA_EC")

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

def extraerPendientes(pendientes, cobertura):
    pendientes = arcpy.MakeFeatureLayer_management(pendientes, "pendientes")
    mfl = arcpy.MakeFeatureLayer_management(cobertura, "cobertura")
    pendienteCobertura = arcpy.SelectLayerByLocation_management("pendientes", 'INTERSECT', "cobertura", '#', '#', 'NOT_INVERT')
    fields = [CODIGO, "SHAPE@X", "SHAPE@Y"]
    ultimaMilla = [x for x in arcpy.da.SearchCursor(pendienteCobertura, fields)]
    arcpy.SelectLayerByAttribute_management(pendienteCobertura, "CLEAR_SELECTION")

    pendienteDentroCobertura = arcpy.SelectLayerByLocation_management(pendientes, 'INTERSECT', "cobertura", '#', '#', 'INVERT')
    pendiente = arcpy.CopyFeatures_management(pendienteDentroCobertura, os.path.join(pathgdb, "PENDIENTE"))
    return pendiente, ultimaMilla

def addUltimaMillaToTb(ultimaMilla, tb_near):
    fields = ["CODIGO_PENDIENTE", "X_PENDIENTE", "Y_PENDIENTE", "CODIGO_N"]
    for row in ultimaMilla:
        lista = [row[0], row[1], row[2]]
        m = "UltimaMilla_" + row[0]
        lista.append(m)
        with arcpy.da.InsertCursor(tb_near, fields) as cursor:
            cursor.insertRow(lista)

def buffer(feature, tamano, nombre):
    bufferXY = arcpy.Buffer_analysis(feature, os.path.join(pathgdb, "BF_"+nombre), '{} Meters'.format(tamano))
    return bufferXY

def fx(x):
    if x== CODIGO:
        res= "{0} {0} VISIBLE NONE"        
    else:
        res="{0} {0} HIDDEN NONE"
    return res.format(x)

def extractCentroid(pendienteBuffer, pendientePunto, cotizado):
    campos = 'ORIG_FID "ORIG_FID" true true false 4 Long 0 0 ,First,#,multipart,ORIG_FID,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,multipart,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0 ,First,#,multipart,Shape_Area,-1,-1;CODIGO "CODIGO" true true false 8000 Text 0 0 ,Join,"_",PENDIENTES_Layer,CODIGO,-1,-1;X "X" true true false 8 Double 0 0 ,First,#,PENDIENTES_Layer,X,-1,-1;Y "Y" true true false 8 Double 0 0 ,First,#,PENDIENTES_Layer,Y,-1,-1'
    dissol1 = arcpy.Dissolve_management(pendienteBuffer, "in_memory\\dissolve1", '#', '#', 'MULTI_PART', 'DISSOLVE_LINES').getOutput(0)
    multipart = arcpy.MultipartToSinglepart_management(dissol1, os.path.join(pathgdb, "multipart")).getOutput(0)
    field_pend = "_ ".join(list(map(fx,pendientePunto)))
    pendientelyr = arcpy.MakeFeatureLayer_management(pendientePunto, 'PENDIENTES_Layer', '#', '#',field_info = field_pend).getOutput(0)
    sp_pendiente = arcpy.SpatialJoin_analysis(multipart, pendientelyr, "in_memory\\sp_pendiente", 'JOIN_ONE_TO_ONE', 'KEEP_ALL', campos, 'INTERSECT', '#', '#').getOutput(0)
    m_Centroide = arcpy.FeatureToPoint_management(sp_pendiente, os.path.join(pathgdb, "pendientesCentroide"), 'INSIDE').getOutput(0)
    return m_Centroide

def createTable(pendienteCentroide, cotizado, longBuffer):
    cantidadCotizados = 10
    tb_near = arcpy.GenerateNearTable_analysis(pendienteCentroide, cotizado, os.path.join(pathgdb, "TB_resumen"), '{} Meters'.format(longBuffer), 'NO_LOCATION', 'NO_ANGLE', 'ALL', cantidadCotizados, 'GEODESIC')
    codigoCotizado  = {x[0]:[x[1], x[2], x[3]] for x in arcpy.da.SearchCursor(cotizado, ["OBJECTID", CODIGO, "SHAPE@X", "SHAPE@Y"])}
    codigoPendiente = {x[0]:[x[1], x[2], x[3]] for x in arcpy.da.SearchCursor(pendienteCentroide, ["OBJECTID", CODIGO, "SHAPE@X", "SHAPE@Y"])}

    arcpy.AddField_management(tb_near, "X_COTIZADO", "DOUBLE")
    arcpy.AddField_management(tb_near, "Y_COTIZADO", "DOUBLE")
    arcpy.AddField_management(tb_near, "X_PENDIENTE", "DOUBLE")
    arcpy.AddField_management(tb_near, "Y_PENDIENTE", "DOUBLE")
    arcpy.AddField_management(tb_near, "DISTANCIA", "DOUBLE")
    arcpy.AddField_management(tb_near, "CODIGO_PENDIENTE", "TEXT", "#", "#", 100)
    arcpy.AddField_management(tb_near, "CODIGO_COTIZADO", "TEXT", "#", "#", 100)
    arcpy.AddField_management(tb_near, "CODIGO_N", "TEXT", "#", "#", 100)

    with arcpy.da.UpdateCursor(tb_near, ["IN_FID", "NEAR_FID", "NEAR_DIST", "CODIGO_COTIZADO", "CODIGO_PENDIENTE", "DISTANCIA", "X_COTIZADO", "Y_COTIZADO", "X_PENDIENTE", "Y_PENDIENTE", "CODIGO_N"]) as cursor:
        for x in cursor:
            x[3] = codigoCotizado.get(x[1])[0]
            x[4] = codigoPendiente.get(x[0])[0]
            x[5] = round(x[2],2)

            x[6] = codigoCotizado.get(x[1])[1]
            x[7] = codigoCotizado.get(x[1])[2]

            x[8] = codigoPendiente.get(x[0])[1]
            x[9] = codigoPendiente.get(x[0])[2]

            if len(x[4].split("_"))==1:
                x[10] = "ClusterSimple_"+x[4]
            else:
                x[10] = "SuperCluster_"+x[4]
            cursor.updateRow(x)
    return tb_near
    
def extraerDistancia(x1, y1, x2, y2):
    return round(math.sqrt((pow(x1 - x2, 2) + pow(y1 - y2, 2))) * 111110, 1)

def tabla2csv(tabla, output_csv, csv_delimiter):
    with open(os.path.join(ws, output_csv), 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=csv_delimiter)
        fld_names = [x.name for x in arcpy.ListFields(tabla)]
        print(fld_names)
        writer.writerow(fld_names)
        with arcpy.da.SearchCursor(tabla, fld_names) as cursor:
            for row in cursor:
                print(row)
                writer.writerow(row)
        csv_file.close()

def spjoinTb(tablaPrincipal, tablaCopia):
    tb_join = arcpy.SpatialJoin_analysis(
        tablaPrincipal, 
        tablaCopia, 
        "in_memory\\tb_join2", 
        "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "INTERSECT")
    fields = ["CODIGO", "ZONAL_1", "JEFATURA", "EE_CC"]
    fieldsURA = [x for x in arcpy.da.SearchCursor(tb_join, fields)]
    return fieldsURA

def updateTbFieldsURA(tabla, fieldsUpdate, campos):
    for campo in campos:
        arcpy.AddField_management(tabla, campo, "TEXT", "#", "#", 100)
    fields = ["CODIGO_PENDIENTE"] + campos
    with arcpy.da.UpdateCursor(tabla, fields) as cursor:
        for x in cursor:
            for f in fieldsUpdate:
                if f[0] == x[0].split("_")[0]:
                    x[1] = f[1]
                    x[2] = f[2]
                    x[3] = f[3]
                    cursor.updateRow(x)
    return tabla

def main():
    cotizados = leerCsv(TB_COTIZADOS)
    pendientes = leerCsv(TB_PENDIENTES)

    pendientes, ultimaMilla = extraerPendientes(pendientes, COBERTURA_P2P)

    bufferPendiente = buffer(pendientes, 150, "pendiente")
    centroide = extractCentroid(bufferPendiente, pendientes, cotizados)
    
    fieldsupdateURA = spjoinTb(pendientes, URA)

    tabla = createTable(centroide, cotizados, 500)
    addUltimaMillaToTb(ultimaMilla, tabla)

    tabla = updateTbFieldsURA(tabla, fieldsupdateURA, ["ZONAL", "JEFATURA", "EE_CC"])

    tabla2csv(tabla, "Tabla_resumen.csv", ",")

if __name__ == '__main__':
    main()
    print "\a"
