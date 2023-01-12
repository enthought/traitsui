# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Display an editable List of Strings.

The ListStrEditor uses a custom ListStrAdapter to define colors and tooltips.
"""

from traitsui.list_str_adapter import ListStrAdapter
from traits.api import HasTraits, List, Str
from traitsui.api import View, Item, ListStrEditor


# -- The adapter ----------------------------------------------------------

class HeadlinesListAdapter(ListStrAdapter):
    """ Custom adapter for string lists being edited in the ListStrEditor.

    - Style ALL CAPS titles in red.
    - Describe the capitalization in the tooltip.
    """

    def get_text_color(self, object, trait, row):
        try:
            row_data = getattr(object, trait)[row]
        except IndexError:
            return ""

        if row_data.isupper():
            return "red"
        return super().get_text_color(object, trait, row)

    def get_tooltip(self, object, trait, row):
        try:
            row_data = getattr(object, trait)[row]
        except IndexError:
            # if the ListStr is editable, IndexError indicates the empty next slots
            return ""

        if row_data.isupper():
            return "An uppercase headline"
        elif row_data.istitle():
            return "A headline in title case"
        elif row_data.islower():
            return "A fully lowercase headline"
        else:
            return self.tooltip


# -- The class providing the view -------------------------------------

class HeadlinesListDemo(HasTraits):

    headlines = List(Str)

    view = View(
        Item(
            "headlines",
            show_label=False,
            editor=ListStrEditor(
                title="List of headlines (hover for description)",
                adapter=HeadlinesListAdapter(
                    # the default tooltip for generic rows
                    tooltip="A headline"
                ),
                auto_add=True
            ),
            # (QT only) the tooltip shown in the area outside of rows
            # or when the row's tooltip is empty
            tooltip="List of headlines"
        ),
        title='List of headlines',
        width=320,
        height=370,
        resizable=True,
    )


# -- Set up the Demo ------------------------------------------------------

demo = HeadlinesListDemo(
    headlines=[
        "Shark bites man",
        "MAN BITES SHARK",
        "The London Stock Exchange Collapses",
        "she sells sea shells on the sea shore"
    ]
)

# Run the demo (in invoked from the command line):
if __name__ == "__main__":
    demo.configure_traits()
