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
from traitsui.testing.tester import command, query
from traitsui.testing.tester.wx import helpers


def readonly_DisplayedText_handler(wrapper, interaction):
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
        return wrapper.target.control.label


def register(registry):
    
    handlers = [
        (command.KeyClick, (lambda wrapper, interaction: helpers.key_click_text_ctrl(
                            wrapper.target.control, interaction, wrapper.delay))),
        (command.KeySequence, (lambda wrapper, interaction:  helpers.key_sequence_text_ctrl(
                                wrapper.target.control, interaction, wrapper.delay))),
        (query.DisplayedText, lambda wrapper, _: wrapper.target.control.GetValue())
    ]

    for target_class in [CustomEditor, SimpleEditor]:
        for interaction_class, handler in handlers:
            registry.register_handler(
                target_class=target_class,
                interaction_class=interaction_class,
                solver=handler,
            )

    registry.register_handler(
        target_class=ReadonlyEditor,
        interaction_class=query.DisplayedText,
        solver=readonly_DisplayedText_handler,
    )
