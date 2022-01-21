import arcpy
import config

lateral_vertices = arcpy.FeatureVerticesToPoints_management(config.laterals, "in_memory/lateral_vertices", "BOTH_ENDS")
vertices_mains_sj = arcpy.SpatialJoin_analysis(lateral_vertices, config.mains, "in_memory/vertices_mains_sj", "JOIN_ONE_TO_MANY", "KEEP_COMMON", "#", "INTERSECT", 0.5)
# do join field to attach mainline fields from sj result to laterals (make a copy of laterals - can't attach to original source)