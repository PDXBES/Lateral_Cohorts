import arcpy
import utility
import config

log_obj = utility.Logger(config.log_file)
log_obj.info("MASTER LATERAL PREP - starting Main".format())

log_obj.info("Adding mainline fields".format())

# get mainline attr attached to lateral geom
lateral_vertices = arcpy.FeatureVerticesToPoints_management(config.laterals_copy, "in_memory/lateral_vertices", "BOTH_ENDS")
vertices_mains_sj = arcpy.SpatialJoin_analysis(lateral_vertices, config.mains_copy, "in_memory/vertices_mains_sj", "JOIN_ONE_TO_MANY", "KEEP_COMMON", "#", "INTERSECT", 0.5)

join_field = "Lateral_GLOBALID"
join_field_list = utility.prepare_renamed_dict(config.mains_field_list, "Lateral_").values() + utility.prepare_renamed_dict(config.laterals_field_list, "Main_").values()
arcpy.JoinField_management(config.master_laterals, join_field, vertices_mains_sj, join_field, join_field_list)
print utility.get_field_names(config.master_laterals)

#get taxlot attr attached to lateral geom
TL_centroid = arcpy.FeatureToPoint_management(config.taxlots_copy, r"in_memory/taxlot_centroid", "INSIDE")
near_centroid_to_mainline = arcpy.GenerateNearTable_analysis(TL_centroid, config.mains_copy, r"in_memory/near_centroid_to_mainline", '#', "LOCATION", "NO_ANGLE", "CLOSEST")
centroid_main_line = arcpy.XYToLine_management(near_centroid_to_mainline, r"in_memory/near_centroid_main_line", "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "IN_FID", config.projection_file)

mains_buff_25ft = arcpy.Buffer_analysis(config.mains_copy, r"in_memory/mains_buff_25ft", "25 Feet", "FULL", "ROUND", "ALL")
centroid_main_line_erase = arcpy.Erase_analysis(centroid_main_line, mains_buff_25ft, r"in_memory/centroid_main_line_erase")
centroid_main_line_endpoint = arcpy.FeatureVerticesToPoints_management(centroid_main_line_erase, r"in_memory/centroid_main_line_endpoint", "END")

log_obj.info("MASTER LATERAL PREP COMPLETE".format())