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
Dynamic changing an Enum selection list, depending on checked items

Another way to dynamically change the values shown by an EnumEditor.

The scenario is a restaurant that at the beginning of the day has a menu list
of entrees based upon a fully stocked kitchen. However, as the day progresses,
the kitchen's larder gets depleted, and the kitchen may no longer be able to
prepare certain entrees, which must then be deleted from the menu. Similarly,
deliveries may allow certain entrees to be added back onto the menu.

The demo is divided into two tabs: Order and Kitchen.

The Order tab represents a customer's order and consists of a single Entree
field, which represents the customer's selection from the drop-down list of
entrees that the kitchen can currently prepare.

The Kitchen tab represents the current set of entrees that the kitchen can
prepare, based upon the current contents of its larder.

As entrees are checked on or off from the Kitchen tab, the customer's Entree
drop-down is dynamically updated with the current list of available entrees.

Notes:

- The key point of the demo is the use of the 'name' trait in the EnumEditor
  definition, which links the list of available entrees from the
  KitchenCapabilities object to the OrderMenu object's entree EnumEditor.

- The user can freely type any value they want, but only items in the
  capabilities will be accepted, due to the use of the 'values' argument
  to the Enum trait.  This will be updated as the capabilities change.

- With the Qt backend, the user can type text and it will be auto-completed
  to valid values as a the user types. The Wx backend doesn't support this
  capability in the underlying toolkit.

- The design will work with any number of active OrderMenu objects, since they
  all share a common KitchenCapabilities object. As the KitchenCapabilities
  object is updated, all OrderMenu UI's will automatically update their
  associated Entree's drop-down list.

- A careful reader will also observe that this example contains only
  declarative code. No imperative code is required to handle the automatic
  updating of the Entree list.

"""


from traits.api import Enum, HasPrivateTraits, Instance, List

from traitsui.api import (
    View,
    Item,
    VGroup,
    HSplit,
    EnumEditor,
    CheckListEditor,
)

# -- The list of possible entrees -----------------------------------------

possible_entrees = [
    'Chicken Fried Steak',
    'Chicken Fingers',
    'Chicken Enchiladas',
    'Cheeseburger',
    'Pepper Steak',
    'Beef Tacos',
    'Club Sandwich',
    'Ceasar Salad',
    'Cobb Salad',
]

# -- The KitchenCapabilities class ----------------------------------------


class KitchenCapabilities(HasPrivateTraits):

    # The current set of entrees the kitchen can make (based on its larder):
    available = List(possible_entrees)


# The KitchenCapabilities are shared by all waitstaff taking orders:
kitchen_capabilities = KitchenCapabilities()

# -- The OrderMenu class --------------------------------------------------


class OrderMenu(HasPrivateTraits):

    # The person's entree order:
    entree = Enum(values='capabilities.available')

    # Reference to the restaurant's current entree capabilities:
    capabilities = Instance(KitchenCapabilities)

    def _capabilities_default(self):
        return kitchen_capabilities

    # The user interface view:
    view = View(
        HSplit(
            VGroup(
                Item(
                    'entree',
                    editor=EnumEditor(
                        name='object.capabilities.available',
                        evaluate=str,
                        completion_mode='popup',
                    ),
                ),
                label='Order',
                show_border=True,
                dock='tab',
            ),
            VGroup(
                Item(
                    'object.capabilities.available',
                    show_label=False,
                    style='custom',
                    editor=CheckListEditor(values=possible_entrees),
                ),
                label='Kitchen',
                show_border=True,
                dock='tab',
            ),
        ),
        title='Dynamic EnumEditor Demo',
        resizable=True,
    )


# -------------------------------------------------------------------------

# Create the demo:
demo = OrderMenu()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    print(demo.entree)
