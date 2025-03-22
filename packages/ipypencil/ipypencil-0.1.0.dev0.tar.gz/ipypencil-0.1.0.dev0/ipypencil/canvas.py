#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Matthias Fischer.
# Distributed under the terms of the Modified BSD License.

import base64
import numpy as np

from ipywidgets import DOMWidget, ValueWidget, register
from traitlets import Int, Float, Unicode
from ._frontend import module_name, module_version


@register
class Canvas(DOMWidget, ValueWidget):
    """A canvas widget for drawing in Jupyter notebooks.
    
    Allows specifying size in pixels and zoom level for display.
    Outputs the image as uncompressed byte array.
    """
    
    # Sync with frontend
    _model_name = Unicode('CanvasModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('CanvasView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)
    
    # Canvas properties
    width = Int(28).tag(sync=True)   # Canvas width in pixels
    height = Int(28).tag(sync=True)  # Canvas height in pixels
    zoom = Float(8.0).tag(sync=True)  # Zoom level for display
    
    # Canvas image as byte array
    base64_data = Unicode('').tag(sync=True)
    
    def __init__(self, width=28, height=28, zoom=8.0, **kwargs):
        """Initialize the canvas widget.
        
        Parameters
        ----------
        width : int
            Width of the canvas in pixels
        height : int
            Height of the canvas in pixels
        zoom : float
            Initial zoom level for display
        """
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.zoom = zoom
    
    def clear(self):
        """Clear the canvas."""
        self.send({'action': 'clear'})
        
    def set_zoom(self, zoom):
        """Set the zoom level for display.
        
        Parameters
        ----------
        zoom : float
            Zoom level (1.0 is 100%)
        """
        if zoom > 0:
            self.zoom = zoom

    @property
    def image(self):  
        """Get the image as numpy array."
        """      
        # decode base64 data
        raw_bytes = base64.b64decode(self.base64_data)
        # convert to numpy array
        return np.array(np.frombuffer(raw_bytes, dtype=np.uint8))