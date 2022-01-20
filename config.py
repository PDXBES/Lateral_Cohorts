import os
import arcpy


connections = r"\\oberon\grp117\DAshney\Scripts\connections"

EGH_PUBLIC = os.path.join(connections, "egh_public on gisdb1.rose.portland.local.sde")
BESGEORPT_TEST = os.path.join(connections, "BESDBTEST1.BESGEORPT.OSA.sde")

collection_lines = EGH_PUBLIC + r"\EGH_Public.ARCMAP_ADMIN.collection_lines_bes_pdx"
taxlots = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.taxlots_pdx"
tv_obs_lines = EGH_PUBLIC + r"\EGH_PUBLIC.ARCMAP_ADMIN.collection_tvobs_line_bes_pdx"
WOs = arcpy.MakeQueryLayer_management(BESGEORPT_TEST, "WOs", "SELECT MY_ID, OWNER1, SITEADDR, PROPERTYID, TLID, COMPKEY, MODBY, DISTRICT, WO, ACTCODE, UNITID, UNITID2, INITDTTM, STARTDTTM,"
                                                             " SCHEDDTTM, PRI, PROB, COMPFLAG, STRUCTURAL_RATING, STRUCTURALSCORE, SHAPE_STArea__, SHAPE_STLength__, STATUS, Shape "
                                                             "from BESGEORPT.GIS.V_WOS_COMBINED_COPY20211006", "MY_ID")

mains = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\pipes", "LAYER_GROUP not in ('LATERALS', 'INLETS') AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%'")
laterals = arcpy.MakeFeatureLayer_management(collection_lines, r"in_memory\laterals", "LAYER_GROUP = 'LATERALS' AND SERVSTAT not in ('ABAN', 'TBAB' ) AND SYMBOL_GROUP not like 'ABANDONED%'")
roots = arcpy.MakeFeatureLayer_management(tv_obs_lines, r"in_memory\roots", "OBDESC = 'ROOTS'")


