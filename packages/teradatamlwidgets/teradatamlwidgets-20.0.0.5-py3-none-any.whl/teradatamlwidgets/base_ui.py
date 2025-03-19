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
import IPython
from IPython.display import clear_output, HTML,Javascript, display
import teradataml
from teradataml import get_connection
from teradataml.context.context import _get_current_databasename

class _TDVBoxWidget(ipywidgets.VBox):
    """
    Overriden ipywidgets VBox which we use to avoid the standard repr being shown in notebook
    """
    def __repr__(self):
        return ""

class _BaseUi:
    """
    Base UI class - this is a private class and is meant to be overriden
    """
    
    show_native_dialog = True # "linux" in sys.platform.lower()
    
    def __init__(self, default_database="", connection = None, val_location=None, search_path=None, widget_output=None):
        """
        Constructor for the Base UI class - this is a private class and is meant to be overriden

        PARAMETERS:
            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection instance) or another platform.

            default_database: 
                Optional Argument. 
                Specifies the default database. 
                Types: str
                
            val_location
                Optional Argument. 
                Specifies the VAL location. 
                Types: str
                
            search_path: 
                Optional Argument. 
                Specifies the database search path for the SCRIPT execution.  
                Types: Str

            widget_output:
                Optional Argument.
                Specifies an ipywidget that this Ui should be embedded into, otherwise will create its own output.
                Default Value: None
                Types: ipywidgets.Output

        RETURNS:
            Instance of the UI class.

        RAISES:
            None.

        """

        self._login_info = {}
        self._connection = connection

        if not self._connection:
            self._connection = Connection()
        
        self._widget_output = widget_output
        if not self._widget_output:
            self._widget_output = ipywidgets.Output()
            self._main_panel = ipywidgets.HBox([])
            vbox = _TDVBoxWidget([self._main_panel, self._widget_output])
            IPython.display.display(vbox)
            
        self._val_location = val_location
        self._search_path = search_path
        self._default_db = default_database
        
        self._folder = os.path.realpath(os.path.dirname(__file__))
        with open(os.path.join(self._folder, "progress.gif"), 'rb') as f:
            img = f.read()
        self._loading_bar = ipywidgets.Image(value=img)
        self._show_display(self._loading_bar, False)

        self._login_info['username'] = ""
        self._login_info['password'] = ""
        self._login_info['default_db'] = ""
        self._login_info['val_location'] = ""
        self._login_info['search_path'] = ""
        if not self._connection.is_logged_in():
            self._login_info['default_db'] = default_database if default_database else _get_current_databasename()
            self._login_info['val_location'] = val_location if val_location != None else "VAL"
            self._login_info['search_path'] = search_path if search_path != None else _get_current_databasename()
            self._create_login_ui() 
        else:
            self._show_display(ipywidgets.HBox([]), True)
            
    def _show_error_message(self, e):
        """
        Private function that creates the ipywidgets UI for the Login screen.

        PARAMETERS:
            e: Exception error to show in UI
            Type instance of Exception
        
        RAISES:
            None.

        RETURNS:
            None.
        """ 
        output_value = '''
            require(
                ["base/js/dialog"], 
                function(dialog) {
                    dialog.modal({
                        title: "Error",
                        body: $("<div></div>").append('__BODY__'),
                        buttons: {
                            "OK": {
                            }}
                    });
                }
            );'''
        error_message = str(e)
        error_list = error_message.split("\n")
        filter_error_list = [line for line in error_list if not line.strip(" ").startswith("at")]
        error_message = "\n".join(filter_error_list)

        error_message = error_message.replace("'", '"')
        error_message = error_message.replace('\n', '<br>');
        output_value = output_value.replace("__BODY__", error_message)
        # use display on non-linux to avoid pressing OK twice
        if _BaseUi.show_native_dialog:
            error_message = '<h5>' + error_message + '</h5>'
            self._show_dialog(error_message)
            return
        else:
            IPython.display.display(Javascript(output_value))

        # Hide Progress Bar
        self._open_ui()
    
    def _create_login_ui(self):
        """
        Private function that creates the ipywidgets UI for the Login screen.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """ 
        self._show_display(self._loading_bar)

        self._host = ipywidgets.Text(
            value= self._login_info.get('host', ""),
            placeholder='Enter host URL',
            description='Host:',
        )
        self._username = ipywidgets.Text(
            value= self._login_info.get('username', ""),
            placeholder='Enter username',
            description='Username:',
            disabled=False
        )
        self._password = ipywidgets.Password(
            value=self._login_info.get('password', ""),
            placeholder='Enter password',
            description='Password:',
            disabled=False
        )
        if self._default_db:
            self._default_db_ui = ipywidgets.Text(
                value=self._login_info.get('default_db', ""),
                placeholder='Enter default database',
                description='Schema:',
                disabled=False
            )
        if self._val_location != None:
            self._val_location_ui = ipywidgets.Text(
                value=self._login_info.get('val_location', ""),
                placeholder='Enter VAL location',
                description='VAL:',
                disabled=False
            )
        if self._search_path != None:
            self._search_path_ui = ipywidgets.Text(
                value=self._login_info.get('search_path', ""),
                placeholder='Enter Script Search Path',
                description='Path:',
                disabled=False
            )
        
        self._output = ipywidgets.Output(layout={})

        self._login = ipywidgets.Button(description="Login")
        self._login.on_click(lambda x : self._on_login())
        
        ui_list = [self._host,self._username,self._password]
        if self._default_db:
            ui_list.append(self._default_db_ui)
        if self._val_location != None:
            ui_list.append(self._val_location_ui)
        if self._search_path != None:
            ui_list.append(self._search_path_ui)
        ui_list.append(self._output)
            
        self._login_ui = ipywidgets.HBox([ipywidgets.VBox(ui_list), self._login])
        self._show_display(self._login_ui)

        


    def _on_login(self):
        """
        Private function that takes the values from the Login UI and sets up a connection.

        PARAMETERS:
            None.

        RAISES:
            Exception
            
        RETURNS:
            None.
        """
        try:
            self._login_info['host'] = self._host.value
            self._login_info['username'] = self._username.value
            self._login_info['password'] = self._password.value
            if self._default_db:
                self._login_info['default_db'] = self._default_db_ui.value
            if self._val_location != None:
                self._login_info['val_location'] = self._val_location_ui.value
            if self._search_path != None:
                self._login_info['search_path'] = self._search_path_ui.value

            self._show_display(self._loading_bar, True)
            self._connection.login(self._login_info['host'], self._login_info['username'], self._login_info['password'], self._login_info.get('default_db', ''), self._login_info.get('val_location', ''))
            if not self._connection.is_logged_in():
                self._show_display(self._login_ui)
                return
            self._password.value = ""
            self._login_info['password'] = ""
            if not self._login_info.get('default_db', ''):
                self._login_info['default_db'] = _get_current_databasename()
            if not self._login_info.get('search_path', ''):
                self._login_info['search_path'] = _get_current_databasename()
            self._create_ui()
            self._open_ui()
        except Exception as e:
            self._show_display(self._login_ui)
            with self._widget_output:
                print(str(e))
            raise e

    def _on_logout(self):
        """
        Private function that allows for the logout, which calls _create_login_ui again.

        PARAMETERS:
            None.

        RAISES:
            None.
            
        RETURNS:
            None.
        """
        self._connection.logout()
        self._create_login_ui()

    def _show_display(self, item, clear=True):
        """
        Private function that displays a widget in the cell.

        PARAMETERS:
            item: 
                The widget you want to display.
                Types: ipywidget

            clear:
                Clear the cell.
                Default Value: True
                Types: bool

        RAISES:
            None.
            
        RETURNS:
            None.
        """
        if clear:
            self._widget_output.clear_output(wait=True)
        with self._widget_output:
            IPython.display.display(item)
            
    def _show_dialog(self, html, clear=True):
        """
        DESCRIPTION:
            Private function that shows a HTML message in the cell with a close button.

        PARAMETERS:
            html:
                Specifies the HTML message to be shown in the cell.
                Types: str

            clear:
                Optional Argument.
                Specifies if the HTML message should first clear the cell.
                Default Value: True
                Types: bool

        RAISES:
            None.
            
        RETURNS:
            None.
        """
        html = ipywidgets.HTML(value=html)
        close_button = ipywidgets.Button(description="Close")
        close_button.on_click(lambda x : self._open_ui())
        container = ipywidgets.VBox([html, close_button])
        self._show_display(container, clear)
        
    def _create_ui(self):
        """
        Private function that is meant to be overriden and purpose is to create the UI.

        PARAMETERS:
            None.

        RAISES:
            NotImplemented.
            
        RETURNS:
            None.
        """
        raise NotImplemented
    
    def _open_ui(self):
        """
        Private function that is meant to be overriden and purpose is to open the UI.

        PARAMETERS:
            None.

        RAISES:
            NotImplemented.
            
        RETURNS:
            None.
        """
        raise NotImplemented


