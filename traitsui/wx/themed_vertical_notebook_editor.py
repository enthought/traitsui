#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   07/07/2007
#
#-------------------------------------------------------------------------------

""" Traits UI vertical notebook editor for editing lists of objects with traits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Instance, Str, Any, List, Bool, Undefined, on_trait_change

from traits.trait_base \
    import user_name_for

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

from traitsui.ui_traits \
    import AView, ATheme

from themed_vertical_notebook \
    import ThemedVerticalNotebook

#-------------------------------------------------------------------------------
#  '_ThemedVerticalNotebookEditor' class:
#-------------------------------------------------------------------------------

class _ThemedVerticalNotebookEditor ( Editor ):
    """ Traits UI vertical notebook editor for editing lists of objects with
        traits.
    """

    #-- Trait Definitions ------------------------------------------------------

    # Is the notebook editor scrollable? This values overrides the default:
    scrollable = True

    #-- Private Traits ---------------------------------------------------------

    # The currently selected notebook page object (or objects):
    selected_item = Any
    selected_list = List

    # The ThemedVerticalNotebook we use to manager the notebook:
    notebook = Instance( ThemedVerticalNotebook )

    # Dictionary of page counts for all unique names:
    pages = Any( {} )

    #-- Editor Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        self.notebook = ThemedVerticalNotebook( **factory.get(
            'closed_theme', 'open_theme', 'multiple_open', 'scrollable',
            'double_click' ) ).set( editor = self )
        self.control = self.notebook.create_control( parent )

        # Set up the additional 'list items changed' event handler needed for
        # a list based trait:
        self.context_object.on_trait_change( self.update_editor_item,
                               self.extended_name + '_items?', dispatch = 'ui' )

        # Synchronize the editor selection with the user selection:
        if factory.multiple_open:
            self.sync_value( factory.selected, 'selected_list', 'both',
                             is_list = True )
        else:
            self.sync_value( factory.selected, 'selected_item', 'both' )

        self.set_tooltip()

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        # Replace all of the current notebook pages:
        self.notebook.pages = [ self._create_page( object )
                                for object in self.value ]

    def update_editor_item ( self, event ):
        """ Handles an update to some subset of the trait's list.
        """
        # Replace the updated notebook pages:
        self.notebook.pages[ event.index: event.index + len( event.removed ) ] \
            = [ self._create_page( object ) for object in event.added ]

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_trait_change( self.update_editor_item,
                                self.name + '_items?', remove = True )
        del self.notebook.pages[:]

        super( _ThemedVerticalNotebookEditor, self ).dispose()

    #-- Trait Event Handlers ---------------------------------------------------

    def _selected_item_changed ( self, old, new ):
        """ Handles the selected item being changed.
        """
        if new is not None:
            self.notebook.open( self._find_page( new ) )
        elif old is not None:
            self.notebook.close( self._find_page( old ) )

    def _selected_list_changed ( self, old, new ):
        """ Handles the selected list being changed.
        """
        notebook = self.notebook
        for object in old:
            notebook.close( self._find_page( object ) )

        for object in new:
            notebook.open( self._find_page( object ) )

    def _selected_list_items_changed ( self, event ):
        self._selected_list_changed( event.removed, event.added )

    @on_trait_change( 'notebook:pages:is_open' )
    def _page_state_modified ( self, page, name, old, is_open ):
        if self.factory.multiple_open:
            object = page.data
            if is_open:
                if object not in self.selected_list:
                    self.selected_list.append( object )
            elif object in self.selected_list:
                self.selected_list.remove( object )
        elif is_open:
            self.selected_item = page.data
        else:
            self.selected_item = None

    #-- Private Methods --------------------------------------------------------

    def _create_page ( self, object ):
        """ Creates and returns a notebook page for a specified object with
            traits.
        """
        # Create a new notebook page:
        page = self.notebook.create_page().set( data = object )

        # Create the Traits UI for the object to put in the notebook page:
        ui = object.edit_traits( parent = page.parent,
                                 view   = self.factory.view,
                                 kind   = 'subpanel' ).set(
                                 parent = self.ui )

        # Get the name of the page being added to the notebook:
        name      = ''
        page_name = self.factory.page_name
        if page_name[0:1] == '.':
            if getattr( object, page_name[1:], Undefined ) is not Undefined:
                page.register_name_listener( object, page_name[1:] )
        else:
            name = page_name

        if name == '':
            name = user_name_for( object.__class__.__name__ )

        # Make sure the name is not a duplicate, then save it in the page:
        if page.name == '':
            self.pages[ name ] = count = self.pages.get( name, 0 ) + 1
            if count > 1:
                name += (' %d' % count)
            page.name = name

        # Save the Traits UI in the page so it can dispose of it later:
        page.ui = ui

        # Return the new notebook page
        return page

    def _find_page ( self, object ):
        """ Find the notebook page corresponding to a specified object. Returns
            the page if found, and **None** otherwise.
        """
        for page in self.notebook.pages:
            if object is page.data:
                return page

        return None

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for themed slider editors:
class ThemedVerticalNotebookEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = _ThemedVerticalNotebookEditor

    # The theme to use for closed notebook pages:
    closed_theme = ATheme

    # The theme to use for open notebook pages:
    open_theme = ATheme

    # Allow multiple open pages at once?
    multiple_open = Bool( False )

    # Should the notebook be scrollable?
    scrollable = Bool( False )

    # Use double clicks (True) or single clicks (False) to open/close pages:
    double_click = Bool( True )

    # Extended name to use for each notebook page. It can be either the actual
    # name or the name of an attribute on the object in the form:
    # '.name[.name...]'
    page_name = Str

    # Name of the view to use for each page:
    view = AView

    # Name of the [object.]trait[.trait...] to synchronize notebook page
    # selection with:
    selected = Str

