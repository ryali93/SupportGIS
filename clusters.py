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
TB_COTIZADOS = arcpy.GetParameterAsText(0)
TB_PENDIENTES = arcpy.GetParameterAsText(1)
ws = arcpy.GetParameterAsText(2)
# TB_COTIZADOS = os.path.join(ws, "COTIZADOS_6m.csv")
# TB_PENDIENTES = os.path.join(ws, "PENDIENTES_xCOTIZAR.csv")
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

def fx(x):
    if x== CODIGO:
        res= "{0} {0} VISIBLE NONE"        
    else:
        res="{0} {0} HIDDEN NONE"
    return res.format(x)


def spatialAnalysis(pendienteBuffer, pendientePunto, cotizado, longBuffer):
    cantidadCotizados = 10
    # campos = 'ORIG_FID "ORIG_FID" true true false 4 Long 0 0 ,First,#,multipart,ORIG_FID,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,multipart,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0 ,First,#,multipart,Shape_Area,-1,-1;CODIGO "CODIGO" true true false 8000 Text 0 0 ,Join,#,PENDIENTES,CODIGO,-1,-1;CLIENTE "CLIENTE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,CLIENTE,-1,-1;TIPO_REQUERIMIENTO "TIPO REQUERIMIENTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,TIPO_REQUERIMIENTO,-1,-1;ALIAS "ALIAS" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ALIAS,-1,-1;RESPONSABLE_VU "RESPONSABLE VU" true true false 8000 Text 0 0 ,First,#,PENDIENTES,RESPONSABLE_VU,-1,-1;SALESFORCE "SALESFORCE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,SALESFORCE,-1,-1;PROYECTO "PROYECTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PROYECTO,-1,-1;REGISTRO "REGISTRO" true true false 8 Date 0 0 ,First,#,PENDIENTES,REGISTRO,-1,-1;SEGMENTO "SEGMENTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,SEGMENTO,-1,-1;DEPARTAMENTO "DEPARTAMENTO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,DEPARTAMENTO,-1,-1;PROVINCIA "PROVINCIA" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PROVINCIA,-1,-1;DISTRITO "DISTRITO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,DISTRITO,-1,-1;DIRECCION "DIRECCION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,DIRECCION,-1,-1;NUMERO "NUMERO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,NUMERO,-1,-1;ACCESO "ACCESO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ACCESO,-1,-1;TENDIDO_EXTERNO "TENDIDO EXTERNO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,TENDIDO_EXTERNO,-1,-1;TIPO_SEDE "TIPO SEDE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,TIPO_SEDE,-1,-1;NRO_PISOS "NRO PISOS" true true false 4 Long 0 0 ,First,#,PENDIENTES,NRO_PISOS,-1,-1;ZONAL "ZONAL" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ZONAL,-1,-1;RESPONSABLE "RESPONSABLE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,RESPONSABLE,-1,-1;REGION "REGION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,REGION,-1,-1;ENLACE "ENLACE" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ENLACE,-1,-1;LATITUD "LATITUD" true true false 8 Double 0 0 ,First,#,PENDIENTES,LATITUD,-1,-1;LONGITUD "LONGITUD" true true false 8 Double 0 0 ,First,#,PENDIENTES,LONGITUD,-1,-1;UNIDAD_DE_NEGOCIO "UNIDAD DE NEGOCIO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,UNIDAD_DE_NEGOCIO,-1,-1;ESTUDIO "ESTUDIO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ESTUDIO,-1,-1;NODO "NODO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,NODO,-1,-1;DIAS "DIAS" true true false 4 Long 0 0 ,First,#,PENDIENTES,DIAS,-1,-1;PEP "PEP" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PEP,-1,-1;PEP2 "PEP2" true true false 8000 Text 0 0 ,First,#,PENDIENTES,PEP2,-1,-1;GRAFO "GRAFO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,GRAFO,-1,-1;TOTAL_SOLES "TOTAL SOLES" true true false 8 Double 0 0 ,First,#,PENDIENTES,TOTAL_SOLES,-1,-1;TOTAL_DOLARES "TOTAL DOLARES" true true false 4 Long 0 0 ,First,#,PENDIENTES,TOTAL_DOLARES,-1,-1;ESTADO_ESTUDIO "ESTADO ESTUDIO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ESTADO_ESTUDIO,-1,-1;COTIZACION_SOLES "COTIZACION SOLES" true true false 4 Long 0 0 ,First,#,PENDIENTES,COTIZACION_SOLES,-1,-1;COTIZACION_DOLARES "COTIZACION DOLARES" true true false 4 Long 0 0 ,First,#,PENDIENTES,COTIZACION_DOLARES,-1,-1;FECHA_ENVIO "FECHA ENVIO" true true false 8 Date 0 0 ,First,#,PENDIENTES,FECHA_ENVIO,-1,-1;INICIO_ESTUDIO "INICIO ESTUDIO" true true false 8 Date 0 0 ,First,#,PENDIENTES,INICIO_ESTUDIO,-1,-1;FIN_ESTUDIO "FIN ESTUDIO" true true false 8 Date 0 0 ,First,#,PENDIENTES,FIN_ESTUDIO,-1,-1;FIN_CONSOLIDACION "FIN CONSOLIDACION" true true false 8 Date 0 0 ,First,#,PENDIENTES,FIN_CONSOLIDACION,-1,-1;INICIO_EJECUCION "INICIO EJECUCION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,INICIO_EJECUCION,-1,-1;INICIO_IMPLEMENTACION "INICIO IMPLEMENTACION" true true false 8000 Text 0 0 ,First,#,PENDIENTES,INICIO_IMPLEMENTACION,-1,-1;ESTADO "ESTADO" true true false 8000 Text 0 0 ,First,#,PENDIENTES,ESTADO,-1,-1;X "X" true true false 8 Double 0 0 ,First,#,PENDIENTES,X,-1,-1;Y "Y" true true false 8 Double 0 0 ,First,#,PENDIENTES,Y,-1,-1'
    campos = 'ORIG_FID "ORIG_FID" true true false 4 Long 0 0 ,First,#,multipart,ORIG_FID,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,multipart,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0 ,First,#,multipart,Shape_Area,-1,-1;CODIGO "CODIGO" true true false 8000 Text 0 0 ,Join,"_",PENDIENTES_Layer,CODIGO,-1,-1;X "X" true true false 8 Double 0 0 ,First,#,PENDIENTES_Layer,X,-1,-1;Y "Y" true true false 8 Double 0 0 ,First,#,PENDIENTES_Layer,Y,-1,-1'
    dissol1 = arcpy.Dissolve_management(pendienteBuffer, "in_memory\\dissolve1", '#', '#', 'MULTI_PART', 'DISSOLVE_LINES').getOutput(0)
    multipart = arcpy.MultipartToSinglepart_management(dissol1, os.path.join(pathgdb, "multipart")).getOutput(0)
    field_pend = "_ ".join(list(map(fx,pendientePunto)))
    pendientelyr = arcpy.MakeFeatureLayer_management(pendientePunto, 'PENDIENTES_Layer', '#', '#',field_info = field_pend).getOutput(0)
    sp_pendiente = arcpy.SpatialJoin_analysis(multipart, pendientelyr, os.path.join(pathgdb, "sp_pendiente"), 'JOIN_ONE_TO_ONE', 'KEEP_ALL', campos, 'INTERSECT', '#', '#').getOutput(0)
    featurePoint = arcpy.FeatureToPoint_management(sp_pendiente, os.path.join(pathgdb, "featurePoint"), 'INSIDE').getOutput(0)
    # OJO buffer de 500???????
    bufferPoint = arcpy.Buffer_analysis(featurePoint, os.path.join(pathgdb, "BF_Pendiente_N"), '{} Meters'.format(longBuffer))
    tb_near = arcpy.GenerateNearTable_analysis(bufferPoint, cotizado, os.path.join(pathgdb, "TB_resumen"), '{} Meters'.format(longBuffer), 'NO_LOCATION', 'NO_ANGLE', 'ALL', cantidadCotizados, 'GEODESIC')
    codigoCotizado = {x[0]:x[1] for x in arcpy.da.SearchCursor(cotizado, ["OBJECTID", CODIGO])}
    codigoPendiente = {x[0]:x[1] for x in arcpy.da.SearchCursor(bufferPoint, ["OBJECTID", CODIGO])}
    len_pen= max([len(v)for v in codigoPendiente.values()])
    print len_pen

    arcpy.AddField_management(tb_near, "DISTANCIA", "DOUBLE")
    arcpy.AddField_management(tb_near, "CODIGO_PENDIENTE", "TEXT", "#", "#", len_pen)
    arcpy.AddField_management(tb_near, "CODIGO_COTIZADO", "TEXT", "#", "#", 100)
    arcpy.AddField_management(tb_near, "CODIGO_N", "TEXT", "#", "#", 100)

    with arcpy.da.UpdateCursor(tb_near, ["IN_FID", "NEAR_FID", "NEAR_DIST", "CODIGO_COTIZADO", "CODIGO_PENDIENTE", "DISTANCIA"]) as cursor:
        for x in cursor:
            x[3] = codigoCotizado.get(x[1])
            x[4] = codigoPendiente.get(x[1])
            x[4] = codigoPendiente.get(x[0])
            x[5] = x[2]
            cursor.updateRow(x)

    codPendientes = Counter([x[0] for x in arcpy.da.SearchCursor(tb_near, ["CODIGO_PENDIENTE"])])

    with arcpy.da.UpdateCursor(tb_near, ["CODIGO_PENDIENTE", "CODIGO_N"]) as cursor:
        for x in cursor:
            # Caso 1
<<<<<<< HEAD
            # if codPendientes.get(x[0]) == 1:
=======
>>>>>>> c703a92ba2d3a663ce26f521805ae112b50175fb
            if len(x[0].split("_"))==1:
                x[1] = "ClusterSimple_"+x[0]
            # Caso 2
            else:
                x[1] = "SuperCluster_"+x[0]
            cursor.updateRow(x)

    with arcpy.da.UpdateCursor(tb_near, ["CODIGO_PENDIENTE", "CODIGO_COTIZADO", "DISTANCIA"]) as cursorTbpend:
        for rowtb in cursorTbpend:
            
            sqlPendiente = "{}='{}'".format(CODIGO, rowtb[0])
            x1, y1 = [m for m in arcpy.da.SearchCursor(featurePoint, ["SHAPE@X", "SHAPE@Y"], sqlPendiente)][0]

            sqlCotizado = "{}='{}'".format(CODIGO, rowtb[1])
            x2, y2 = [n for n in arcpy.da.SearchCursor(cotizado, ["SHAPE@X", "SHAPE@Y"], sqlCotizado)][0]

            rowtb[2] = extraerDistancia(x1, y1, x2, y2)
            cursorTbpend.updateRow(rowtb)

    return tb_near
    
def extraerDistancia(x1, y1, x2, y2):
    return round(math.sqrt((pow(x1 - x2, 2) + pow(y1 - y2, 2))) * 111110, 1)

def tabla2csv(tabla, output_csv, csv_delimiter):
    with open(os.path.join(ws, output_csv), 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=csv_delimiter)
        fld_names = [x.name for x in arcpy.ListFields(tabla)]
        writer.writerow(fld_names)
        with arcpy.da.SearchCursor(tabla, fld_names) as cursor:
            for row in cursor:
                writer.writerow(row)
        csv_file.close()

def main():
    cotizados = leerCsv(TB_COTIZADOS)
    pendientes = leerCsv(TB_PENDIENTES)

    bufferPendiente = buffer(pendientes, 150, "pendiente")
    tabla = spatialAnalysis(bufferPendiente, pendientes, cotizados, 500)
    tabla2csv(tabla, "Tabla_resumen.csv", ",")

if __name__ == '__main__':
    main()
    print "\a"
