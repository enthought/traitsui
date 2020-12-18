#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!

import unittest
from unittest import mock

from traits.api import HasTraits, Str
from traitsui.api import HTMLEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class HTMLModel(HasTraits):
    """ Dummy class for testing HTMLEditor."""

    content = Str()

    model_base_url = Str()


def get_view(base_url_name, format_text=True, open_externally=False):
    return View(
        Item(
            "content",
            editor=HTMLEditor(
                format_text=format_text,
                base_url_name=base_url_name,
                open_externally=open_externally
            )
        )
    )


# Run this against wx as well once enthought/traitsui#752 is fixed.
@requires_toolkit([ToolkitName.qt])
class TestHTMLEditor(BaseTestMixin, unittest.TestCase):
    """ Test HTMLEditor """

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_init_and_dispose(self):
        # Smoke test to check init and dispose do not fail.
        model = HTMLModel()
        view = get_view(base_url_name="")
        with reraise_exceptions(), \
                create_ui(model, dict(view=view)):
            pass

    def test_base_url_changed(self):
        # Test if the base_url is changed after the UI closes, nothing
        # fails because sync_value is unhooked in the base class.
        model = HTMLModel()
        view = get_view(base_url_name="model_base_url")
        with reraise_exceptions():
            with create_ui(model, dict(view=view)):
                pass
            # It is okay to modify base_url after the UI is closed
            model.model_base_url = "/new_dir"

    @requires_toolkit([ToolkitName.qt])
    @mock.patch('webbrowser.open_new')
    def test_open_externally_qt(self, open_new_mock):
        from pyface.qt import QtCore, QtWebKit

        model = HTMLModel(
            content="<a href='enthought.com'>Link to click</a>"
        )
        view = get_view(
            base_url_name="",
            open_externally=True,
            format_text=False,
        )

        with reraise_exceptions():
            with create_ui(model, dict(view=view)) as ui:
                control = ui.info.content.control
                page = control.page()
                url = QtCore.QUrl('http://example.com')
                if hasattr(page, 'linkClicked'):
                    page.linkClicked.emit(url)
                else:
                    result = page.acceptNavigationRequest(
                        url,
                        QtWebKit.QWebPage.NavigationTypeLinkClicked,
                        True,
                    )
                    self.assertFalse(result)

        open_new_mock.assert_called_once_with("http://example.com")
