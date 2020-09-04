#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

import wx

from traitsui.wx.text_editor import CustomEditor, ReadonlyEditor, SimpleEditor
from traitsui.testing.tester import query
from traitsui.testing.tester.wx.registry_helper import (
    register_editable_textbox_handlers,
)


def readonly_displayed_text_handler(wrapper, interaction):
    ''' Handler for ReadonlyEditor to handle query.DisplayedText interactions.

    Parameters
    ----------
    wrapper : UIWrapper
        the UIWrapper object wrapping the ReadonlyEditor
    interaction : Instance of query.DisplayedText
        This arguiment is not used by this function. It is included so that
        the function matches the standard format for a handler.  The intended
        interaction should always be query.DisplayedText

    Notes
    -----
    wx Readonly Editors occassionally use wx.TextCtrl as their control, and
    other times use wx.StaticText.
    '''
    if isinstance(wrapper.target.control, wx.TextCtrl):
        return wrapper.target.control.GetValue()
    elif isinstance(wrapper.target.control, wx.StaticText):
        return wrapper.target.control.GetLabel()
    raise TypeError("readonly_displayed_text_handler expected a UIWrapper with"
                    " a ReadonlyEditor as a target. ReadonlyEditor control"
                    " should always be either wx.TextCtrl, or wx.StaticText."
                    " {} was found".format(wrapper.target.control))


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """

    for target_class in [CustomEditor, SimpleEditor]:
        register_editable_textbox_handlers(
            registry=registry,
            target_class=target_class,
            widget_getter=lambda wrapper: wrapper.target.control,
        )

    registry.register_handler(
        target_class=ReadonlyEditor,
        interaction_class=query.DisplayedText,
        handler=readonly_displayed_text_handler,
    )
