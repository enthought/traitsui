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
from traitsui.testing.tester import command
from traitsui.testing.tester.qt4 import _interaction_helpers, _registry_helper


class LocatedTextbox:
    """ Wrapper class for a located Textbox in Qt.

    Parameters
    ----------
    textbox : Instance of QtGui.QLineEdit
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
        _registry_helper.register_editable_textbox_handlers(
            registry=registry,
            target_class=cls,
            widget_getter=lambda wrapper: wrapper._target.textbox,
        )


class LocatedSlider:
    """ Wrapper class for a located Slider in Qt.

    Parameters
    ----------
    slider : Instance of QtGui.QSlider
    """

    def __init__(self, slider):
        self.slider = slider

    @classmethod
    def register(cls, registry):
        """ Class method to register interactions on a LocatedSlider for the
        given registry.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        registry.register_handler(
            target_class=cls,
            interaction_class=command.KeyClick,
            handler=lambda wrapper, interaction:
                _interaction_helpers.key_click_qslider(
                    wrapper._target.slider, interaction, wrapper.delay)
        )
