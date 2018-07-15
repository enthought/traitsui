from traitsui.toolkit import assert_toolkit_import
assert_toolkit_import(['ipywidgets'])

from traits.trait_notifiers import set_ui_handler
from pyface.base_toolkit import Toolkit as PyfaceToolkit
from traitsui.toolkit import Toolkit

from IPython.display import display
import ipywidgets


toolkit = PyfaceToolkit(
    'pyface',
    'ipywidgets',
    'traitsui.ipywidgets'
)

def ui_handler(handler, *args, **kwds):
    """ Handles UI notification handler requests that occur on a thread other
        than the UI thread.
    """
    # XXX should really have some sort of queue based system
    handler(*args, **kwds)

set_ui_handler(ui_handler)


class GUIToolkit(Toolkit):
    """ Implementation class for ipywidgets toolkit """

    def ui_panel(self, ui, parent):
        from .ui_panel import ui_panel
        ui_panel(ui, parent)

    def ui_live(self, ui, parent):
        from .ui_panel import ui_panel
        ui_panel(ui, parent)

    def view_application(self, context, view, kind=None, handler=None,
                         id='', scrollable=None, args=None):
        """ Creates a PyQt modal dialog user interface that
            runs as a complete application, using information from the
            specified View object.

        Parameters
        ----------
        context : object or dictionary
            A single object or a dictionary of string/object pairs, whose trait
            attributes are to be edited. If not specified, the current object is
            used.
        view : view or string
            A View object that defines a user interface for editing trait
            attribute values.
        kind : string
            The type of user interface window to create. See the
            **traitsui.view.kind_trait** trait for values and
            their meanings. If *kind* is unspecified or None, the **kind**
            attribute of the View object is used.
        handler : Handler object
            A handler object used for event handling in the dialog box. If
            None, the default handler for Traits UI is used.
        id : string
            A unique ID for persisting preferences about this user interface,
            such as size and position. If not specified, no user preferences
            are saved.
        scrollable : Boolean
            Indicates whether the dialog box should be scrollable. When set to
            True, scroll bars appear on the dialog box if it is not large enough
            to display all of the items in the view at one time.

        """
        ui = view.ui(
            context,
            kind=kind,
            handler=handler,
            id=id,
            scrollable=scrollable,
            args=args
        )
        display(ui.control)
        # XXX ideally this would spawn a web server that has enough support of
        # IPyWidgets to interface

    def rebuild_ui(self, ui):
        """ Rebuilds a UI after a change to the content of the UI.
        """
        if ui.control is not None:
            ui.recycle()
            ui.info.ui = ui
        ui.rebuild(ui, ui.parent)

    def constants(self):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:

            - 'WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        return {'WindowColor': None}


    def color_trait(self, *args, **traits):
        #import color_trait as ct
        #return ct.PyQtColor(*args, **traits)
        from traits.api import Unicode
        return Unicode

    def rgb_color_trait(self, *args, **traits):
        #import rgb_color_trait as rgbct
        #return rgbct.RGBColor(*args, **traits)
        from traits.api import Unicode
        return Unicode

    def font_trait(self, *args, **traits):
        #import font_trait as ft
        #return ft.PyQtFont(*args, **traits)
        from traits.api import Unicode
        return Unicode
