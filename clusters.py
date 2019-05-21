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

def spatialJoin(tablaIn, tablaJoin):
    nameFieldsTbIn = [x.name for x in arcpy.ListFields(tablaIn)] + [CODIGO+"_1", DISTANCIA, "X_1", "Y_1"]
    spJoin = arcpy.SpatialJoin_analysis(tablaIn, tablaJoin, os.path.join(pathgdb, "SJ_PENDIENTE"), "JOIN_ONE_TO_MANY","KEEP_ALL")
    nameFieldsSpJn = [x.name for x in arcpy.ListFields(spJoin)]
    extraerDistancia(spJoin)
    codigos = Counter([x[1] for x in arcpy.da.SearchCursor(spJoin, [CODIGO, CODIGO + "_1"])])
    for x in codigos.items():
        if x[1]==1:
            ejecutar1cluster(x)
        elif x[1]>1:
            ejecutarNcluster(x)
    
    nameFieldsRm = [x for x in nameFieldsSpJn if x not in nameFieldsTbIn]
    arcpy.DeleteField_management(spJoin, nameFieldsRm)

    return spJoin

def extraerDistancia(tabla):
    arcpy.AddField_management(tabla, DISTANCIA, "DOUBLE")
    with arcpy.da.UpdateCursor(tabla, ["X","Y","X_1","Y_1", DISTANCIA]) as cursor:
        for m in cursor:
            try:
                m[4] = round(math.sqrt((pow(m[0] - m[2], 2) + pow(m[1] - m[3], 2))) * 111110, 1)
                cursor.updateRow(m)
            except:
                pass
            
def ejecutar1cluster(tabla):
    arcpy.AddField_management(tabla, CODIGO + "_N", "TEXT", "#","#",100)
    # acont = arcpy.SelectLayerByLocation_management("ACONT_mfl", 'INTERSECT', "cli", '#', 'NEW_SELECTION', 'NOT_INVERT')


def ejecutarNcluster(tabla):
    pass

def main():
    cotizados = leerCsv(TB_COTIZADOS)
    pendientes = leerCsv(TB_PENDIENTES)
    bufferCotizado = buffer(cotizados, 500, "cotizado")
    bufferPendiente = buffer(pendientes, 500, "pendiente")
    spatialJoin(pendientes, bufferCotizado)

if __name__ == '__main__':
    main()
