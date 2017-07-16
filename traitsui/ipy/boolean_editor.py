""" Defines the Boolean editors for the ipywidgets user interface toolkit.
"""
from ipywidgets import Checkbox

from editor import Editor
# widgets.Checkbox(
#     value=False,
#     description='Check me',
#     disabled=False
# )


class SimpleEditor(Editor):
    """ Simple style of editor for Boolean values, which displays a check box.
    """
    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = CheckBox()
        self.control.stateChanged.connect(self.update_object)
        self.set_tooltip()
