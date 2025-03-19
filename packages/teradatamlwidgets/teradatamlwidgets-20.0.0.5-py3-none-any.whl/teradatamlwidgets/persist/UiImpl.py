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

Primary Owner: Saroop Samra (saroop.samra@teradata.com)
Secondary Owner: 
'''


import os
import sys
import json
import ipywidgets
from IPython.display import clear_output, HTML,Javascript, display
from teradatasqlalchemy.types import *
import teradataml
from teradataml import DataFrame
from teradatamlwidgets.base_ui import _BaseUi


class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Persist UI.
    """
    def __init__(
        self, 
        df):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Persist UI.

        PARAMETERS:
            df: 
                Required Argument. 
                Specifies the name of the input table.
                Type: DataFrame
                

        RETURNS:
            Instance of the Persist UI Implementation.

        RAISES:
            None.
        """
        
        _BaseUi.__init__(self, default_database="", connection=None)
        
        self._df = df
        self._target_columns_type_map = {}
        
        if self._connection.is_logged_in():
            self._create_ui()
            self._open_ui()

    def _create_output_tab(self):
        """
        DESCRIPTION:
            Private method that creates the Output UI tab.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            The ipywidgets for all of the parameters in Output tab.
        """
        rows = []

        format_list = []
        style = {'description_width': '150px'}

        self._table_name = ipywidgets.Text(
            value = "",
            description = "Table Name",
            style = style,
            tooltip = '''Required Argument.
            Specifies the name of the table to be created in Teradata Vantage.''')
        format_list.append(self._table_name)

        self._schema_name = ipywidgets.Text(
            description="Schema",
            value=None,
            style = style,
            tooltip='''Optional Argument.
            Specifies the name of the SQL schema in Teradata Vantage to write to.
            Default Value: None (Use default Teradata Vantage schema).
            Types: str

            Note: schema_name will be ignored when temporary=True.''')
        format_list.append(self._schema_name)

        self._temporary = ipywidgets.Checkbox(
            description="Volatile",
            value=False,
            tooltip='''Optional Argument.
            Creates Teradata SQL tables as permanent or volatile.
            When True,
                1. volatile tables are created, and
                2. schema_name is ignored.
            When False, permanent tables are created.''')
        format_list.append(self._temporary)
        rows.append(ipywidgets.HBox(format_list))

        set_format = []
        self._if_exists = ipywidgets.Dropdown(
            description="If exists",
            value="fail",
            style = style,
            options=['fail', 'replace', 'append'],
            tooltip='''Optional Argument.
            Specifies the action to take when table already exists in Teradata Vantage.
            Default Value: 'fail'
            Permitted Values: 'fail', 'replace', 'append'
                - fail: If table exists, do nothing.
                - replace: If table exists, drop it, recreate it, and insert data.
                - append: If table exists, insert data. Create table, if does not exist.
            Types: str

            Note: Replacing a table with the contents of a teradataml DataFrame based on
                  the same underlying table is not supported.''')
        set_format.append(self._if_exists)

        self._primary_index = ipywidgets.Text(
            description="Primary Index",
            value=None,
            style = style,
            tooltip='''Optional Argument.
            Creates Teradata table(s) with primary index column(s) when specified.
            When None, No primary index Teradata tables are created.
            Default Value: None
            Types: str or List of Strings (str)
                Example:
                    primary_index = 'my_primary_index'
                    primary_index = ['my_primary_index1', 'my_primary_index2', 'my_primary_index3']''')
        set_format.append(self._primary_index)
        rows.append(ipywidgets.HBox(set_format))
        
        return ipywidgets.VBox(rows)

    def _create_pti_tab(self):
        """
        DESCRIPTION:
            Private method that creates the PTI UI tab.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            The ipywidgets for all of the parameters in PTI tab.
        """

        style = {'description_width': '150px'}

        self._set_table = ipywidgets.Checkbox(
            description="Set Table",
            value=False,
            style = style,
            tooltip='''Optional Argument. Specifies a flag to determine whether to create a SET or a MULTISET table. When True, a SET table is created. When False, a MULTISET table is created.

            Note: 1. Specifying set_table=True also requires specifying primary_index or timecode_column.
                  2. Creating SET table (set_table=True) may result in loss of duplicate rows.
                  3. This argument has no effect if the table already exists and if_exists='append'.''')
        

        self._primary_time_index_name = ipywidgets.Text(
            description="Name",
            value=None,
            style = style,
            tooltip='''Optional Argument.
            Specifies a name for the Primary Time Index (PTI) when the table
            to be created must be a PTI table.

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.''')
        

        self._columns_list = ipywidgets.SelectMultiple(
            options=self._df.columns + [None],
            value=(),
            style = style,
            layout={'height': '160px'},
            tooltip='''Optional Argument.
            Required if timebucket_duration is not specified.
            Used when the DataFrame must be saved as a PTI table.
            Specifies a list of one or more PTI table column names.
            Types: String or list of Strings

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.''')
        
        self._timecode_column = ipywidgets.Select(
            options= self._df.columns + [None],
            value=None,
            style = style,
            layout={'height': '160px'},
            tooltip='''Optional Argument.
            Required when the DataFrame must be saved as a PTI table.
            Specifies the column in the DataFrame that reflects the form
            of the timestamp data in the time series.
            This column will be the TD_TIMECODE column in the table created.
            It should be of SQL type TIMESTAMP(n), TIMESTAMP(n) WITH TIMEZONE, or DATE,
            corresponding to Python types datetime.datetime or datetime.date.

            Note: When you specify this parameter, an attempt to create a PTI table
                  will be made. This argument is not required when the table to be created
                  is not a PTI table. If this argument is specified, primary_index will be ignored.''')
        
        self._timezero_date = ipywidgets.Text(
            description="Timezero Date",
            value=None,
            style = style,
            tooltip='''Optional Argument.
            Used when the DataFrame must be saved as a PTI table.
            Specifies the earliest time series data that the PTI table will accept;
            a date that precedes the earliest date in the time series data.
            Value specified must be of the following format: DATE 'YYYY-MM-DD'

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.''')
        
        self._timebucket_duration = ipywidgets.Text(
            description="Timebucket Duration",
            value=None,
            style = style,
            tooltip='''Optional Argument.
            Required if columns_list is not specified or is None.
            Used when the DataFrame must be saved as a PTI table.
            Specifies a duration that serves to break up the time continuum in
            the time series data into discrete groups or buckets.
            Specified using the formal form time_unit(n), where n is a positive
            integer, and time_unit can be any of the following:
            CAL_YEARS, CAL_MONTHS, CAL_DAYS, WEEKS, DAYS, HOURS, MINUTES,
            SECONDS, MILLISECONDS, or MICROSECONDS.
            Types:  String

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.''')
        
        self._sequence_column = ipywidgets.Text(
            description="Sequence Column",
            style = style,
            tooltip='''Optional Argument.
            Used when the DataFrame must be saved as a PTI table.
            Specifies the column of type Integer containing the unique identifier for
            time series data readings when they are not unique in time.
            * When specified, implies SEQUENCED, meaning more than one reading from the same
              sensor may have the same timestamp.
              This column will be the TD_SEQNO column in the table created.
            * When not specified, implies NONSEQUENCED, meaning there is only one sensor reading
              per timestamp.
              This is the default.
            Types: str

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.''',
            value=None)
        
        self._seq_max = ipywidgets.BoundedIntText(
            description="Max Sequence",
            style = style,
            tooltip='''Optional Argument.
            Used when the DataFrame must be saved as a PTI table.
            Specifies the maximum number of sensor data rows that can have the
            same timestamp. Can be used when 'sequenced' is True.
            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.
            ''',
            min=1,
            max=2147483647,
            value=None)

        first_column = ipywidgets.VBox([
            self._set_table, self._primary_time_index_name, self._timezero_date, 
            self._timebucket_duration, self._sequence_column, self._seq_max
        ])
        
        second_column = ipywidgets.VBox([
            ipywidgets.Label("Column List", layout=ipywidgets.Layout(display="flex", justify_content="center")), 
            self._columns_list
        ])
          
        third_column = ipywidgets.VBox([
            ipywidgets.Label("Timecode Column", layout=ipywidgets.Layout(display="flex", justify_content="center")), 
            self._timecode_column
        ])
        
        return ipywidgets.HBox([first_column, second_column, third_column])

    def _create_column_types_tab(self):
        """
        DESCRIPTION:    
            Private method that creates the Column Type UI tab.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            The ipywidgets for all of the parameters in Column Type tab.
        """
        rows = []

        self._source_columns = ipywidgets.SelectMultiple(
            options=self._df.columns,
            value=(),
            tooltip='All the columns of the DataFrame',
            layout={'height': '125px'})

        first_column = ipywidgets.VBox([
            ipywidgets.Label("Source", layout=ipywidgets.Layout(display="flex", justify_content="center")), 
            self._source_columns
        ])

        right_all_button = ipywidgets.Button(
            icon='angle-double-right',
            disabled=False,
            style={'button_color' : '#4169E1', 'text_color' : 'white'},
            tooltip='Move All columns to the target.')
        right_all_button.on_click(lambda x: self._move_all_to_target())

        right_selected_button = ipywidgets.Button(
            icon='angle-right',
            disabled=False,
            style={'button_color' : '#4169E1', 'text_color' : 'white'},
            tooltip='Move selected columns to the target.')  

        right_selected_button.on_click(lambda x: self._move_selected_to_target())      
        
        left_all_button = ipywidgets.Button(
            icon='angle-double-left',
            disabled=False,
            style={'button_color' : '#4169E1', 'text_color' : 'white'},
            tooltip='Remove all columns from target.')
        left_all_button.on_click(lambda x: self._move_all_back_to_source())

        left_selected_button = ipywidgets.Button(
            icon='angle-left',
            disabled=False,
            style={'button_color' : '#4169E1', 'text_color' : 'white'},
            tooltip='Remove selected columns to the target.')       
        left_selected_button.on_click(lambda x: self._move_selected_back_to_source())      

        second_column = ipywidgets.VBox([ipywidgets.Label(""), left_selected_button, right_selected_button, left_all_button, right_all_button])

        self._target_columns = ipywidgets.SelectMultiple(
            options=(),
            value=(),
            tooltip='Selected Target Columns of the DataFrame',
            layout={'height': '125px'})
 
        third_column = ipywidgets.VBox([
            ipywidgets.Label("Target", layout=ipywidgets.Layout(display="flex", justify_content="center")), 
            self._target_columns
        ])

        self._target_columns.observe(lambda x: self._on_target_columns_change(), names='value')

        self._types = ipywidgets.Combobox(
            options = list(_UiImpl._type_names.keys()),
            value="",
            tooltip='Selected Target Columns of the DataFrame',
            layout={'height': '125px'})

        self._types.observe(lambda x: self._on_types_change(), names='value')

        self._types_column = ipywidgets.VBox([
            ipywidgets.Label("Type", layout=ipywidgets.Layout(display="flex", justify_content="center")), 
            self._types
        ])

        self._types_column.layout.visibility = 'hidden'

        rows.append(ipywidgets.HBox([first_column, second_column, third_column, self._types_column]))

        return ipywidgets.VBox(rows)

    def _on_types_change(self):
        """
        DESCRIPTION:    
            Private method that stores the type value chosen when it is changed.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        for key in self._target_columns.value:
            self._target_columns_type_map[key] = self._types.value
        
    def _on_target_columns_change(self):
        """
        DESCRIPTION:    
            Private method that either shows or hides the types parameter.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        # When there are no or more than one target columns selected, then the types will be hidden
        if len(self._target_columns.value) != 1:
            self._types_column.layout.visibility = 'hidden'
        else:
            self._types_column.layout.visibility = 'visible'
            self._types.value = self._target_columns_type_map[self._target_columns.value[0]]
        
    def _move_selected_to_target(self):
        """
        DESCRIPTION:    
            Private method that handles when the user moves a column from source to the target.
        Called when the user selects the right arrow button.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        if len(self._source_columns.value) == 0:
            return
        # new target columns options will be the source column value plus whatever options already exist in target columns
        self._target_columns.options = list(self._source_columns.value) + list(self._target_columns.options)
        updated_src_columns = list(self._source_columns.options)
        # the source columns will be updated to remove the value from source that was selected to go to target columns
        for key in self._source_columns.value:
            self._target_columns_type_map[key] = ""
            updated_src_columns.remove(key)
        self._source_columns.options = updated_src_columns

    def _move_selected_back_to_source(self):
        """
        DESCRIPTION:    
            Private method that handles when the user moves a column from target back to source.
        Called when the user selects the left arrow button.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        if len(self._target_columns.value) == 0:
            return
        # new source columns options will be the target column value plus whatever options already exist in source columns
        self._source_columns.options = list(self._source_columns.options) + list(self._target_columns.value)
        updated_target_columns = list(self._target_columns.options)
        # the target columns will be updated to remove the value from target that was selected to go to source columns
        for key in self._target_columns.value:
            del self._target_columns_type_map[key]
            updated_target_columns.remove(key)
        self._target_columns.options = updated_target_columns

    def _move_all_to_target(self):
        """
        DESCRIPTION:    
            Private method that handles when the user wants to move all the source columns to target columns.
        Called when the user selects the double right arrow button.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        # if there are no source columns to move to target columns then return
        if len(self._source_columns.options) == 0:
            return
        # new target columns options will be all source columns value plus whatever options already exist in target columns
        self._target_columns.options = list(self._source_columns.options) + list(self._target_columns.options)
        # the new target column type values will be set to empty string
        for key in self._source_columns.options:
            self._target_columns_type_map[key] = ""
        self._source_columns.options = []

    def _move_all_back_to_source(self):
        """
        DESCRIPTION:    
            Private method that handles when the user wants to move all the target columns back to source columns.
        Called when the user selects the double left arrow button.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        # if there are no target columns to move to source columns then return
        if len(self._target_columns.options) == 0:
            return
        # new source columns options will be all target columns plus whatever options already exist in source columns
        self._source_columns.options = list(self._target_columns.options) + list(self._source_columns.options)
        self._target_columns.options = []
        self._target_columns_type_map = {}
        

    def _execute(self):
        """
        DESCRIPTION:
            Private function that executes the ipywidgets UI for Persist.

        PARAMETERS:
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            types = {}
            for key in self._target_columns_type_map:
                value_string = self._target_columns_type_map[key]
                value_string = value_string.strip()
                if value_string not in _UiImpl._type_names:
                    # Data arguments specifed
                    value_type = None
                    bracket_index_start = value_string.find("(")
                    bracket_index_end = value_string.find(")")
                    if bracket_index_start != -1 and bracket_index_end != -1 and bracket_index_start < bracket_index_end:
                        args = value_string[bracket_index_start+1:bracket_index_end]
                        args = args.split(",")
                        type_name = value_string[:bracket_index_start]
                        if type_name == "VARCHAR":
                            value_type = self._validate_varchar(args)
                    if value_type == None:
                        raise Exception("Illegal type :" + value_string)
                else:       
                    value_type = _UiImpl._type_names[value_string]
                types[key] = None if value_type == None else value_type

            self._df.to_sql(
                            table_name=self._table_name.value,
                            if_exists=self._if_exists.value,
                            primary_index=None if self._primary_index.value == ""  else self._primary_index.value,
                            temporary=self._temporary.value,
                            schema_name=None if self._schema_name.value == ""  else self._schema_name.value,
                            types=None if len(types) == 0 else types,
                            primary_time_index_name=None if self._primary_time_index_name.value == ""  else self._primary_time_index_name.value,
                            timecode_column=None if self._timecode_column.value == ""  else self._timecode_column.value,
                            timebucket_duration=None if self._timebucket_duration.value == ""  else self._timebucket_duration.value,
                            timezero_date=None if self._timezero_date.value == ""  else self._timezero_date.value,
                            columns_list=None if self._columns_list.value == "" else self._columns_list.value,
                            sequence_column=None if self._sequence_column.value == ""  else self._sequence_column.value,
                            seq_max=None if self._seq_max.value == "" else self._seq_max.value,
                            set_table=self._set_table.value)
            self._error_label.value = ""

        except Exception as e:
            self._error_label.value = str(e)

    def _create_ui(self):      
        """
        DESCRIPTION:
            Private function that creates the ipywidgets UI for Persist.

        PARAMETERS:
        
        RAISES:
            None.

        RETURNS:
            None.
        """ 
        confirm_button = ipywidgets.Button(
            description='Execute',
            disabled=False,
            style = {'button_color' : '#4169E1', 'text_color' : 'white'},
            tooltip='Confirm to Persist the DataFrame in a table')
        confirm_button.on_click(lambda x: self._execute())
        self._error_label = ipywidgets.Label(
            disabled=False,
            style = {'text_color' : 'red'})

        self._line_divider = ipywidgets.HTML("<hr>")

        output_tab = self._create_output_tab()
        column_types_tab = self._create_column_types_tab()
        pti_tab = self._create_pti_tab()
        persist_tab = ipywidgets.Tab()
        persist_tab.children = [output_tab, column_types_tab, pti_tab]
        persist_tab.titles = ['Output', 'Column Type', 'Primary Time Index']
        self._persist_ui = ipywidgets.VBox([persist_tab, confirm_button, self._line_divider, self._error_label])
    
        
    def _open_ui(self):
        """
        DESCRIPTION:
            Private function that opens the teradatamlwidgets Persist UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        
        self._show_display(self._persist_ui, False)

    def get_widget(self):
        """
        DESCRIPTION:
            Private function that returns the Persist UI so that it can be called in EDA. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            Instance of Persist UI.
        """
        return self._persist_ui

    def _validate_varchar(self, args):
        """
        DESCRIPTION:
            Private function that validates the varchar type with user entered value. 

        PARAMETERS:
            args: 
                Required Argument. 
                Arguments the user has specified for the varchar.
                Type: list of str
        
        RAISES:
            None.

        RETURNS:
            A teradatamlsqlalchemy type if valid VARCHAR string.
        """
        if len(args) != 1:
            return None
        try:
            length_arg = int(args[0])
            result = VARCHAR(length_arg)
            return result
        except:
            return None
        
    # Mapping from string to sqlalchemy types
    _type_names = {
                    "" : None, 
                    "BYTEINT" : BYTEINT, "SMALLINT" : SMALLINT, "INTEGER" : INTEGER, "BIGINT" : BIGINT, 
                    "DECIMAL" : DECIMAL, "FLOAT" : FLOAT, "NUMBER" : NUMBER,
                    "TIMESTAMP" : TIMESTAMP, "DATE" : DATE, "TIME" : TIME, "CHAR" : CHAR, 
                    "VARCHAR" : VARCHAR, "CLOB" : CLOB, "BYTE" : BYTE, 
                    "VARBYTE" : VARBYTE, "BLOB" : BLOB, "PERIOD_DATE" : PERIOD_DATE, 
                    "PERIOD_TIME" : PERIOD_TIME, "PERIOD_TIMESTAMP" : PERIOD_TIMESTAMP,
                    "INTERVAL_YEAR" : INTERVAL_YEAR, "INTERVAL_YEAR_TO_MONTH" : INTERVAL_YEAR_TO_MONTH, "INTERVAL_MONTH" : INTERVAL_MONTH,
                    "INTERVAL_DAY" : INTERVAL_DAY, "INTERVAL_DAY_TO_HOUR" : INTERVAL_DAY_TO_HOUR, "INTERVAL_DAY_TO_MINUTE" : INTERVAL_DAY_TO_MINUTE,
                    "INTERVAL_DAY_TO_SECOND" : INTERVAL_DAY_TO_SECOND, "INTERVAL_HOUR" : INTERVAL_HOUR,
                    "INTERVAL_HOUR_TO_MINUTE" : INTERVAL_HOUR_TO_MINUTE, "INTERVAL_HOUR_TO_SECOND" : INTERVAL_HOUR_TO_SECOND,
                    "INTERVAL_MINUTE" : INTERVAL_MINUTE, "INTERVAL_MINUTE_TO_SECOND" : INTERVAL_MINUTE_TO_SECOND, "INTERVAL_SECOND" : INTERVAL_SECOND
                    }


    
