#!/usr/bin/env python
# coding: utf-8

import arcpy
import os
import time

# Statics
BASE_DIR = os.path.dirname(__file__)
CONN = os.path.join(BASE_DIR, "conn.sde")

# Parameters
name_gdb = 'BACKUP.gdb' # Modify the name of the backup geodatabase
workspace = r'C:\CLUSTERS' # Modifiy your out path
datasets = ['DATA_EDIT.DS_DGAR', 'DATA_EDIT.DS_DRME'] # Modify your feature datasets

arcpy.env.workspace = CONN

# print os.path.join(workspace, name_gdb)
def create_gdb(folder):
    fecha = time.strftime('%d%b%y')
    hora = time.strftime('%H%M%S')
    nameFile = "BACKUP-{}-{}".format(fecha, hora)
    folder_gdb = arcpy.CreateFolder_management(folder, nameFile).getOutput(0)
    path_gdb = arcpy.CreateFileGDB_management(folder_gdb, name_gdb, "10.0")
    return os.path.join(folder, nameFile, name_gdb)

def create_datasets(gdb, datasets):
    for ds in [x.split(".")[-1] for x in datasets]:
        arcpy.CreateFeatureDataset_management(gdb, ds)

def copy_features(sde, gdb, datasets):
    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            path_sde = os.path.join(sde, ds, fc)
            path_gdb = os.path.join(gdb, ds.split(".")[-1])
            arcpy.FeatureClassToFeatureClass_conversion(path_sde, path_gdb, fc.split(".")[-1])

def main():
    if os.path.exists(workspace)==False: os.mkdir(workspace)
    path_gdb = create_gdb(workspace)
    create_datasets(path_gdb, datasets)
    copy_features(CONN, path_gdb, datasets)

if __name__ == '__main__':
    main()
