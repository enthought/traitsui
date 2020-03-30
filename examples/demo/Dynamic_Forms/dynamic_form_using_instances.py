"""
Dynamic restructuring a user interface using Instance editor and Handler

How to dynamically change the *structure* of a user interface (not merely which
components are visible), depending on the value of another trait.

This code sample shows a simple implementation of the dynamic
restructuring of a View on the basis of some trait attribute's
assigned value.

The demo class "Person" has attributes that apply to all instances
('first_name', 'last_name', 'age') and a single attribute 'misc'
referring to another object whose traits are specific to age
group (AdultSpec for adults 18 and over, ChildSpec for children
under 18).  The 'misc' attribute is re-assigned to a new instance
of the appropriate type when a change to 'age' crosses the range
boundary.

The multi-attribute instance assigned to 'misc' is edited by means
of a single InstanceEditor, which is displayed in the 'custom' style
so that the dynamic portion of the interface is displayed in a panel
rather than a separate window.

It is necessary to use a Handler because otherwise when the instance is
updated dynamically, Traits UI will not detect the change and the UI will not
be reconfigured. This is due to architectural limitations of the current
version of Traits UI.

Compare this to the simpler, but less powerful demo of *enabled_when*.
"""

from traits.api import HasTraits, Str, Range, Enum, Bool, Instance

from traitsui.api import Item, Group, View, Handler, Label


class Spec(HasTraits):
    """ An empty class from which all age-specific trait list classes are
        derived.
    """
    pass


class ChildSpec(Spec):
    """ Trait list for children (assigned to 'misc' for a Person when age < 18).
    """
    legal_guardian = Str
    school = Str
    grade = Range(1, 12)

    traits_view = View('legal_guardian',
                       'school',
                       'grade')


class AdultSpec(Spec):
    """ Trait list for adults (assigned to 'misc' for a Person when age >= 18).
    """

    marital_status = Enum('single', 'married', 'divorced', 'widowed')
    registered_voter = Bool
    military_service = Bool

    traits_view = View('marital_status',
                       'registered_voter',
                       'military_service')


class PersonHandler(Handler):
    """ Handler class to perform restructuring action when conditions are met.
    The restructuring consists of replacing a ChildSpec instance by an
    AdultSpec instance, or vice-versa. We would not need a handler to listen
    for a change in age, but we do need a Handler so that Traits UI will
    respond immediately to changes in the viewed Person, which require
    immediate restructuring of the UI.
    """

    def object_age_changed(self, info):
        if ((info.object.age >= 18) and
                (not isinstance(info.object.misc, AdultSpec))):
            info.object.misc = AdultSpec()
        elif ((info.object.age < 18) and
              (not isinstance(info.object.misc, ChildSpec))):
            info.object.misc = ChildSpec()


class Person(HasTraits):
    """ Demo class for demonstrating dynamic interface restructuring.
    """
    first_name = Str
    last_name = Str
    age = Range(0, 120)
    misc = Instance(Spec)

    # Interface for attributes that are always visible in interface:
    gen_group = Group(
        Item(name='first_name'),
        Item(name='last_name'),
        Item(name='age'),
        label='General Info',
        show_border=True
    )

    # Interface for attributes that depend on the value of 'age':
    spec_group = Group(
        Group(
            Item(name='misc', style='custom'),
            show_labels=False
        ),
        label='Additional Info',
        show_border=True
    )

    # A simple View is enough as long as the right handler is specified:
    view = View(
        Group(
            gen_group,
            '10',
            Label("Using Instances and a Handler:"),
            '10',
            spec_group
        ),
        title='Personal Information',
        buttons=['OK'],
        resizable=True,
        width=300,
        handler=PersonHandler()
    )

# Create the demo:
demo = Person(first_name="Samuel",
              last_name="Johnson",
              age=18,
              misc=AdultSpec())

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
