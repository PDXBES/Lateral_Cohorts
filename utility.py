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
        arcpy.AlterField_management(existing_table, key, value)

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
