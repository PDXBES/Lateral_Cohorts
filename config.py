import os
import arcpy
import utility
from datetime import datetime

arcpy.env.overwriteOutput = True

print "MASTER LATERAL PREP - Starting Config: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

log_file = r"\\besfile1\ASM_AssetMgmt\Projects\Lateral_Failure_Cohorts\master_lateral"

projection_file = r"\\besfile1\ASM_AssetMgmt\Projects\Lateral_Failure_Cohorts\prj\WKID_2913.prj"

master_output_gdb = r"\\besfile1\ASM_AssetMgmt\Projects\Lateral_Failure_Cohorts\master_lateral.gdb"
working_gdb = r"\\besfile1\ASM_AssetMgmt\Projects\Lateral_Failure_Cohorts\master_lateral_working.gdb"

connections = r"\\besfile1\grp117\DAshney\Scripts\connections"

EGH_PUBLIC = os.path.join(connections, "egh_public on gisdb1.rose.portland.local.sde")
BESGEORPT_TEST = os.path.join(connections, "BESDBTEST1.BESGEORPT.OSA.sde")

collection_lines = EGH_PUBLIC + r"\EGH_Public.ARCMAP_ADMIN.collection_lines_bes_pdx"
taxlots = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.taxlots_pdx"
tv_obs_lines = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.collection_tvobs_line_bes_pdx"
pdx_boundary = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.portland_pdx"
WOs_all = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.COLLECTION_TAXLOTS_BES_ALL_WOS"
#WOs = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.COLLECTION_TAXLOTS_BES_MR_WOS" # will replace query layer

print "MASTER LATERAL PREP -    Subsetting inputs: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

# this will become a standalone table which will no longer require the make query layer
WOs = arcpy.MakeQueryLayer_management(BESGEORPT_TEST, "WOs", "SELECT * from BESGEORPT.GIS.v_WOs_max_INITDTTM", "OBJECTID")

mains = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\pipes", "LAYER_GROUP not in ('LATERALS', 'INLETS') AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%' AND LAYER_GROUP = 'SEWER PIPES'")
laterals = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\laterals", "LAYER_GROUP = 'LATERALS' AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%'")
roots = arcpy.MakeFeatureLayer_management(tv_obs_lines, r"in_memory\roots", "OBDESC = 'ROOTS'")
taxlots_layer = arcpy.MakeFeatureLayer_management(taxlots, r"in_memory\taxlots_layer")

#subset to lots within city boundary
arcpy.SelectLayerByLocation_management(WOs, "HAVE_THEIR_CENTER_IN", pdx_boundary)
arcpy.SelectLayerByLocation_management(taxlots_layer, "HAVE_THEIR_CENTER_IN", pdx_boundary)

print "MASTER LATERAL PREP -    Reading features into memory: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
WOs_copy = arcpy.CopyFeatures_management(WOs, r"in_memory\WOs_copy") # can add DCA_ID here if still needed - hopefully can use OBJECTID
#WOs_copy = arcpy.CopyFeatures_management(WOs, os.path.join(working_gdb, "WOs_copy"))
mains_copy = arcpy.CopyFeatures_management(mains, r"in_memory\mains_copy")
laterals_copy = arcpy.CopyFeatures_management(laterals, r"in_memory\laterals_copy")
taxlots_copy = arcpy.CopyFeatures_management(taxlots_layer, r"in_memory\taxlots_copy")
roots_copy = arcpy.CopyFeatures_management(roots, r"in_memory\roots_copy")

mains_field_list = ['UNITID', 'COMPKEY', 'GLOBALID', 'SERVSTAT', 'FRM_DEPTH', 'TO_DEPTH', 'PIPESIZE', 'MATERIAL', 'JobNo', 'Install_Date', 'LAYER_GROUP', 'SYMBOL_GROUP', 'DETAIL_SYMBOL']
laterals_field_list = ['UNITID', 'COMPKEY', 'GLOBALID', 'OWNRSHIP', 'SERVSTAT', 'SRVY_LEN', 'PIPESIZE', 'MATERIAL', 'JobNo', 'DATA_SRC', 'Install_Date', 'LAYER_GROUP', 'SYMBOL_GROUP', 'DETAIL_SYMBOL', 'Address', 'Lateral_Depth']
WOs_field_list = ['WO', 'COMPKEY', 'PROPERTYID', 'COMPFLAG', 'ACTCODE', 'PROB', 'INITDTTM', 'STARTDTTM', 'SCHEDDTTM', 'COMPDTTM', 'ACTUALPROB', 'FINDING', 'MAINLINE_COMPKEY', 'WO_COMMENTS']
taxlot_field_list = ['PROPERTYID', 'YEARBUILT','LANDUSE', 'SITEADDR']
TV_obs_field_list = ['COMPKEY', 'OBDEGREE', 'OBRATING']

print "MASTER LATERAL PREP -    Preparing fields: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
utility.prepare_fields(mains_copy, mains_field_list, "Main_")
print "Mains..."
print utility.get_field_names(mains_copy)
print arcpy.GetCount_management(mains_copy)

utility.prepare_fields(laterals_copy, laterals_field_list, "Lateral_")
print "Laterals..."
print utility.get_field_names(laterals_copy)
print arcpy.GetCount_management(laterals_copy)

utility.prepare_fields(WOs_copy, WOs_field_list, "WO_")
print "Work Orders..."
print utility.get_field_names(WOs_copy)
print arcpy.GetCount_management(WOs_copy)

utility.prepare_fields(taxlots_copy, taxlot_field_list, "TL_")
print "Taxlots..."
print utility.get_field_names(taxlots_copy)
print arcpy.GetCount_management(taxlots_copy)

utility.prepare_fields(roots_copy, TV_obs_field_list, "Roots_")
print "Roots..."
print utility.get_field_names(roots_copy)
print arcpy.GetCount_management(roots_copy)

# creates "empty" laterals with only ID - to append all other fields onto
print "Master Laterals..."
master_laterals = arcpy.CopyFeatures_management(laterals_copy, r"in_memory\master_laterals")
#master_laterals = arcpy.CopyFeatures_management(laterals_copy, os.path.join(working_gdb, "master_laterals"))
print utility.get_field_names(master_laterals)
print arcpy.GetCount_management(master_laterals)

print "Config Complete: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")