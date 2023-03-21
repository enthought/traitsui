# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Editor factory for scrubber-based integer or float value editors.
"""

from pyface.ui_traits import Alignment
from traits.api import Float, Property

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.toolkit import toolkit_object
from traitsui.toolkit_traits import Color

# -------------------------------------------------------------------------
#  Create the editor factory object:
# -------------------------------------------------------------------------

# Editor factory for scrubber-based integer or float value editors.


class ScrubberEditor(BasicEditorFactory):

    #: The editor class to be instantiated:
    klass = Property()

    #: The low end of the scrubber range:
    low = Float()

    #: The high end of the scrubber range:
    high = Float()

    #: The normal increment (default: auto-calculate):
    increment = Float()

    #: The alignment of the text within the scrubber:
    alignment = Alignment("center")

    #: The background color for the scrubber:
    color = Color(None)

    #: The hover mode background color for the scrubber:
    hover_color = Color(None)

    #: The active mode background color for the scrubber:
    active_color = Color(None)

    #: The scrubber border color:
    border_color = Color(None)

    #: The color to use for the value text:
    text_color = Color("black")

    def _get_klass(self):
        """Returns the toolkit-specific editor class to be instantiated."""
        return toolkit_object("scrubber_editor:_ScrubberEditor")
