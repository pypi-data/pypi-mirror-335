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
import ipywidgets
from IPython.display import clear_output, HTML, Javascript, display
from teradataml import * 
from teradatamlwidgets.plot.PlotImpl import _BasePlot, _LinePlot, _BarPlot, _ScatterPlot, _CorrPlot, _WigglePlot, _MeshPlot, _GeomPlot
from teradatamlwidgets.connection_teradataml import *
import IPython
from teradatamlwidgets.base_ui import _BaseUi
from teradataml.context.context import _get_current_databasename
import base64

class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Interactive Plot UI.
    """

    ui_plots = []
    def __init__(self, 
                current_plot = "Line", 
                table_name="", 
                df=None, 
                connection = None, 
                default_database="", 
                eda_mode = False,
                **kwargs):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Interactive Plot UI.

        PARAMETERS:
            df: 
                Required Argument.
                Specifies the name of database table.

            current_plot:
                Optional Argument. 
                Specifies the type of plot, there is regardless a drop down to choose from.

            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection instance) 
                or another platform.

            default_database: 
                Optional Argument. 
                Specifies the default database.

        RETURNS:
            Instance of the UI class

        """
        
        _BaseUi.__init__(self, connection=connection, default_database=default_database)

        self._kwargs = kwargs
        self._database_table_name = table_name
        self._current_plot = current_plot
        self._plot_map = {}
        self._df = df

        if 'plot_type' in self._kwargs:
            self._current_plot = self._kwargs['plot_type']

        # EDA Mode support
        self._eda_mode = eda_mode
        self._eda_open_ui = False
        self._download_ui = True

        if self._connection.is_logged_in():
            self._login_info['default_db'] = default_database if default_database else _get_current_databasename()
            self._login_info['val_location'] = "VAL"
            self._create_ui()
            self._open_ui()
            
    def _get_base_args(self):
        """
        Private method that returns properties the user has entered into UI

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            dict with key as property name and value it has in UI 
        """
        base_args = {}
        if self._grid_color.value:
            base_args["grid_color"] = self._grid_color.value 
        if self._grid_format.value:
            base_args["grid_format"] = self._grid_format.value
        if self._grid_linewidth.value:
            base_args["grid_linewidth"] = self._grid_linewidth.value
        if self._grid_linestyle.value:
            base_args["grid_linestyle"] = self._grid_linestyle.value
        base_args["xlabel"] = self._xlabel.value if self._xlabel.value else None
        base_args["xrange"] = (self._xmin.value, self._xmax.value) if self._xrange.value else None
        if self._xtick_format.value:
            base_args["xtick_format"] = self._xtick_format.value
        base_args["reverse_xaxis"] = self._reverse_xaxis.value
        base_args["ylabel"] = self._ylabel.value if self._ylabel.value else None
        base_args["yrange"]  = (self._ymin.value, self._ymax.value) if self._yrange.value else None
        if self._ytick_format.value:
            base_args["ytick_format"] = self._ytick_format.value
        base_args["reverse_yaxis"] = self._reverse_yaxis.value
        if self._cmap.value:
            base_args["cmap"] = self._cmap.value
        if self._legend.value:
            base_args["legend"] = self._legend.value.split(",")
            base_args["legend_style"] = self._legend_style.value
        if self._vmin.value:
            base_args["vmin"] = self._vmin.value
        if self._vmax.value:
            base_args["vmax"] = self._vmax.value
        if self._width.value != 640 or self._height.value != 480:
            base_args["figsize"] = (self._width.value, self._height.value)
        
        # Series values are lists
        base_args["color"] = []
        base_args["linestyle"] = []
        base_args["linewidth"] = []
        base_args["marker"] = []
        base_args["markersize"] = []
        
        for y_index in range(self._get_num_series_visible()):
            if self._color[y_index].value:
                base_args["color"].append(self._color[y_index].value)
            if self._linestyle[y_index].value:
                base_args["linestyle"].append(self._linestyle[y_index].value)
            if self._linewidth[y_index].value:
                base_args["linewidth"].append(self._linewidth[y_index].value)
            if self._marker[y_index].value:
                base_args["marker"].append(self._marker[y_index].value)
            if self._markersize[y_index].value:
                base_args["markersize"].append(self._markersize[y_index].value)

        if len(base_args["color"]) == 0:
            del base_args["color"]
        if len(base_args["linestyle"]) == 0:
            del base_args["linestyle"]
        if len(base_args["linewidth"]) == 0:
            del base_args["linewidth"]
        if len(base_args["marker"]) == 0:
            del base_args["marker"]
        if len(base_args["markersize"]) == 0:
            del base_args["markersize"]
            
        return base_args

    def _get_num_series_visible(self):
        """
        Private method that returns the number of visible series

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            int
        """
        return self._get_current_plot()._get_num_series_visible()

    def _do_plot(self):
        """
        Private method that executes the plot query and then shows result in cell

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        error_message = ""
        try:
            if self._eda_mode:
                self._progress_bar.layout.display = "inline"
                self._plot_button.layout.display = "none"
            else:
                self._show_display(self._loading_bar)
            self._contents = self._get_current_plot()._get_ui()
            with self._widget_output:
                self._get_current_plot()._do_plot(self._get_base_args())
        except Exception as e:
            error_message = str(e)
        if self._eda_mode:
            self._progress_bar.layout.display = "none"
            self._plot_button.layout.display = "inline"
        if error_message:
            with self._widget_output:
                print(error_message)
                self._download_widget.value = "<p color='red'>{}<p>".format(error_message)
            return
        self._widget_output.clear_output()
        tab_selected_index = self._tab.selected_index
        self._create_tab()
        self._tab.selected_index = tab_selected_index
        if self._download_ui:
            try:
                with open("plot.png", "rb") as image_file:
                    b64 = base64.b64encode(image_file.read())
                payload = b64.decode()
                html_button = '''<html>
                                <head>
                                <meta name="viewport" content="width=device-width, initial-scale=1">
                                </head>
                                <body>
                                <a download="{filename}" href="data:image/png;base64,{payload}" style="border-style:solid; border-color: #727d9c; color:#4169E1; padding: 5px; font-family:Arial;" > Download as PNG  <i title="Download plot as PNG" class="fa fa-download"></i>
                                </a>
                                </body>
                                </html>
                                '''.format(payload=payload,filename='Untitled.png')
                self._download_widget.value = html_button
            except:
                # Download was not possible
                self._download_widget.value = ""

        
    def _change_plot(self):
        """
        Private method changes the plot UI to the current plot selected by user

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """

        if self._eda_mode:
            self._image.layout.visibility = "hidden"
            if self._plot_menu.value == "":
                return
            self._show_display(self._loading_bar, False)

        self._widget_output.clear_output()
        self._contents = self._get_current_plot()._get_ui()
        tab_selected_index = self._tab.selected_index
        self._create_tab()
        self._tab.selected_index = tab_selected_index
        self._plot_button.disabled = False

        if self._eda_mode:
            self._show_display(self._plot_ui)
        
    def _get_current_plot(self):
        """
        Private method that returns the current plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            Instance of current internal plot 
            Type: PlotImpl
        """
        return self._plot_map[self._plot_menu.value]

    def _update_range(self):
        """
        Private method that enables or disables the XY min/max UI controls

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        self._xmin.disabled = not self._xrange.value
        self._xmax.disabled = not self._xrange.value
        self._ymin.disabled = not self._yrange.value
        self._ymax.disabled = not self._yrange.value

    def _get_series_value(self, name, default_value, index):
        """
        Private method that returns the series parameter the user may have specified 
        in constructor otherwise returns the default value

        PARAMETERS:
            name:
                Name of series value
                Type: Str

            default_value:
                The default value returned if series value was not set by user in constructor

            index:
                The index of the series value
                Type: int

        RAISES:
            None.

        RETURNS:
            Value of series value
            Types: int, str, float
        """
        value = default_value
        if name in self._kwargs:
            if type(self._kwargs[name])==list and index<len(self._kwargs[name]):
                value = self._kwargs[name][index]
            elif type(self._kwargs[name])==str:
                value = self._kwargs[name]
        return value

    def _create_series_tabs(self):
        """
        Private method that creates the series UI tab

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        self._color = []
        self._linestyle = []
        self._linewidth = []
        self._marker = []
        self._markersize = []
        
        
        self._series_tabs = []
        for y_index in range(_BasePlot.NUM_Y_SERIES):
            rows = []
            style_rows = []

            self._color.append(ipywidgets.Text(
                value=self._get_series_value('color', 'blue', y_index),
                tooltip='Specifies the color for the plot. argument: color',
                layout={'width': '200px'},
                description='Style Color:',
                disabled=False   
            ))
            style_rows.append(self._color[-1])


            self._linestyle.append(ipywidgets.Dropdown(
                options=['', '-', '--', '-.', ":"], 
                value=self._get_series_value('linestyle', '', y_index),
                tooltip='Specifies the line style for the plot. argument: linestyle',
                layout={'width': '200px'},
                description='Line Style:',
                disabled=False,
            ))
            style_rows.append(self._linestyle[-1])

            self._linewidth.append(ipywidgets.BoundedFloatText(
                value=self._get_series_value('linewidth', 0.8, y_index),
                tooltip='Specifies the line width for the plot. argument: linewidth',
                description='Line Width:',
                min=0.5,
                max=10,
                step = 0.1,
                layout={'width': '200px'},
                disabled=False
            ))

            style_rows.append(self._linewidth[-1])

            self._marker.append(ipywidgets.Text(
                value=self._get_series_value('marker', '', y_index),
                tooltip='Specifies the type of the marker to be used. argument: marker',
                description='Marker:',
                layout={'width': '200px'},
                disabled=False
            ))

            style_rows.append(self._marker[-1])

            self._markersize.append(ipywidgets.FloatText(
                value=self._get_series_value('markersize', 6, y_index),
                tooltip='Specifies the size of the marker.. argument: markersize',
                description='Marker Size:',
                layout={'width': '200px'},
                disabled=False
            ))

            style_rows.append(self._markersize[-1])

            rows.append(ipywidgets.HBox(style_rows))
            

            self._series_tabs.append(ipywidgets.VBox(rows))

    def _update_settings(self, plot_settings):
        """
        DESCRIPTION:
            Private function that saves latest values in UI into dictionary

        PARAMETERS:
            plot_settings:
                Specifies the dictionary where the ui values should be stored
                Types: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        plot_settings['title'] = self._title.value
        plot_settings['heading'] = self._heading.value
        plot_settings['xlabel'] = self._xlabel.value
        plot_settings['plot_type'] = self._plot_menu.value
        plot_settings['plot_type'] = self._plot_menu.value
        plot_settings['ylabel'] = self._ylabel.value
        plot_settings['grid_color'] = self._grid_color.value
        plot_settings['grid_format'] = self._grid_format.value
        plot_settings['grid_linewidth'] = self._grid_linewidth.value 
        plot_settings['grid_linestyle'] = self._grid_linestyle.value 
        plot_settings['cmap'] = self._cmap.value 
        plot_settings['vmin'] = self._vmin.value 
        plot_settings['vmax'] = self._vmax.value 
        plot_settings['legend'] = self._legend.value 
        plot_settings['legend_style'] = self._legend_style.value
        plot_settings['width'] = self._width.value 
        plot_settings['height'] = self._height.value 
        plot_settings['xtick_format'] = self._xtick_format.value 
        plot_settings['reverse_xaxis'] = self._reverse_xaxis.value 
        plot_settings['xrange'] = self._xrange.value 
        plot_settings['xmin'] = self._xmin.value 
        plot_settings['xmax'] = self._xmax.value
        plot_settings['ytick_format'] = self._ytick_format.value 
        plot_settings['reverse_yaxis'] = self._reverse_yaxis.value 
        plot_settings['yrange'] = self._yrange.value 
        plot_settings['ymin'] = self._ymin.value 
        plot_settings['ymax'] = self._ymax.value 
        current_plot = self._get_current_plot()._get_xy_settings(plot_settings)


    def _create_format_tab(self):
        """
        Private method that creates the format UI tab

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        rows = []
        self._title = ipywidgets.Text(
            value=self._kwargs.get('title', ''),
            tooltip='Specifies the title for the Axis. argument: title',
            placeholder='Enter your chart title',
            description='Title:',   
            layout={'width': '800px'},
            disabled=False   
        )
        rows.append(self._title)

        self._heading = ipywidgets.Text(
            value=self._kwargs.get('heading', ''),
            tooltip='Specifies the heading for the plot. argument: heading',
            placeholder='Enter your chart heading',
            layout={'width': '800px'},
            description='Heading:',
            disabled=False   
        )
        rows.append(self._heading)

        self._xlabel = ipywidgets.Text(
            value=self._kwargs.get('xlabel', ''),
            tooltip='Specifies the label for x-axis. argument: xlabel',
            layout={'width': '800px'},
            description='X Label:',
            disabled=False   
        )
        rows.append(self._xlabel)

        self._ylabel = ipywidgets.Text(
            value=self._kwargs.get('ylabel', ''),
            tooltip='Specifies the label for y-axis. argument: ylabel',
            layout={'width': '800px'},
            description='Y Label:',
            disabled=False)  
        rows.append(self._ylabel)


        grid_rows = []
        self._grid_color = ipywidgets.Text(
            value=self._kwargs.get('grid_color', 'gray'),
            tooltip='Specifies the color of the grid. argument: grid_color',
            layout={'width': '200px'},
            description='Grid Color:',
            disabled=False   
        )
        grid_rows.append(self._grid_color)

        self._grid_format = ipywidgets.Text(
            value=self._kwargs.get('grid_format', ''),
            tooltip='Specifies the format for the grid. argument: grid_format',
            layout={'width': '200px'},
            description='Grid Format:',
            disabled=False   
        )
        grid_rows.append(self._grid_format)

        self._grid_linewidth = ipywidgets.BoundedFloatText(
            value=self._kwargs.get('grid_linewidth', 0.8),
            tooltip='Specifies the line width of the grid. argument: grid_linewidth',
            description='Grid Width:',
            layout={'width': '200px'},
            min=0.4,
            max=10,
            step = 0.1,
            disabled=False
        )
        grid_rows.append(self._grid_linewidth)

        self._grid_linestyle = ipywidgets.Dropdown(
                options=['-', '--', '-.', ":"],
                value=self._kwargs.get('grid_linestyle', '-'),
                tooltip='Specifies the line style of the grid. argument: grid_linestyle',
                layout={'width': '200px'},
                description='Grid Style:',
                disabled=False,
            )
        grid_rows.append(self._grid_linestyle)


        rows.append(ipywidgets.HBox(grid_rows))

        color_map_row = []
        self._cmap = ipywidgets.Text(
            value=self._kwargs.get('cmap', ''),
            tooltip='Specifies the name of the colormap to be used for plotting. argument: cmap',
            layout={'width': '200px'},
            description='Color Map:',
            disabled=False   
        )
        color_map_row.append(self._cmap)
        
        self._vmin = ipywidgets.FloatText(
                description='Min:', 
                value=self._kwargs.get('vmin', 0),
                tooltip='Specifies the lower range of the color map. argument: vmin',
                layout={'width': '200px'},
                disabled=False
            )
        color_map_row.append(self._vmin)

        self._vmax = ipywidgets.FloatText(
                description='Max:',
                value=self._kwargs.get('vmax', 0),
                tooltip='Specifies the upper range of the color map. argument: vmax',
                layout={'width': '200px'},
                disabled=False
            )
        color_map_row.append(self._vmax)
        
        rows.append(ipywidgets.HBox(color_map_row))

        legend_row = []
        self._legend = ipywidgets.Textarea(
            value=self._kwargs.get('legend', ''),
            tooltip='Specifies the legend(s) for the Plot. argument: legend',
            layout={'width': '400px'},
            description='Legend:',
            disabled=False   
        )
        legend_row.append(self._legend)

        self._legend_style = ipywidgets.Dropdown(
            options=['upper right', 'upper left', 'lower right', 'lower left', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'],
            value=self._kwargs.get('legend_style', 'upper right'),
            tooltip='Specifies the location for legend to display on Plot image. By default, legend is displayed at upper right corner. argument: legend_style',
            description='Placement:',
            layout={'width': '200px'},
            disabled=False,
        )
        legend_row.append(self._legend_style)


        self._width = ipywidgets.BoundedIntText(
            value=self._kwargs.get('width', 640),
            tooltip='Specifies the figure size width. argument: width',
            description='Width:',
            layout={'width': '200px'},
            min=640,
            max=1200,
            step = 1,
            disabled=False
        )
        legend_row.append(self._width)

        self._height = ipywidgets.BoundedIntText(
            value=self._kwargs.get('height', 480),
            tooltip='Specifies the figure size height. argument: height',
            description='Height:',
            layout={'width': '200px'},
            min=480,
            max=1200,
            step = 1,
            disabled=False
        )
        legend_row.append(self._height)


        rows.append(ipywidgets.HBox(legend_row))

        # Final UI is a vertical layout of all rows
        return ipywidgets.VBox(rows)

    def _create_range_tab(self):
        """
        Private method that creates the range UI tab

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        rows = []

        x_axis = []
        self._xtick_format = ipywidgets.Text(
            value=self._kwargs.get('xticks', ''),
            tooltip='Specifies whether to format tick values for x-axis or not. argument: xticks',
            layout={'width': '400px'},
            description='X Ticks:',
            disabled=False   
        )
        x_axis.append(self._xtick_format)

        self._reverse_xaxis = ipywidgets.Checkbox(
            value=self._kwargs.get('reverse_xaxis', False),
            tooltip='Specifies whether to reverse tick values on x-axis or not. argument: reverse_xaxis',
            description='Reverse Ticks',
            disabled=False,
            indent=False
        )
        x_axis.append(self._reverse_xaxis)

        rows.append(ipywidgets.HBox(x_axis))


        x_axis_range = []
        self._xrange = ipywidgets.ToggleButton(
            value=self._kwargs.get('xrange', False),
            tooltip='Click if you want to change x-range. argument: xrange',
            description='Change X Range',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            layout={'width': '150px'},
        )
        self._xrange.observe(lambda x : self._update_range(), names='value')
        x_axis_range.append(self._xrange)

        self._xmin = ipywidgets.FloatText(
            value=self._kwargs.get('xmin', -100),
            tooltip='Specify minimum for x-range. argument: xmin',
            description='Min:',
            layout={'width': '200px'},
            disabled=True
        )
        x_axis_range.append(self._xmin)

        self._xmax = ipywidgets.FloatText(
            value=self._kwargs.get('xmax', 100),
            tooltip='Specify maximum for x-range. argument: xmax',
            description='Max:',
            layout={'width': '200px'},
            disabled=True
        )
        x_axis_range.append(self._xmax)

        rows.append(ipywidgets.HBox(x_axis_range))


        y_axis = []
        self._ytick_format = ipywidgets.Text(
            value=self._kwargs.get('yticks', ''),
            tooltip='Specifies whether to format tick values for y-axis or not. argument: yticks',
            layout={'width': '400px'},
            description='Y Ticks:',
            disabled=False   
        )
        y_axis.append(self._ytick_format)
        self._reverse_yaxis = ipywidgets.Checkbox(
            value=self._kwargs.get('reverse_yaxis', False),
            tooltip='Specifies whether to reverse tick values on y-axis or not. argument: reverse_yaxis',
            description='Reverse Ticks',
            disabled=False,
            indent=False
        )
        y_axis.append(self._reverse_yaxis)

        rows.append(ipywidgets.HBox(y_axis))


        y_axis_range = []
        self._yrange = ipywidgets.ToggleButton(
            value=self._kwargs.get('yrange', False),
            tooltip='Click if you want to change y-range. argument: yrange',
            description='Change Y Range',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            layout={'width': '150px'},
        )
        self._yrange.observe(lambda x : self._update_range(), names='value')
        y_axis_range.append(self._yrange)
        self._ymin = ipywidgets.FloatText(
            value=self._kwargs.get('ymin', -100),
            tooltip='Specify minimum for y-range. argument: ymin',
            description='Min:',
            layout={'width': '200px'},
            disabled=True
        )
        y_axis_range.append(self._ymin)
        self._ymax = ipywidgets.FloatText(
            value=self._kwargs.get('ymax', 100),
            tooltip='Specify maximum for x-range. argument: ymax',
            description='Max:',
            layout={'width': '200px'},
            disabled=True
        )
        y_axis_range.append(self._ymax)
        rows.append(ipywidgets.HBox(y_axis_range))

        return ipywidgets.VBox(rows)

    def _create_ui(self):
        """
        Private task that creates the teradatamlwidgets Plot UI

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """    
        if self._df == None and self._database_table_name == "":
            self._widget_output.clear_output(wait=True)
            with self._widget_output:
                print("You are logged in")
            return
        try:
            if self._df == None:
                df = DataFrame(self._database_table_name)
                self._df = df
            else:
                df = self._df
        except:
            self._on_logout(True)
            with self._widget_output:
                print("Error cannot load table", self._database_table_name)
            return
        self._plot_map["Line"] = _LinePlot(self, df)
        self._plot_map["Bar"] = _BarPlot(self, df)
        self._plot_map["Scatter"] = _ScatterPlot(self, df)
        self._plot_map["Corr"] = _CorrPlot(self, df)
        self._plot_map["Wiggle"] = _WigglePlot(self, df)
        self._plot_map["Mesh"] = _MeshPlot(self, df)
        self._plot_map["Geom"] = _GeomPlot(self, df)
        self._widget_output.clear_output(wait=True)

        if self._eda_mode:
            self._eda_open_ui = True
            self._open_ui()
            self._eda_open_ui = False



    def _open_ui(self):
        """
        Private function that opens the teradatamlwidgets Plot UI 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """

        if self._eda_mode and self._eda_open_ui:
            return
        self._plot_menu = ipywidgets.Dropdown(
            options=self._plot_map.keys(),
            value=self._current_plot,
            description='Chart Type:',
            disabled=False)
        self._plot_menu.observe(lambda x : self._change_plot(), names='value')

        self._plot_button = ipywidgets.Button(
            description='Plot',
            disabled=False,
            button_style='',
            style={'button_color' : '#4169E1', 'text_color' : 'white'},
            tooltip='Create Plot',
        )
        if "series" not in self._kwargs:
            self._plot_button.disabled = True
        self._plot_button.on_click(lambda x : self._do_plot())

        top_row = [self._plot_menu]

        bottom_row = [self._plot_button]

        if self._eda_mode: 
            self._folder = os.path.realpath(os.path.dirname(__file__))
            with open(os.path.join(self._folder, "..", "progress.gif"), 'rb') as f:
                img = f.read()
            self._progress_bar = ipywidgets.Image(value=img, layout=ipywidgets.Layout(width='200px'))
            bottom_row.append(self._progress_bar)
            self._progress_bar.layout.display = "none"

        if not self._download_ui:
            self._save_plot_file = ipywidgets.Text(
                value="",
                description="File Name",
                tooltip='Filename to save a figure to.'
            )

            self._save_plot_button = ipywidgets.Button(
                icon='floppy-o',
                disabled=False,
                layout=ipywidgets.Layout(width='40px'),
                style={'button_color' : 'transparent', 'text_color' : '#4169E1'},
                tooltip='Saves the plot to an image file.'
            )
            self._save_plot_button.on_click(lambda x: self._on_save_plot_click(self._save_plot_file.value))
            bottom_row.append(self._save_plot_file, self._save_plot_button)
        
        if self._download_ui:
            self._download_widget = ipywidgets.HTML("")
            bottom_row.append(self._download_widget)

        if not self._eda_mode:
            self._logout_button = ipywidgets.Button(
                description='Logout',
                disabled=False,
                tooltip='Log out of connection',
            )
            self._logout_button.on_click(lambda x : self._on_logout())
            bottom_row.append(self._logout_button)

        # HTML Message
        self._message_widget = ipywidgets.HTML("")
        bottom_row.append(self._message_widget)

        self._top_row = ipywidgets.HBox(top_row)
        self._bottom_row = ipywidgets.HBox(bottom_row)
        self._line_divider = ipywidgets.HTML("<hr>")

        if self._eda_mode:
            self._tab = ipywidgets.Tab()

        self._contents = self._get_current_plot()._get_ui()
        self._image = ipywidgets.Image(format='png')
        # Hide it by Default
        self._image.layout.visibility = "hidden"
        # base ui
        self._format_tab = self._create_format_tab()
        self._range_tab = self._create_range_tab()
        self._create_series_tabs()
        self._create_tab()

        if self._eda_mode:
            self._plot_ui = ipywidgets.VBox([self._top_row, self._tab, self._bottom_row, self._line_divider, self._image])
            self._show_display(self._plot_ui, False)
            self._plot_menu.value = self._current_plot


    def _on_save_plot_click(self, file_name):
        """
        Private function that creates all the tab widget and displays it in the cell

        PARAMETERS:
            file_name
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._get_current_plot()._plot.save(file_name)

    def _create_tab(self):
        """
        Private function that creates all the tab widget and displays it in the cell

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        if not self._eda_mode:
            self._tab = ipywidgets.Tab()
        children = [self._contents, self._format_tab, self._range_tab]
        titles = ['Chart', 'Format', 'Range']
        for y_index in range(self._get_num_series_visible()):
            children.append(self._series_tabs[y_index])
            titles.append('Y[{}]'.format(y_index))
        self._tab.children = children
        for index in range(len(titles)):
            self._tab.set_title(title=titles[index], index=index)
        
        if not self._eda_mode:
            self._plot_ui = ipywidgets.VBox([self._top_row, self._tab, self._bottom_row, self._line_divider, self._image])
            self._show_display(self._plot_ui, False)
    
