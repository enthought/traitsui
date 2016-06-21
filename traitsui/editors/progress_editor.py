#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

""" Defines the progress editor factory for all traits toolkit backends,
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from traits.api import Int, Bool, Str

from ..editor_factory import EditorFactory


class ToolkitEditorFactory(EditorFactory):
    """ Editor factory for code editors.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The title
    title = Str

    # The message to be displayed along side the progress guage
    message = Str

    # The name of an [object.]trait that defines the message string
    message_name = Str

    # The starting value
    min = Int

    # The name of an [object.]trait that defines the starting value
    min_name = Str

    # The ending value
    max = Int

    # The name of an [object.]trait that defines the ending value
    max_name = Str

    # If the cancel button should be shown (not very sensible as an editor)
    can_cancel = Bool(False)

    # If the estimated time should be shown (not very sensible as an editor)
    show_time = Bool(False)

    # if the percent complete should be shown
    show_percent = Bool(False)


# Define the Code Editor class.
ProgressEditor = ToolkitEditorFactory

### EOF #######################################################################
