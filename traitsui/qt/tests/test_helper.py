# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import textwrap
import unittest

from pyface.qt import is_pyqt, qt_api, QtCore, QtGui
from traitsui.tests._tools import is_mac_os, requires_toolkit, ToolkitName
from traitsui.qt.helper import qobject_is_valid, wrap_text_with_elision
from traitsui.qt.font_trait import create_traitsfont


lorem_ipsum = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat.\n"
    "    \n"
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum "
    "dolore eu fugiat nulla pariatur.\n"
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui "
    "officia deserunt mollit anim id est laborum."
)


def get_expected_lines(text, width):
    expected_lines = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            expected_lines.append("")
            continue
        expected_lines += textwrap.wrap(paragraph, width)
    return expected_lines


@requires_toolkit([ToolkitName.qt])
class TestWrapText(unittest.TestCase):

    def test_wrap_text_basic(self):
        font = create_traitsfont("Courier")
        font_metrics = QtGui.QFontMetrics(font)

        average_char_width = font_metrics.averageCharWidth()
        line_spacing = font_metrics.lineSpacing()

        width = 500 * average_char_width
        height = 100 * line_spacing

        lines = wrap_text_with_elision(lorem_ipsum, font, width, height)

        self.assertEqual(
            lines, [line.rstrip() for line in lorem_ipsum.splitlines()]
        )

    def test_wrap_text_empty(self):
        font = create_traitsfont("Courier")
        font_metrics = QtGui.QFontMetrics(font)

        average_char_width = font_metrics.averageCharWidth()
        line_spacing = font_metrics.lineSpacing()

        width = 500 * average_char_width
        height = 100 * line_spacing

        lines = wrap_text_with_elision("", font, width, height)

        self.assertEqual(lines, [])

    def test_wrap_text_narrow(self):
        font = create_traitsfont("Courier")
        font_metrics = QtGui.QFontMetrics(font)

        average_char_width = font_metrics.averageCharWidth()
        line_spacing = font_metrics.lineSpacing()

        width = 20 * average_char_width
        height = 100 * line_spacing

        lines = wrap_text_with_elision(lorem_ipsum, font, width, height)

        # add one char slack as depends on OS, exact font, etc.
        self.assertTrue(all(len(line) <= 21 for line in lines))

    def test_wrap_text_narrow_short(self):
        font = create_traitsfont("Courier")
        font_metrics = QtGui.QFontMetrics(font)

        average_char_width = font_metrics.averageCharWidth()
        line_spacing = font_metrics.lineSpacing()

        width = 20 * average_char_width
        height = 20 * line_spacing

        lines = wrap_text_with_elision(lorem_ipsum, font, width, height)

        # add one char slack as depends on OS, exact font, etc.
        self.assertTrue(all(len(line) <= 21 for line in lines))
        # different os elide the last line slightly differently,
        # just check end of last line shows elision.
        # In most systems elision is marked with ellipsis
        # but it has been reported as "..." on NetBSD.
        if lines[19][-1] == ".":
            self.assertEqual(lines[19][-3:], "...")
        else:
            self.assertEqual(lines[19][-1], "\u2026")

    def test_wrap_text_short(self):
        font = create_traitsfont("Courier")
        font_metrics = QtGui.QFontMetrics(font)

        average_char_width = font_metrics.averageCharWidth()
        line_spacing = font_metrics.lineSpacing()

        width = 500 * average_char_width
        height = 3 * line_spacing

        lines = wrap_text_with_elision(lorem_ipsum, font, width, height)

        expected_lines = get_expected_lines(lorem_ipsum, 500)[:3]
        self.assertEqual(lines, expected_lines)

    @unittest.skipIf(
        is_mac_os and qt_api == "pyside6",
        "causes next test to segfault on Mac OS/PySide6 (see #1974)",
    )
    def test_qobject_is_valid(self):
        qobject = QtCore.QObject()

        if is_pyqt:
            from sip import delete
        elif qt_api == "pyside2":
            from shiboken2 import delete
        elif qt_api == "pyside6":
            from shiboken6 import delete
        else:
            with self.assertRaises(RuntimeError):
                qobject_is_valid(qobject)
            return

        result = qobject_is_valid(qobject)

        self.assertTrue(result)

        delete(qobject)
        result = qobject_is_valid(qobject)

        self.assertFalse(result)
