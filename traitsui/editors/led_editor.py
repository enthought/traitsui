# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

""" A Traits UI editor that wraps a LED-style integer display.
"""

from traitsui.editor_factory import EditorFactory
from traits.api import Enum


class LEDEditor(EditorFactory):
    """ Editor factory for an LED editor. """

    #: The alignment of the numeric text within the control. (Wx only)
    alignment = Enum("right", "center", "left")
