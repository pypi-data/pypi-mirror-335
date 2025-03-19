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

import os
import json
import pprint
import sys


def isMultipleTagsInput(item):
    """
    Returns True if the argument datatype is not a column or a table, and if it allows lists and if it has no permitted value.
    
    This function is used to check whether the argument values have to be delimited by the null character (returns True) or not.
    :param item: Table argument.
    """
    return item.get('datatype', 'STRING') in ['STRING','DOUBLE','INTEGER','DRIVER','SQLEXPR', 'LONG']\
        and item.get('allowsLists', False)\
        and not item.get('permittedValues', [])
        
def defaultValuesFromArg(item):
    """
    Returns the default value for the given item.
    
    If the argument is not a required argument and not a boolean, we reset the default value to the empty string.
    :param item: Table argument.
    """
    defaultvalues = item.get('defaultValue', '')    
    if isMultipleTagsInput(item) and isinstance(defaultvalues, (list, tuple)):
        DELIMITER = chr(0)
        return DELIMITER.join(str(x) for x in defaultvalues)
    return defaultvalues

def inNativeCheck(a, a_n):
    """
    Checks if each argument in `a` is in the native function's list of arguments `a_n`.
    
    :param a: List of arguments.
    :param a_n: List of native arguments.
    """
    arg_native_names = map(lambda d: d.get('name'), a_n)
    arg_native_alt_names = map(lambda d: d.get('alternateNames'), a_n)
    for arg in a:                
        if arg.get('name') in arg_native_names or arg.get('name') in arg_native_alt_names:
            arg["inNative"] = True
    return a 

def load_json(json_dict, inputs=[]):
    try:

        f = json_dict
        d = {
            "name":"",
            "function_alias_name":"",
            "output_tables":"",
            "arguments":"",
            "asterarguments":"",
            "partitionInputKind":[],
            "partitionAttributes":"",
            "isOrdered":False,
            "orderByColumn":"",
            "hasInputTable":False,
            "isQueryMode": False,
            "queries": [],
            "hasNativeJSON": True,
            "function_type" : ""
        }
        
        keys = f.keys()

        # SKS Return the original JSON contents in the dictionary
        d["json_contents"] = json.dumps(f)

        # function type used for valib extension
        d["function_type"] = f.get("function_type", "")

        
        # Get the function name and alias name, and use the function name as the alias name if the latter does not exist.
        d["name"] = f.get("function_name", "")
        d["function_alias_name"] = f.get("function_alias_name", f.get("function_name", ""))
        
        unaliased_inputs = {'desc':{}, 'values':[], 'count':0}
        required_inputs = []
        # Run through all the input tables of the function.
        if "input_tables" in keys:
            d["hasInputTable"] = True
            input_table_list = f["input_tables"]
            num_input_tables = 0
            for table in input_table_list:
                required_input_dict = {"isRequired": True, "partitionAttributes":"", "orderByColumn": ""}
                required_input_dict['isRequired'] = table.get('isRequired', True) # Assume required unless specified False.
                required_input_dict['isOrdered'] = table.get('isOrdered', False) # Assume unordered unless specified True.
                required_input_dict['alternateNames'] = table.get('alternateNames', []) # Assume no alternate names unless specified.
                required_input_dict["description"] = table.get("description", "")
                
                requiredInputKind = table.get("requiredInputKind", [])
                if (type(requiredInputKind) == list and len(requiredInputKind) == 1 and requiredInputKind[0] == "PartitionByKey") or requiredInputKind == []:
                    requiredInputKind = ["PartitionByKey", "HashByKey", "None"]

                #requiredInputKind = table.get("requiredInputKind", ["PartitionByAny"]) # All element of the requiredInputKind list.
                partitionByKey = requiredInputKind[0] if requiredInputKind else "" # partitionByKey is the first element of the requiredInputKind list.
                if 'partitionByOne' in table.keys() and table['partitionByOne']:
                    if 'partitionByOneInclusive' in table.keys() and table['partitionByOneInclusive']:  # Checks if partitionByOneInclusive is a key.
                        requiredInputKind.append("PartitionByOne") # If it is a key, we append PartitionByOne to the inputKindChoices.
                    else:
                        partitionByKey = "PartitionByOne" # If partitionByOneInclusive is not a key, we override the partitionByKey to be partitionByOne.
                required_input_dict['kind'] = partitionByKey
                required_input_dict['inputKindChoices'] = requiredInputKind

                if "uaf" in table:
                    required_input_dict["uaf"] = table["uaf"]
                if "uafType" in table:
                    required_input_dict["uafType"] = table["uafType"]
                
                # Check if the table is named (= required input) or not (unaliased input).
                if 'name' in table.keys() or ('Dimension' in table.get('requiredInputKind',[]) and 0 < unaliased_inputs.get('count',0)):
                    required_input_dict['name'] = table.get('name', 'Dimension')
                    required_input_dict['value'] = ""
                    # Set the Table Value if single Input case for first Table Property
                    if len(inputs) == 1 and num_input_tables == 0:
                        required_input_dict['value'] = inputs[0]
                    required_inputs.append(required_input_dict)
                else:
                    unaliased_inputs['count'] += 1
                    d["isOrdered"] = table.get("isOrdered", False)
                    if 'partitionByOne' in table.keys() and table['partitionByOne']:
                        d['partitionInputKind'] = ['PartitionByOne']
                    else:
                        d['partitionInputKind'] = table.get("requiredInputKind", [])





                num_input_tables += 1
                        
        d["required_input"] = required_inputs
        d["unaliased_inputs"] = unaliased_inputs
        
        # Run through all output tables.
        if 'output_tables' in keys:
            ot = []
            out_table_list = f["output_tables"]
            for table in out_table_list:
                outtbl = {"name":"","isRequired":"","value":"", "datatype": "", "allowsLists":True}
                if table.get('alternateNames', []):
                    outtbl["name"] = table.get('alternateNames', [''])[0]
                outtbl["name"] = table.get("name", "")
                outtbl["isRequired"] = table.get("isRequired", False)
                outtbl["datatype"] = table.get("datatype", "")

                # SKS: Add upper and lower bounds
                outtbl["lowerBound"] = table.get("lowerBound", "")
                outtbl["upperBound"] = table.get("upperBound", "")

                # fixes future problem where the type in JSON is both numeric and string
                #if outtbl["datatype"].contains("STRING") and outtbl["datatype"] != "STRING":
                #    outtbl["datatype"] = "STRING"

                outtbl["allowsLists"] = table.get("allowsLists", True)
                outtbl["targetTable"] = table.get("targetTable", [])
                outtbl["isOutputTable"] = table.get("isOutputTable", False)
                outtbl["permittedValues"] = table.get("permittedValues", [])
                if 'defaultValue' in table:
                    outtbl["value"] = defaultValuesFromArg(table)
                    # SKS: 
                    outtbl["defaultValue"] = outtbl["value"]
                ot.append(outtbl)
            d["output_tables"] = ot
        
        # Similar to output tables.
        if 'argument_clauses' in keys:
            args = []
            arg_lst = f['argument_clauses']
            for argument in arg_lst:
                arg = {"name":"","isRequired":"","value":"", "datatype": "", "allowsLists":True}
                if argument.get('alternateNames', []):
                    arg["name"] = argument.get('alternateNames', [''])[0]
                arg["name"] = argument.get("name", "")
                arg["isRequired"] = argument.get("isRequired", False)
                arg["datatype"] = argument.get("datatype", "")
                #if arg["datatype"] == "GROUPEND":
                #    continue
                if type(arg["datatype"]) != str:
                    arg["datatype"] = "STRING"
                arg["datatype"] = arg["datatype"].upper()
                if arg["datatype"] == "NUMERIC":
                    arg["datatype"] = "DOUBLE PRECISION"
                if arg["datatype"] == "COLUMN":
                    arg["datatype"] = "COLUMNS"

                if "useDefaultInQuery" in argument:
                    arg["useDefaultInQuery"] = argument["useDefaultInQuery"]

                # SKS: Add upper and lower bounds
                arg["lowerBound"] = str(argument.get("lowerBound", ""))
                arg["upperBound"] = str(argument.get("upperBound", ""))

                # SKS: fixes future problem where the type in JSON is both numeric and string
                #if arg["datatype"].contains("STRING") and arg["datatype"] != "STRING":
                #    arg["datatype"] = "STRING"


                arg["description"] = argument.get("description", "")
                arg["allowsLists"] = argument.get("allowsLists", True)
                arg["targetTable"] = argument.get("targetTable", [])
                arg["isOutputTable"] = argument.get("isOutputTable", False)
                arg["permittedValues"] = argument.get("permittedValues", [])
                if 'defaultValue' in argument:
                    arg["value"] = defaultValuesFromArg(argument)
                    # SKS: Added Default Value for frontend to use as well
                    arg["defaultValue"] = arg["value"]
                else:
                    arg["defaultValue"] = ""

                if "Type" in argument:
                    arg["Type"] = argument["Type"]

                # arg["inNative"] = True # Setting to True because all files should be native and not MLE.
                args.append(arg)
                
            d['arguments'] = args
            # f_native = json.loads(open('%s/data/%s' % (os.getenv("DKU_CUSTOM_RESOURCE_FOLDER"), f.get("native"))).read())
            f_native = f
            keys_native = f_native.keys()
            if 'argument_clauses' in keys_native:
                a_n = []
                arg_lst_native = f_native['argument_clauses']
                for argument_native in arg_lst_native:
                    arg_n = {}
                    arg_n["alternateNames"] = argument_native.get("alternateNames", [""])[0] if argument_native.get("alternateNames", []) else ""
                    arg_n["name"] = argument_native.get("name", "")
                    a_n.append(arg_n)                                                           
                args = inNativeCheck(args, a_n)
        return d
        
    except ValueError:
        logging.info("%s is not a valid json file." % file_name)
       
