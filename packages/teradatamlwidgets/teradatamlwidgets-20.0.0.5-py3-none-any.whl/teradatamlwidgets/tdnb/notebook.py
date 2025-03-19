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

Primary Owner: pradeep.garre@teradata.com

'''


from teradatamlwidgets.tdnb.utils import run_notebook_helper, replace_widget_values
from nbconvert.preprocessors import CellExecutionError
import re


class Notebook:
    """
    Class to run a notebook from another notebook.
    """
    def __init__(self):
        """ Constructor for Notebook class. """
        self._is_execution_from_tdnb = False

    @staticmethod
    def run_notebook(path, timeout_seconds=None, arguments=None):
        """
        DESCRIPTION:
            Function to run the notebook.

        PARAMETERS:
            path:
                Required Argument.
                Specifies the path of notebook.
                Types: str

            timeout_seconds:
                Optional Argument.
                Specifies the timeout period in seconds to run the notebook.
                Note:
                    timeout period is for cell and not for entire notebook.
                Types: int OR float

            arguments:
                Optional Argument.
                Specifies the arguments to be used in place of widgets.
                Types: dict

        RAISES:
            None

        RETURNS:
            str, if executed notebook uses 'exit' method.

        EXAMPLES:
            # Example 1 : Run the notebook 'abc.ipynb'.
            from teradatamlwidgets import tdnb
            tdnb.run_notebook('abc.ipynb', arguments={'x': 5, y:'a'})

            # Example 2 : Run the notebook 'abc.ipynb'. Make sure to not run
            #             every cell more than 5 seconds.
            from teradatamlwidgets import tdnb
            tdnb.run_noteobok('abc.ipynb', arguments={'x': 5, y:'a'}, timeout=5)
        """
        try:
            result = run_notebook_helper(path, widget_values=arguments, timeout=timeout_seconds)
            return result
        except CellExecutionError as e:
            # Retrieve message from notebook execution.
            msg = re.findall('<TDNB_MSG>(.*)<TDNB_MSG>', str(e))
            if msg:
                return msg[-1]
            else:
                raise e

    def exit(self, message):
        """
        DESCRIPTION:
            Function to exit the notebook execution with a message.

        PARAMETERS:
            message:
                Required Argument.
                Specifies the message to be returned from the executed notebook to
                the executor notebook.
                Types: str

        RAISES:
            None

        RETURNS:
            str, if executed notebook uses 'exit' method.

        EXAMPLES:
            # Example 1 : Exit the notebook with "xyz".
            from teradatamlwidgets import tdnb
            tdnb.exit('xyz')
        """
        if self._is_execution_from_tdnb:
            # Building a custom message so that caller will decode
            # the message properly.
            message = "<TDNB_MSG>{}<TDNB_MSG>".format(message)
            raise Exception(message)

        return message

    def replace_widgets(self, source, destination, widget_values):
        """
        DESCRIPTION:
            Function to replace widget values and prepare a new notebook.

        PARAMETERS:
            source:
                Required Argument.
                Specifies the path of existing notebook.
                Types: str

            destination:
                Required Argument.
                Specifies the path for new notebook.
                Types: str

            widget_values:
                Required Argument.
                Specifies the arguments to be replaced in place of widgets.
                Types: dict

        RAISES:
            None

        RETURNS:
            None

        EXAMPLES:
            # Example 1 : Create a new notebook from existing notebook by
                          replacing the widget values with arguments.
            from teradatamlwidgets import tdnb
            tdnb.notebook.replace_widgets('abc.ipynb', 'pqr.ipynb', {'x':1, 'y':2})
        """
        replace_widget_values(source, destination, widget_values)

