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


from teradatamlwidgets.script.UiImpl import _UiImpl


class Ui:
    """
    The teradatamlwidgets Interactive Script UI.
    """

    def __init__(
                self, 
                search_path="", 
                default_database="", 
                connection = None,
                data=None,
                script_name=None,
                files_local_path=None,
                script_command=None,
                delimiter="\t",
                returns=None,
                auth=None,
                charset=None,
                quotechar=None,
                data_partition_column=None,
                data_hash_column=None,
                data_order_column=None,
                is_local_order=False,
                sort_ascending=True,
                nulls_first=True
                ):
        """
        Constructor for teradatamlwidgets Interactive Script UI.

        PARAMETERS:

            search_path: 
                Required Argument. 
                Specifies the database search path for the SCRIPT execution.  
                Types: Str

            default_database: 
                Optional Argument. 
                Specifies the default database. 
                Types: str

            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection instance) or another platform.

            data:
                Required Argument.
                Specifies a teradataml DataFrame containing the input data for the
                script.
                Types: teradataml DataFrame or str

            script_name:
                Optional Argument.
                Specifies the name of user script.
                User script should have at least permissions of mode 644.
                Types: str

            files_local_path:
                Optional Argument.
                Specifies the absolute local path where user script and all supporting.
                files like model files, input data file reside.
                Types: str

            script_command:
                Optional Argument.
                Specifies the command/script to run.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns.
                Default Value: "\t" (tab)
                Types: str of length 1 character
                Notes:
                    1) This argument cannot be same as "quotechar" argument.
                    2) This argument cannot be a newline character i.e., '\\n'.

            returns:
                Optional Argument.
                Specifies output column definition.
                Types: Dictionary specifying column name to teradatasqlalchemy type mapping.
                Default: None
                Note:
                    User can pass a dictionary (dict or OrderedDict) to the "returns" argument,
                    with the keys ordered to represent the order of the output columns.
                    Teradata recommends to use OrderedDict.

            auth:
                Optional Argument.
                Specifies an authorization to use when running the script.
                Types: str

            charset:
                Optional Argument.
                Specifies the character encoding for data.
                Permitted Values: utf-16, latin
                Types: str

            quotechar:
                Optional Argument.
                Specifies a character that forces all input and output of the script
                to be quoted using this specified character.
                Using this argument enables the Advanced SQL Engine to distinguish
                between NULL fields and empty strings. A string with length zero is
                quoted, while NULL fields are not.
                If this character is found in the data, it will be escaped by a second
                quote character.
                Types: character of length 1
                Notes:
                    1) This argument cannot be same as "delimiter" argument.
                    2) This argument cannot be a newline character i.e., '\\n'.

            data_partition_column:
                Optional Argument.
                Specifies Partition By columns for "data".
                Values to this argument can be provided as a list, if multiple
                columns are used for partition.
                Default Value: ANY
                Types: str OR list of Strings (str)
                Note:
                    1) "data_partition_column" cannot be specified along with
                       "data_hash_column".
                    2) "data_partition_column" cannot be specified along with
                       "is_local_order = True".

            data_hash_column:
                Optional Argument.
                Specifies the column to be used for hashing.
                The rows in the data are redistributed to AMPs based on the hash value of
                the column specified.
                The user-installed script file then runs once on each AMP.
                If there is no "data_partition_column", then the entire result set,
                delivered by the function, constitutes a single group or partition.
                Types: str
                Note:
                    "data_hash_column" cannot be specified along with
                    "data_partition_column", "is_local_order" and "data_order_column".
            
            data_order_column:
                Optional Argument.
                Specifies Order By columns for "data".
                Values to this argument can be provided as a list, if multiple
                columns are used for ordering. This argument is used with in both cases:
                "is_local_order = True" and "is_local_order = False".
                Types: str OR list of Strings (str)
                Note:
                    "data_order_column" cannot be specified along with "data_hash_column".


            is_local_order:
                Optional Argument.
                Specifies a boolean value to determine whether the input data is to be
                ordered locally or not. Order by specifies the order in which the
                values in a group, or partition, are sorted. Local Order By specifies
                orders qualified rows on each AMP in preparation to be input to a table
                function. This argument is ignored, if "data_order_column" is None. When
                set to True, data is ordered locally.
                Default Value: False
                Types: bool
                Note:
                    1) "is_local_order" cannot be specified along with "data_hash_column".
                    2) When "is_local_order" is set to True, "data_order_column" should be
                       specified, and the columns specified in "data_order_column" are
                       used for local ordering.

            sort_ascending:
                Optional Argument.
                Specifies a boolean value to determine if the result set is to be sorted
                on the "data_order_column" column in ascending or descending order.
                The sorting is ascending when this argument is set to True, and descending
                when set to False. This argument is ignored, if "data_order_column" is
                None.
                Default Value: True
                Types: bool

            nulls_first:
                Optional Argument.
                Specifies a boolean value to determine whether NULLS are listed first or
                last during ordering. This argument is ignored, if "data_order_column" is
                None. NULLS are listed first when this argument is set to True, and last
                when set to False.
                Default Value: True
                Types: bool
                

        RETURNS:
            Instance of the UI class.

        RAISES:
            None.

        EXAMPLE:
        >>> from teradatamlwidgets.script.Ui import * 
        >>> ui = Ui(search_path = "alice")
        """
        
        self._ui_impl=_UiImpl(
                        search_path=search_path, 
                        default_database=default_database, 
                        connection=connection,
                        data=data,
                        script_name=script_name,
                        files_local_path=files_local_path,
                        script_command=script_command,
                        delimiter=delimiter,
                        returns=returns,
                        auth=auth,
                        charset=charset,
                        quotechar=quotechar,
                        data_partition_column=data_partition_column,
                        data_hash_column=data_hash_column,
                        data_order_column=data_order_column,
                        is_local_order=is_local_order,
                        sort_ascending=sort_ascending,
                        nulls_first=nulls_first)

    def get_output_dataframe(self):
        """
        DESCRIPTION:
            Function returns the STO dataframe output generated.

        PARAMETERS:
            None.

        RETURNS:
            teradataml.DataFrame 
        """
        return self._ui_impl._get_output_dataframe()
    
