import random

fc      = "ALA"  # Cambiar por el nombre del campo
nrandom = 30	 # Cambiar por la cantidad de objetos seleccionados

cantidad = int(str(arcpy.GetCount_management(fc)))
list_oid = range(1, cantidad+1)
ran_values = random.sample(list_oid, nrandom)
str_ranvalues = str(ran_values)
str_select = "("+ str_ranvalues[1:-1] +")"
oid_fieldname = arcpy.Describe(fc).OIDFieldName
sql = oid_fieldname +  ' IN ' + str_select
arcpy.SelectLayerByAttribute_management(fc, "NEW_SELECTION", sql)