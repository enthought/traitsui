""" Defines the various html editors for the ipywidgets user interface toolkit.
"""
import ipywidgets as widgets

from pyface.ui_traits import convert_bitmap

from .editor import Editor


class _ImageEditor(Editor):
    """ Simple 'display only' for Image Editor.
    """

    #-------------------------------------------------------------------------
    #  'Editor' interface
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        image = factory.image
        if image is None:
            image = self.value
        value = convert_bitmap(image)

        self.control = widgets.Image(value=value, description='')

        self.set_tooltip()

    def update_editor(self):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        if self.factory.image is not None:
            return

        image = self.value
        value = convert_bitmap(image)

        self.control.value = value
