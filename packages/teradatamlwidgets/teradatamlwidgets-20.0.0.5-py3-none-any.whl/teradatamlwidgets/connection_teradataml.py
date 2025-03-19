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
import sys
import json
import pprint
from teradatamlwidgets.connection import *
from teradataml import *

class Connection(BaseConnection):
    def __init__(self):
        super().__init__()
        self.teradataml_connection = None
        try:
            # Try the global context
            self.teradataml_connection = get_context()
        except:
            pass
        
    def setup_executor(self, dataset, autocommit, pre_query, post_query):
        super().setup_executor(dataset, autocommit, pre_query, post_query) 

    def execute(self, query_string):
        if not self.teradataml_connection:
            return
        if hasattr(self.teradataml_connection, 'execute'):
            return self.teradataml_connection.execute(query_string)
        else:
            # SQLAlchemy 2.*.* support (no execute method now)
            return execute_sql(query_string)
            # Or use this
            # return self.teradataml_connection.exec_driver_sql(query_string)

    def iteratable(self, result):
        return result

    def row_value(self, row, column_name):
        if column_name in row:
            return row[column_name]
        else:
            return row[0]

    def login(self, host, username, password, default_db, val_location):
        super().login(self, username, password, default_db, val_location)
        configure.val_install_location = val_location
        self.teradataml_connection = create_context(host, username, password)
        #self.teradataml_connection = teradataml.get_connection()

    def is_logged_in(self):
        return self.teradataml_connection != None

    def can_log_out(self):
        return True

    def logout(self):
        self.teradataml_connection =  None

    def get_dataset_name(self, datasets):
        result = []
        for dataset in datasets:
            if "." in dataset:
                result.append(dataset.split(".")[1])
            else:
                result.append(dataset)
        return result
        
    def get_columns_of_dataset(self, dataset_name):
        # Add empty column "" as an option too
        if dataset_name == "":
            return []
        return DataFrame(dataset_name).columns

    def get_schema_table_name(self, dataset_name, datasets):
        for dataset in datasets:
            if "." in dataset:
                split_names = dataset.split(".")
                schema_name = split_names[0]
                table_name = split_names[1]
            else:
                table_name = dataset
                schema_name = ""
            if table_name == dataset_name:
                return schema_name, table_name  
        return None

    def get_pandas_dataframe(self, full_name, dataset_name):
        return self.get_output_dataframe(full_name, dataset_name).to_pandas()

    def get_output_dataframe(self, full_name, dataset_name):
        return DataFrame(full_name)
       
