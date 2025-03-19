# -*- coding: utf-8 -*-
'''
Copyright © 2024 by Teradata.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import json
import os

def ungroupParameters(json_data):
    argument_clauses = []
    for argument_clause in json_data["argument_clauses"]:
        if argument_clause["Type"].lower() == "record":
            group_name = argument_clause["Name"] 
            
            num_optional = 0
            num_mandatory = 0
            child_clauses = []
            for NestedParams in argument_clause["NestedParams"]:
                if type(group_name) == list:
                    group_name = group_name[0] 
                NestedParams["Name"] = group_name + "." + NestedParams["Name"]
                if NestedParams["Optional"]:
                    num_optional += 1
                else:
                    num_mandatory += 1
                child_clauses.append(NestedParams)
            
            data_type = 'GROUPSTART'
            if num_mandatory>0:
                argument_clauses.append({"name" : group_name, "Type" : data_type, "Description" : argument_clause["Description"], "Optional" : False })
                data_type = 'GROUPSTARTOPTIONAL' # For the group of the optional parameters
            if num_optional>0:
                argument_clauses.append({"name" : group_name, "Type" : data_type, "Description" : argument_clause["Description"], "Optional" : True })
            argument_clauses.extend(child_clauses)
            argument_clauses.append({"name" : group_name + "_GROUPEND", "Type" : 'GROUPEND', "Description" : argument_clause["Description"], "Optional" : False})
            

            continue
        argument_clauses.append(argument_clause)
    json_data["argument_clauses"] = argument_clauses


def uaf_to_indb(json_data):

    datatypes = {}
    datatypes2 = {}

    if "InputDistributionStrategy" in json_data and "Input" not in json_data:
        json_data["Input"] = json_data.pop("InputDistributionStrategy")
    if "OutputDistributionStrategy" in json_data and "Output" not in json_data:
        json_data["Output"] = json_data.pop("OutputDistributionStrategy")

    rOrderNum = 1

    json_data["function_type"] = "uaf"
    json_data["json_schema_major_version"] = "1"
    json_data["json_schema_minor_version"] = "2"
    json_data["json_content_version"] = "1"
    json_data["function_name"] = json_data.pop("FuncName")
    json_data["function_r_name"] = "aa." + json_data["function_name"].lower()
    json_data["ref_function_r_name"] = "aa." + json_data["function_name"].lower()
    json_data["function_version"] = json_data.pop("FunctionVersion")
    json_data["short_description"] = json_data.pop("FuncDescriptionShort")
    json_data["long_description"] = ". ".join(json_data.pop("FuncDescriptionLong"))


    # Do input_tables
    uaf_index = 0
    if "Input" in json_data:
        json_data["input_tables"] = json_data.pop("Input")

        if json_data["function_name"] == "TD_PLOT":
            for plot_input in range(15):
                clone_input = json_data["input_tables"][0].copy()
                clone_input['name'] = "Input {}".format(plot_input+1)
                json_data["input_tables"].append(clone_input)

        for input_table in json_data["input_tables"]:
            input_table["requiredInputKind"] = ["PartitionByNone"]
            input_table["isOrdered"] = False
            input_table["partitionByOne"] = False
            input_table["alternateNames"] = []
            input_table["isRequired"] = not input_table.pop("Optional")

            input_table["description"] = "".join(input_table.pop("Description"))
            input_table["rDescription"] = input_table["description"]
            input_table["datatype"] = "TABLE_ALIAS"
            input_table["allowsLists"] = False
            if rOrderNum == 2:
                input_table["name"] = "Input2"
            elif rOrderNum == 1:
                input_table["name"] = "Input"
            else:
                input_table["name"] = "Input" + str(rOrderNum)
            input_table["rName"] = input_table["name"]
            input_table["useInR"] = True

            input_table["rOrderNum"] = rOrderNum

            # UAF content
            input_table["uaf"] = {}
            input_table["uaf"]["requiredUafKind"] = input_table.pop("Type")
            if type(input_table["uaf"]["requiredUafKind"]) == str:
                # Make into list
                input_table["uaf"]["requiredUafKind"] = [ input_table["uaf"]["requiredUafKind"] ]
            input_table["uafType"] = "" if len(input_table["uaf"]["requiredUafKind"]) !=1 else input_table["uaf"]["requiredUafKind"][0]
            input_table["uaf"]["is_row_sequence"] = "SEQUENCE"
            input_table["uaf"]["is_col_sequence"] = "SEQUENCE"
            input_table["uaf"]["row_axis_name"] = ""
            input_table["uaf"]["column_axis_name"] = ""
            input_table["uaf"]["id_name"] = ""
            input_table["uaf"]["id_sequence"] = ""
            input_table["uaf"]["payload_fields"] = ""
            input_table["uaf"]["payload_content"] = ""
            input_table["uaf"]["layer"] = ""
            input_table["uaf"]["where"] = ""
            input_table["uaf"]["time_duration"] = ""
            input_table["uaf"]["time_zero"] = ""
            input_table["uaf"]["time_type"] = ""
            input_table["uaf"]["seq_zero"] = ""
            input_table["uaf"]["interval"] = "Off"
            input_table["uaf"]["details"] = True

            input_table["uaf"]["instance_names"] = ""
            input_table["uaf"]["data_type"] = ""
            input_table["uaf"]["payload_start_value"] = ""
            input_table["uaf"]["payload_offset_value"] = ""
            input_table["uaf"]["payload_num_entries"] = ""
            input_table["uaf"]["index"] = uaf_index
            uaf_index += 1
            
            rOrderNum +=1

        
    else:
        print("This does not have an input table ", uaf_filename)
        pass

    # Do output_tables - TODO
    if "Output" in json_data:
        out_table_num = 1
        json_data["output_tables"] = json_data.pop("Output")
        for output_table in json_data["output_tables"]:
            output_table["isOutputTable"] = True
            output_table["omitPossible"] = True
            output_table["partitionByOne"] = False
            output_table["alternateNames"] = []
            output_table["isRequired"] = False

            if "Description" in output_table:
                output_table["description"] = "".join(output_table.pop("Description"))
                output_table["rDescription"] = output_table["description"]
            output_table["datatype"] = "TABLE_NAME"
            output_table["allowsLists"] = False
            output_table["name"] = "OutputTable" + str(out_table_num)
            output_table["rName"] = output_table["name"]
            output_table["useInR"] = True
            output_table["rOrderNum"] = rOrderNum
            rOrderNum +=1
            out_table_num += 1
        if len(json_data["output_tables"])>2:
            #print("More than 2 outputs", uaf_filename, len(json_data["output_tables"]))
            pass


    # argument clauses
    json_data["argument_clauses"] = json_data.pop("Params")

    # Deal with records - a group parameter - remove it and add children
    ungroupParameters(json_data)
    # Do it again as somecases we have group of groups
    ungroupParameters(json_data)

    # Add InFormat and OutFormat Parameter
    if json_data.get("InputFmt", False):
        input_format = json_data["InputFmt"][0]
        name = input_format["Name"]
        input_format["Name"] = "InputFormat"
        if input_format.get("DefaultValue", ""):
            input_format["DefaultValue"] = name + "(" + input_format["DefaultValue"] + ")"
        if input_format.get("PermittedValues", []):
            for i in range(len(input_format["PermittedValues"])):
                input_format["PermittedValues"][i] = name + "(" + input_format["PermittedValues"][i] + ")"                  


        json_data["argument_clauses"].insert(0, input_format)

    if json_data.get("OutputFmt", False):
        output_format = json_data["OutputFmt"][0]
        name = output_format["Name"]
        output_format["Name"] = "OutputFormat"
        if output_format.get("Default", ""):
            output_format["DefaultValue"] = name + "(" + output_format["Default"] + ")"
        if output_format.get("PermittedValues", []):
            for i in range(len(output_format["PermittedValues"])):
                output_format["PermittedValues"][i] = name + "(" + output_format["PermittedValues"][i] + ")"                  

        json_data["argument_clauses"].insert(0, output_format)



    for argument_clause in json_data["argument_clauses"]:

        # Convert all keys to lower case
        for ItemKey in argument_clause.copy():
            if type(ItemKey) != str:
                print(ItemKey)
            itemKey = ItemKey[0].lower() + ItemKey[1:]
            argument_clause[itemKey]  = argument_clause.pop(ItemKey)

        argument_clause["allowsLists"]  = False


        datatypes[argument_clause["type"]] = True
        if argument_clause["type"] == "list":
            argument_clause["type"] = argument_clause["listType"]
            argument_clause["allowsLists"]  = True  

        # Keep the original type
        argument_clause["Type"] = argument_clause["type"]

        if argument_clause["type"] == "enumeration":
            argument_clause["type"] = "STRING"
        elif argument_clause["type"] == "<td_formula>":
            argument_clause["type"] = "STRING"
        elif argument_clause["type"] == "enumeration<string>":
            argument_clause["type"] = "STRING"
        elif argument_clause["type"]=="enum<string>":
            argument_clause["type"] = "STRING"
        elif argument_clause["type"]=="enumeration<time-unit>":
            argument_clause["type"] = "STRING"
        elif argument_clause["type"] == "float":
            argument_clause["type"] = "DOUBLE"
        elif argument_clause["type"] == "<varies>":
            argument_clause["type"] = "DOUBLE"

        argument_clause["datatype"]  = argument_clause.pop("type").upper()
        argument_clause["description"]  = "".join(argument_clause.pop("description"))
        argument_clause["isRequired"]  = not argument_clause.pop("optional")

        if not "allowsLists" in argument_clause:
            argument_clause["allowsLists"]  = False

        if "permittedValues" in argument_clause:
            permittedValues = []
            # remove quotes from permitted values
            for permittedValue in argument_clause["permittedValues"]:
                if type(permittedValue) == str:
                    permittedValue = permittedValue.strip("'")
                permittedValues.append(permittedValue)
            argument_clause["permittedValues"] = permittedValues


        datatypes2[argument_clause["datatype"]] = True

        argument_clause["rOrderNum"] = rOrderNum
        rOrderNum += 1

    return json_data



