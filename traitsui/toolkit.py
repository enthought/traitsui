#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#
#------------------------------------------------------------------------------

""" Defines the stub functions used for creating concrete implementations of
    the standard EditorFactory subclasses supplied with the Traits package.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

import pkg_resources
import logging

from traits.api import HasPrivateTraits, TraitError
from traits.trait_base import ETSConfig
import pyface.base_toolkit

#-------------------------------------------------------------------------
#  Logging:
#-------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# List of implemented UI toolkits:
TraitUIToolkits = ['qt4', 'wx', 'null']
not_implemented_message = "the '{}' toolkit does not implement this method"

#-------------------------------------------------------------------------
#  Data:
#-------------------------------------------------------------------------

# The current GUI toolkit object being used:
_toolkit = None

#-------------------------------------------------------------------------
#  Low-level GUI toolkit selection function:
#-------------------------------------------------------------------------

try:
    provisional_toolkit = ETSConfig.provisional_toolkit
except AttributeError:
    from contextlib import contextmanager

    # for backward compatibility
    @contextmanager
    def provisional_toolkit(toolkit_name):
        """ Perform an operation with toolkit provisionally set

        This sets the toolkit attribute of the ETSConfig object set to the
        provided value. If the operation fails with an exception, the toolkit
        is reset to nothing.
        """
        if ETSConfig.toolkit:
            raise AttributeError("ETSConfig toolkit is already set")
        ETSConfig.toolkit = toolkit_name
        try:
            yield
        except:
            # reset the toolkit state
            ETSConfig._toolkit = ''
            raise

try:
    import_name = pyface.base_toolkit.import_toolkit
except AttributeError:
    def import_toolkit(toolkit_name, entry_point='traitsui.toolkits'):
        """ Attempt to import an toolkit specified by an entry point.

        Parameters
        ----------
        toolkit_name : str
            The name of the toolkit we would like to load.
        entry_point : str
            The name of the entry point that holds our toolkits.

        Returns
        -------
        toolkit_object : callable
            A callable object that implements the Toolkit interface.

        Raises
        ------
        RuntimeError
            If no toolkit is found, or if the toolkit cannot be loaded for some
            reason.
        """
        print(entry_point, toolkit_name)
        plugins = list(pkg_resources.iter_entry_points(entry_point, toolkit_name))
        if len(plugins) == 0:
            msg = 'No {} plugin found for toolkit {}'
            msg = msg.format(entry_point, toolkit_name)
            logger.debug(msg)
            raise RuntimeError(msg)
        elif len(plugins) > 1:
            msg = ("multiple %r plugins found for toolkit %r: %s")
            modules = ', '.join(plugin.module_name for plugin in plugins)
            logger.warning(msg, entry_point, toolkit_name, modules)

        for plugin in plugins:
            try:
                toolkit_object = plugin.load()
            except (ImportError, AttributeError) as exc:
                msg = "Could not load plugin %r from %r"
                logger.info(msg, plugin.name, plugin.module_name)
                logger.debug(exc, exc_info=True)
            else:
                return toolkit_object
        else:
            msg = 'No {} plugin could be loaded for {}'
            msg = msg.format(entry_point, toolkit_name)
            logger.info(msg)
            raise RuntimeError(msg)


def assert_toolkit_import(names):
    """ Raise an error if a toolkit with the given name should not be allowed
    to be imported.
    """
    if ETSConfig.toolkit and ETSConfig.toolkit not in names:
        raise RuntimeError("Importing from %s backend after selecting %s "
                           "backend!" % (names[0], ETSConfig.toolkit))


def toolkit_object(name, raise_exceptions=False):
    """ Return the toolkit specific object with the given name.  The name
    consists of the relative module path and the object name separated by a
    colon.
    """
    global _toolkit
    if _toolkit is None:
        toolkit()
    return _toolkit(name)


def toolkit(*toolkits):
    """ Selects and returns a low-level GUI toolkit.

    Use this function to get a reference to the current toolkit.

    Parameters
    ----------
    *toolkits : strings
        Toolkit names to try if toolkit not already selected.  If not supplied,
        defaults to order in TraitUIToolkits variable.

    Returns
    -------
    toolkit
        Appropriate concrete Toolkit subclass for selected toolkit.
    """
    global _toolkit

    # If _toolkit has already been set, simply return it.
    if _toolkit is not None:
        return _toolkit

    if ETSConfig.toolkit:
        # If a toolkit has already been set for ETSConfig, then use it:
        _toolkit = import_toolkit(ETSConfig.toolkit)
        return _toolkit

    if not toolkits:
        toolkits = ('qt4', 'wx')

    # Try known toolkits first.
    for toolkit_name in toolkits:
        try:
            with provisional_toolkit(toolkit_name):
                _toolkit = import_toolkit(toolkit_name, 'traitsui.toolkits')
                return _toolkit
        except RuntimeError as exc:
            # not found or import failed, log exception and try again
            msg = "Could not import traits UI backend '{0}'"
            logger.info(msg.format(toolkit_name))
            if logger.getEffectiveLevel() <= logging.INFO:
                logger.exception(exc)

    # Try all non-null plugins we can find until success.
    for plugin in pkg_resources.iter_entry_points('traitsui.toolkits'):
        if plugin.name == 'null':
            continue
        try:
            with provisional_toolkit(plugin.name):
                _toolkit = plugin.load()
                return _toolkit
        except ImportError as exc:
            # not found or import failed, log exception and try again
            msg = "Could not import traits UI backend '{0}'"
            logger.info(msg.format(toolkit_name))
            if logger.getEffectiveLevel() <= logging.INFO:
                logger.exception(exc)

    # Try using the null toolkit and printing a warning
    try:
        with provisional_toolkit('null'):
            _toolkit = import_toolkit('null', 'traitsui.toolkits')
            import warnings
            msg = (
                "Unable to import the '{0}' backend for traits UI; " +
                "using the 'null' backend instead.")
            warnings.warn(msg.format(toolkit_name), RuntimeWarning)
            return _toolkit

    except ImportError as exc:
        logger.exception(exc)
        raise TraitError("Could not import any UI toolkit.")


#-------------------------------------------------------------------------
#  'Toolkit' class (abstract base class):
#-------------------------------------------------------------------------

class Toolkit(pyface.base_toolkit.Toolkit):
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

    #-------------------------------------------------------------------------
    #  Positions the associated dialog window on the display:
    #-------------------------------------------------------------------------

    def position(self, ui):
        """ Positions the associated dialog window on the display.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Shows a 'Help' window for a specified UI and control:
    #-------------------------------------------------------------------------

    def show_help(self, ui, control):
        """ Shows a Help window for a specified UI and control.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Sets the title for the UI window:
    #-------------------------------------------------------------------------

    def set_title(self, ui):
        """ Sets the title for the UI window.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Sets the icon for the UI window:
    #-------------------------------------------------------------------------

    def set_icon(self, ui):
        """ Sets the icon for the UI window.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Saves user preference information associated with a UI window:
    #-------------------------------------------------------------------------

    def save_window(self, ui):
        """ Saves user preference information associated with a UI window.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Rebuilds a UI after a change to the content of the UI:
    #-------------------------------------------------------------------------

    def rebuild_ui(self, ui):
        """ Rebuilds a UI after a change to the content of the UI.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Converts a keystroke event into a corresponding key name:
    #-------------------------------------------------------------------------

    def key_event_to_name(self, event):
        """ Converts a keystroke event into a corresponding key name.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Hooks all specified events for all controls in a ui so that they can be
    #  routed to the corrent event handler:
    #-------------------------------------------------------------------------

    def hook_events(self, ui, control, events=None, handler=None):
        """ Hooks all specified events for all controls in a UI so that they
            can be routed to the correct event handler.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Routes a 'hooked' event to the corrent handler method:
    #-------------------------------------------------------------------------

    def route_event(self, ui, event):
        """ Routes a "hooked" event to the corrent handler method.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Indicates that an event should continue to be processed by the toolkit
    #-------------------------------------------------------------------------

    def skip_event(self, event):
        """ Indicates that an event should continue to be processed by the
            toolkit.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Destroys a specified GUI toolkit control:
    #-------------------------------------------------------------------------

    def destroy_control(self, control):
        """ Destroys a specified GUI toolkit control.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Destroys all of the child controls of a specified GUI toolkit control:
    #-------------------------------------------------------------------------

    def destroy_children(self, control):
        """ Destroys all of the child controls of a specified GUI toolkit
            control.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Returns a ( width, height ) tuple containing the size of a specified
    #  toolkit image:
    #-------------------------------------------------------------------------

    def image_size(self, image):
        """ Returns a ( width, height ) tuple containing the size of a
            specified toolkit image.
        """
        raise NotImplementedError(
            not_implemented_message.format(ETSConfig.toolkit))

    #-------------------------------------------------------------------------
    #  Returns a dictionary of useful constants:
    #-------------------------------------------------------------------------

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
