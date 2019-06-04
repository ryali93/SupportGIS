import arcpy, os
import math
import pythonaddins
from datetime import datetime

now = datetime.now()
arcpy.AddMessage(now)

arcpy.env.overwriteOutput = True

Fecha = datetime(2019, 6, 15)

#Carpeta = arcpy.GetParameterAsText(0)
#GDB_E = arcpy.GetParameterAsText(1)
Cod_Expression = arcpy.GetParameterAsText(3)
Contrasena = arcpy.GetParameterAsText(4)

EDI_KMZ     = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\FTTH\18-0111100100\18-0111100100 AV. DEL PARQUE SUR 475-479 SBG054.kmz'
DISTRITO    = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\BASE\EDIFICIOS.gdb\DISTRITO'
SECTOR      = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\BASE\EDIFICIOS.gdb\SECTOR'
CALLE       = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\BASE\EDIFICIOS.gdb\CALLE'
ly_taps_    = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\BASE\EDIFICIOS.gdb\ly_taps'
ly_areain_  = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\BASE\EDIFICIOS.gdb\ly_areain'
ly_troba_   = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\BASE\EDIFICIOS.gdb\ly_troba'
ly_nodo_    = r'D:\DESPLIEGUE_AMPLIACIONES\2_EDIFICIOS\BASE\EDIFICIOS.gdb\ly_nodo'
ly_taps     = r'C:\EDIFICIOS\CARPETA\GDB_E.gdb\ly_taps'
ly_areain   = r'C:\EDIFICIOS\CARPETA\GDB_E.gdb\ly_areain'
ly_troba    = r'C:\EDIFICIOS\CARPETA\GDB_E.gdb\ly_troba'
ly_nodo     = r'C:\EDIFICIOS\CARPETA\GDB_E.gdb\ly_nodo'
CodExpression = "!PRU001![-2:]"

def process():
    arcpy.CreateFolder_management(out_folder_path="C:/", out_name="EDIFICIOS")
    arcpy.CreateFileGDB_management(out_folder_path="C:/EDIFICIOS", out_name="GDB", out_version="CURRENT")
    arcpy.CreateFolder_management(out_folder_path="C:/EDIFICIOS", out_name="CARPETA")
    arcpy.CreateFileGDB_management(out_folder_path="C:/EDIFICIOS/CARPETA", out_name="GDB_E", out_version="CURRENT")

    #COPIAR PLANTILLA#
    arcpy.Copy_management(ly_taps_, out_data="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_taps", data_type="FeatureClass")
    arcpy.Copy_management(ly_areain_, out_data="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_areain", data_type="FeatureClass")
    arcpy.Copy_management(ly_troba_, out_data="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_troba", data_type="FeatureClass")
    arcpy.Copy_management(ly_nodo_, out_data="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_nodo", data_type="FeatureClass")

    #KMZ A FEATURE#
    EDIFICIO_KMZ = arcpy.KMLToLayer_conversion(EDI_KMZ, output_folder="C:/EDIFICIOS", output_data="EDIFICIO_KMZ", include_groundoverlay="NO_GROUNDOVERLAY")
    arcpy.AddField_management(in_table="C:/EDIFICIOS/EDIFICIO_KMZ.gdb/Points", field_name="COD_TAP", field_type="TEXT")
    arcpy.CalculateField_management(in_table="C:/EDIFICIOS/EDIFICIO_KMZ.gdb/Points", field="COD_TAP", expression="[Name]", expression_type="VB")

    #RELLENAR PLANTILLAS#
    arcpy.Append_management(inputs="C:/EDIFICIOS/EDIFICIO_KMZ.gdb/Points", target="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_taps", schema_type="NO_TEST")
    arcpy.Append_management(inputs="C:/EDIFICIOS/EDIFICIO_KMZ.gdb/Polygons", target="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_troba", schema_type="NO_TEST")
    arcpy.Append_management(inputs="C:/EDIFICIOS/EDIFICIO_KMZ.gdb/Polygons", target="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_areain", schema_type="NO_TEST")
    arcpy.Append_management(inputs="C:/EDIFICIOS/EDIFICIO_KMZ.gdb/Polygons", target="C:/EDIFICIOS/CARPETA/GDB_E.gdb/ly_nodo", schema_type="NO_TEST")

    #RELLENAR CAMPOS CODIGO DE TROBA#
    arcpy.CalculateField_management(ly_taps, "MTCODNOD", CodExpression, "PYTHON_9.3")



def main():
    if Fecha < now:
        arcpy.AddMessage("***El Presente Script ha caducado, Por favor Contactarse con el encargado TdP***")
        pythonaddins.MessageBox("***El Presente Script ha caducado, Por favor Contactarse con el encargado TdP***", "Mensaje:")
    else:
        process()
main()
