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
#  Date:   11/01/2004
#
#------------------------------------------------------------------------------

""" Creates a panel-based wxPython user interface for a specified UI object.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
import wx.html as wh
import re

from cgi \
    import escape

from traits.api \
    import Instance, Undefined

from traitsui.api \
    import Group

from traits.trait_base \
    import enumerate

from traitsui.undo \
    import UndoHistory

from traitsui.dockable_view_element \
    import DockableViewElement

from traitsui.help_template \
    import help_template

from traitsui.menu \
    import UndoButton, RevertButton, HelpButton

from pyface.dock.api \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl

from pyface.sizers.flow \
    import FlowSizer

from helper \
    import position_window, TraitsUIPanel, TraitsUIScrolledPanel, GroupEditor

from constants \
    import screen_dx, screen_dy, WindowColor

from ui_base \
    import BaseDialog
from constants import is_mac

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Pattern of all digits
all_digits = re.compile( r'\d+' )

# Global font used for emphasis
emphasis_font = None

# Global color used for emphasis
emphasis_color = wx.Colour( 0, 0, 127 )

#-------------------------------------------------------------------------------
#  Creates a panel-based wxPython user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_panel ( ui, parent ):
    """ Creates a panel-based wxPython user interface for a specified UI object.
    """
    ui_panel_for( ui, parent, True )

#-------------------------------------------------------------------------------
#  Creates a subpanel-based wxPython user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_subpanel ( ui, parent ):
    """ Creates a subpanel-based wxPython user interface for a specified UI
        object. A subpanel does not allow control buttons (other than those
        specified in the UI object).
    """
    ui_panel_for( ui, parent, False )

#-------------------------------------------------------------------------------
#  Creates a panel-based wxPython user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_panel_for ( ui, parent, buttons ):
    """ Creates a panel-based wxPython user interface for a specified UI object.
    """
    # Disable screen updates on the parent control while we build the view:
    parent.Freeze()

    # Build the view:
    ui.control = control = Panel( ui, parent, buttons ).control

    # Allow screen updates to occur again:
    parent.Thaw()

    control._parent = parent
    control._object = ui.context.get( 'object' )
    control._ui     = ui
    try:
        ui.prepare_ui()
    except:
        control.Destroy()
        ui.control = None
        ui.result  = False
        raise
    ui.restore_prefs()
    ui.result = True

#-------------------------------------------------------------------------------
#  'Panel' class:
#-------------------------------------------------------------------------------

class Panel ( BaseDialog ):
    """ wxPython user interface panel for Traits-based user interfaces.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, ui, parent, allow_buttons ):
        """ Initializes the object.
        """
        self.ui = ui
        history = None
        view    = ui.view
        title   = view.title

        # Reset any existing history listeners:
        history = ui.history
        if history is not None:
            history.on_trait_change( self._on_undoable,
                                     'undoable', remove = True )
            history.on_trait_change( self._on_redoable,
                                     'redoable', remove = True )
            history.on_trait_change( self._on_revertable,
                                     'undoable', remove = True )

        # Determine if we need any buttons or an 'undo' history:
        buttons  = [ self.coerce_button( button ) for button in view.buttons ]
        nbuttons = len( buttons )
        if nbuttons == 0:
            if view.undo:
                self.check_button( buttons, UndoButton )
            if view.revert:
                self.check_button( buttons, RevertButton )
            if view.help:
                self.check_button( buttons, HelpButton )

        if allow_buttons and (history is None):
            for button in buttons:
                if (self.is_button( button, 'Undo' ) or
                    self.is_button( button, 'Revert' )):
                    history = UndoHistory()
                    break
        ui.history = history

        # Create a container panel to put everything in:
        cpanel = getattr( self, 'control', None )
        if cpanel is not None:
            cpanel.SetSizer( None )
            cpanel.DestroyChildren()
        else:
            if is_mac:
                # Groups with borders have a two-tone background, and the
                # getter is picking the wrong color.  Set to transparent
                # and hope that the parent has been painted.
                bg_color = wx.Colour(224, 224, 224, 0)
                self.control = cpanel = TraitsUIPanel( parent, -1,
                                                       bg_color=bg_color )
            else:
                self.control = cpanel = TraitsUIPanel( parent, -1 )

        # Create the actual trait sheet panel and embed it in a scrollable
        # window (if requested):
        sw_sizer = wx.BoxSizer( wx.VERTICAL )
        if ui.scrollable:
            sizer = wx.BoxSizer( wx.VERTICAL )
            sw    = TraitsUIScrolledPanel( cpanel )
            sizer.Add( panel( ui, sw ), 1, wx.EXPAND )

            sw.SetSizerAndFit( sizer )
            sw.SetScrollRate( 16, 16 )
        else:
            sw = panel( ui, cpanel )

        if ((title != '') and
            (not isinstance( getattr( parent, 'owner', None ), DockWindow ))):
            sw_sizer.Add( heading_text( cpanel, text = title ).control, 0,
                          wx.EXPAND )

        self.add_toolbar( sw_sizer )

        sw_sizer.Add( sw, 1, wx.EXPAND )

        if (allow_buttons and
            ((nbuttons != 1) or (not self.is_button( buttons[0], '' )))):
            # Add the special function buttons:
            sw_sizer.Add( wx.StaticLine( cpanel, -1 ), 0, wx.EXPAND )
            b_sizer = wx.BoxSizer( wx.HORIZONTAL )
            for button in buttons:
                if self.is_button( button, 'Undo' ):
                    self.undo = self.add_button( button, b_sizer,
                                                 self._on_undo, False )
                    self.redo = self.add_button( button, b_sizer,
                                                 self._on_redo, False, 'Redo' )
                    history.on_trait_change( self._on_undoable, 'undoable',
                                             dispatch = 'ui' )
                    history.on_trait_change( self._on_redoable, 'redoable',
                                             dispatch = 'ui' )
                elif self.is_button( button, 'Revert' ):
                    self.revert = self.add_button( button, b_sizer,
                                                   self._on_revert, False )
                    history.on_trait_change( self._on_revertable, 'undoable',
                                             dispatch = 'ui' )
                elif self.is_button( button, 'Help' ):
                    self.add_button( button, b_sizer, self._on_help )
                elif not self.is_button( button, '' ):
                    self.add_button( button, b_sizer )

            sw_sizer.Add( b_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )

        cpanel.SetSizerAndFit( sw_sizer )

    #---------------------------------------------------------------------------
    #  Handles an 'Undo' change request:
    #---------------------------------------------------------------------------

    def _on_undo ( self, event ):
        """ Handles a request to undo a change.
        """
        self.ui.history.undo()

    #---------------------------------------------------------------------------
    #  Handles a 'Redo' change request:
    #---------------------------------------------------------------------------

    def _on_redo ( self, event ):
        """ Handles a request to redo a change.
        """
        self.ui.history.redo()

    #---------------------------------------------------------------------------
    #  Handles a 'Revert' all changes request:
    #---------------------------------------------------------------------------

    def _on_revert ( self, event ):
        """ Handles a request to revert all changes.
        """
        ui = self.ui
        ui.history.revert()
        ui.handler.revert( ui.info )

    #---------------------------------------------------------------------------
    #  Handles the 'Help' button being clicked:
    #---------------------------------------------------------------------------

    def _on_help ( self, event ):
        """ Handles the **Help** button being clicked.
        """
        self.ui.handler.show_help( self.ui.info, event.GetEventObject() )

    #-----------------------------------------------------------------------
    #  Handles the undo history 'undoable' state changing:
    #-----------------------------------------------------------------------

    def _on_undoable ( self, state ):
        """ Handles a change to the "undoable" state of the undo history.
        """
        self.undo.Enable( state )

    #---------------------------------------------------------------------------
    #  Handles the undo history 'redoable' state changing:
    #---------------------------------------------------------------------------

    def _on_redoable ( self, state ):
        """ Handles a change to the "redoable" state of the undo history.
        """
        self.redo.Enable( state )

    #---------------------------------------------------------------------------
    #  Handles the 'revert' state changing:
    #---------------------------------------------------------------------------

    def _on_revertable ( self, state ):
        """ Handles a change to the "revert" state.
        """
        self.revert.Enable( state )

    #---------------------------------------------------------------------------
    #  Adds an optional tool bar to the dialog (base class override):
    #---------------------------------------------------------------------------

    def add_toolbar ( self, sizer ):
        """ Adds an optional toolbar to the dialog.
        """
        toolbar = self.ui.view.toolbar
        if toolbar is not None:
            self._last_group = self._last_parent = None
            sizer.Add( toolbar.create_tool_bar( self.control, self ),
                       0, wx.EXPAND )
            self._last_group = self._last_parent = None

#-------------------------------------------------------------------------------
#  Creates a panel-based wxPython user interface for a specified UI object:
#
#  Note: This version does not modify the UI object passed to it.
#-------------------------------------------------------------------------------

def panel ( ui, parent ):
    """ Creates a panel-based wxPython user interface for a specified UI object.

        This function does not modify the UI object passed to it
    """
    # Bind the context values to the 'info' object:
    ui.info.bind_context()

    # Get the content that will be displayed in the user interface:
    content = ui._groups

    # If there is 0 or 1 Groups in the content, create a single panel for it:
    if len( content ) <= 1:
        panel = TraitsUIPanel( parent, -1 )
        if len( content ) == 1:
            # Fill the panel with the Group's content:
            sg_sizer, resizable, contents = fill_panel_for_group( panel,
                                                                content[0], ui )
            sizer = panel.GetSizer()
            if sizer is not sg_sizer:
                sizer.Add( sg_sizer, 1, wx.EXPAND )

            # Make sure the panel and its contents have been laid out properly:
            sizer.Fit( panel )

        # Return the panel that was created:
        return panel

    # Create a notebook which will contain a page for each group in the content:
    nb    = create_notebook_for_items( content, ui, parent, None )
    nb.ui = ui

    # Notice when the notebook page changes (to display correct help)
    ###wx.EVT_NOTEBOOK_PAGE_CHANGED( parent, nb.GetId(), _page_changed )

    # Return the notebook as the result:
    return nb

#-------------------------------------------------------------------------------
#  Creates a notebook and adds a list of groups or items to it as separate
#  pages:
#-------------------------------------------------------------------------------

def create_notebook_for_items ( content, ui, parent, group,
                                item_handler = None, is_dock_window = False ):
    """ Creates a notebook and adds a list of groups or items to it as separate
        pages.
    """
    if is_dock_window:
        nb = parent
    else:
        dw = DockWindow( parent, handler      = ui.handler,
                                 handler_args = ( ui.info, ),
                                 id           = ui.id )
        if group is not None:
            dw.theme = group.dock_theme
        nb = dw.control
    pages     = []
    count     = 0
    has_theme = ((group is not None) and (group.group_theme is not None))

    # Create a notebook page for each group or item in the content:
    active = 0
    for index, item in enumerate( content ):
        if isinstance( item, Group ):
            # Create the group as a nested DockWindow item:
            if item.selected:
                active = index
            sg_sizer, resizable, contents = \
                fill_panel_for_group( nb, item, ui, suppress_label = True,
                                                    is_dock_window = True )

            # If the result is a region (i.e. notebook) with only one page,
            # collapse it down into just the contents of the region:
            if (isinstance( contents, DockRegion ) and
               (len( contents.contents ) == 1)):
                contents = contents.contents[0]

            # Add the content to the notebook as a new page:
            pages.append( contents )
        else:
            # Create the new page as a simple DockControl containing the
            # specified set of controls:
            page_name = item.get_label( ui )
            count    += 1
            if page_name == '':
               page_name = 'Page %d' % count

            sizer = wx.BoxSizer( wx.VERTICAL )
            if has_theme:
                image_panel, image_sizer = add_image_panel( nb, group )
                panel = image_panel.control
                image_sizer.Add( sizer, 1, wx.EXPAND )
            else:
                panel = TraitsUIPanel( nb, -1 )
                panel.SetSizer( sizer )

            pages.append( DockControl( name     = page_name,
                                       image    = item.image,
                                       id       = item.get_id(),
                                       style    = item.dock,
                                       dockable = DockableViewElement(
                                                      ui = ui, element = item ),
                                       export   = item.export,
                                       control  = panel ) )
            item_handler( item, panel, sizer )
            panel.GetSizer().Fit( panel )

    region = DockRegion( contents = pages, active = active )

    # If the caller is a DockWindow, return the region as the result:
    if is_dock_window:
        return region

    nb.SetSizer( DockSizer( contents = DockSection( contents = [ region ] ) ) )

    # Return the notebook as the result:
    return nb

#-------------------------------------------------------------------------------
#  Creates a themed ImagePanel for the specified group and parent window:
#-------------------------------------------------------------------------------

def add_image_panel ( window, group ):
    """ Creates a themed ImagePanel for the specified group and parent window.
    """
    from image_panel import ImagePanel

    image_panel = ImagePanel( theme = group.group_theme, text = group.label )
    panel       = image_panel.create_control( window )

    return ( image_panel, panel.GetSizer() )

#-------------------------------------------------------------------------------
#  Handles a notebook page being 'turned':
#-------------------------------------------------------------------------------

def _page_changed ( event ):
    nb = event.GetEventObject()
    nb.ui._active_group = event.GetSelection()

#-------------------------------------------------------------------------------
#  Displays a help window for the specified UI's active Group:
#-------------------------------------------------------------------------------

def show_help ( ui, button ):
    """ Displays a help window for the specified UI's active Group.
    """
    group    = ui._groups[ ui._active_group ]
    template = help_template()
    if group.help != '':
        header = template.group_help % escape( group.help )
    else:
        header = template.no_group_help
    fields = []
    for item in group.get_content( False ):
        if not item.is_spacer():
            fields.append( template.item_help % (
                           escape( item.get_label( ui ) ),
                           escape( item.get_help( ui ) ) ) )
    html = template.group_html % ( header, '\n'.join( fields ) )
    HTMLHelpWindow( button, html, .25, .33 )

#-------------------------------------------------------------------------------
#  Displays a pop-up help window for a single trait:
#-------------------------------------------------------------------------------

def show_help_popup ( event ):
    """ Displays a pop-up help window for a single trait.
    """
    control  = event.GetEventObject()
    template = help_template()

    # Note: The following check is necessary because under Linux, we get back
    # a control which does not have the 'help' trait defined (it is the parent
    # of the object with the 'help' trait):
    help = getattr( control, 'help', None )
    if help is not None:
        html = template.item_html % ( control.GetLabel(), help )
        HTMLHelpWindow( control, html, .25, .13 )

#-------------------------------------------------------------------------------
#  Builds the user interface for a specified Group within a specified Panel:
#-------------------------------------------------------------------------------

def fill_panel_for_group ( panel, group, ui, suppress_label = False,
                           is_dock_window = False, create_panel = False ):
    """ Builds the user interface for a specified Group within a specified
        Panel.
    """
    fp = FillPanel( panel, group, ui, suppress_label, is_dock_window,
                    create_panel )
    return ( fp.control or fp.sizer, fp.resizable, fp.dock_contents )

#-------------------------------------------------------------------------------
#  'FillPanel' class:
#-------------------------------------------------------------------------------

class FillPanel ( object ):
    """ A subpanel for a single group of items.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, panel, group, ui, suppress_label, is_dock_window,
                   create_panel ):
        """ Initializes the object.
        """
        # Get the contents of the group:
        content = group.get_content()

        # Create a group editor object if one is needed:
        self.control       = self.sizer = editor = None
        self.ui            = ui
        self.group         = group
        self.is_horizontal = (group.orientation == 'horizontal')
        layout             = group.layout
        is_scrolled_panel  = group.scrollable
        is_splitter        = (layout == 'split')
        is_tabbed          = (layout == 'tabbed')
        id                 = group.id

        # Assume our contents are not resizable:
        self.resizable = False

        if is_dock_window and (is_splitter or is_tabbed):
            if is_splitter:
                self.dock_contents = self.add_dock_window_splitter_items(
                                              panel, content, group )
            else:
                self.resizable     = group.springy
                self.dock_contents = create_notebook_for_items( content, ui,
                                    panel, group, self.add_notebook_item, True )
            return

        theme = group.group_theme
        if (is_dock_window             or
            create_panel               or
            is_scrolled_panel          or
            (id != '')                 or
            (theme is not None)        or
            (group.visible_when != '') or
            (group.enabled_when != '')):
            if theme is not None:
                image_panel, image_sizer = add_image_panel( panel, group )
                new_panel       = image_panel.control
                suppress_label |= image_panel.can_show_text
            elif is_scrolled_panel:
                new_panel = TraitsUIScrolledPanel( panel )
                new_panel.SetMinSize( panel.GetMinSize() )
                self.resizable = True
            else:
                new_panel = TraitsUIPanel( panel, -1 )

            sizer = panel.GetSizer()
            if sizer is None:
                sizer = wx.BoxSizer( wx.VERTICAL )
                panel.SetSizer( sizer )
            self.control = panel = new_panel
            if is_splitter or is_tabbed:
                editor = DockWindowGroupEditor( control = panel, ui = ui )
            else:
                editor = GroupEditor( control = panel )
            if id != '':
                ui.info.bind( group.id, editor )
            if group.visible_when != '':
                ui.add_visible( group.visible_when, editor )
            if group.enabled_when != '':
                ui.add_enabled( group.enabled_when, editor )

        self.panel         = panel
        self.dock_contents = None

        # Determine the horizontal/vertical orientation of the group:
        if self.is_horizontal:
            orientation = wx.HORIZONTAL
        else:
            orientation = wx.VERTICAL

        # Set up a group with or without a border around its contents:
        label = ''
        if not suppress_label:
            label = group.label

        if group.show_border:
            box = wx.StaticBox( panel, -1, label )
            self._set_owner( box, group )
            self.sizer = wx.StaticBoxSizer( box, orientation )
        else:
            if layout == 'flow':
                self.sizer = FlowSizer( orientation )
            else:
                self.sizer = wx.BoxSizer( orientation )
            if label != '':
                self.sizer.Add( heading_text( panel, text = label ).control,
                                0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 4 )

        # If no sizer has been specified for the panel yet, make the new sizer
        # the layout sizer for the panel:
        if panel.GetSizer() is None:
            panel.SetSizer( self.sizer )

        # Set up scrolling now that the sizer has been set:
        if is_scrolled_panel:
            if self.is_horizontal:
                panel.SetupScrolling( scroll_y = False )
            else:
                panel.SetupScrolling( scroll_x = False )

        if is_splitter:
            dw = DockWindow( panel, handler      = ui.handler,
                                    handler_args = ( ui.info, ),
                                    id           = ui.id,
                                    theme        = group.dock_theme ).control
            if editor is not None:
                editor.dock_window = dw

            dw.SetSizer( DockSizer( contents =
                   self.add_dock_window_splitter_items( dw, content, group ) ) )
            self.sizer.Add( dw, 1, wx.EXPAND )
        elif len( content ) > 0:
            if is_tabbed:
                self.resizable = group.springy
                dw = create_notebook_for_items( content, ui, panel, group,
                                                self.add_notebook_item )
                if editor is not None:
                    editor.dock_window = dw

                self.sizer.Add( dw, self.resizable, wx.EXPAND )
            # Check if content is all Group objects:
            elif layout == 'fold':
                self.resizable = True
                self.sizer.Add( self.create_fold_for_items( panel, content ),
                                1, wx.EXPAND )
            elif isinstance( content[0], Group ):
                # If so, add them to the panel and exit:
                self.add_groups( content, panel )
            else:
                self.add_items(content, panel, self.sizer)

        # If the caller is a DockWindow, we need to define the content we are
        # adding to it:
        if is_dock_window:
            self.dock_contents = DockRegion( contents = [
                        DockControl( name     = group.get_label( self.ui ),
                                     image    = group.image,
                                     id       = group.get_id(),
                                     style    = group.dock,
                                     dockable = DockableViewElement(
                                                    ui = ui, element = group ),
                                     export   = group.export,
                                     control  = panel ) ] )

        # If we are using an background image, add the sizer to the image sizer:
        if theme is not None:
            image_sizer.Add( self.sizer, 1, wx.EXPAND )

    #---------------------------------------------------------------------------
    #  Adds a set of groups or items separated by splitter bars to a DockWindow:
    #---------------------------------------------------------------------------

    def add_dock_window_splitter_items ( self, window, content, group ):
        """ Adds a set of groups or items separated by splitter bars to a
            DockWindow.
        """
        contents = [ self.add_dock_window_splitter_item( window, item, group )
                     for item in content ]

        # Create a splitter group to hold the contents:
        result = DockSection( contents = contents, is_row = self.is_horizontal )

        # If nothing is resizable, then mark each DockControl as such:
        if not self.resizable:
            for item in result.get_controls():
                item.resizable = False

        # Return the DockSection we created:
        return result

    #---------------------------------------------------------------------------
    #  Adds a single group or item to a DockWindow:
    #---------------------------------------------------------------------------

    def add_dock_window_splitter_item ( self, window, item, group ):
        """ Adds a single group or item to a DockWindow.
        """
        if isinstance( item, Group ):
            sizer, resizable, contents = fill_panel_for_group( window,
                item, self.ui, suppress_label = True, is_dock_window = True )
            self.resizable |= resizable

            return contents

        orientation = wx.VERTICAL
        if self.is_horizontal:
            orientation = wx.HORIZONTAL
        sizer = wx.BoxSizer( orientation )

        if group.group_theme is not None:
            image_panel, image_sizer = add_image_panel( window, group )
            panel = image_panel.control
            image_sizer.Add( sizer, 1, wx.EXPAND )
        else:
            panel = TraitsUIPanel( window, -1 )
            panel.SetSizer( sizer )

        self.add_items( [ item ], panel, sizer )

        return DockRegion( contents = [
                 DockControl( name     = item.get_label( self.ui ),
                              image    = item.image,
                              id       = item.get_id(),
                              style    = item.dock,
                              dockable = DockableViewElement(
                                             ui = self.ui, element = item ),
                              export   = item.export,
                              control  = panel ) ] )

    #---------------------------------------------------------------------------
    #  Adds a set of groups or items as vertical notebook pages to a vertical
    #  notebook:
    #---------------------------------------------------------------------------

    def create_fold_for_items ( self, window, content ):
        """ Adds a set of groups or items as vertical notebook pages to a
            vertical notebook.
        """
        from themed_vertical_notebook import ThemedVerticalNotebook

        # Create the vertical notebook:
        nb     = ThemedVerticalNotebook( scrollable = True )
        result = nb.create_control( window )

        # Create the notebook pages:
        nb.pages = [ self.create_fold_for_item( nb, item ) for item in content ]

        # Return the notebook we created:
        return result

    #---------------------------------------------------------------------------
    #  Adds a single group or item to a vertical notebook:
    #---------------------------------------------------------------------------

    def create_fold_for_item ( self, notebook, item ):
        """ Adds a single group or item to a vertical notebook.
        """
        # Create a new notebook page:
        page = notebook.create_page()

        # Create the page contents:
        if isinstance( item, Group ):
            panel, resizable, contents = fill_panel_for_group( page.parent,
                item, self.ui, suppress_label = True, create_panel = True )
        else:
            panel = TraitsUIPanel( page.parent, -1 )
            sizer = wx.BoxSizer( wx.VERTICAL )
            panel.SetSizer( sizer )
            self.add_items( [ item ], panel, sizer )

        # Set the page name and control:
        page.name    = item.get_label( self.ui )
        page.control = panel

        # Return the new notebook page:
        return page

    #---------------------------------------------------------------------------
    #  Adds a single Item to a notebook:
    #---------------------------------------------------------------------------

    def add_notebook_item ( self, item, parent, sizer ):
        """ Adds a single Item to a notebook.
        """
        self.add_items( [ item ], parent, sizer )

    #---------------------------------------------------------------------------
    #  Adds a list of Group objects to the panel:
    #---------------------------------------------------------------------------

    def add_groups ( self, content, panel ):
        """ Adds a list of Group objects to the panel.
        """
        sizer = self.sizer

        # Process each group:
        for subgroup in content:
            # Add the sub-group to the panel:
            sg_sizer, sg_resizable, contents = \
                fill_panel_for_group( panel, subgroup, self.ui )

            # If the sub-group is resizable:
            if sg_resizable:

                # Then so are we:
                self.resizable = True

                # Add the sub-group so that it can be resized by the layout:
                sizer.Add( sg_sizer, 1, wx.EXPAND | wx.ALL, 2 )

            else:
                style    = wx.EXPAND | wx.ALL
                growable = 0
                if self.is_horizontal:
                    if subgroup.springy:
                        growable = 1
                    if subgroup.orientation == 'horizontal':
                        style |= wx.ALIGN_CENTER_VERTICAL
                sizer.Add( sg_sizer, growable, style, 2 )

    #---------------------------------------------------------------------------
    #  Adds a list of Item objects to the panel:
    #---------------------------------------------------------------------------

    def add_items ( self, content, panel, sizer ):
        """ Adds a list of Item objects to the panel.
        """
        # Get local references to various objects we need:
        ui      = self.ui
        info    = ui.info
        handler = ui.handler

        group            = self.group
        show_left        = group.show_left
        padding          = group.padding
        col              = -1
        col_incr         = 1
        self.label_flags = 0
        show_labels      = False
        for item in content:
            show_labels |= item.show_label
        if (not self.is_horizontal) and (show_labels or (group.columns > 1)):
            # For a vertical list of Items with labels or multiple columns, use
            # a 'FlexGridSizer':
            self.label_pad = 0
            cols           = group.columns
            if show_labels:
                cols    *= 2
                col_incr = 2
            flags       = wx.TOP | wx.BOTTOM
            border_size = 1
            item_sizer  = wx.FlexGridSizer( 0, cols, 0, 5 )
            if show_left:
                self.label_flags = wx.ALIGN_RIGHT
                if show_labels:
                    for i in range( 1, cols, 2 ):
                        item_sizer.AddGrowableCol( i )
        else:
            # Otherwise, the current sizer will work as is:
            self.label_pad = 4
            cols           = 1
            flags          = wx.ALL
            border_size    = 1
            item_sizer     = sizer

        # Process each Item in the list:
        for item in content:

            # Get the item theme (if any):
            theme = item.item_theme

            # Get the name in order to determine its type:
            name = item.name

            # Check if is a label:
            if name == '':
                label = item.label
                if label != '':
                    # Update the column counter:
                    col += col_incr

                    # If we are building a multi-column layout with labels,
                    # just add space in the next column:
                    if (cols > 1) and show_labels:
                        item_sizer.Add( ( 1, 1 ) )

                    if theme is not None:
                        from image_text import ImageText

                        label = ImageText( panel, theme, label )
                        item_sizer.Add( label, 0, wx.EXPAND )
                    elif item.style == 'simple':
                        # Add a simple text label:
                        label = wx.StaticText( panel, -1, label,
                                               style = wx.ALIGN_LEFT )
                        item_sizer.Add( label, 0, wx.EXPAND )
                    else:
                        # Add the label to the sizer:
                        label = heading_text( panel, text = label ).control
                        item_sizer.Add( label, 0,
                                        wx.TOP | wx.BOTTOM | wx.EXPAND, 3 )

                    if item.emphasized:
                        self._add_emphasis( label )

                # Continue on to the next Item in the list:
                continue

            # Update the column counter:
            col += col_incr

            # Check if it is a separator:
            if name == '_':
                for i in range( cols ):
                    if self.is_horizontal:
                        # Add a vertical separator:
                        line = wx.StaticLine( panel, -1,
                                              style = wx.LI_VERTICAL )
                        item_sizer.Add( line, 0,
                                        wx.LEFT | wx.RIGHT | wx.EXPAND, 2 )
                    else:
                        # Add a horizontal separator:
                        line = wx.StaticLine( panel, -1,
                                              style = wx.LI_HORIZONTAL )
                        item_sizer.Add( line, 0,
                                        wx.TOP | wx.BOTTOM | wx.EXPAND, 2 )
                    self._set_owner( line, item )
                # Continue on to the next Item in the list:
                continue

            # Convert a blank to a 5 pixel spacer:
            if name == ' ':
                name = '5'

            # Check if it is a spacer:
            if all_digits.match( name ):

                # If so, add the appropriate amount of space to the sizer:
                n = int( name )
                if self.is_horizontal:
                    item_sizer.Add( ( n, 1 ) )
                else:
                    spacer = ( 1, n )
                    item_sizer.Add( spacer )
                    if show_labels:
                        item_sizer.Add( spacer )

                # Continue on to the next Item in the list:
                continue

            # Otherwise, it must be a trait Item:
            object = eval( item.object_, globals(), ui.context )
            trait  = object.base_trait( name )
            desc   = trait.desc or ''
            label  = None

            # If we are displaying labels on the left, add the label to the
            # user interface:
            if show_left:
                if item.show_label:
                    label = self.create_label( item, ui, desc, panel,
                                               item_sizer,
                                               border=group.show_border )
                elif (cols > 1) and show_labels:
                    label = self.dummy_label( panel, item_sizer )

            # Get the editor factory associated with the Item:
            editor_factory = item.editor
            if editor_factory is None:
                editor_factory = trait.get_editor()

                # If still no editor factory found, use a default text editor:
                if editor_factory is None:
                    from text_editor import ToolkitEditorFactory
                    editor_factory = ToolkitEditorFactory()

                # If the item has formatting traits set them in the editor
                # factory:
                if item.format_func is not None:
                    editor_factory.format_func = item.format_func

                if item.format_str != '':
                    editor_factory.format_str = item.format_str

                # If the item has an invalid state extended trait name, set it
                # in the editor factory:
                if item.invalid != '':
                    editor_factory.invalid = item.invalid

            # Set up the background image (if used):
            item_panel = panel
            if theme is not None:
                from image_panel import ImagePanel

                text = ''
                if item.show_label:
                    text = item.get_label( ui )
                image_panel = ImagePanel( theme = theme, text = text )
                item_panel  = image_panel.create_control( panel )

            # Create the requested type of editor from the editor factory:
            factory_method = getattr( editor_factory, item.style + '_editor' )
            editor         = factory_method( ui, object, name, item.tooltip,
                                        item_panel ).set(
                                 item        = item,
                                 object_name = item.object )

            # Tell editor to actually build the editing widget:
            editor.prepare( item_panel )

            # Set the initial 'enabled' state of the editor from the factory:
            editor.enabled = editor_factory.enabled

            # Add emphasis to the editor control if requested:
            if item.emphasized:
                self._add_emphasis( editor.control )

            # Give the editor focus if it requested it:
            if item.has_focus:
                editor.control.SetFocus()

            # Adjust the maximum border size based on the editor's settings:
            border_size = min( border_size, editor.border_size )

            # Set up the reference to the correct 'control' to use in the
            # following section, depending upon whether we have wrapped an
            # ImagePanel around the editor control or not:
            control = editor.control
            if theme is None:
                width, height = control.GetSizeTuple()
            else:
                item_panel.GetSizer().Add( control, 1, wx.EXPAND )
                control       = item_panel
                width, height = image_panel.adjusted_size

            # Set the correct size on the control, as specified by the user:
            scrollable  = editor.scrollable
            item_width  = item.width
            item_height = item.height
            growable    = 0
            if (item_width != -1.0) or (item_height != -1.0):
                if (0.0 < item_width <= 1.0) and self.is_horizontal:
                    growable   = int( 1000.0 * item_width )
                    item_width = -1

                item_width = int( item_width )
                if item_width < -1:
                    item_width = -item_width
                elif item_width != -1:
                    item_width = max( item_width, width )

                if (0.0 < item_height <= 1.0) and (not self.is_horizontal):
                    growable    = int( 1000.0 * item_height )
                    item_height = -1

                item_height = int( item_height )
                if item_height < -1:
                    item_height = -item_height
                elif item_height != -1:
                    item_height = max( item_height, height )

                control.SetMinSize( wx.Size( item_width, item_height ) )

            # Bind the item to the control and all of its children:
            self._set_owner( control, item )

            # Bind the editor into the UIInfo object name space so it can be
            # referred to by a Handler while the user interface is active:
            id = item.id or name
            info.bind( id, editor, item.id )

            # Also, add the editors to the list of editors used to construct
            # the user interface:
            ui._editors.append( editor )

            # If the handler wants to be notified when the editor is created,
            # add it to the list of methods to be called when the UI is
            # complete:
            defined = getattr( handler, id + '_defined', None )
            if defined is not None:
                ui.add_defined( defined )

            # If the editor is conditionally visible, add the visibility
            # 'expression' and the editor to the UI object's list of monitored
            # objects:
            if item.visible_when != '':
                ui.add_visible( item.visible_when, editor )

            # If the editor is conditionally enabled, add the enabling
            # 'expression' and the editor to the UI object's list of monitored
            # objects:
            if item.enabled_when != '':
                ui.add_enabled( item.enabled_when, editor )

            # Add the created editor control to the sizer with the appropriate
            # layout flags and values:
            ui._scrollable |= scrollable
            item_resizable  = ((item.resizable is True) or
                               ((item.resizable is Undefined) and scrollable))
            if item_resizable:
                growable = growable or 500
                self.resizable = True
            elif item.springy:
                growable = growable or 500

            # The following is a hack to allow 'readonly' text fields to
            # work correctly (wx has a bug that setting wx.EXPAND on a
            # StaticText control seems to cause the text to be aligned higher
            # than it would be otherwise, causing it to misalign with its
            # label).
            layout_style = editor.layout_style
            if not show_labels:
                layout_style |= wx.EXPAND

            item_sizer.Add( control, growable,
                            flags | layout_style | wx.ALIGN_CENTER_VERTICAL,
                            max( 0, border_size + padding + item.padding ) )

            # If we are displaying labels on the right, add the label to the
            # user interface:
            if not show_left:
                if item.show_label:
                    label = self.create_label( item, ui, desc, panel,
                                               item_sizer, '', wx.RIGHT )
                elif (cols > 1) and show_labels:
                    label = self.dummy_label( panel, item_sizer )

            # If the Item is resizable, and we are using a multi-column grid:
            if item_resizable and (cols > 1):
                # Mark the entire row as growable:
                item_sizer.AddGrowableRow( col / cols )

            # Save the reference to the label control (if any) in the editor:
            editor.label_control = label

        # If we created a grid sizer, add it to the original sizer:
        if item_sizer is not sizer:
            growable = 0
            if self.resizable:
                growable = 1

            sizer.Add( item_sizer, growable, wx.EXPAND | wx.ALL, 2 )

    #---------------------------------------------------------------------------
    #  Creates an item label:
    #---------------------------------------------------------------------------

    def create_label ( self, item, ui, desc, parent, sizer, suffix = ':',
                       pad_side = wx.LEFT, border=False ):
        """ Creates an item label.
        """
        from image_text import ImageText

        label = item.get_label( ui )
        if (label == '') or (label[-1:] in '?=:;,.<>/\\"\'-+#|'):
            suffix = ''

        control = ImageText( parent, item.label_theme, label + suffix,
                             border=border )

        self._set_owner( control, item )

        if item.emphasized:
            self._add_emphasis( control )

        # XXX: Turning off help popups for now
        #wx.EVT_LEFT_UP( control, show_help_popup )

        control.help = item.get_help( ui )
        sizer.Add( control, 0, self.label_flags | wx.ALIGN_CENTER_VERTICAL |
                               pad_side, self.label_pad )

        if desc != '':
            control.SetToolTipString( 'Specifies ' + desc )

        return control

    #---------------------------------------------------------------------------
    #  Creates a dummy item label:
    #---------------------------------------------------------------------------

    def dummy_label ( self, parent, sizer ):
        """ Creates an item label.
        """
        control = wx.StaticText( parent, -1, '', style = wx.ALIGN_RIGHT )
        sizer.Add( control, 0 )
        return control

    #---------------------------------------------------------------------------
    #  Adds 'emphasis' to a specified control:
    #---------------------------------------------------------------------------

    def _add_emphasis ( self, control ):
        """ Adds emphasis to a specified control's font.
        """
        global emphasis_font

        control.SetForegroundColour( emphasis_color )
        if emphasis_font is None:
            font          = control.GetFont()
            emphasis_font = wx.Font( font.GetPointSize() + 1,
                                     font.GetFamily(),
                                     font.GetStyle(),
                                     wx.BOLD )
        control.SetFont( emphasis_font )

    #---------------------------------------------------------------------------
    #  Sets the owner of a specified control and all of its children:
    #---------------------------------------------------------------------------

    def _set_owner ( self, control, owner ):
        control._owner = owner
        for child in control.GetChildren():
            self._set_owner( child, owner )

#-------------------------------------------------------------------------------
#  'DockWindowGroupEditor' class:
#-------------------------------------------------------------------------------

class DockWindowGroupEditor ( GroupEditor ):
    """ Editor for a group which displays a DockWindow.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # DockWindow for the group
    dock_window = Instance( wx.Window )

    #-- UI preference save/restore interface -----------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if isinstance( prefs, dict ):
            structure = prefs.get( 'structure' )
        else:
            structure = prefs
        self.dock_window.GetSizer().SetStructure( self.dock_window, structure )
        self.dock_window.Layout()

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return { 'structure': self.dock_window.GetSizer().GetStructure() }

    #-- End UI preference save/restore interface -------------------------------

#-------------------------------------------------------------------------------
#  'HTMLHelpWindow' class:
#-------------------------------------------------------------------------------

class HTMLHelpWindow ( wx.Frame ):
    """ Window for displaying Traits-based help text with HTML formatting.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, parent, html, scale_dx, scale_dy ):
        """ Initializes the object.
        """
        wx.Frame.__init__( self, parent, -1, 'Help', style = wx.SIMPLE_BORDER )
        self.SetBackgroundColour( WindowColor )

        # Wrap the dialog around the image button panel:
        sizer        = wx.BoxSizer( wx.VERTICAL )
        html_control = wh.HtmlWindow( self )
        html_control.SetBorders( 2 )
        html_control.SetPage( html )
        sizer.Add( html_control, 1, wx.EXPAND )
        sizer.Add( wx.StaticLine( self, -1 ), 0, wx.EXPAND )
        b_sizer = wx.BoxSizer( wx.HORIZONTAL )
        button  = wx.Button( self, -1, 'OK' )
        wx.EVT_BUTTON( self, button.GetId(), self._on_ok )
        b_sizer.Add( button, 0 )
        sizer.Add( b_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )
        self.SetSizer( sizer )
        self.SetSize( wx.Size( int( scale_dx * screen_dx ),
                               int( scale_dy * screen_dy ) ) )

        # Position and show the dialog:
        position_window( self, parent = parent )
        self.Show()

    #---------------------------------------------------------------------------
    #  Handles the window being closed:
    #---------------------------------------------------------------------------

    def _on_ok ( self, event ):
        """ Handles the window being closed.
        """
        self.Destroy()

#-------------------------------------------------------------------------------
#  Creates a PyFace HeadingText control:
#-------------------------------------------------------------------------------

HeadingText = None

def heading_text ( *args, **kw ):
    """ Creates a PyFace HeadingText control.
    """
    global HeadingText

    if HeadingText is None:
        from pyface.heading_text import HeadingText

    return HeadingText( *args, **kw )

