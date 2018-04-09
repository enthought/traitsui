#  Copyright (c) 2005-18, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/07/2004

"""
Defines the stub functions used for creating concrete implementations of
the standard EditorFactory subclasses supplied with the Traits package.

Most of the logic for determining which backend toolkit to use can now be
found in :py:mod:`pyface.base_toolkit`.
"""

from __future__ import absolute_import

import logging

from traits.trait_base import ETSConfig
from pyface.base_toolkit import Toolkit, find_toolkit


logger = logging.getLogger(__name__)

not_implemented_message = "the '{}' toolkit does not implement this method"

#: The current GUI toolkit object being used:
_toolkit = None


def assert_toolkit_import(names):
    """ Raise an error if a toolkit with the given name should not be allowed
    to be imported.
    """
    if ETSConfig.toolkit and ETSConfig.toolkit not in names:
        raise RuntimeError("Importing from %s backend after selecting %s "
                           "backend!" % (names[0], ETSConfig.toolkit))


def toolkit_object(name, raise_exceptions=False):
    """ Return the toolkit specific object with the given name.

    Parameters
    ----------
    name : str
        The relative module path and the object name separated by a colon.
    raise_exceptions : bool
        Whether or not to raise an exception if the name cannot be imported.

    Raises
    ------
    TraitError
        If no working toolkit is found.
    RuntimeError
        If no ETSConfig.toolkit is set but the toolkit cannot be loaded for
        some reason.  This is also raised if raise_exceptions is True the
        backend does not implement the desired object.
    """
    global _toolkit

    if _toolkit is None:
        toolkit()
    obj = _toolkit(name)

    if raise_exceptions and obj.__name__ == 'Unimplemented':
        raise RuntimeError("Can't import {} for backend {}".format(
            repr(name), _toolkit.toolkit))

    return obj


def toolkit(*toolkits):
    """ Selects and returns a low-level GUI toolkit.

    Use this function to get a reference to the current toolkit.

    Parameters
    ----------
    *toolkits : strings
        Toolkit names to try if toolkit not already selected.  If not supplied,
        will try all ``traitsui.toolkits`` entry points until a match is found.

    Returns
    -------
    toolkit
        Appropriate concrete Toolkit subclass for selected toolkit.

    Raises
    ------
    TraitError
        If no working toolkit is found.
    RuntimeError
        If no ETSConfig.toolkit is set but the toolkit cannot be loaded for
        some reason.
    """
    global _toolkit

    if _toolkit is None:
        if len(toolkits) > 0:
            _toolkit = find_toolkit('traitsui.toolkits', toolkits)
        else:
            _toolkit = find_toolkit('traitsui.toolkits')
    return _toolkit


class Toolkit(Toolkit):
    """ Abstract base class for GUI toolkits.
    """

    #-------------------------------------------------------------------------
    #  Create GUI toolkit specific user interfaces using information from the
    #  specified UI object:
    #-------------------------------------------------------------------------

    def ui_panel(self, ui, parent):
        """ Creates a GUI-toolkit-specific panel-based user interface using
            information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_subpanel(self, ui, parent):
        """ Creates a GUI-toolkit-specific subpanel-based user interface using
            information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_livemodal(self, ui, parent):
        """ Creates a GUI-toolkit-specific modal "live update" dialog user
            interface using information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_live(self, ui, parent):
        """ Creates a GUI-toolkit-specific non-modal "live update" window user
            interface using information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_modal(self, ui, parent):
        """ Creates a GUI-toolkit-specific modal dialog user interface using
            information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_nonmodal(self, ui, parent):
        """ Creates a GUI-toolkit-specific non-modal dialog user interface using
            information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_popup(self, ui, parent):
        """ Creates a GUI-toolkit-specific temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_popover(self, ui, parent):
        """ Creates a GUI-toolkit-specific temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_info(self, ui, parent):
        """ Creates a GUI-toolkit-specific temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ui_wizard(self, ui, parent):
        """ Creates a GUI-toolkit-specific wizard dialog user interface using
            information from the specified UI object.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def view_application(self, context, view, kind=None, handler=None,
                         id='', scrollable=None, args=None):
        """ Creates a GUI-toolkit-specific modal dialog user interface that
            runs as a complete application using information from the
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
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def position(self, ui):
        """ Positions the associated dialog window on the display.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def show_help(self, ui, control):
        """ Shows a Help window for a specified UI and control.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def set_title(self, ui):
        """ Sets the title for the UI window.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def set_icon(self, ui):
        """ Sets the icon for the UI window.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def save_window(self, ui):
        """ Saves user preference information associated with a UI window.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def rebuild_ui(self, ui):
        """ Rebuilds a UI after a change to the content of the UI.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def key_event_to_name(self, event):
        """ Converts a keystroke event into a corresponding key name.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def hook_events(self, ui, control, events=None, handler=None):
        """ Hooks all specified events for all controls in a UI so that they
            can be routed to the correct event handler.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def route_event(self, ui, event):
        """ Routes a "hooked" event to the corrent handler method.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def skip_event(self, event):
        """ Indicates that an event should continue to be processed by the
            toolkit.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def destroy_control(self, control):
        """ Destroys a specified GUI toolkit control.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def destroy_children(self, control):
        """ Destroys all of the child controls of a specified GUI toolkit
            control.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def image_size(self, image):
        """ Returns a ( width, height ) tuple containing the size of a
            specified toolkit image.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def constants(self):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:

            - WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    #-------------------------------------------------------------------------

    def color_trait(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def rgb_color_trait(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def rgba_color_trait(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def font_trait(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def kiva_font_trait(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  'Editor' class methods:
    #-------------------------------------------------------------------------

    def ui_editor(self):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  'EditorFactory' factory methods:
    #-------------------------------------------------------------------------

    def array_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def boolean_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def button_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def check_list_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def code_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def color_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def compound_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def custom_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def directory_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def drop_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def dnd_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def enum_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def file_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def font_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def key_binding_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def history_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def html_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def image_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def image_enum_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def instance_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def list_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def list_str_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def null_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def ordered_set_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def plot_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def range_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def rgb_color_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def rgba_color_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def shell_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def table_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def tabular_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def text_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def title_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def tree_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def tuple_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    def value_editor(self, *args, **traits):
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))
