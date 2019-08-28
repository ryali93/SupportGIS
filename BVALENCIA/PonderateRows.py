import arcpy
import pythonaddins

feature = arcpy.GetParameterAsText(0)
fields = arcpy.GetParameterAsText(1).split(";")
fieldPond = [arcpy.GetParameterAsText(2)]

campos = fieldPond + fields

with arcpy.da.UpdateCursor(feature, campos) as cursor:
    for x in cursor:
    	mayor = int(max(x[1:]))
    	x[0] = fields[x[1:].index(mayor)]
    	if mayor == 0:
    		x[0] = ""
        cursor.updateRow(x)

msg = "*"*40+"\n" +"Developed by Geocodery"+"\n" +"Cel: 953527306"+"\n" +"email: Geocodery@gmail.com"+"\n" +"*"*40+"\n"
arcpy.AddMessage(msg)
pythonaddins.MessageBox(msg, 'INFO', 0)  

