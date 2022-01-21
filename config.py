import os
import arcpy
import utility


connections = r"\\oberon\grp117\DAshney\Scripts\connections"

EGH_PUBLIC = os.path.join(connections, "egh_public on gisdb1.rose.portland.local.sde")
BESGEORPT_TEST = os.path.join(connections, "BESDBTEST1.BESGEORPT.OSA.sde")

collection_lines = EGH_PUBLIC + r"\EGH_Public.ARCMAP_ADMIN.collection_lines_bes_pdx"
taxlots = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.taxlots_pdx"
tv_obs_lines = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.collection_tvobs_line_bes_pdx"
# move WOs source to PROD
WOs = arcpy.MakeQueryLayer_management(BESGEORPT_TEST, "WOs", "SELECT MY_ID, OWNER1, SITEADDR, PROPERTYID, TLID, COMPKEY, MODBY, DISTRICT, WO, ACTCODE, UNITID, UNITID2, INITDTTM, STARTDTTM,"
                                                             " SCHEDDTTM, PRI, PROB, COMPFLAG, STRUCTURAL_RATING, STRUCTURALSCORE, SHAPE_STArea__, SHAPE_STLength__, STATUS, Shape "
                                                             "from BESGEORPT.GIS.V_WOS_COMBINED_COPY20211006", "MY_ID")

mains = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\pipes", "LAYER_GROUP not in ('LATERALS', 'INLETS') AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%'")
laterals = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\laterals", "LAYER_GROUP = 'LATERALS' AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%'")
roots = arcpy.MakeFeatureLayer_management(tv_obs_lines, r"in_memory\roots", "OBDESC = 'ROOTS'")

mains_field_list = ['UNITID', 'COMPKEY', 'GLOBALID', 'SERVSTAT', 'FRM_DEPTH', 'TO_DEPTH', 'PIPESIZE', 'MATERIAL', 'JobNo', 'Install_Date', 'LAYER_GROUP', 'SYMBOL_GROUP', 'DETAIL_SYMBOL']
laterals_field_list = ['UNITID', 'COMPKEY', 'GLOBALID', 'OWNRSHIP', 'SERVSTAT', 'SRVY_LEN', 'PIPESIZE', 'MATERIAL', 'JobNo', 'DATA_SRC', 'Install_Date', 'LAYER_GROUP', 'SYMBOL_GROUP', 'DETAIL_SYMBOL', 'Address', 'Lateral_Depth']
WO_field_list = ['MY_ID', 'WO', 'COMPKEY', 'PROPERTYID', 'STATUS', 'ACTCODE', 'PROB', 'INITDTM', 'STARTDTM', 'SCHEDDTM']
taxlot_field_list = ['PROPERTYID', 'YEARBUILT','LANDUSE']
TV_obs_field_list = ['COMPKEY', 'OBDEGREE', 'OBRATING']

renamed_mains_field_dict = utility.prep_renamed_mains_dict(mains_field_list, "Main_")
renamed_laterals_field_dict = utility.prep_renamed_mains_dict(laterals_field_list, "Lateral_")
renamed_WOs_field_dict = utility.prep_renamed_mains_dict(laterals_field_list, "WO_")
renamed_taxlot_field_dict = utility.prep_renamed_mains_dict(taxlot_field_list, "Taxlot_")
renamed_tv_obs_field_dict = utility.prep_renamed_mains_dict(TV_obs_field_list, "TVObs_")

prepared_mains = utility.prepare_fields(mains, renamed_mains_field_dict)
prepared_laterals = utility.prepare_fields(laterals, renamed_laterals_field_dict)
prepared_WOs = utility.prepare_fields(WOs, renamed_WOs_field_dict)
prepared_taxlots = utility.prepare_fields(taxlots, renamed_taxlot_field_dict)
prepared_tv_obs = utility.prepare_fields(tv_obs_lines, renamed_tv_obs_field_dict)

print utility.get_field_names(prepared_mains)
print arcpy.GetCount_management(prepared_mains)
print utility.get_field_names(prepared_laterals)
print arcpy.GetCount_management(prepared_laterals)
print utility.get_field_names(prepared_WOs)
print arcpy.GetCount_management(prepared_WOs)
print utility.get_field_names(prepared_taxlots)
print arcpy.GetCount_management(prepared_taxlots)
print utility.get_field_names(prepared_tv_obs)
print arcpy.GetCount_management(prepared_tv_obs)