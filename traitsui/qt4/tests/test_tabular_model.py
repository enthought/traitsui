#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

""" Tests for TabularModel (an implementation of QAbstractTableModel)
"""

import unittest

from traits.api import HasTraits, List, Str
from traitsui.api import Item, TabularEditor, View
from traitsui.tabular_adapter import TabularAdapter

from traitsui.tests._tools import (
    create_ui,
    is_current_backend_qt4,
    skip_if_not_qt4,
    store_exceptions_on_all_threads,
)
try:
    from pyface.qt import QtCore
except ImportError:
    # The entire test case should be skipped if the current backend is not Qt
    # But if it is Qt, then re-raise
    if is_current_backend_qt4():
        raise


class DummyHasTraits(HasTraits):
    names = List(Str)


def get_view(adapter):
    return View(
        Item(
            "names",
            editor=TabularEditor(
                adapter=adapter,
            ),
        )
    )


@skip_if_not_qt4
class TestTabularModel(unittest.TestCase):

    def test_drop_mime_data_below_list(self):
        # Test dragging an item in the list and drop it below the last item
        obj = DummyHasTraits(names=["A", "B", "C", "D"])
        view = get_view(TabularAdapter(columns=["Name"]))
        with store_exceptions_on_all_threads(), \
                create_ui(obj, dict(view=view)) as ui:
            editor, = ui.get_editors("names")

            model = editor.model
            # sanity check
            self.assertEqual(model.rowCount(None), 4)

            # drag and drop row=1 from within the table.
            # drag creates a PyMimeData object for dropMimeData to consume.
            index = model.createIndex(1, 0)
            mime_data = model.mimeData([index])

            # when
            # dropped below the list, the "parent" is invalid.
            parent = QtCore.QModelIndex()   # invalid index object
            model.dropMimeData(mime_data, QtCore.Qt.MoveAction, -1, -1, parent)

            # then
            mime_data = model.mimeData(
                [model.createIndex(i, 0) for i in range(model.rowCount(None),)]
            )
            content = mime_data.instance()
            self.assertEqual(content, ["A", "C", "D", "B"])

    def test_drop_mime_data_within_list(self):
        # Test dragging an item in the list and drop it somewhere within the
        # list
        obj = DummyHasTraits(names=["A", "B", "C", "D"])
        view = get_view(TabularAdapter(columns=["Name"]))

        with store_exceptions_on_all_threads(), \
                create_ui(obj, dict(view=view)) as ui:
            editor, = ui.get_editors("names")

            model = editor.model
            # sanity check
            self.assertEqual(model.rowCount(None), 4)

            # drag and drop from within the table.
            # drag row index 0
            index = model.createIndex(0, 0)
            mime_data = model.mimeData([index])

            # when
            # drop it to row index 2
            parent = model.createIndex(2, 0)
            model.dropMimeData(mime_data, QtCore.Qt.MoveAction, -1, -1, parent)

            # then
            mime_data = model.mimeData(
                [model.createIndex(i, 0) for i in range(model.rowCount(None),)]
            )
            content = mime_data.instance()
            self.assertEqual(content, ["B", "C", "A", "D"])

    def test_copy_item(self):
        # Test copy 'A' to the row after 'C'
        obj = DummyHasTraits(names=["A", "B", "C"])
        view = get_view(TabularAdapter(columns=["Name"], can_drop=True))

        with store_exceptions_on_all_threads(), \
                create_ui(obj, dict(view=view)) as ui:
            editor, = ui.get_editors("names")

            model = editor.model
            # sanity check
            self.assertEqual(model.rowCount(None), 3)

            # drag and drop from within the table for copy action.
            # drag index 0
            index = model.createIndex(0, 0)
            mime_data = model.mimeData([index])

            # when
            # drop to index 2
            parent = model.createIndex(2, 0)
            model.dropMimeData(mime_data, QtCore.Qt.CopyAction, -1, -1, parent)

            # then
            self.assertEqual(model.rowCount(None), 4)
            mime_data = model.mimeData(
                [model.createIndex(i, 0) for i in range(model.rowCount(None),)]
            )
            content = mime_data.instance()
            self.assertEqual(content, ["A", "B", "C", "A"])

    def test_move_rows_invalid_index(self):
        # Test the last resort to prevent segfault

        obj = DummyHasTraits(names=["A", "B", "C"])
        view = get_view(TabularAdapter(columns=["Name"]))

        with store_exceptions_on_all_threads(), \
                create_ui(obj, dict(view=view)) as ui:
            editor, = ui.get_editors("names")

            model = editor.model
            # sanity check
            self.assertEqual(model.rowCount(None), 3)

            # when
            # -1 is an invalid row. This should not cause segfault.
            model.moveRows([1], -1)

            # then
            mime_data = model.mimeData(
                [model.createIndex(i, 0) for i in range(model.rowCount(None),)]
            )
            content = mime_data.instance()
            self.assertEqual(content, ["A", "C", "B"])
