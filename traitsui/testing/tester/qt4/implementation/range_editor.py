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

from traitsui.qt4.range_editor import (
    LargeRangeSliderEditor,
    LogRangeSliderEditor,
    RangeTextEditor,
    SimpleSliderEditor,
    SimpleSpinEditor,
)

from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.qt4 import helpers


class RangeEditorTextbox:
    def __init__(self, textbox):
        self.textbox = textbox

    @classmethod
    def register(cls, registry):
        handlers = [
            (command.KeySequence, (lambda wrapper, interaction: helpers.key_sequence_qwidget(
                                    wrapper.target.textbox, interaction.sequence, wrapper.delay))),
            (command.KeyClick, (lambda wrapper, interaction: helpers.key_click_qwidget(
                                wrapper.target.textbox, interaction.key, wrapper.delay))),
            (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_qwidget(
                wrapper.target.textbox, wrapper.delay))),
            (query.DisplayedText, lambda wrapper, _: wrapper.target.textbox.displayText()),
        ]
        for interaction_class, handler in handlers:
            registry.register_handler(
                target_class=cls,
                interaction_class=interaction_class,
                handler=handler,
            )


def resolve_location_simple_slider(wrapper, location):
    if location == locator.WidgetType.textbox:
        return RangeEditorTextbox(textbox=wrapper.editor.control.text)

    raise NotImplementedError()


def register(registry):

    targets = [SimpleSliderEditor,
               LogRangeSliderEditor,
               LargeRangeSliderEditor,
               RangeTextEditor]
    for target_class in targets:
        registry.register_solver(
            target_class=target_class,
            locator_class=locator.WidgetType,
            solver=resolve_location_simple_slider,
        )
    RangeEditorTextbox.register(registry)
