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
    """

    @contextmanager
    def create_ui(self, object=None, **kwargs):
        if object is None:
            object = self.object
        ui = object.edit_traits(**kwargs)
        try:
            yield ui
        finally:
            with self.delete_widget(ui.control):
                ui.dispose()

    def set_editor_later(self, ui, item_name, value, trait_name='value'):
        if '.' in item_name:
            __, item_name = item_name.rsplit('.', 1)
        editor = getattr(ui.info, item_name)
        self.gui.set_trait_later(editor, trait_name, value)

    def invoke_editor_later(self, ui, item_name, method='update_object',
                            *args, **kwargs):
        if '.' in item_name:
            __, item_name = item_name.rsplit('.', 1)
        editor = getattr(ui.info, item_name)
        method = getattr(editor, method)
        self.gui.invoke_later(method, *args, **kwargs)

    def assertItemChanges(self, name, value, object=None, **ui_args):
        if object is None:
            object = self.object
        with self.create_ui(object, **ui_args) as ui:
            target, extended_trait = self._process_item_name(ui, name)
            with self.event_loop_until_traits_change(target, extended_trait):
                self.set_editor_later(ui, extended_trait, value)

        self.assertEqual(xgetattr(target, extended_trait), value)

    def _process_item_name(self, ui, name):
        if '.' in name:
            target, extended_trait = name.split('.', 1)
            target = ui.context[target]
        else:
            extended_trait = name
            target = ui.context['object']
        return target, extended_trait
