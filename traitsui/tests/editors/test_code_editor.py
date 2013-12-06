#------------------------------------------------------------------------------
#
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#------------------------------------------------------------------------------

from traits.has_traits import HasTraits
from traits.trait_types import Bool, Enum, Instance, Str
from traitsui.handler import ModelView
from traitsui.view import View, Group
from traitsui.item import Item
from traitsui.editors.code_editor import CodeEditor


from traitsui.tests._tools import *


class CodeModel(HasTraits):
    code = Str('world domination code')

class CodeView(ModelView):
    model = Instance(CodeModel)
    show_line_numbers = Bool(True)
    style = Enum('simple', 'readonly')

    def default_traits_view(self):
        traits_view = View(
            Item('model.code',
                 editor=CodeEditor(show_line_numbers=self.show_line_numbers),
                 style=self.style)
        )
        return traits_view


@skip_if_not_qt4
def test_code_editor_show_line_numbers():
    """ CodeEditor should honor the `show_line_numbers` setting
    """
    def is_line_numbers_visible(ui):
        from pyface import qt
        txt_ctrl = ui.control.findChild(qt.QtGui.QPlainTextEdit)
        return txt_ctrl.line_number_widget.isVisible()

    def test_line_numbers_visibility(show=True):
        with store_exceptions_on_all_threads():
            code_model = CodeModel()
            code_view = CodeView(model=code_model,
                                 show_line_numbers=show)
            ui = code_view.edit_traits()
            nose.tools.assert_equal(is_line_numbers_visible(ui), show)
            ui.control.close()

    test_line_numbers_visibility(True)
    test_line_numbers_visibility(False)

@skip_if_not_qt4
def test_code_editor_readonly():
    """ Test readonly editor style for CodeEditor
    """
    from pyface import qt
    with store_exceptions_on_all_threads():
        code_model = CodeModel()
        code_view = CodeView(model=code_model,
                             style='readonly')
        ui = code_view.edit_traits()
        txt_ctrl = ui.control.findChild(qt.QtGui.QPlainTextEdit)
        nose.tools.assert_true(txt_ctrl.isReadOnly())

        # Test changing the object's text
        nose.tools.assert_equal(txt_ctrl.toPlainText(), code_model.code)
        code_model.code += 'some more code'
        nose.tools.assert_true(txt_ctrl.isReadOnly())
        nose.tools.assert_equal(txt_ctrl.toPlainText(), code_model.code)

        # Test changing the underlying object
        code_model2 = CodeModel(code=code_model.code*2)
        code_view.model = code_model2
        nose.tools.assert_true(txt_ctrl.isReadOnly())
        nose.tools.assert_equal(txt_ctrl.toPlainText(), code_model.code)

        ui.control.close()


if __name__ == '__main__':
    nose.main()
