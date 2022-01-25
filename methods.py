import arcpy
import config
import utility

log_obj = utility.Logger(config.log_file)
log_obj.info("MASTER LATERAL PREP - starting main".format())

log_obj.info("Adding main fields".format())
lateral_vertices = arcpy.FeatureVerticesToPoints_management(config.prepared_laterals, "in_memory/lateral_vertices", "BOTH_ENDS")
vertices_mains_sj = arcpy.SpatialJoin_analysis(lateral_vertices, config.prepared_mains, "in_memory/vertices_mains_sj", "JOIN_ONE_TO_MANY", "KEEP_COMMON", "#", "INTERSECT", 0.5)
join_field = "Lateral_GLOBALID"
arcpy.JoinField_management(config.master_laterals, join_field, vertices_mains_sj, join_field, config.renamed_laterals_field_dict.values())
print utility.get_field_names(config.master_laterals)

log_obj.info("MASTER LATERAL PREP COMPLETE".format())