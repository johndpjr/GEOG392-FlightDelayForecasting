import arcpy
import requests

folder_path = r"C:\path\to\your\folder"
gdb_name = "my_geodatabase.gdb"

arcpy.CreateFileGDB_management(folder_path, gdb_name)

gdb_path = f"{folder_path}\\{gdb_name}"

feature_class = arcpy.CreateFeatureclass_management(gdb_path, "real_time_data", "POINT")

api_url = "https://example.com/api/real-time-data"
response = requests.get(api_url)
data = response.json()

with arcpy.da.InsertCursor(feature_class, ["SHAPE@XY", "Field1", "Field2"]) as cursor:
    for record in data['features']:
        x, y = record['geometry']['coordinates']  
        field1 = record['properties']['field1']   
        field2 = record['properties']['field2']   
        cursor.insertRow([(x, y), field1, field2])

print("Data inserted successfully.")
