import logging
import logging.config
import sys
import arcpy


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

def delete_fields(existing_table, keep_fields_list):
    field_name_required_dict = get_field_names_and_required(existing_table)
    remove_list = create_remove_list(field_name_required_dict, keep_fields_list)
    arcpy.DeleteField_management(existing_table, remove_list)

def rename_fields(existing_table, keep_fields_list, appended_string):
    keep_fields_dict = prepare_renamed_dict(keep_fields_list, appended_string)
    for key, value in keep_fields_dict.items():
        arcpy.AlterField_management(existing_table, key, value, value)

def list_field_names(input_fc):
    field_names = []
    fields = arcpy.ListFields(input_fc)
    for field in fields:
        field_names.append(field.name)
    return field_names

def add_field_if_needed(input_fc, field_to_add, field_type, precision='', scale='', length=''):
    field_names = list_field_names(input_fc)
    if field_to_add not in field_names:
        arcpy.AddField_management(input_fc, field_to_add, field_type, precision, scale, length)

def prepare_fields(table_in, keep_fields_list, appended_string):
    delete_fields(table_in, keep_fields_list)
    rename_fields(table_in, keep_fields_list, appended_string)

def prepare_renamed_dict(field_list, appended_string):
    renamed_dict = {}
    for item in field_list:
        renamed_dict[item] = appended_string + item
    return renamed_dict

def get_field_names(input):
    name_list = []
    fields = arcpy.ListFields(input)
    for field in fields:
        name_list.append(field.name)
    return name_list

def get_field_names_and_required(input):
    name_and_required_dict = {}
    fields = arcpy.ListFields(input)
    for field in fields:
        name_and_required_dict[field.name] = field.required
    return name_and_required_dict

def create_remove_list(existing_names_and_required, field_list):
    remove_field_list = []
    for key, value in existing_names_and_required.items():
        # second param tests for required fields (OID, Shape, etc), don't want to include these as we cannot modify them
        if key not in field_list and key not in ('Shape', 'OBJECTID') and value != True:
            remove_field_list.append(key)
    return remove_field_list

def get_field_value_as_dict(input, key_field, value_field):
    value_dict = {}
    with arcpy.da.SearchCursor(input, [key_field, value_field]) as cursor:
        for row in cursor:
            value_dict[row[0]] = row[1]
    return value_dict

def get_field_values_as_dict(input, key_field, value_fields_list):
    value_dict = {}
    fields_list = [key_field]
    for field in value_fields_list:
        fields_list.append(field)
    with arcpy.da.SearchCursor(input, fields_list) as cursor:
        for row in cursor:
            value_dict[row[0]] = row[1:]
    return value_dict

def assign_field_value_from_dict(input_dict, target, target_key_field, target_field):
    with arcpy.da.UpdateCursor(target, (target_key_field, target_field)) as cursor:
        for row in cursor:
            if row[0] in input_dict.keys() and row[1] is None:
                row[1] = input_dict[row[0]]
            cursor.updateRow(row)

def assign_field_values_from_dict(input_dict, target, target_key_field, target_fields):
    cursor_fields_list = [target_key_field]
    for field in target_fields:
        cursor_fields_list.append(field)
    counter_max = len(cursor_fields_list) - 1
    with arcpy.da.UpdateCursor(target, cursor_fields_list) as cursor:
        for row in cursor:
            counter = 1
            values_counter = counter - 1
            while counter <= counter_max:
                for key, values in input_dict.items():
                    if row[0] == key and row[counter] is None and values[values_counter] is not None:
                        row[counter] = values[values_counter]
                counter = counter + 1
                values_counter = counter - 1
            cursor.updateRow(row)

def get_and_assign_field_value(source, source_key_field, source_field, target, target_key_field, target_field):
    value_dict = get_field_value_as_dict(source, source_key_field, source_field)
    assign_field_value_from_dict(value_dict, target, target_key_field, target_field)

def get_and_assign_field_values(source, source_key_field, source_fields, target, target_key_field, target_fields):
    value_dict = get_field_values_as_dict(source, source_key_field, source_fields)
    assign_field_values_from_dict(value_dict, target, target_key_field, target_fields)

# will ignore records that have any letters
def cast_text_to_short(input, text_field_to_cast):
    int_field = text_field_to_cast + "_int"
    add_field_if_needed(input, int_field, "SHORT")
    with arcpy.da.UpdateCursor(input, [text_field_to_cast, int_field]) as cursor:
        for row in cursor:
            if row[0] is not None and row[0].isdigit():
                row[1] = int(row[0])
                cursor.updateRow(row)
    arcpy.DeleteField_management(input, [text_field_to_cast])
    arcpy.AlterField_management(input, int_field, text_field_to_cast)