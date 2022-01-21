import logging
import logging.config
import sys
import arcpy
import random


unique_random_list = random.sample(range(0, 1000), 50)

# https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module
def Logger(file_name):
    formatter = logging.Formatter(fmt='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                                  datefmt='%Y/%m/%d %H:%M:%S')  # %I:%M:%S %p AM|PM format
    logging.basicConfig(filename='%s.log' % (file_name),
                        format='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S', filemode='a', level=logging.INFO)
    log_obj = logging.getLogger()
    log_obj.setLevel(logging.DEBUG)
    # log_obj = logging.getLogger().addHandler(logging.StreamHandler())

    # console printer
    screen_handler = logging.StreamHandler(stream=sys.stdout)  # stream=sys.stdout is similar to normal print
    screen_handler.setFormatter(formatter)
    logging.getLogger().addHandler(screen_handler)

    log_obj.info("Starting log session..")
    return log_obj

def reorder_fields(table_in, out_table, field_order, add_missing=False):
    """
    Reorders fields in input featureclass/table
    :table:         input table (fc, table, layer, etc)
    :out_table:     output table (fc, table, layer, etc)
    :field_order:   order of fields (objectid, shape not necessary)
    :add_missing:   add missing fields (that were not specified in field_order) to end if True (leave out if False) - good way to delete a bunch of fields if you need to
    -> path to output table
    """
    existing_fields = arcpy.ListFields(table_in)
    existing_field_names = [field.name for field in existing_fields]

    existing_mapping = arcpy.FieldMappings()
    existing_mapping.addTable(table_in)

    new_mapping = arcpy.FieldMappings()

    def add_mapping(field_name):
        mapping_index = existing_mapping.findFieldMapIndex(field_name)

        # required fields (OBJECTID, etc) will not be in existing mappings
        # they are added automatically
        if mapping_index != -1:
            field_map = existing_mapping.fieldMappings[mapping_index]
            new_mapping.addFieldMap(field_map)

    # add user fields from field_order
    for field_name in field_order:
        if field_name not in existing_field_names:
            raise Exception("Field: {0} not in {1}".format(field_name, table_in))

        add_mapping(field_name)

    # add missing fields at end
    if add_missing:
        missing_fields = [f for f in existing_field_names if f not in field_order]
        for field_name in missing_fields:
            add_mapping(field_name)

    # use merge with single input just to use new field_mappings
    arcpy.Merge_management(table_in, out_table, new_mapping)
    return out_table

def rename_fields(table_in, out_table, new_name_by_old_name):
    """ Renames specified fields in input feature class/table
    :table:                 input table (fc, table, layer, etc)
    :out_table:             output table (fc, table, layer, etc)
    :new_name_by_old_name:  {'old_field_name':'new_field_name',...}
    ->  out_table
    """
    existing_field_names = [field.name for field in arcpy.ListFields(table_in)]

    field_mappings = arcpy.FieldMappings()
    field_mappings.addTable(table_in)

    for old_field_name, new_field_name in new_name_by_old_name.iteritems():
        if old_field_name not in existing_field_names:
            message = "Field: {0} not in {1}".format(old_field_name, table_in)
            raise Exception(message)

        mapping_index = field_mappings.findFieldMapIndex(old_field_name)
        field_map = field_mappings.fieldMappings[mapping_index]
        output_field = field_map.outputField
        output_field.name = new_field_name
        output_field.aliasName = new_field_name
        field_map.outputField = output_field
        field_mappings.replaceFieldMap(mapping_index, field_map)

    # use merge with single input just to use new field_mappings
    arcpy.Merge_management(table_in, out_table, field_mappings)
    return out_table

def prepare_fields(table_in, new_name_by_old_name):
    number1 = get_unique_number()
    number2 = get_unique_number()
    reorder = reorder_fields(table_in, r"in_memory\reorder_" + str(number1), new_name_by_old_name.keys(), add_missing=False)
    rename = rename_fields(reorder, r"in_memory\rename_" + str(number2), new_name_by_old_name)
    return rename

def prep_renamed_mains_dict(mains_field_list, appended_string):
    renamed_dict = {}
    for item in mains_field_list:
        renamed_dict[item] = appended_string + item
    return renamed_dict

def get_unique_number():
    my_number = unique_random_list[0]
    unique_random_list.remove(my_number)
    return my_number

def get_field_names(input):
    name_list = []
    fields = arcpy.ListFields(input)
    for field in fields:
        name_list.append(field.name)
    return name_list