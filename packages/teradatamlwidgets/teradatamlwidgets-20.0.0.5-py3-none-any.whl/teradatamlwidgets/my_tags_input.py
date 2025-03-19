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
'''

import ipywidgets as widgets

# This is added if the version of ipywidgets does not support the newer TagsInput
class MyTagsInput(widgets.HBox):
    def __init__(self, value, allow_duplicates, style, layout, direction = None, description_tooltip="", has_direction = False):
        self.value = []
        self.direction = []
        self.allow_duplicates = allow_duplicates
        self.allowed_tags = []
        self.tag_observers = []
        self.has_direction = has_direction
        
        self.tags = widgets.VBox([])
        add_tag = widgets.Button(description="+", layout=widgets.Layout(width="30px"), tooltip = description_tooltip)
        add_tag.on_click(lambda x : self.on_add_tag(x))
        remove_tag = widgets.Button(description="-", layout=widgets.Layout(width="30px"), tooltip = description_tooltip)
        remove_tag.on_click(lambda x : self.on_remove_tag(x))
        children = [add_tag, remove_tag, self.tags]

        if self.has_direction:
            self.tags_direction = widgets.VBox([])
            children.append(self.tags_direction)
        
        super().__init__(children, style=style, layout=layout)

        for i in range(len(value)):
            v = value[i]
            direction_value = "ASC"
            if self.has_direction and i < len(self.direction):
                direction_value = self.direction[i]
            self.add_tag(v, direction_value)
        
    def on_add_tag(self, changed):
        self.add_tag("", "ASC")
    
    def add_tag(self, value, direction_value):
        if value not in self.allowed_tags:
            self.allowed_tags = [value] + self.allowed_tags
        tag = widgets.Combobox(value=value, options=self.allowed_tags, layout=widgets.Layout(width="300px"))
        self.value.append(value)
        tag_index = len(self.tags.children)
        if self.has_direction:
            tag_direction = widgets.Dropdown(value=direction_value, options=["ASC", "DESC"], layout=widgets.Layout(width="70px"))
            self.direction.append(direction_value)
            tag_direction.observe(lambda x : self.on_tag_direction_changed(tag_index, x), names='value')
            self.tags_direction.children = list(self.tags_direction.children) + [tag_direction]
        tag.observe(lambda x : self.on_tag_changed(tag_index, x), names='value')
        self.tags.children = list(self.tags.children) + [tag]
        self.value_changed()
        
    def on_remove_tag(self, changed):
        if len(self.value)==0:
            return
        self.value = self.value[:-1]
        self.tags.children = list(self.tags.children[:-1])
        if self.has_direction:
            self.direction = self.direction[:-1]
            self.tags_direction.children = list(self.tags_direction.children[:-1])
        self.value_changed()

    def set_allowed_tags(self, allowed_tags):
        # We need to remove and then add them all back again - this is due to bug in ipywidgets that does not allow to update options
        # of a Combobox once it is created!
        
        # Do not update observers
        tag_observers = self.tag_observers
        self.tag_observers = []
        self.allowed_tags = allowed_tags
        old_tags = self.tags.children
        self.tags.children = []
        self.value = []
        self.direction = []
        if self.has_direction:
            self.tags_direction.children = []
        for i in range(len(old_tags)):
            old_tag = old_tags[i]
            direction_value = "ASC"
            if self.has_direction and i < len(self.direction):
                direction_value = self.direction[i]
            self.add_tag(old_tag.value, direction_value)
        self.tag_observers = tag_observers
    
    def on_tag_changed(self, tag_index, changed):
        self.value[tag_index] = self.tags.children[tag_index].value
        self.value_changed()

    def on_tag_direction_changed(self, tag_index, changed):
        self.direction[tag_index] = self.tags_direction.children[tag_index].value
        self.value_changed()

    def value_changed(self):
        # Update something changed
        change = {}
        change['owner'] = self
        for tag_observer in self.tag_observers:
            tag_observer(change)

    def observe(self, func, names, type=""):
        super().observe(func, names, type)
        if names == "value":
            self.tag_observers.append(func)
        
    

