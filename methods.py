import arcpy
import config
import utility

log_obj = utility.Logger(config.log_file)
log_obj.info("MASTER LATERAL PREP - starting Main".format())

log_obj.info("Adding main fields".format())
lateral_vertices = arcpy.FeatureVerticesToPoints_management(config.laterals_copy, "in_memory/lateral_vertices", "BOTH_ENDS")
vertices_mains_sj = arcpy.SpatialJoin_analysis(lateral_vertices, config.mains_copy, "in_memory/vertices_mains_sj", "JOIN_ONE_TO_MANY", "KEEP_COMMON", "#", "INTERSECT", 0.5)
join_field = "Lateral_GLOBALID"
arcpy.JoinField_management(config.master_laterals, join_field, vertices_mains_sj, join_field, utility.prepare_renamed_dict(config.laterals_field_list).values())
print utility.get_field_names(config.master_laterals)

log_obj.info("MASTER LATERAL PREP COMPLETE".format())