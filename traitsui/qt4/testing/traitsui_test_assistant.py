#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!

from contextlib import contextmanager

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.trait_base import xgetattr


class TraitsUITestAssistant(GuiTestAssistant):
    """ A Test Assistant for testing TraitsUI views.

    For most efficient usage, this class expects the setUp to provide an
    'object' attribute containing the main object being viewed.

    Note
    ----

    This API is experimental and may change before the next feature release.
    """

    @contextmanager
    def create_ui(self, object=None, **kwargs):
        """ Create and dispose of a TraitsUI UI

        This is a context manager which calls edit_traits on an object in
        when entered and calls dispose when exiting, running the event
        loop until the underlying toolkit object is destroyed.

        Parameters
        ----------
        object : HasTraits instance or None
            The object to call edit_traits on.  If None, then the method
            will attempt to use self.object, if it exists.
        **kwargs : keyword arguments
            Additional keyword arguments will be passed through to
            edit_traits.

        Returns
        -------
        ui : UI instance
            The context manager returns the UI instance created by
            edit_traits.
        """
        if object is None:
            object = self.object
        ui = object.edit_traits(**kwargs)
        try:
            yield ui
        finally:
            with self.delete_widget(ui.control):
                ui.dispose()

    def set_editor_later(self, info, editor_id, value, trait_name='value'):
        """ Set the a trait on an editor during ethe event loop.

        Parameters
        ----------
        info : UIInfo instance
            The UIInfo instance for the UI.
        editor_id : str
            The ID of the editor in the UI (defaults to the trait name of the
            item).
        value : any
            The value to set on the editor.
        trait_name : str
            The trait to set on the editor.
        """
        if '.' in editor_id:
            __, editor_id = editor_id.rsplit('.', 1)
        editor = getattr(info, editor_id)
        self.gui.set_trait_later(editor, trait_name, value)

    def invoke_editor_later(self, info, editor_id, method='update_object',
                            *args, **kwargs):
        """ Call a method on an editor during ethe event loop.

        Parameters
        ----------
        info : UIInfo instance
            The UIInfo instance for the UI.
        editor_id : str
            The ID of the editor in the UI (defaults to the trait name of the
            item).
        method : str
            The name of the method on the editor.
        *args, **kwargs
            Additional positional and keyword arguments to pass to the method.
        """
        if '.' in editor_id:
            __, editor_id = editor_id.rsplit('.', 1)
        editor = getattr(info, editor_id)
        method = getattr(editor, method)
        self.gui.invoke_later(method, *args, **kwargs)

    def assertItemChanges(self, name, value, object=None, **ui_args):
        """ Test that setting a value on an editor changes the underlying trait.

        Parameters
        ----------
        name : str
            The identifier of the Item being changed.
        value : str
            The value being changed.
        object : HasTraits instance
            The object to call edit_traits on.  If None, then the method
            will attempt to use self.object, if it exists.
        **uiargs
            Additional keyword arguments to pass to the edit_traits method.
        """
        if object is None:
            object = self.object
        with self.create_ui(object, **ui_args) as ui:
            target, extended_trait = self._process_item_name(ui, name)
            with self.event_loop_until_traits_change(target, extended_trait):
                self.set_editor_later(ui.info, extended_trait, value)

        self.assertEqual(xgetattr(target, extended_trait), value)

    # ------------------------------------------------------------------------
    # Private API
    # ------------------------------------------------------------------------

    def _process_item_name(self, ui, name):
        """ Extract the target object and extended trait name from the item id
        """
        # XXX this almost certainly exists elsewhere,
        # XXX or _should_ exist elsewhere
        if '.' in name:
            target, extended_trait = name.split('.', 1)
            target = ui.context[target]
        else:
            extended_trait = name
            target = ui.context['object']
        return target, extended_trait
