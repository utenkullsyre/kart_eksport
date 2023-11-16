import arcpy


def get_feature_point(geom, north_point=False):
    if geom.type == "point":
        arcpy.AddMessage("Input geometry is a point.")
        return geom
    elif geom.type in ["polygon", "polyline"]:
        if geom.type == "polygon":
            arcpy.AddMessage("Input geometry is a polygon.")
            # Return northernmost point if user has chosen that, else return centroid
            feature_point = max(geom.exterior, key=lambda pt: pt.Y) if north_point else geom.centroid
        else:
            arcpy.AddMessage("Input geometry is a polyline.")
            feature_point = max((pt for part in geom for pt in part),
                                key=lambda pt: pt.Y) if north_point else geom.centroid

        return arcpy.Point(feature_point.X, feature_point.Y)
    else:
        arcpy.AddMessage("Input geometry type is not recognized.")
        return None


def add_number_field(layers):
    for layer in layers:
        field_name = "nummerering"
        if field_name not in [field.name for field in arcpy.ListFields(layer)]:
            arcpy.AddField_management(layer, field_name, "INTEGER")


def find_nearest_points_along_line(polyline, input_layers, north_point, start_number):
    # Create a geometry object for the polyline
    # polyline_geom = arcpy.Polyline(arcpy.Array([arcpy.Point(*coords) for coords in polyline]))
    polyline_geom = polyline
    # Create a list to store information about each point
    points_info = []

    # Iterate through input layers
    for input_layer in input_layers:
        # Create a search cursor for the input layer
        fields = ["SHAPE@", "OID@"]  # Include any additional fields you need
        with arcpy.da.SearchCursor(input_layer, fields) as cursor:
            for row in cursor:
                geom, oid = row[0], row[1]
                feature_point = get_feature_point(geom, north_point)

                if feature_point:
                    points_info.append({"lag": input_layer, "oid": oid, "pkt_geom": feature_point})

    for pkt in points_info:
        resultat = geometri.queryPointAndDistance(pkt["pkt_geom"])
        pkt["avstand"] = resultat[1]
    # Sort the list by distance
    points_info.sort(key=lambda obj: obj["avstand"])

    # Start an edit session. Must provide the workspace.
    p = arcpy.mp.ArcGISProject("CURRENT")

    edit = arcpy.da.Editor(p.defaultGeodatabase)

    # Edit session is started without an undo/redo stack for versioned data

    # Set multiuser_mode to False if working with unversioned enterprise gdb data
    edit.startEditing(with_undo=False, multiuser_mode=True)

    # Iterate over points_info and update the features in their respective layers
    for index, pkt in enumerate(points_info):
        # Update the field with the index along the line
        with arcpy.da.UpdateCursor(pkt["lag"], ["OID@", "nummerering"]) as update_cursor:
            for update_row in update_cursor:
                if update_row[0] == pkt["oid"]:
                    update_row[1] = index + start_number
                    update_cursor.updateRow(update_row)
                    break

    # Stop the edit operation.
    edit.stopOperation()

    # Stop the edit session and save the changes
    edit.stopEditing(save_changes=True)


if __name__ == "__main__":
    # Get input parameters
    param0 = arcpy.GetParameter(0)
    geometri = ""
    fields = ["SHAPE@"]
    with arcpy.da.SearchCursor(param0, fields) as cursor:
        for row in cursor:
            geometri = row[0]
            break  # Break after processing the first feature
    lagre_pkt = arcpy.GetParameter(1)
    start_nr = arcpy.GetParameter(2)
    input_layers = arcpy.GetParameter(3)  # MultiValue parameter for input layers
    north_point = arcpy.GetParameter(4)
    add_number_field(input_layers)

    # Call the function to find nearest points along the line and store the index
    find_nearest_points_along_line(geometri, input_layers, north_point, start_nr)
    if not lagre_pkt:
        arcpy.AddMessage([geometri, input_layers, param0.name])
        arcpy.Delete_management(param0.name)
