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
from teradatamlwidgets.connection_teradataml import Connection
import ipywidgets
from IPython.display import clear_output, HTML,Javascript, display
import teradataml
from teradataml import get_connection, DataFrame
from teradatamlwidgets.base_ui import _BaseUi


class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Interactive Login UI.
    """

    def __init__(self, default_database="", val_location=None, connection = None, search_path=None):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Interactive Login UI.

        PARAMETERS:

             default_database: 
                Optional Argument. 
                Specifies the default database. 
                Types: str
                
            val_location
                Optional Argument. 
                Specifies the VAL location 
                Types: str
                
            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection instance) or another platform.

            search_path
                Optional Argument. 
                Specifies the search path location 
                Types: str

        RETURNS:
            Instance of the UI class.

        RAISES:
            None.

        EXAMPLE:
            >>> from teradatamlwidgets.login.Ui import * 
            >>> ui = Ui(default_database="dssDB")
        """
        
        _BaseUi.__init__(self, default_database=default_database, connection=connection, val_location=val_location, search_path=search_path)
        
        
        if self._connection.is_logged_in():
            self._create_ui()
            self._open_ui()

    
    def _create_ui(self):      
        """
        Private task that creates the teradatamlwidgets UI for Login

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """      
        self._logout_button = ipywidgets.Button(
            description='Logout',
            disabled=False,
            tooltip='Log out of connection',
        )
        self._logout_button.on_click(lambda x : self._on_logout())
        self._main_ui = ipywidgets.HBox([self._logout_button])
        

            
    def _open_ui(self):
        """
        Private function that opens the teradatamlwidgets UI 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._show_display(self._main_ui, True)

