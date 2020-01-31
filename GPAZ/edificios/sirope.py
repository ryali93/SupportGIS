#!/usr/bin/env python
# coding: utf-8
import arcpy, os
import time
from datetime import datetime

arcpy.env.overwriteOutput = True

now = datetime.now()
arcpy.AddMessage(now)

contrasena = '987123'
BASE_DIR = os.path.dirname(__file__)
GDB = os.path.join(BASE_DIR, 'BASE.gdb')
TABLA = os.path.join(BASE_DIR, 'Registrar_Edificios.csv')

class sirope(object):
    def __init__(self):
        self.gdb = GDB
        self.tabla = TABLA
        self.workspace = r"C:/EDIFICIOS"
        self.nameGDB = "Edificios"
        self.scratch = arcpy.env.scratchGDB

    def create_gdb(self):
        fecha = time.strftime('%d%b%y')
        hora = time.strftime('%H%M%S')
        name_file = "Edificios_SIROPE-{}-{}".format(fecha, hora)
        folder = arcpy.CreateFolder_management(self.workspace, name_file)
        self.pathfolder = os.path.join(self.workspace, name_file)
        arcpy.CreateFileGDB_management(folder, self.nameGDB, "10.0")
        self.pathgdb = os.path.join(self.workspace, name_file, self.nameGDB + ".gdb")

    def llenar_ly_taps(self):
        pathpuntos = os.path.join(self.pathgdb, "ly_taps")
        arcpy.CopyFeatures_management(os.path.join(self.gdb, "ly_taps"), pathpuntos)
        ly_taps = arcpy.MakeXYEventLayer_management(self.tabla, "X", "Y", "in_memory\\tabla_tmp", arcpy.SpatialReference(4326))
        self.ly_taps = arcpy.CopyFeatures_management(ly_taps, os.path.join(self.scratch, "ly_taps"))

        fields_pathpuntos = ["MTREFER", "COMENTARIO", "COD_TAP", "MTDESDIR", "MTNUMERO", "MTPISO"] # "MTTIPO"
        fields_ly_taps = ["ITEM_PLAN", "CTO_SIROPE", "CTO_GIS_CMS", "DIRECCION", "NUMERO", "PISO"] # "TIPO"

        with arcpy.da.SearchCursor(self.ly_taps, ["SHAPE@X", "SHAPE@Y"] + fields_ly_taps) as sCur:
            with arcpy.da.InsertCursor(pathpuntos, ["SHAPE@X", "SHAPE@Y"] + fields_pathpuntos) as iCur:
                for row in sCur:
                    iCur.insertRow(row)

        print("COD_TAP - MTCODNOD - MTTIPTRO - MTTRONCAL - MTEXTLIN - MTTAP - MTNUMPLA")
        i = 0
        with arcpy.da.UpdateCursor(pathpuntos, ["SHAPE@X", "SHAPE@Y", "COD_TAP", "MTCODNOD", "MTTIPTRO", "MTTRONCAL", "MTEXTLIN", "MTTAP", "MTNUMPLA"]) as cursor:
            for x in cursor:
                i += 1
                if x[2] != None:
                    if len(x[2]) > 9:
                        x[3] = x[2][0:2]
                        x[4] = x[2][2]
                        x[5] = x[2][3:6]
                        x[6] = x[2][6:8]
                        x[7] = x[2][8:10]
                        x[8] = x[4] + x[5]
                    else:
                        print("el indice {} no tiene la cantidad de caracteres necesaria".format(i))
                else:
                    print("el indice {} no tiene datos".format(i))
                cursor.updateRow(x)

        print("MTDESDIR - MTTIPVIA - MTTIPO - MTPISO")
        i = 0
        with arcpy.da.UpdateCursor(pathpuntos, ["SHAPE@X", "SHAPE@Y", "MTDESDIR", "MTTIPVIA", "MTTIPO", "MTPISO"]) as cursor:
            for x in cursor:
                i += 1
                mtdesdir = x[2]
                if mtdesdir != None:
                    if len(mtdesdir) > 4:
                        x[3] = mtdesdir[0:2]
                        x[2] = mtdesdir[4:]
                    else:
                        print("el indice {} no tiene la cantidad de caracteres necesaria".format(i))
                else:
                    print("el indice {} no tiene datos".format(i))
                if x[4] != None:
                    if len(x[4]) > 4:
                        x[4] = "B" if x[4][0] == "P" else x[4][0]
                        x[5] = x[4][-2:]
                    else:
                        print("el indice {} no tiene la cantidad de caracteres necesaria".format(i))
                else:
                    print("el indice {} no tiene datos".format(i))
                cursor.updateRow(x)

        print("NUMCOO_X - NUMCOO_Y - MTIMPEDA - MTNUMBOR - MTCNTBORLBR - MTCNTBOROCU - NRO_POSTE")
        with arcpy.da.UpdateCursor(pathpuntos, ["SHAPE@X", "SHAPE@Y", "NUMCOO_X", "NUMCOO_Y", "MTIMPEDA", "MTNUMBOR", "MTCNTBORLBR", "MTCNTBOROCU", "NRO_POSTE"]) as cursor:
            for x in cursor:
                x[2] = x[0]
                x[3] = x[1]
                x[4] = "99"
                x[5] = "08"
                x[6] = "8"
                x[7] = "0"
                x[8] = "0"
                cursor.updateRow(x)

    def create_building_area(self):
        ctos_buffer = arcpy.Buffer_analysis(self.ly_taps, "in_memory\\ctos_buffer", "10 Meters", "FULL", "ROUND")
        edificio_pol = arcpy.FeatureEnvelopeToPolygon_management(ctos_buffer, "in_memory\\edificio_pol", "SINGLEPART")
        self.edificio_area = arcpy.Dissolve_management(edificio_pol, os.path.join(self.pathgdb, "edificio_area"), '''"ITEM_PLAN"''')

    def create_kmls(self):
        print(os.path.join(self.pathfolder, "CTOs_K.kmz"))
        CTOs_lyr = arcpy.MakeFeatureLayer_management(self.ly_taps, "CTOs_mfl")
        Edificio_Area_lyr = arcpy.MakeFeatureLayer_management(self.edificio_area, "Edificio_Area_mfl")
        arcpy.LayerToKML_conversion(CTOs_lyr, os.path.join(self.pathfolder, "CTOs_K.kmz"))
        arcpy.LayerToKML_conversion(Edificio_Area_lyr, os.path.join(self.pathfolder, "Edificio_Area_K.kmz"))

    def delete_schema(self):
        os.remove(os.path.join(BASE_DIR, "schema.ini"))

    def llenar_spatialjoin(self):
        pathpuntos = os.path.join(self.pathgdb, "ly_taps")
        tap_sector = arcpy.SpatialJoin_analysis(pathpuntos, os.path.join(GDB, "SECTOR"), "in_memory\\tap_sector", "JOIN_ONE_TO_ONE", "KEEP_COMMON")
        tap_ubigeo = arcpy.SpatialJoin_analysis(pathpuntos, os.path.join(GDB, "DISTRITO"), "in_memory\\tap_ubigeo", "JOIN_ONE_TO_ONE", "KEEP_COMMON")

        list_sector = [x for x in arcpy.da.SearchCursor(tap_sector, ["COMENTARIO", "COD_SECT", "COD_URA"])]
        list_ubigeo = [x for x in arcpy.da.SearchCursor(tap_ubigeo, ["COMENTARIO", "UBIGEO"])]

        with arcpy.da.UpdateCursor(pathpuntos, ["COMENTARIO", "MTSECTOR", "MTCODDPT", "MTCODPRO", "MTCODDIS"]) as cursor:
            for x in cursor:
                for y in list_sector:
                    if x[0] == y[0]:
                        x[1] = y[1]
                for y in list_ubigeo:
                    if x[0] == y[0]:
                        x[2] = y[1][0:2]
                        x[3] = y[1][2:4]
                        x[4] = y[1][4:6]
                cursor.updateRow(x)

    def main(self):
        if os.path.exists(self.workspace) == False:
            os.mkdir(self.workspace)
        self.create_gdb()
        self.llenar_ly_taps()
        self.llenar_spatialjoin()
        self.create_building_area()
        self.create_kmls()
        self.delete_schema()

if __name__ == '__main__':
    poo = sirope()
    poo.main()
