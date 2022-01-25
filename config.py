import os
import arcpy
import utility

log_file = r"\\besfile1\ASM_AssetMgmt\Projects\Lateral_Failure_Cohorts\master_lateral"
log_obj = utility.Logger(log_file)
log_obj.info("MASTER LATERAL PREP - Starting Config".format())

master_output_gdb = r"\\besfile1\ASM_AssetMgmt\Projects\Lateral_Failure_Cohorts\master_lateral.gdb"

connections = r"\\oberon\grp117\DAshney\Scripts\connections"

EGH_PUBLIC = os.path.join(connections, "egh_public on gisdb1.rose.portland.local.sde")
BESGEORPT_TEST = os.path.join(connections, "BESDBTEST1.BESGEORPT.OSA.sde")

collection_lines = EGH_PUBLIC + r"\EGH_Public.ARCMAP_ADMIN.collection_lines_bes_pdx"
taxlots = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.taxlots_pdx"
tv_obs_lines = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.collection_tvobs_line_bes_pdx"

# move WOs source to PROD - revise WO views to combine into one or get an alternate created for this - include missing fields that are in Hansen but not in mapped - verify with Joe/Grant that query is what we want
WOs = arcpy.MakeQueryLayer_management(BESGEORPT_TEST, "WOs",
                                      "SELECT OID, DCA_ID, OWNER1, SITEADDR, PROPERTYID, TLID, COMPKEY, MODBY, DISTRICT, WO, ACTCODE, UNITID, UNITID2, INITDTTM, STARTDTTM,"
                                      " SCHEDDTTM, PRI, PROB, COMPFLAG, STRUCTURAL_RATING, STRUCTURALSCORE, SHAPE_STArea__, SHAPE_STLength__, STATUS, Shape "
                                      "from BESGEORPT.GIS.V_WOS_COMBINED_COPY20211006 WHERE ACTCODE in ('LNRLAT','R/RLAT')", "OID")

mains = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\pipes", "LAYER_GROUP not in ('LATERALS', 'INLETS') AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%'")
laterals = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\laterals", "LAYER_GROUP = 'LATERALS' AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%'")
roots = arcpy.MakeFeatureLayer_management(tv_obs_lines, r"in_memory\roots", "OBDESC = 'ROOTS'")

WOs_copy = arcpy.CopyFeatures_management(WOs, r"in_memory\WOs_copy")
mains_copy = arcpy.CopyFeatures_management(mains, r"in_memory\mains_copy")
laterals_copy = arcpy.CopyFeatures_management(laterals, r"in_memory\laterals_copy")
master_laterals = arcpy.CopyFeatures_management(laterals, r"in_memory\master_laterals")
roots_copy = arcpy.CopyFeatures_management(roots, r"in_memory\roots_copy")

mains_field_list = ['UNITID', 'COMPKEY', 'GLOBALID', 'SERVSTAT', 'FRM_DEPTH', 'TO_DEPTH', 'PIPESIZE', 'MATERIAL', 'JobNo', 'Install_Date', 'LAYER_GROUP', 'SYMBOL_GROUP', 'DETAIL_SYMBOL']
laterals_field_list = ['UNITID', 'COMPKEY', 'GLOBALID', 'OWNRSHIP', 'SERVSTAT', 'SRVY_LEN', 'PIPESIZE', 'MATERIAL', 'JobNo', 'DATA_SRC', 'Install_Date', 'LAYER_GROUP', 'SYMBOL_GROUP', 'DETAIL_SYMBOL', 'Address', 'Lateral_Depth']
WOs_field_list = ['DCA_ID', 'WO', 'COMPKEY', 'PROPERTYID', 'STATUS', 'ACTCODE', 'PROB', 'INITDTTM', 'STARTDTTM', 'SCHEDDTTM']
taxlot_field_list = ['PROPERTYID', 'YEARBUILT','LANDUSE']
TV_obs_field_list = ['COMPKEY', 'OBDEGREE', 'OBRATING']

prepared_mains = utility.prepare_fields(mains, mains_field_list, "Main_")
print utility.get_field_names(prepared_mains)
print arcpy.GetCount_management(prepared_mains)

prepared_laterals = utility.prepare_fields(laterals, laterals_field_list, "Lateral_")
print utility.get_field_names(prepared_laterals)
print arcpy.GetCount_management(prepared_laterals)

prepared_WOs = utility.prepare_fields(WOs, WOs_field_list, "WO_")
print utility.get_field_names(prepared_WOs)
print arcpy.GetCount_management(prepared_WOs)

prepared_taxlots = utility.prepare_fields(taxlots, taxlot_field_list, "TL_")
print utility.get_field_names(prepared_taxlots)
print arcpy.GetCount_management(prepared_taxlots)

prepared_tv_obs = utility.prepare_fields(tv_obs_lines, TV_obs_field_list, "TVObs_")
print utility.get_field_names(prepared_tv_obs)
print arcpy.GetCount_management(prepared_tv_obs)

# creates "empty" laterals with only ID - to append all other fields onto
prepared_master_laterals = utility.delete_fields(master_laterals, ["Lateral_GLOBALID"])

log_obj.info("Config Complete".format())