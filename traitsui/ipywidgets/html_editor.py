""" Defines the various html editors for the ipywidgets user interface toolkit.
"""
import ipywidgets as widgets

from traits.api import Str

from editor import Editor


class SimpleEditor(Editor):
    """ Simple style editor for HTML.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Flag for window styles:
    base_style = widgets.HTML

    # Is the HTML editor scrollable? This values override the default.
    scrollable = True

    # External objects referenced in the HTML are relative to this URL
    base_url = Str

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        wtype = self.base_style

        control = wtype(velue=self.str_value, description='')

        self.control = control
        self.base_url = factory.base_url
        self.sync_value(factory.base_url_name, 'base_url', 'from')

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        text = self.str_value
        if self.factory.format_text:
            text = self.factory.parse_text(text)

        self.control.value = text

    #-- Event Handlers -------------------------------------------------------

    def _base_url_changed(self):
        self.update_editor()

#-EOF--------------------------------------------------------------------------
