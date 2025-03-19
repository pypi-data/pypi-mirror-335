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
from teradatamlwidgets.teradata_analytic_lib.query_engine_wrapper import QueryEngineWrapper

# Subclass of query engine wrapper implemented with a Dataiku SQLExecutor2
# An instance of this class will be created when we use the functions in analytic_function_utility and vantage_version
class BaseConnection(QueryEngineWrapper):
    def __init__(self):
        self.connection_settings = {}
        self.connection_settings["default_db"] = ""
        self.connection_settings["val_location"] = "VAL"
        self.jdbc_setting = {}

    def setup_executor(self, dataset, autocommit, pre_query, post_query):
        self.autocommit = autocommit
        self.pre_query = pre_query
        self.post_query = post_query

    def execute(self, query_string):
        pass

    def iteratable(self, result):
        pass

    def row_value(self, row, column_name):
        pass

    def login(self, host, username, password, default_db, val_location):
        self.connection_settings["default_db"] = default_db
        self.connection_settings["val_location"] = val_location

    def is_logged_in(self):
        return False

    def can_log_out(self):
        return True

    def logout(self):
        return

    def get_connection_setting(self, dataset, key, default_value=""):
        return self.connection_settings.get(key, default_value)

    def get_jdbc_setting(self, dataset, key, default_value=""):
        return self.jdbc_setting.get(key, default_value)

    def get_dataset_name(self, datasets):
        return [] 

    def get_columns_of_dataset(self, dataset_name):
        return []
        
    def get_schema_table_name(self, dataset_name, inputs):
        return None

    def get_output_dataframe(self, full_name, dataset_name):
        return None

    def get_pandas_dataframe(self, full_name, dataset_name):
        return None

    def set_schema_from_vantage(self, dataset, schema, table):
        return
       
