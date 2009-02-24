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
#  Author: Enthought, Inc.
#
#------------------------------------------------------------------------------

""" The wx implementation of the workbench window layout interface.
"""

# Standard library imports.
import cPickle
import logging

# Major package imports.
import wx

# Enthought library imports.
from enthought.pyface.dock.api import DOCK_BOTTOM, DOCK_LEFT, DOCK_RIGHT
from enthought.pyface.dock.api import DOCK_TOP
from enthought.pyface.dock.api import DockControl, DockRegion, DockSection
from enthought.pyface.dock.api import DockSizer
from enthought.traits.api import Delegate
from enthought.traits.ui.dockable_view_element import DockableViewElement

# Mixin class imports.
from enthought.pyface.workbench.i_workbench_window_layout import \
     MWorkbenchWindowLayout

# Local imports.
from editor_set_structure_handler import EditorSetStructureHandler
from view_set_structure_handler import ViewSetStructureHandler
from workbench_dock_window import WorkbenchDockWindow


# Logging.
logger = logging.getLogger(__name__)

# Mapping from view position to the appropriate dock window constant.
_POSITION_MAP = {
    'top'    : DOCK_TOP,
    'bottom' : DOCK_BOTTOM,
    'left'   : DOCK_LEFT,
    'right'  : DOCK_RIGHT
}


class WorkbenchWindowLayout(MWorkbenchWindowLayout):
    """ The wx implementation of the workbench window layout interface.

    See the 'IWorkbenchWindowLayout' interface for the API documentation.
    
    """

    #### 'IWorkbenchWindowLayout' interface ###################################

    editor_area_id = Delegate('window')

    ###########################################################################
    # 'IWorkbenchWindowLayout' interface.
    ###########################################################################

    def activate_editor(self, editor):
        """ Activate an editor. """
        
        # This brings the dock control tab to the front.
        self._wx_editor_dock_window.activate_control(editor.id)

        editor.set_focus()

        return editor

    def activate_view(self, view):
        """ Activate a view. """
        
        # This brings the dock control tab to the front.
        self._wx_view_dock_window.activate_control(view.id)
        
        view.set_focus()
        
        return view

    def add_editor(self, editor, title):
        """ Add an editor. """
        
        try:
            self._wx_add_editor(editor, title)
            
        except Exception:
            logger.exception('error creating editor control <%s>', editor.id)

        return editor

    def add_view(self, view, position=None, relative_to=None, size=(-1, -1)):
        """ Add a view. """
        
        try:
            self._wx_add_view(view, position, relative_to, size)
            view.visible = True

        except Exception:
            logger.exception('error creating view control <%s>', view.id)

            # Even though we caught the exception, it sometimes happens that
            # the view's control has been created as a child of the application
            # window (or maybe even the dock control).  We should destroy the
            # control to avoid bad UI effects.
            view.destroy_control()

            # Additionally, display an error message to the user.
            self.window.error('Unable to add view %s' % view.id)

        return view

    def close_editor(self, editor):
        """ Close and editor. """
        
        self._wx_editor_dock_window.close_control(editor.id)

        return editor

    def close_view(self, view):
        """ Close a view. """
        
        self.hide_view(view)

        return view

    def close(self):
        """ Close the entire window layout. """
        
        self._wx_editor_dock_window.close()
        self._wx_view_dock_window.close()

        return

    def create_initial_layout(self, parent):
        """ Create the initial window layout. """
        
        # The view dock window is where all of the views live. It also contains
        # a nested dock window where all of the editors live.
        self._wx_view_dock_window = WorkbenchDockWindow(parent)

        # The editor dock window (which is nested inside the view dock window)
        # is where all of the editors live.
        self._wx_editor_dock_window = WorkbenchDockWindow(
            self._wx_view_dock_window.control
        )
        editor_dock_window_sizer = DockSizer(contents=DockSection())
        self._wx_editor_dock_window.control.SetSizer(editor_dock_window_sizer)

        # Nest the editor dock window in the view dock window.
        editor_dock_window_control = DockControl(
            id      = self.editor_area_id,
            name    = 'Editors',
            control = self._wx_editor_dock_window.control,
            style   = 'fixed',
            width   = self.window.editor_area_size[0],
            height  = self.window.editor_area_size[1],
        )

        view_dock_window_sizer = DockSizer(
            contents=[editor_dock_window_control]
        )

        self._wx_view_dock_window.control.SetSizer(view_dock_window_sizer)

        return self._wx_view_dock_window.control

    def contains_view(self, view):
        """ Return True if the view exists in the window layout. """

        view_control = self._wx_view_dock_window.get_control(view.id, False)

        return view_control is not None

    def hide_editor_area(self):
        """ Hide the editor area. """
        
        dock_control = self._wx_view_dock_window.get_control(
            self.editor_area_id, visible_only=False
        )
        dock_control.show(False, layout=True)

        return

    def hide_view(self, view):
        """ Hide a view. """
        
        dock_control = self._wx_view_dock_window.get_control(
            view.id, visible_only=False
        )

        dock_control.show(False, layout=True)
        view.visible = False

        return view

    def refresh(self):
        """ Refresh the window layout to reflect any changes. """
        
        self._wx_view_dock_window.update_layout()

        return

    def reset_editors(self):
        """ Activate the first editor in every group. """
        
        self._wx_editor_dock_window.reset_regions()

        return

    def reset_views(self):
        """ Activate the first view in every group. """
        
        self._wx_view_dock_window.reset_regions()

        return

    def show_editor_area(self):
        """ Show the editor area. """
        
        dock_control = self._wx_view_dock_window.get_control(
            self.editor_area_id, visible_only=False
        )
        dock_control.show(True, layout=True)

        return

    def show_view(self, view):
        """ Show a view. """
        
        dock_control = self._wx_view_dock_window.get_control(
            view.id, visible_only=False
        )

        dock_control.show(True, layout=True)
        view.visible = True
        
        return

    #### Methods for saving and restoring the layout ##########################

    def get_view_memento(self):
        structure = self._wx_view_dock_window.get_structure()

        # We always return a clone.
        return cPickle.loads(cPickle.dumps(structure))

    def set_view_memento(self, memento):
        # We always use a clone.
        memento = cPickle.loads(cPickle.dumps(memento))

        # The handler knows how to resolve view Ids when setting the dock
        # window structure.
        handler = ViewSetStructureHandler(self)

        # Set the layout of the views.
        self._wx_view_dock_window.set_structure(memento, handler)

        # fixme: We should be able to do this in the handler but we don't get a
        # reference to the actual dock control in 'resolve_id'.
        for view in self.window.views:
            control = self._wx_view_dock_window.get_control(view.id)
            if control is not None:
                self._wx_initialize_view_dock_control(view, control)
                view.visible = control.visible
            else:
                view.visible = False

        return

    def get_editor_memento(self):
        # Get the layout of the editors.
        structure = self._wx_editor_dock_window.get_structure()

        # Get a memento to every editor.
        editor_references = self._get_editor_references()

        return (structure, editor_references)

    def set_editor_memento(self, memento):
        # fixme: Mementos might want to be a bit more formal than tuples!
        structure, editor_references = memento

        if len(structure.contents) > 0:
            # The handler knows how to resolve editor Ids when setting the dock
            # window structure.
            handler = EditorSetStructureHandler(self, editor_references)

            # Set the layout of the editors.
            self._wx_editor_dock_window.set_structure(structure, handler)

            # fixme: We should be able to do this in the handler but we don't
            # get a reference to the actual dock control in 'resolve_id'.
            for editor in self.window.editors:
                control = self._wx_editor_dock_window.get_control(editor.id)
                if control is not None:
                    self._wx_initialize_editor_dock_control(editor, control)

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _wx_add_editor(self, editor, title):
        """ Adds an editor. """

        # Create a dock control that contains the editor.
        editor_dock_control = self._wx_create_editor_dock_control(editor)

        # If there are no other editors open (i.e., this is the first one!),
        # then create a new region to put the editor in.
        controls = self._wx_editor_dock_window.get_controls()
        if len(controls) == 0:
            # Get a reference to the empty editor section.
            sizer   = self._wx_editor_dock_window.control.GetSizer()
            section = sizer.GetContents()

            # Add a region containing the editor dock control.
            region  = DockRegion(contents=[editor_dock_control])
            section.contents = [region]

        # Otherwise, add the editor to the same region as the first editor
        # control.
        #
        # fixme: We might want a more flexible placement strategy at some
        # point!
        else:
            region = controls[0].parent
            region.add(editor_dock_control)

        # fixme: Without this the window does not draw properly (manually
        # resizing the window makes it better!).
        self._wx_editor_dock_window.update_layout()

        return

    def _wx_add_view(self, view, position, relative_to, size):
        """ Adds a view. """

        # If no specific position is specified then use the view's default
        # position.
        if position is None:
            position = view.position
            
        # Create a dock control that contains the view.
        dock_control = self._wx_create_view_dock_control(view)

        if position == 'with':
            # Does the item we are supposed to be positioned 'with' actual
            # exist?
            with_item = self._wx_view_dock_window.get_control(relative_to.id)

            # If so then we put the items in the same tab group.
            if with_item is not None:
                self._wx_add_view_with(dock_control, relative_to)

            # Otherwise, just fall back to the 'left' of the editor area.
            else:
                self._wx_add_view_relative(dock_control, None, 'left', size)

        else:
            self._wx_add_view_relative(dock_control,relative_to,position,size)

        return

    # fixme: Make the view dock window a sub class of dock window, and add
    # 'add_with' and 'add_relative_to' as methods on that.
    #
    # fixme: This is a good idea in theory, but the sizing is a bit iffy, as
    # it requires the window to be passed in to calculate the relative size
    # of the control. We could just calculate that here and pass in absolute
    # pixel sizes to the dock window subclass?
    def _wx_add_view_relative(self, dock_control, relative_to, position, size):
        """ Adds a view relative to another item. """

        # If no 'relative to' Id is specified then we assume that the position
        # is relative to the editor area.
        if relative_to is None:
            relative_to_item = self._wx_view_dock_window.get_control(
                self.editor_area_id, visible_only=False
            )

        # Find the item that we are adding the view relative to.
        else:
            relative_to_item = self._wx_view_dock_window.get_control(
                relative_to.id
            )

        # Set the size of the dock control.
        self._wx_set_item_size(dock_control, size)

        # The parent of a dock control is a dock region.
        region  = relative_to_item.parent
        section = region.parent
        section.add(dock_control, region, _POSITION_MAP[position])

        return

    def _wx_add_view_with(self, dock_control, with_obj):
        """ Adds a view in the same region as another item. """

        # Find the item that we are adding the view 'with'.
        with_item = self._wx_view_dock_window.get_control(with_obj.id)
        if with_item is None:
            raise ValueError('Cannot find item %s' % with_obj)

        # The parent of a dock control is a dock region.
        with_item.parent.add(dock_control)

        return

    def _wx_set_item_size(self, dock_control, size):
        """ Sets the size of a dock control. """

        window_width, window_height = self.window.control.GetSize()
        width,        height        = size

        if width != -1:
            dock_control.width = int(window_width * width)

        if height != -1:
            dock_control.height = int(window_height * height)

        return

    def _wx_create_editor_dock_control(self, editor):
        """ Creates a dock control that contains the specified editor. """
        
        self._wx_get_editor_control(editor)

        # Wrap a dock control around it.
        editor_dock_control = DockControl(
            id        = editor.id,
            name      = editor.name,
            closeable = True,
            control   = editor.control,
            style     = 'tab',
            # fixme: Create a subclass of dock control and give it a proper
            # editor trait!
            _editor   = editor
        )
        
        # Hook up the 'on_close' and trait change handlers etc.
        self._wx_initialize_editor_dock_control(editor, editor_dock_control)

        return editor_dock_control

    def _wx_create_view_dock_control(self, view):
        """ Creates a dock control that contains the specified view. """
        
        # Get the view's toolkit-specific control.
        control = self._wx_get_view_control(view)

        # Wrap a dock control around it.
        view_dock_control = DockControl(
            id        = view.id,
            name      = view.name,
            # fixme: We would like to make views closeable, but closing via the
            # tab is different than calling show(False, layout=True) on the
            # control! If we use a close handler can we change that?!?
            closeable = False,
            control   = control,
            style     = view.style_hint,
            # fixme: Create a subclass of dock control and give it a proper
            # view trait!
            _view     = view
        )

        # Hook up the 'on_close' and trait change handlers etc.
        self._wx_initialize_view_dock_control(view, view_dock_control)

        return view_dock_control

    def _wx_get_editor_control(self, editor):
        """ Returns the editor's toolkit-specific control.

        If the editor has not yet created its control, we will ask it to create
        it here.

        """

        if editor.control is None:
            parent = self._wx_editor_dock_window.control

            # This is the toolkit-specific control that represents the 'guts'
            # of the editor.
            self.editor_opening = editor
            editor.control = editor.create_control(parent)
            self.editor_opened = editor

            # Hook up toolkit-specific events that are managed by the framework
            # etc.
            self._wx_initialize_editor_control(editor)

        return editor.control

    def _wx_initialize_editor_control(self, editor):
        """ Initializes the toolkit-specific control for an editor.

        This is used to hook events managed by the framework etc.

        """

        def on_set_focus(event):
            """ Called when the control gets the focus. """

            editor.has_focus = True
            
            # Let the default wx event handling do its thang.
            event.Skip()

            return

        def on_kill_focus(event):
            """ Called when the control gets the focus. """

            editor.has_focus = False

            # Let the default wx event handling do its thang.
            event.Skip()

            return

        self._wx_add_focus_listeners(editor.control,on_set_focus,on_kill_focus)

        return

    def _wx_get_view_control(self, view):
        """ Returns a view's toolkit-specific control.

        If the view has not yet created its control, we will ask it to create
        it here.

        """

        if view.control is None:
            parent = self._wx_view_dock_window.control

            # Make sure that the view knows which window it is in.
            view.window = self.window
            
            # This is the toolkit-specific control that represents the 'guts'
            # of the view.
            self.view_opening = view
            view.control = view.create_control(parent)
            self.view_opened = view

            # Hook up toolkit-specific events that are managed by the
            # framework etc.
            self._wx_initialize_view_control(view)

        return view.control

    def _wx_initialize_view_control(self, view):
        """ Initializes the toolkit-specific control for a view.

        This is used to hook events managed by the framework.

        """

        def on_set_focus(event):
            """ Called when the control gets the focus. """

            view.has_focus = True

            # Let the default wx event handling do its thang.
            event.Skip()

            return

        def on_kill_focus(event):
            """ Called when the control gets the focus. """

            view.has_focus = False

            # Let the default wx event handling do its thang.
            event.Skip()

            return

        self._wx_add_focus_listeners(view.control, on_set_focus, on_kill_focus)

        return

    def _wx_add_focus_listeners(self, control, on_set_focus, on_kill_focus):
        """ Recursively adds focus listeners to a control. """

        # NOTE: If we are passed a wx control that isn't correctly initialized
        # (like when the TraitsUIView isn't properly creating it) but it is
        # actually a wx control, then we get weird exceptions from trying to
        # register event handlers.  The exception messages complain that
        # the passed control is a str object instead of a wx object.
        if on_set_focus is not None:
            #control.Bind(wx.EVT_SET_FOCUS, on_set_focus)
            wx.EVT_SET_FOCUS(control, on_set_focus)
            
        if on_kill_focus is not None:
            #control.Bind(wx.EVT_KILL_FOCUS, on_kill_focus)
            wx.EVT_KILL_FOCUS(control, on_kill_focus)
        
        for child in control.GetChildren():
            self._wx_add_focus_listeners(child, on_set_focus, on_kill_focus)
            
        return

    def _wx_initialize_editor_dock_control(self, editor, editor_dock_control):
        """ Initializes an editor dock control.

        fixme: We only need this method because of a problem with the dock
        window API in the 'SetStructureHandler' class. Currently we do not get
        a reference to the dock control in 'resolve_id' and hence we cannot set
        up the 'on_close' and trait change handlers etc.

        """

        # Some editors append information to their name to indicate status (in
        # our case this is often a 'dirty' indicator that shows when the
        # contents of an editor have been modified but not saved). When the
        # dock window structure is persisted it contains the name of each dock
        # control, which obviously includes any appended state information.
        # Here we make sure that when the dock control is recreated its name is
        # set to the editor name and nothing more!
        editor_dock_control.set_name(editor.name)

        # fixme: Should we roll the traits UI stuff into the default editor.
        if hasattr(editor, 'ui') and editor.ui is not None:
            # This makes the control draggable outside of the main window.
            #editor_dock_control.export = 'enthought.pyface.workbench.editor'
            editor_dock_control.dockable = DockableViewElement(
                should_close=True, ui=editor.ui
            )

        editor_dock_control.on_close = self._wx_on_editor_closed

        def on_id_changed(editor, trait_name, old, new):
            editor_dock_control.id = editor.id
            return

        editor.on_trait_change(on_id_changed, 'id')

        def on_name_changed(editor, trait_name, old, new):
            editor_dock_control.set_name(editor.name)
            return

        editor.on_trait_change(on_name_changed, 'name')

        def on_activated_changed(editor_dock_control, trait_name, old, new):
            if editor_dock_control._editor is not None:
                editor_dock_control._editor.set_focus()
            return

        editor_dock_control.on_trait_change(on_activated_changed, 'activated')

        return

    def _wx_initialize_view_dock_control(self, view, view_dock_control):
        """ Initializes a view dock control.

        fixme: We only need this method because of a problem with the dock
        window API in the 'SetStructureHandler' class. Currently we do not get
        a reference to the dock control in 'resolve_id' and hence we cannot set
        up the 'on_close' and trait change handlers etc.

        """

        # Some views append information to their name to indicate status (in
        # our case this is often a 'dirty' indicator that shows when the
        # contents of a view have been modified but not saved). When the
        # dock window structure is persisted it contains the name of each dock
        # control, which obviously includes any appended state information.
        # Here we make sure that when the dock control is recreated its name is
        # set to the view name and nothing more!
        view_dock_control.set_name(view.name)

        # fixme: Should we roll the traits UI stuff into the default editor.
        if hasattr(view, 'ui') and view.ui is not None:
            # This makes the control draggable outside of the main window.
            #view_dock_control.export = 'enthought.pyface.workbench.view'
            
            # If the ui's 'view' trait has an 'export' field set, pass that on 
            # to the dock control. This makes the control detachable from the 
            # main window (if 'export' is not an empty string).
            if view.ui.view is not None:
                view_dock_control.export = view.ui.view.export
            view_dock_control.dockable = DockableViewElement(
                should_close=True, ui=view.ui
            )

        view_dock_control.on_close = self._wx_on_view_closed

        def on_id_changed(view, trait_name, old, new):
            view_dock_control.id = view.id
            return

        view.on_trait_change(on_id_changed, 'id')

        def on_name_changed(view, trait_name, old, new):
            view_dock_control.set_name(view.name)
            return

        view.on_trait_change(on_name_changed, 'name')

        def on_activated_changed(view_dock_control, trait_name, old, new):
            if view_dock_control._view is not None:
                view_dock_control._view.set_focus()
            return

        view_dock_control.on_trait_change(on_activated_changed, 'activated')

        return

    #### Trait change handlers ################################################

    #### Static ####

    def _window_changed(self, old, new):
        """ Static trait change handler. """

        if old is not None:
            old.on_trait_change(
                self._wx_on_editor_area_size_changed, 'editor_area_size',
                remove=True
            )


        if new is not None:
            new.on_trait_change(
                self._wx_on_editor_area_size_changed, 'editor_area_size',
            )

    #### Dynamic ####

    def _wx_on_editor_area_size_changed(self, new):
        """ Dynamic trait change handler. """

        window_width, window_height = self.window.control.GetSize()

        # Get the dock control that contains the editor dock window.
        control = self._wx_view_dock_window.get_control(self.editor_area_id)

        # We actually resize the region that the editor area is in.
        region = control.parent
        region.width  = int(new[0] * window_width)
        region.height = int(new[1] * window_height)

        return

    #### Dock window handlers #################################################

    # fixme: Should these just fire events that the window listens to?
    def _wx_on_view_closed(self, dock_control, force):
        """ Called when a view is closed via the dock window control. """

        view = self.window.get_view_by_id(dock_control.id)
        if view is not None:
            logger.debug('workbench destroying view control <%s>', view)
            try:
                view.visible = False

                self.view_closing = view
                view.destroy_control()
                self.view_closed = view
                
            except:
                logger.exception('error destroying view control <%s>', view)

        return True

    def _wx_on_editor_closed(self, dock_control, force):
        """ Called when an editor is closed via the dock window control. """

        dock_control._editor = None
        editor = self.window.get_editor_by_id(dock_control.id)

##         import weakref
##         editor_ref = weakref.ref(editor)

        if editor is not None:
            logger.debug('workbench destroying editor control <%s>', editor)
            try:
                # fixme: We would like this event to be vetoable, but it isn't
                # just yet (we will need to modify the dock window package).
                self.editor_closing = editor
                editor.destroy_control()
                self.editor_closed = editor

            except:
                logger.exception('error destroying editor control <%s>',editor)

##         import gc
##         gc.collect()

##         print 'Editor references', len(gc.get_referrers(editor))
##         for r in gc.get_referrers(editor):
##             print '********************************************'
##             print type(r), id(r), r

##         del editor
##         gc.collect()

##         print 'Is editor gone?', editor_ref() is None, 'ref', editor_ref()
        
        return True

#### EOF ######################################################################
