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

from traitsui.wx.enum_editor import (
    ListEditor,
    RadioEditor,
    SimpleEditor,
)
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.wx import helpers


class _IndexedListEditor:
    """ Wrapper for (list) EnumEditor and index """

    def __init__(self, target, index):
        self.target = target
        self.index = index

    @classmethod
    def register(cls, registry):
        registry.register_solver(
            target_class=ListEditor,
            locator_class=locator.Index,
            solver=lambda wrapper, location: 
                cls(target=wrapper.target, index=location.index),
        )
        registry.register_handler(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: helpers.mouse_click_listbox(
                control=wrapper.target.target.control,
                index=wrapper.target.index,
                delay=wrapper.delay,
            )
        )


class _IndexedRadioEditor:
    """ Wrapper for RadioEditor and an index.
    """

    def __init__(self, target, index):
        self.target = target
        self.index = index

    @classmethod
    def register(cls, registry):
        registry.register_solver(
            target_class=RadioEditor,
            locator_class=locator.Index,
            solver=lambda wrapper, location:
                cls(target=wrapper.target,index=location.index),
        )
        registry.register_handler(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: helpers.mouse_click_child_in_panel(
                control=wrapper.target.target.control,
                index=wrapper.target.index,
                delay=wrapper.delay,
            )
        )


class _IndexedSimpleEditor:
    """ Wrapper for (simple) EnumEditor and an index."""

    def __init__(self, target, index):
        self.target = target
        self.index = index

    @classmethod
    def register(cls, registry):
        registry.register_solver(
            target_class=SimpleEditor,
            locator_class=locator.Index,
            solver=lambda wrapper, location:
                cls(target=wrapper.target, index=location.index),
        )
        registry.register_handler(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: helpers.mouse_click_combobox_or_choice(
                control=wrapper.target.target.control,
                index=wrapper.target.index,
                delay=wrapper.delay,
            ),
        )


def register(registry):
    """ Registry location and interaction handlers for EnumEditor.

    Parameters
    ----------
    registry : InteractionRegistry
    """
    _IndexedListEditor.register(registry)
    _IndexedRadioEditor.register(registry)
    _IndexedSimpleEditor.register(registry)