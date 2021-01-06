# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Control the height and width of a Group

TraitsUI does not permit explicit specification of the height or width of a
Group (or its descendants). The workaround is to put each Group whose size you
wish to control into its own View class, which can be an Item (hence can be
size-controlled) in the larger View. Sometimes it is necessary to repeat such
surgery at several levels to get the desired layout.

We separate the left and right groups by a splitter (HSplit), and also
make the window itself resizable.

This demo includes a simple Chaco plot for variety, but it is not a Chaco demo.

"""
from numpy import linspace, pi, sin
from traits.api import HasTraits, Instance, Str, Int
# UItem is Unlabeled Item
from traitsui.api import View, Item, UItem, HSplit, InstanceEditor, \
    VGroup, HGroup
from chaco.api import Plot, AbstractPlotData, ArrayPlotData
from enable.component_editor import ComponentEditor


class InstanceUItem(UItem):
    """Convenience class for including an Instance in a View"""
    style = Str('custom')
    editor = Instance(InstanceEditor, ())


class PlotView(HasTraits):
    """Defines a sub-view whose size we wish to explicitly control."""
    n = Int(123)
    data = Instance(AbstractPlotData)
    plot1 = Instance(Plot)
    view = View(
        # This HGroup keeps 'n' from over-widening, by implicitly placing
        # a spring to the right of the item.
        HGroup(Item('n')),
        UItem('plot1', editor=ComponentEditor()),
        resizable=True,
    )

    def create_plot(self, data, name, color):
        p = Plot(self.data)
        p.plot(data, name=name, color=color)
        return p

    def _data_changed(self):
        self.plot1 = self.create_plot(("x", "y1"), "sin plot", "red")


class VerticalBar(HasTraits):
    """Defines a sub-view whose size we wish to explicitly control."""
    a = Str('abcdefg')
    b = Int(123)
    view = View(
        VGroup(
            Item('a'),
            Item('b'),
            show_border=True,
        ),
    )


class BigView(HasTraits):
    """Defines the top-level view. It contains two side-by-side panels (a
    vertical bar and a plot under an integer) whose relative sizes we wish
    to control explicitly. If these were simply defined as Groups, we could
    not control their sizes. But by extracting them as separate classes with
    their own views, the resizing becomes possible, because they are loaded
    as Items now.
    """
    bar = Instance(VerticalBar, ())
    plot = Instance(PlotView)
    view = View(
        HSplit(
            # Specify pixel width of each sub-view. (Or, to specify
            # proportionate width, use a width < 1.0)
            # We specify the height here for sake of demonstration;
            # it could also be specified for the top-level view.
            InstanceUItem('bar', width=150),
            InstanceUItem('plot', width=500, height=500),
            show_border=True,
        ),
        resizable=True,
    )

x = linspace(-2 * pi, 2 * pi, 100)
pv = PlotView(data=ArrayPlotData(x=x, y1=sin(x)))
bv = BigView(plot=pv)
bv.configure_traits()
