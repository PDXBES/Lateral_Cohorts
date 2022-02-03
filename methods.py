import arcpy
import utility
import config

log_obj = utility.Logger(config.log_file)
log_obj.info("MASTER LATERAL PREP - starting Main".format())

log_obj.info("ADDING MAINLINE FIELDS TO MASTER LATERALS".format())

lateral_vertices = arcpy.FeatureVerticesToPoints_management(config.laterals_copy, "in_memory/lateral_vertices", "BOTH_ENDS") #both ends because laterals can be drawn backwards
vertices_mains_sj = arcpy.SpatialJoin_analysis(lateral_vertices, config.mains_copy, "in_memory/vertices_mains_sj", "JOIN_ONE_TO_MANY", "KEEP_COMMON", "#", "INTERSECT", 0.5)

lateral_join_field = "Lateral_GLOBALID"
lateral_join_field_list = utility.prepare_renamed_dict(config.mains_field_list, "Lateral_").values() + utility.prepare_renamed_dict(config.laterals_field_list, "Main_").values()
arcpy.JoinField_management(config.master_laterals, lateral_join_field, vertices_mains_sj, lateral_join_field, lateral_join_field_list)
print utility.get_field_names(config.master_laterals)

log_obj.info("ADDING TAXLOT FIELDS TO MASTER LATERALS".format())

log_obj.info("   Converting taxlots to centroid".format())
taxlot_centroid = arcpy.FeatureToPoint_management(config.taxlots_copy, r"in_memory/taxlot_centroid", "INSIDE")
log_obj.info("   Finding the nearest main".format())
centroid_to_main_near_table = arcpy.GenerateNearTable_analysis(taxlot_centroid, config.mains_copy, r"in_memory/centroid_to_main_near_table", '100 Feet', "LOCATION", "NO_ANGLE", "CLOSEST")
log_obj.info("   Converting nearest result to lines".format())
centroid_to_main_line = arcpy.XYToLine_management(centroid_to_main_near_table, r"in_memory/centroid_to_main_line", "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "IN_FID", config.projection_file)
#centroid_to_main_line = arcpy.XYToLine_management(centroid_to_main_near_table, r"c:\temp_work\lateral_cohort_working.gdb/centroid_to_main_line", "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "IN_FID", config.projection_file)

log_obj.info("   Buffering mains".format())
mains_buff_25ft = arcpy.Buffer_analysis(config.mains_copy, r"in_memory/mains_buff_25ft", "25 Feet", "FULL", "ROUND", "ALL")
#mains_buff_25ft = arcpy.Buffer_analysis(config.mains_copy, r"c:\temp_work\lateral_cohort_working.gdb\mains_buff_25ft", "25 Feet", "FULL", "ROUND", "ALL")
log_obj.info("   Shortening near lines".format())
centroid_to_main_erase = arcpy.Erase_analysis(centroid_to_main_line, mains_buff_25ft, r"in_memory/centroid_to_main_erase")
log_obj.info("   Converting near lines to their endpoints".format())
centroid_to_main_endpoint = arcpy.FeatureVerticesToPoints_management(centroid_to_main_erase, r"in_memory/centroid_to_main_endpoint", "END")
log_obj.info("   Finding the nearest lateral to the endpoint".format())
endpoint_to_lateral_near_table = arcpy.GenerateNearTable_analysis(centroid_to_main_endpoint, config.laterals_copy, r"in_memory/endpoint_to_lateral_near_table", "30 Feet", "LOCATION", "NO_ANGLE", "CLOSEST")

taxlot_join_field_list = utility.prepare_renamed_dict(config.taxlot_field_list, "TL_").values()
log_obj.info("   Joining taxlot fields to intermediate table".format())
arcpy.JoinField_management(endpoint_to_lateral_near_table, "IN_FID", config.taxlots_copy, "OBJECTID", taxlot_join_field_list)
log_obj.info("   Joining taxlot fields to master laterals".format())
arcpy.JoinField_management(config.master_laterals, "OBJECTID", endpoint_to_lateral_near_table, "NEAR_FID", taxlot_join_field_list)
print utility.get_field_names(config.master_laterals)

log_obj.info("ADDING WORK ORDER FIELDS TO MASTER LATERALS".format())

log_obj.info("MASTER LATERAL PREP COMPLETE".format())