# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Bool, Enum, Instance, Str
from traitsui.handler import ModelView
from traitsui.view import View
from traitsui.item import Item
from traitsui.editors.code_editor import CodeEditor


from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class CodeModel(HasTraits):
    code = Str("world domination code")


class CodeView(ModelView):
    model = Instance(CodeModel)
    show_line_numbers = Bool(True)
    style = Enum("simple", "readonly")

    def default_traits_view(self):
        traits_view = View(
            Item(
                "model.code",
                editor=CodeEditor(show_line_numbers=self.show_line_numbers),
                style=self.style,
            )
        )
        return traits_view


class TestCodeEditor(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.qt])
    def test_code_editor_show_line_numbers(self):
        """CodeEditor should honor the `show_line_numbers` setting"""

        def is_line_numbers_visible(ui):
            from pyface import qt

            txt_ctrl = ui.control.findChild(qt.QtGui.QPlainTextEdit)
            return txt_ctrl.line_number_widget.isVisible()

        def test_line_numbers_visibility(show=True):
            code_model = CodeModel()
            code_view = CodeView(model=code_model, show_line_numbers=show)
            with reraise_exceptions(), create_ui(code_view) as ui:
                self.assertEqual(is_line_numbers_visible(ui), show)
                ui.control.close()

        test_line_numbers_visibility(True)
        test_line_numbers_visibility(False)

    @requires_toolkit([ToolkitName.qt])
    def test_code_editor_readonly(self):
        """Test readonly editor style for CodeEditor"""
        from pyface import qt

        code_model = CodeModel()
        code_view = CodeView(model=code_model, style="readonly")
        with reraise_exceptions(), create_ui(code_view) as ui:
            txt_ctrl = ui.control.findChild(qt.QtGui.QPlainTextEdit)
            self.assertTrue(txt_ctrl.isReadOnly())

            # Test changing the object's text
            self.assertEqual(txt_ctrl.toPlainText(), code_model.code)
            code_model.code += "some more code"
            self.assertTrue(txt_ctrl.isReadOnly())
            self.assertEqual(txt_ctrl.toPlainText(), code_model.code)

            # Test changing the underlying object
            code_model2 = CodeModel(code=code_model.code * 2)
            code_view.model = code_model2
            self.assertTrue(txt_ctrl.isReadOnly())
            self.assertEqual(txt_ctrl.toPlainText(), code_model.code)

            ui.control.close()
