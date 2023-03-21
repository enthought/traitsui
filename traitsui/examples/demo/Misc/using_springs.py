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
Spacing widgets using springs

*Springs* are a simple technique for adding space before, after, or between
Traits UI editors (a.k.a. widgets).

By default, Traits UI arranges widgets immediately adjacent to each other --
from left to right in a horizontal group, or from top to bottom in a vertical
group. Sometimes this works well, but sometimes it results in widgets that are
placed confusingly, or have been unattractively stretched to fill available
space.

When you place a *spring* in a horizontal group, Traits UI will not try to fill
that space with an adjacent widget, instead allowing empty space which varies
depending on the overall size of the containing group.
"""

from traits.api import HasTraits, Button
from traitsui.api import View, VGroup, HGroup, Item, spring, Label

# dummy button which will be used repeatedly to demonstrate widget spacing:
button = Item('ignore', show_label=False)


class SpringDemo(HasTraits):

    ignore = Button('Ignore')

    view = View(
        VGroup(
            '10',
            Label(label='Spring in a horizontal group moves widget right:'),
            '10',
            HGroup(
                button,
                button,
                show_border=True,
                label='Left justified (no springs)',
            ),
            HGroup(
                spring,
                button,
                button,
                show_border=True,
                label='Right justified with a spring ' 'before any buttons',
            ),
            HGroup(
                button,
                spring,
                button,
                show_border=True,
                label='Left and right justified with a '
                'spring between buttons',
            ),
            HGroup(
                button,
                button,
                spring,
                button,
                button,
                spring,
                button,
                button,
                show_border=True,
                label='Left, center and right justified '
                'with springs after the 2nd and 4th '
                'buttons',
            ),
            spring,
            Label(
                'Spring in vertical group moves widget down '
                '(does not work on Wx backend).'
            ),
            button,
        ),
        width=600,
        height=600,
        resizable=True,
        title='Spring Demo',
        buttons=['OK'],
    )


demo = SpringDemo()

if __name__ == '__main__':
    demo.configure_traits()
