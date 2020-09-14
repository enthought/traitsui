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

""" This module contains targets for UIWrapper so that the logic related to
them can be reused. All handlers and solvers for these objects are
registered to the default registry via the register class methods. To use the
logic in these objects, one simply needs to register a solver with their
target_class of choice to one of these as the locator_class. For an example,
see the implementation of range_editor.
"""

from traitsui.testing.tester import command, query
from traitsui.testing.tester.wx import helpers


class LocatedTextbox:
    """ Wrapper class for a located Textbox in Wx.

    Parameters
    ----------
    textbox : Instance of wx.TextCtrl
    """

    def __init__(self, textbox):
        self.textbox = textbox

    @classmethod
    def register(cls, registry):
        """ Class method to register interactions on a LocatedTextbox for the
        given registry.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        handlers = [
            (command.KeySequence,
                (lambda wrapper, interaction: helpers.key_sequence_text_ctrl(
                    wrapper.target.textbox, interaction, wrapper.delay))),
            (command.KeyClick,
                (lambda wrapper, interaction: helpers.key_click_text_entry(
                    wrapper.target.textbox, interaction, wrapper.delay))),
            (command.MouseClick,
                (lambda wrapper, _: helpers.mouse_click_object(
                    wrapper.target.textbox, wrapper.delay))),
            (query.DisplayedText,
                lambda wrapper, _: wrapper.target.textbox.GetValue()),
        ]
        for interaction_class, handler in handlers:
            registry.register_handler(
                target_class=cls,
                interaction_class=interaction_class,
                handler=handler,
            )
