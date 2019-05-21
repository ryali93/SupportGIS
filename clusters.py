#!/usr/bin/env python
# coding: utf-8

import os
import arcpy
import time
arcpy.env.overwriteOutput = True

workspace = r"C:\CLUSTERS"
nameGdb = "clusters"
ws = r'E:\2019\GUSTAVO\CLUSTER'
TB_COTIZADOS = os.path.join(ws, "COTIZADOS_6m.csv")
TB_PENDIENTES = os.path.join(ws, "PENDIENTES_xCOTIZAR.csv")
Y = "LATITUD"
X = "LONGITUD"

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
    spJoin = arcpy.SpatialJoin_analysis(tablaIn, tablaJoin, "in_memory\\spJoinTmp")
    return spJoin

# def modificarCodigo(tablaJoin):

def main():
    cotizados = leerCsv(TB_COTIZADOS)
    pendientes = leerCsv(TB_PENDIENTES)
    bufferCotizado = buffer(cotizados, 500, "cotizado")
    bufferPendiente = buffer(pendientes, 500, "pendiente")
    spatialJoin(cotizados, bufferPendiente)

if __name__ == '__main__':
    main()