import arcpy
import utility
import config
#import config_for_testing as config
import os

arcpy.env.overwriteOutput = True

log_obj = utility.Logger(config.log_file)
log_obj.info("MASTER LATERAL PREP - starting Main".format())

log_obj.info("ADDING MAINLINE FIELDS TO MASTER LATERALS".format())

lateral_vertices = arcpy.FeatureVerticesToPoints_management(config.master_laterals, "in_memory/lateral_vertices", "BOTH_ENDS") #both ends because laterals can be drawn backwards
lateral_to_main_tolerance_ft = 10
vertices_mains_sj = arcpy.SpatialJoin_analysis(lateral_vertices, config.mains_copy, "in_memory/vertices_mains_sj", "JOIN_ONE_TO_ONE", "KEEP_COMMON", "#", "CLOSEST", lateral_to_main_tolerance_ft)

lateral_join_field = "Lateral_GLOBALID" #check - how much confidence in GLOBALID?
main_fields = utility.prepare_renamed_dict(config.mains_field_list, "Main_").values()
join_field_list = main_fields
#join_field_list.remove("Lateral_GLOBALID") #remove from join fields or else you get "Lateral_GLOBALID_1"
#join_field_list.remove("Lateral_COMPKEY") #ditto
arcpy.JoinField_management(config.master_laterals, lateral_join_field, vertices_mains_sj, lateral_join_field, join_field_list)
print utility.get_field_names(config.master_laterals)

log_obj.info("ADDING TAXLOT FIELDS TO MASTER LATERALS".format())

log_obj.info("   Converting taxlots to centroid".format())
taxlot_centroid = arcpy.FeatureToPoint_management(config.taxlots_copy, r"in_memory/taxlot_centroid", "INSIDE")
log_obj.info("   Finding the nearest main".format())
centroid_to_main_near_table = arcpy.GenerateNearTable_analysis(taxlot_centroid, config.mains_copy, r"in_memory/centroid_to_main_near_table", '100 Feet', "LOCATION", "NO_ANGLE", "CLOSEST")
log_obj.info("   Converting nearest result to lines".format())
centroid_to_main_line = arcpy.XYToLine_management(centroid_to_main_near_table, r"in_memory/centroid_to_main_line", "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "IN_FID", config.projection_file)
#centroid_to_main_line = arcpy.XYToLine_management(centroid_to_main_near_table, os.path.join(config.working_gdb,"centroid_to_main_line"), "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "IN_FID", config.projection_file)

log_obj.info("   Buffering mains".format())
mains_buff_25ft = arcpy.Buffer_analysis(config.mains_copy, r"in_memory/mains_buff_25ft", "25 Feet", "FULL", "ROUND", "ALL")
#mains_buff_25ft = arcpy.Buffer_analysis(config.mains_copy, r"c:\temp_work\lateral_cohort_working.gdb\mains_buff_25ft", "25 Feet", "FULL", "ROUND", "ALL")
log_obj.info("   Shortening near lines".format())
centroid_to_main_erase = arcpy.Erase_analysis(centroid_to_main_line, mains_buff_25ft, r"in_memory/centroid_to_main_erase")
#centroid_to_main_erase = arcpy.Erase_analysis(centroid_to_main_line, mains_buff_25ft, os.path.join(config.working_gdb, "centroid_to_main_erase"))
log_obj.info("   Converting near lines to their endpoints".format())
centroid_to_main_endpoint = arcpy.FeatureVerticesToPoints_management(centroid_to_main_erase, r"in_memory/centroid_to_main_endpoint", "END")
log_obj.info("   Finding the nearest lateral to the endpoint".format())
endpoint_to_lateral_near_table = arcpy.GenerateNearTable_analysis(centroid_to_main_endpoint, config.laterals_copy, r"in_memory/endpoint_to_lateral_near_table", "30 Feet", "LOCATION", "NO_ANGLE", "CLOSEST")
#endpoint_to_lateral_near_table = arcpy.GenerateNearTable_analysis(centroid_to_main_endpoint, config.master_laterals, os.path.join(config.working_gdb, "endpoint_to_lateral_near_table"), "30 Feet", "LOCATION", "NO_ANGLE", "CLOSEST")

taxlot_join_field_list = utility.prepare_renamed_dict(config.taxlot_field_list, "TL_").values()
log_obj.info("   Joining taxlot fields to intermediate table".format())
arcpy.JoinField_management(centroid_to_main_endpoint, "IN_FID", config.taxlots_copy, "OBJECTID", taxlot_join_field_list)
#centroid_to_main_endpoint.OID is the alias not name - not sure why its using the alias here but OBJECTID fails
arcpy.JoinField_management(endpoint_to_lateral_near_table, "IN_FID", centroid_to_main_endpoint, "OID", taxlot_join_field_list)
log_obj.info("   Joining taxlot fields to master laterals".format())
arcpy.JoinField_management(config.master_laterals, "OBJECTID", endpoint_to_lateral_near_table, "NEAR_FID", taxlot_join_field_list)
print utility.get_field_names(config.master_laterals)

log_obj.info("ADDING WORK ORDER FIELDS TO MASTER LATERALS".format())
WO_join_field_list = utility.prepare_renamed_dict(config.WOs_field_list, "WO_").values()
log_obj.info("   Joining WO fields to master_laterals using COMPKEY".format())
arcpy.JoinField_management(config.master_laterals, "Lateral_COMPKEY", config.WOs_copy, "WO_COMPKEY", WO_join_field_list)
print utility.get_field_names(config.master_laterals)
log_obj.info("   Calculating WO fields in master_laterals using PROPERTYID".format())
#utility.get_and_assign_field_values(config.WOs_copy, "WO_PROPERTYID", WO_join_field_list, config.master_laterals,
#                                        "TL_PROPERTYID", WO_join_field_list)
for field in WO_join_field_list:
    log_obj.info("   --- for {}".format(field))
    utility.get_and_assign_field_value(config.WOs_copy, "WO_PROPERTYID", field, config.master_laterals, "TL_PROPERTYID", field)

#log_obj.info("ADDING ROOTS FIELDS TO MASTER LATERALS".format())

#log_obj.info("ADDING LATERL ASSESSMENT FIELDS TO MASTER LATERALS".format())

log_obj.info("Saving master laterals to disk".format())
arcpy.CopyFeatures_management(config.master_laterals, os.path.join(config.master_output_gdb, "master_laterals"))

log_obj.info("MASTER LATERAL PREP COMPLETE".format())