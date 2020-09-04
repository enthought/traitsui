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

from traitsui.wx.enum_editor import (
    ListEditor,
    RadioEditor,
    SimpleEditor,
)
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.base_classes import _BaseSourceWithLocation
from traitsui.testing.tester.wx import helpers


class _IndexedListEditor(_BaseSourceWithLocation):
    """ Wrapper class for EnumListEditor and Index.
    """
    source_class = ListEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_listbox(
            control=wrapper.target.source.control,
            index=wrapper.target.location.index,
            delay=wrapper.delay))),
    ]


class _IndexedRadioEditor(_BaseSourceWithLocation):
    """ Wrapper class for EnumRadioEditor and Index.
    """
    source_class = RadioEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick,
            (lambda wrapper, _: helpers.mouse_click_radiobutton_child_in_panel(
                control=wrapper.target.source.control,
                index=wrapper.target.location.index,
                delay=wrapper.delay))),
    ]


class _IndexedSimpleEditor(_BaseSourceWithLocation):
    """ Wrapper class for Simple EnumEditor and Index.
    """
    source_class = SimpleEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick,
            (lambda wrapper, _: helpers.mouse_click_combobox_or_choice(
                control=wrapper.target.source.control,
                index=wrapper.target.location.index,
                delay=wrapper.delay))),
    ]


def displayed_text_handler(wrapper, interaction):
    """ Handler function used to query DisplayedText for different
    styles of Enum Editor.

    Parameters
    ----------
    wrapper : UIWrapper
        The UIWrapper containing that object with text to be displayed.
    interaction : query.DisplayedText
        Unused in this function but included to match the expected format of a
        handler.  Should only be query.DisplayedText
    """
    control = wrapper.target.control
    if isinstance(control, wx.ComboBox):
        return control.GetValue()
    else:  # wx.Choice or wx.ListBox
        return control.GetString(control.GetSelection())


def register(registry):
    """ Registry location and interaction handlers for EnumEditor.

    Parameters
    ----------
    registry : InteractionRegistry
    """
    _IndexedListEditor.register(registry)
    _IndexedRadioEditor.register(registry)
    _IndexedSimpleEditor.register(registry)

    simple_editor_text_handlers = [
        (command.KeyClick,
            (lambda wrapper, interaction: helpers.key_click_text_ctrl(
                control=wrapper.target.control,
                interaction=interaction,
                delay=wrapper.delay))),
        (command.KeySequence,
            (lambda wrapper, interaction: helpers.key_sequence_text_ctrl(
                control=wrapper.target.control,
                interaction=interaction,
                delay=wrapper.delay))),
    ]

    for interaction_class, handler in simple_editor_text_handlers:
        registry.register_handler(
            target_class=SimpleEditor,
            interaction_class=interaction_class,
            handler=handler
        )

    for target_class in [SimpleEditor, RadioEditor, ListEditor]:
        registry.register_handler(
            target_class=target_class,
            interaction_class=query.DisplayedText,
            handler=displayed_text_handler,
        )
