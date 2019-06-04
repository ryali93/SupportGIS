#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arcpy, os
from datetime import datetime
import math
import numpy as np

startTime = datetime.now()
print startTime

arcpy.env.overwriteOutput = True

BASE_DIR    = os.path.abspath(os.path.join(__file__, '..'))
GDB         = os.path.join(BASE_DIR, 'Parametros.gdb')
cuenca      = os.path.join(GDB, 'GPO_PM_Cuenca')
redhidrica  = os.path.join(GDB, 'GPL_PM_RedHidrica')
dem         = os.path.join(BASE_DIR, 'dem.tif')

class Parameters(object):
    def __init__(self):
        self.area = [x[0] for x in arcpy.da.SearchCursor(cuenca, ["AREA"])][0]
        self.perimetro = [x[0] for x in arcpy.da.SearchCursor(cuenca, ["PERIMETRO"])][0]
        self.scratch = arcpy.env.scratchGDB
        self.scratchFolder = arcpy.env.scratchFolder

    def area_1(self):
        return self.area

    def coefCompacidad_2(self):
        kc = self.perimetro / (2*math.sqrt(math.pi*self.area))
        return kc

    def factorForma_3(self):
        sql = "RPRIN = 1"
        longrio = sum([x[0] for x in arcpy.da.SearchCursor(redhidrica, ["RPRIN"], sql, arcpy.SpatialReference(32717))])
        return longrio

    def ordenRio_4(self):
        ordenRio = max([x[0] for x in arcpy.da.SearchCursor(redhidrica, ["grid_code"])])
        return ordenRio

    def densDrenaje_5(self):
        sql = ""
        # sql = "RPRIN = 1" # Si solo es el rio principal
        longTotalrio = sum([x[0] for x in arcpy.da.SearchCursor(redhidrica, ["RPRIN"], sql, arcpy.SpatialReference(32717))])
        dd = longTotalrio/self.area
        return dd

    def extEsc_6(self):
        sql = ""
        # sql = "RPRIN = 1" # Si solo es el rio principal
        longrio = sum([x[0] for x in arcpy.da.SearchCursor(redhidrica, ["RPRIN"], sql, arcpy.SpatialReference(32717))])
        es = self.area/4*longrio
        return es

    def freqRio_7(self):
        dissol = arcpy.Dissolve_management(in_features=redhidrica, 
            out_feature_class=os.path.join(self.scratchFolder, "temp1"), 
            dissolve_field="grid_code")
        mp = arcpy.MultipartToSinglepart_management(dissol, "in_memory\\multipart")
        NTc = int(arcpy.GetCount_management(mp).getOutput(0))
        fr = NTc/self.area
        return fr

    def rect_equiv_11(self):
        Lmayor = (self.perimetro/4)+math.sqrt((self.perimetro**2/16)-self.area)
        Lmenor = (self.perimetro/4)-math.sqrt((self.perimetro**2/16)-self.area)
        return [Lmayor, Lmenor]

    def coef_torrenc_16(self):
        sql = "grid_code = 1"
        N1 = len([x[0] for x in arcpy.da.SearchCursor(redhidrica, ["grid_code"], sql)])
        Ct = N1/self.area
        return Ct


    def main(self):
        temp = self.area_1()
        print "1) area: " + str(round(temp, 2))
        temp = self.coefCompacidad_2()
        print "2) Coeficiente de compacidad: " + str(round(temp, 2))
        temp = self.factorForma_3()
        print "3) Factor Forma: " + str(round(temp, 2))
        temp = self.ordenRio_4()
        print "4) Orden de rios: " + str(round(temp, 2))
        temp = self.densDrenaje_5()
        print "5) Densidad de drenaje: " + str(round(temp, 2))
        temp = self.extEsc_6()
        print "6) Extension media de esc. superficial: " + str(round(temp, 2))
        temp = self.freqRio_7()
        print "7) Frecuencia de rio: " + str(round(temp, 2))
        temp = self.rect_equiv_11()
        print "11) Rectangulo equivalente: " + "\n" + "Lado mayor: " + str(round(temp[0],2)) + "\n" + "Lado menor: " + str(round(temp[1],2)) 
        temp = self.coef_torrenc_16()
        print "16) Coeficiente de torrencialidad: " + str(round(temp, 2))

if __name__ == "__main__":
    poo = Parameters()
    poo.main()

totalTime = datetime.now() - startTime
print totalTime
