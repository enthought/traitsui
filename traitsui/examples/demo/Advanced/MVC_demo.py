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
Supporting Model/View/Controller (MVC) pattern

Demonstrates one approach to writing Model/View/Controller (MVC)-based
applications using Traits UI.

This example contains a trivial model containing only one data object, the
string 'myname'.

In this example, the Controller contains the View. A more rigorous example
would separate these.

A few key points:

- the Controller itself accesses the model as self.model
- the Controller's View can access model traits directly ('myname')
"""

from traits.api import HasTraits, Str, Bool, TraitError
from traitsui.api import View, VGroup, HGroup, Item, Controller


class MyModel(HasTraits):
    """Define a simple model containing a single string, 'myname'"""

    # Simple model data:
    myname = Str()


class MyViewController(Controller):
    """Define a combined controller/view class that validates that
    MyModel.myname is consistent with the 'allow_empty_string' flag.
    """

    # When False, the model.myname trait is not allowed to be empty:
    allow_empty_string = Bool()

    # Last attempted value of model.myname to be set by user:
    last_name = Str()

    # Define the view associated with this controller:
    view = View(
        VGroup(
            HGroup(
                Item('myname', springy=True),
                '10',
                Item('controller.allow_empty_string', label='Allow Empty'),
            ),
            # Add an empty vertical group so the above items don't end up
            # centered vertically:
            VGroup(),
        ),
        resizable=True,
    )

    # -- Handler Interface ----------------------------------------------------

    def myname_setattr(self, info, object, traitname, value):
        """Validate the request to change the named trait on object to the
        specified value.  Validation errors raise TraitError, which by
        default causes the editor's entry field to be shown in red.
        (This is a specially named method <model trait name>_setattr,
        which is available inside a Controller.)
        """
        self.last_name = value
        if (not self.allow_empty_string) and (value.strip() == ''):
            raise TraitError('Empty string not allowed.')

        return super().setattr(info, object, traitname, value)

    # -- Event handlers -------------------------------------------------------

    def controller_allow_empty_string_changed(self, info):
        """'allow_empty_string' has changed, check the myname trait to ensure
        that it is consistent with the current setting.
        """
        if (not self.allow_empty_string) and (self.model.myname == ''):
            self.model.myname = '?'
        else:
            self.model.myname = self.last_name


# Create the model and (demo) view/controller:
demo = MyViewController(MyModel())

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
