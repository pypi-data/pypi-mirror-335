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


from teradatamlwidgets.byom_functions.UiImpl import _UiImpl

class Ui:
    """
    The teradatamlwidgets Interactive BYOM UI.
    """

    def __init__(
        self, 
        function = "DataRobotPredict", 
        byom_location = "", 
        data="", 
        model_id="", 
        model_table="", 
        default_database="", 
        connection = None):
        """
        DESCRIPTION:
            Constructor for teradatamlwidgets Interactive BYOM UI.

        PARAMETERS:
            function: 
                Optional Argument. 
                Specifies the name of the function. 
                Default Value: "DataRobotPredict"
                Permitted Values: "DataRobotPredict", "H2OPredict", "DataikuPredict", ONNXPredict", "PMMLPredict"
                Types: str

            byom_location: 
                Optional Argument. 
                Specifies the BYOM location. 
                Types: str

            data: 
                Required Argument. 
                Specifies the input teradataml DataFrame that contains the data to be scored. 
                Types: Str or teradataml DataFrame

            model_table: 
                Optional Argument. 
                Specifies the name of the table to retrieve external model from. 
                Types: str

            model_id: 
                Optional Argument. 
                Specifies the unique model identifier of the model to be retrieved. 
                Types: str

            connection: 
                Optional Argument. 
                Specifies the specific connection; the specific connection. It can accept either 
                connection created using teradataml or another platform.

            default_database: 
                Optional Argument. 
                Specifies the default database. 
                Types: str

        RETURNS:
            Instance of the UI class.

        RAISES:
            None.

        EXAMPLE:
        from teradatamlwidgets.byom_functions.Ui import * 
        ui = Ui(function = "DataRobotPredict", 
            byom_location = "mldb", 
            data="iris_test", 
            model_id="dr_iris_rf", 
            model_table="byom_models")
        """

        self._ui_impl = _UiImpl(
                        function = function, 
                        byom_location = byom_location, 
                        data=data, 
                        model_id=model_id, 
                        model_table=model_table, 
                        default_database=default_database, 
                        connection = connection)
            
    def get_output_dataframe(self):
        """
        DESCRIPTION:
            Access the output dataframe of running BYOM function.

        PARAMETERS:
            None.

        RAISES:
            None.
            
        RETURNS: 
            The output dataframe, the type is based on the connection.
            Type: teradataml.DataFrame
        
        EXAMPLE:
            df = ui.get_output_dataframe()
        """
        return self._ui_impl._get_output_dataframe()

