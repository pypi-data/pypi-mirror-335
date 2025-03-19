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

import nbformat, copy


def _replace_widget_value(widget_code, value):
    """
    DESCRIPTION:
        Internal function to replace the widget with the argument passed by user.

    PARAMETERS:
        widget_code:
            Required Argument.
            Specifies the code for the corresponding cell.
            Types: str

        value:
            Optional Argument.
            Specifies the arguments passed by user.
            Types: dict

    RAISES:
        None

    RETURNS:
        str

    EXAMPLES:
        # Example 1 : replace widgets with arguments.
        _replace_widget_value("x=widget1.get('name1')", {"name1": 5})

    """
    # widget_code may come as below -
    #       x = tdnb.get('abc') OR x = tdnb.get("abc")
    # value will be a dictionary.
    for key_, value_ in value.items():
        pattern1 = "tdnb.get('{}')".format(key_)
        pattern2 = 'tdnb.get("{}")'.format(key_)
        value_ = "'{}'".format(value_) if isinstance(value_, str) else str(value_)
        if pattern1 in widget_code:
            widget_code = widget_code.replace(pattern1, value_)
        else:
            widget_code = widget_code.replace(pattern2, value_)
    return widget_code


def replace_widget_values(existing_notebook, new_notebook, widget_values):
    """
    Function to replace widget values from arguments.
    """
    return run_notebook_helper(existing_notebook, widget_values, new_notebook, run_=False)


def run_notebook_helper(existing_notebook, widget_values, new_notebook=None, run_=True, timeout=None):
    """
    DESCRIPTION:
        Function to either run the notebook and store the result as new notebook
        or to replace the widget values with given arguments.

    PARAMETERS:
        existing_notebook:
            Required Argument.
            Specifies the path to existing notebook.
            Types: str

        widget_values:
            Required Argument.
            Specifies the arguments to be passed for notebook.
            Types: dict

        new_notebook:
            Optional Argument.
            Specifies the new notebook to be created.
            Types: str

        run_:
            Optional Argument.
            A flag whether to run the existing notebook or create a new notebook from arguments.
            When set to True, the notebook is executed by replacing the
            widget values with arguments and result is stored in 'new_notebook'.
            Otherwise, 'existing_notebook' won't be executed instead 'new_notebook'
            is created by replacing the widget values with arguments from 'existing_notebook'.
            Types: str

        timeout:
            Required Argument.
            Specifies time out period in seconds for every cell.
            Types: str

    RAISES:
        None

    RETURNS:
        None

    EXAMPLES:
            # Example 1 : Run the notebook 'abc.ipynb'.
            run_notebook('abc.ipynb', widget_values={'x': 5, y:'a'})

            # Example 2 : create a new notebook 'pqr.ipynb' from 'abc.ipynb' by replacing
            #             the widget values with arguments.
            run_notebook('abc.ipynb', {'x': 5, y:'a'}, new_notebook='pqr.ipynb', run_=False)
    """

    notebook_ = nbformat.read(existing_notebook, nbformat.NO_CONVERT)

    if widget_values is None:
        widget_values = {}

    # Iterate through cells and replace the code with input.
    new_cell = None
    for cell in notebook_['cells']:
        if cell['cell_type'] == 'code':
            cell['source'] = _replace_widget_value(cell['source'], widget_values)
            cell['execution_count'] = None
            cell['outputs'] = []

            # Get a new cell. This is to identify whether the notebook is running
            # from another notebook.
            if new_cell is None:
                new_cell = copy.copy(cell)
                new_cell['source'] = 'from teradatamlwidgets import tdnb\ntdnb.notebook._is_execution_from_tdnb=True'

    # Run the notebook.
    if run_:
        try:
            from nbconvert.preprocessors import ExecutePreprocessor
            kw = {'kernel_name': 'python3'}
            if timeout:
                kw['timeout'] = timeout
            ep = ExecutePreprocessor(**kw)
            
            # Insert the new Cell at the beginning of notebook node.
            if new_cell:
                notebook_['cells'].insert(0, new_cell)

            ep.preprocess(notebook_)

        except Exception as e:
            raise e
        finally:

            if new_notebook:
                with open(new_notebook, 'w', encoding='utf-8') as fp:
                    nbformat.write(notebook_, fp, version=nbformat.NO_CONVERT)

                # Store it in HTML format.
                nb_html_name = "{}.html".format(new_notebook[:-6])
                from nbconvert import HTMLExporter
                html_exporter = HTMLExporter()
                html_data, resources = html_exporter.from_notebook_node(notebook_)
                # write to output file
                with open(nb_html_name, "w", encoding='utf-8') as f:
                    f.write(html_data)

    else:
        with open(new_notebook, 'w', encoding='utf-8') as fp:
            nbformat.write(notebook_, fp, version=nbformat.NO_CONVERT)
