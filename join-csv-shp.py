import arcpy

# Define input paths of csv and shp file
csv_path = "C:/path/to/your/csv.csv"
shp_path = "C:/path/to/your/shapefile.shp"

# Define field being joined for csv and shp file
join_field_csv = "FAA ID"  # Field in CSV to join on
join_field_shp = "FAA ID"  # Field in Shapefile to join on

# Perform the join 
arcpy.Join_management(
    input_data=shp_path, 
    join_data=csv_path, 
    join_field=join_field_csv, 
    target_field=join_field_shp
)