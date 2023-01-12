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
Creating settable cached Property in Traits

How to create a Traits Property which is cached but is not read-only.

The example demonstrates how to create a 'settable cached' property. The example
itself is nonsensical, and is provided mainly to show how to set up such a
property, and how it differs from a standard 'cached' property.

A normal 'cached' property does not have a 'setter' method, meaning that the
property is read-only. It usually represents a value which depends upon the
state of other traits for its value. The cached property provides both a
mechanism for remembering (i.e. caching) the current value of the property as
well as a means of automatically detecting when the value of the property
changes (which causes the cache to be flushed), and notifying any associated
trait listeners that the value of the property has changed.

Normally there is no 'setter' for such a property because the value is derived
from the value of other traits.

However, it is possible to define a 'settable cached' property which in addition
to the capabilities of a normal 'cached' property, also allows the property's
value to be explicitly set.

To accomplish this, simply add a '_set_*' method as usual for a settable property
(see the '_set_c' method in the example code) which takes the value provided
and changes the values the property depends on appropriately based on the new
value.

This allows code to set the value of the property directly if desired, subject
to any constraints specified in the property declaration. For example, in the
example, the 'c' trait is a 'settable cached' property whose value must be an
integer. Attempting to set a non-integer value of the property will raise an
exception, just like any other trait would.

If any of the traits which the property depends upon change value, the current
value of the property will be flushed from the cache and a change notification
for the property will be generated. Any code that then attempts to read the
value of the property will result in the cache being reloaded with the new value
returned by the property's 'getter' method.

In the example, trait 'c' is a 'settable cached' property which returns the
product of 'a' times 'b', and trait 'd' is a normal 'cached' property that
returns double the value of 'c'.

To see the effect of these traits in action, try moving the 'a' and 'b' sliders
and watching the 'c' and 'd' traits update. This demonstrates how 'c' and 'd'
are properties that depend upon the values of other traits.

Now try changing the value of the 'c' trait by moving the slider or typing a
new value into the text entry field. You will see that the 'd' trait updates
as well, illustrating that the 'c' trait can be set directly, as well as
indirectly by changes to 'a' and 'b'.

Also, try typing non-numeric values into the 'c' field and you will see that
any values set are being type checked as well (i.e. they must be integer
values).

Now try typing a value into the 'd' trait and you will see that an error
results (indicated by the text entry field turning red), because this is a
normal 'cached' trait that has no 'setter' method defined.
"""
from math import sqrt

from traits.api import HasTraits, Int, Range, Property, cached_property
from traitsui.api import View, Item, RangeEditor

# -- Demo Class -----------------------------------------------------------


class SettableCachedProperty(HasTraits):

    a = Range(1, 10)
    b = Range(1, 10)
    c = Property(Int, observe=['a', 'b'])
    d = Property(observe='c')

    view = View(
        Item('a'),
        Item('b'),
        '_',
        Item('c', editor=RangeEditor(low=1, high=100, mode='slider')),
        Item('c'),
        '_',
        Item('d', editor=RangeEditor(low=1, high=400, mode='slider')),
        Item('d'),
        width=0.3,
    )

    @cached_property
    def _get_c(self):
        return self.a * self.b

    def _set_c(self, value):
        self.a = int(sqrt(value))
        self.b = int(sqrt(value))

    @cached_property
    def _get_d(self):
        return self.c + self.c


# -- Run the demo ---------------------------------------------------------

# Create the demo:
demo = SettableCachedProperty()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
