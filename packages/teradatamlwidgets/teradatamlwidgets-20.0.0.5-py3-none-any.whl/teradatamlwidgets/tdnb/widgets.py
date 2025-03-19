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


import ipywidgets as widgets
from teradatamlwidgets.exceptions import TeradataNotebookException

class Widgets:
    """ Class to create widgets in Teradata Notebook. """
    def __init__(self):
        # Store the reference of widgets so get calls will work seamlessly.
        self.widgets_buffer = {}

        # TODO: IPython widget is behaving same as dropdown. Make sure to implement
        #  properly in JavaScript.
        # def combobox(name: str, default_value: str, choices: str, label: str):
        #     """ Creates a combobox input widget with a given name, default value and choices. """
        #     combobox_widget = widgets.Combobox(
        #         value=default_value,
        #         placeholder='Choose Someone',
        #         options=choices,
        #         description=label,
        #         ensure_option=True,
        #         disabled=False
        #     )
        #     widgets_buffer[name] = combobox_widget
        #     return combobox_widget

    def dropdown(self, name: str, default_value: str, choices: list, label: str):
        """
        DESCRIPTION:
            Function to create dropdown widget.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the widget.
                Types: str

            default_value:
                Required Argument.
                Specifies the default value for widget.
                Types: str

            choices:
                Required Argument.
                Specifies the dropdown values.
                Types: list of str

            label:
                Required Argument.
                Specifies the label for widget.
                Types: str

        RAISES:
            None

        RETURNS:
            dropdown widget.

        Examples:
            Example 1: Create a dropdown widget by setting default value
                       as 1 and remaining dropdown values as 10, 20, 30.
            from teradatamlwidgets import tdnb
            tdnb.dropdown('name1', 1, [10, 20, 30], 'dd_label')
        """
        # Before creating widget, check if default value is already available
        # in choices or not. If not, insert it at 1st position.
        if default_value not in choices:
            choices.insert(0, default_value)

        dropdown_widget = widgets.Dropdown(
            options=choices,
            value=default_value,
            description=label,
            disabled=False,
        )
        self.widgets_buffer[name] = dropdown_widget
        return dropdown_widget

    def get(self, name: str):
        """
        DESCRIPTION:
            Function to get the value of widget.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the widget.
                Types: str

        RAISES:
            When widget is not available in current session.

        RETURNS:
            value of corresponding widget.

        Examples:
            from teradatamlwidgets import tdnb
            tdnb.dropdown('name1', 1, [10, 20, 30], 'dd_label')

            Example 1: get the value of widget name1.
            print(tdnb.get('name1'))
        """
        if name not in self.widgets_buffer:
            raise TeradataNotebookException(f"Widget '{name}' is not available in the current session.")

        return self.widgets_buffer[name].value

    def get_all(self):
        """
        DESCRIPTION:
            Function to get the values for all widgets used in current session.

        RAISES:
            None

        RETURNS:
            dict

        Examples:
            from teradatamlwidgets import tdnb
            tdnb.dropdown('name1', 1, [10, 20, 30], 'dd_label')
            tdnb.text('name2', 'xyz', 'txt_label')

            Example 1: get all the widget values in current session.
            print(tdnb.get_all())
        """
        return {name: self.widgets_buffer[name].value for name in self.widgets_buffer}

    def get_argument(self, name: str, default: str):
        """
        DESCRIPTION:
            Function to get the value of widget.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the widget.
                Types: str

            default:
                Required Argument.
                Specifies the default value if widget do not have any value.
                Types: str

        RAISES:
            None

        RETURNS:
            str

        Examples:
            from teradatamlwidgets import tdnb
            tdnb.dropdown('name1', 1, [10, 20, 30], 'dd_label')

            Example 1: get the value of widget name1.
            print(tdnb.get_argument('name1'))
        """
        if name in self.widgets_buffer:
            return self.get(name)
        return default

    def multi_select(self, name: str, default_value: str, choices: list, label: str):
        """
        DESCRIPTION:
            Function to create multiselect widget.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the widget.
                Types: str

            default_value:
                Required Argument.
                Specifies the default value for widget.
                Types: str

            choices:
                Required Argument.
                Specifies the dropdown values.
                Types: list of str

            label:
                Required Argument.
                Specifies the label for widget.
                Types: str

        RAISES:
            None

        RETURNS:
            tuple

        Examples:
            Example 1: Create a multiselect widget by setting default value
                       as 1 and remaining values as 10, 20, 30.
            from teradatamlwidgets import tdnb
            tdnb.multi_select('name1', 1, [10, 20, 30], 'mm_label')
        """
        # Before creating widget, check if default value is already available
        # in choices or not. If not, insert it at 1st position.
        if default_value not in choices:
            choices.insert(0, default_value)

        multiselect_widget = widgets.SelectMultiple(
            options=choices,
            value=[default_value],
            rows=len(choices)+1,
            description=label,
            disabled=False)
        self.widgets_buffer[name] = multiselect_widget
        return multiselect_widget

    def remove(self, name: str):
        """
        DESCRIPTION:
            Function to remove widget.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the widget.
                Types: str

        RAISES:
            None

        RETURNS:
            None

        Examples:
            from teradatamlwidgets import tdnb
            tdnb.dropdown('name1', 1, [10, 20, 30], 'dd_label')

            Example 1: Remove the widget name1.
            print(tdnb.remove('name1'))
        """
        self.widgets_buffer[name].close()
        self.widgets_buffer.pop(name)
        return

    def remove_all(self):
        """
        DESCRIPTION:
            Function to remove all the widgets.

        RAISES:
            None

        RETURNS:
            None

        Examples:
            from teradatamlwidgets import tdnb
            tdnb.dropdown('name1', 1, [10, 20, 30], 'dd_label')

            Example 1: Remove all the widgets from current session.
            print(tdnb.remove_all())
        """
        # Form a list. Reading dictionary directly wont work because elements
        # will popped up from same dictionary.
        widgets_ = [k for k in self.widgets_buffer.keys()]
        for widget_ in widgets_:
            self.remove(widget_)

    def text(self, name: str, default_value: str, label: str):
        """
        DESCRIPTION:
            Function to create text widget.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the widget.
                Types: str

            default_value:
                Required Argument.
                Specifies the default value for widget.
                Types: str

            label:
                Required Argument.
                Specifies the label for widget.
                Types: str

        RAISES:
            None

        RETURNS:
            text widget.

        Examples:
            Example 1: Create text widget "txt" with value as 'pqr'.
            print(tdnb.text('txt', 'pqr'))
        """
        text_widget = widgets.Text(
            value=default_value,
            placeholder='Type something',
            description=label,
            disabled=False)
        self.widgets_buffer[name] = text_widget
        return text_widget
