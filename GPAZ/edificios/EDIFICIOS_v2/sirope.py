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
        with arcpy.da.SearchCursor(self.ly_taps, ["SHAPE@X", "SHAPE@Y"]) as sCur: # Cambiar los campos de ambos
            with arcpy.da.InsertCursor(pathpuntos, ["SHAPE@X", "SHAPE@Y"]) as iCur: # Cambiar los campos de ambos
                for row in sCur:
                    iCur.insertRow(row)

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
        # llenar a los taps (puntos)
        # Jalar los atributos de la capa ****
        # distritos
        # sectores
        pass

    def main(self):
        if os.path.exists(self.workspace) == False:
            os.mkdir(self.workspace)
        self.create_gdb()
        self.llenar_ly_taps()
        self.create_building_area()
        self.create_kmls()
        self.delete_schema()

if __name__ == '__main__':
    poo = sirope()
    poo.main()
