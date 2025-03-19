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

from teradatamlwidgets.tdnb.notebook import Notebook
from teradatamlwidgets.tdnb.widgets import Widgets

class _TDnb:
    """ Class to hold notebook functions. """

    def __init__(self):
        """ Constructor for _TDnb. """
        self.notebook = Notebook()
        self.run_notebook =self.notebook.run_notebook
        self.exit = self.notebook.exit
        self.replace_widgets = self.notebook.replace_widgets

        self.widgets = Widgets()
        self.text = self.widgets.text
        self.get_argument = self.widgets.get_argument
        self.dropdown = self.widgets.dropdown
        self.multi_select = self.widgets.multi_select
        self.get = self.widgets.get
        self.get_all = self.widgets.get_all
        self.remove = self.widgets.remove
        self.remove_all = self.widgets.remove_all
