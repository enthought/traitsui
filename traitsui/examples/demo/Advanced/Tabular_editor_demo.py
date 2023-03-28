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
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

Tabular editor

The TabularEditor can be used for many of the same purposes as the TableEditor,
that is, for displaying a table of attributes of lists or arrays of objects.

While similar in function, the tabular editor has advantages and disadvantages
relative to the table editor. See the Traits UI User Manual for details.

This example defines three classes:

- *Person*: A single person.
- *MarriedPerson*: A married person (subclass of Person).
- *Report*: Defines a report based on a list of single and married people.

It creates a tabular display of 10,000 single and married people showing the
following information:

- Name of the person.
- Age of the person.
- The person's address.
- The name of the person's spouse (if any).

In addition:

- It uses a Courier 10 point font for each line in the table.
- It displays age column right, instead of left, justified.
- If the person is a minor (age < 18) and married, it displays a red flag
  image in the age column.
- If the person is married, it makes the background color for that row a light
  blue.

- If this demo is running under QT, it displays each person's surname
  in a row label.

This example demonstrates:

- How to set up a *TabularEditor*.
- The display speed of the *TabularEditor*.
- How to create a *TabularAdapter* that meets each of the specified display
  requirements.

Additional notes:

- You can change the current selection using the up and down arrow keys.
- If the demo is running under WX, you can move a selected row up and down in
  the table using the left and right arrow keys.
- If the demo is running under QT, you can move rows by clicking and dragging.

Hopefully, this simple example conveys some of the power and flexibility that
the `TabularAdapter` class provides you. But, just in case it
doesn't, let's go over some of the more interesting details:

- Note the values in the `~TabularAdapter.columns` trait. The first
  three values define *column ids* which map directly to traits defined on our
  data objects, while the last one defines an arbitrary string which we define
  so that we can reference it in the `MarriedPerson_spouse_text` and
  `Person_spouse_text` trait definitions.

- Since the font we want to use applies to all table rows, we just specify a
  new default value for the existing `TabularAdapter.font` trait.

- Since we only want to override the default left alignment for the age column,
  we simply define an `age_alignment` trait as a constant ``'right'``
  value. We could have also used ``age_alignment = Str('right')``, but
  `Constant` never requires storage to be used in an object.

- We define the `MarriedPerson_age_image` property to handle putting
  the ``'red flag'`` image in the age column. By including the class name of
  the items it applies to, we only need to check the `age` value in
  determining what value to return.

- Similary, we use the `MarriedPerson_bg_color` trait to ensure that
  each `MarriedPerson` object has the correct background color in the
  table.

- Finally, we use the `MarriedPerson_spouse_text` and
  `Person_spouse_text` traits, one a property and the other a simple
  constant value, to determine what text to display in the *Spouse* column for
  the different object types.  Note that even though a
  `MarriedPerson` is both a `Person` and a
  `MarriedPerson`, it will correctly use the
  `MarriedPerson_spouse_text` trait since the search for a matching
  trait is always made in *mro* order.

Although this is completely subjective, some of the things that the author
feels stand out about this approach are:

- The class definition is short and sweet. Less code is good.
- The bulk of the code is declarative. Less room for logic errors.
- There is only one bit of logic in the class (the ``if`` statement in the
  `MarriedPerson_age_image` property implementation). Again, less
  logic usually translates into more reliable code).
- The defined traits and even the property implementation method names read
  very descriptively. `_get_MarriedPerson_age_image` pretty much says
  what you would write in a comment or doc string. The implementation almost is
  the documentation.

"""
# Issue related to the demo warning: enthought/traitsui#960

from functools import partial
from random import randint, choice, shuffle

from traits.api import HasTraits, Str, Int, List, Instance, Property, Constant
from traits.etsconfig.api import ETSConfig
from traitsui.api import (
    View,
    Group,
    Item,
    TabularAdapter,
    TabularEditor,
    Color,
)


# -- Person Class Definition ----------------------------------------------
class Person(HasTraits):

    name = Str()
    address = Str()
    age = Int()

    # surname is displayed in qt-only row label:
    surname = Property(fget=lambda self: self.name.split()[-1], observe='name')


# -- MarriedPerson Class Definition ---------------------------------------
class MarriedPerson(Person):

    partner = Instance(Person)


# -- Tabular Adapter Definition -------------------------------------------
class ReportAdapter(TabularAdapter):
    """The tabular adapter interfaces between the tabular editor and the data
    being displayed. For more details, please refer to the traitsUI user guide.
    """

    # List of (Column labels, Column ID).
    columns = [
        ('Name', 'name'),
        ('Age', 'age'),
        ('Address', 'address'),
        ('Spouse', 'spouse'),
    ]

    row_label_name = 'surname'

    # Interfacing between the model and the view: make some of the cell
    # attributes a property whose behavior is then controlled by the get
    # (and optionally set methods). The cell is identified by its column
    # ID (age, spouse).

    # Overwrite default value
    font = 'Courier 10'

    age_alignment = Constant('right')
    MarriedPerson_age_image = Property()
    MarriedPerson_bg_color = Color(0xE0E0FF)
    MarriedPerson_spouse_text = Property()
    Person_spouse_text = Constant('')

    def _get_MarriedPerson_age_image(self):
        if self.item.age < 18:
            return '@icons:red_ball'

        return None

    def _get_MarriedPerson_spouse_text(self):
        return self.item.partner.name


# -- Tabular Editor Definition --------------------------------------------
# The tabular editor works in conjunction with an adapter class, derived from
# TabularAdapter.
tabular_editor = TabularEditor(
    adapter=ReportAdapter(),
    operations=['move', 'edit'],
    # Row titles are not supported in WX:
    show_row_titles=(ETSConfig.toolkit in {"qt", "qt4"}),
)


# -- Report Class Definition ----------------------------------------------
class Report(HasTraits):

    people = List(Person)

    traits_view = View(
        Group(
            Item('people', id='table', editor=tabular_editor),
            show_labels=False,
        ),
        title='Tabular Editor Demo',
        id='traitsui.demo.Applications.tabular_editor_demo',
        width=0.60,
        height=0.75,
        resizable=True,
    )


# -- Generate 10,000 random single and married people ---------------------
male_names = [
    'Michael',
    'Edward',
    'Timothy',
    'James',
    'George',
    'Ralph',
    'David',
    'Martin',
    'Bryce',
    'Richard',
    'Eric',
    'Travis',
    'Robert',
    'Bryan',
    'Alan',
    'Harold',
    'John',
    'Stephen',
    'Gael',
    'Frederic',
    'Eli',
    'Scott',
    'Samuel',
    'Alexander',
    'Tobias',
    'Sven',
    'Peter',
    'Albert',
    'Thomas',
    'Horatio',
    'Julius',
    'Henry',
    'Walter',
    'Woodrow',
    'Dylan',
    'Elmer',
]

female_names = [
    'Leah',
    'Jaya',
    'Katrina',
    'Vibha',
    'Diane',
    'Lisa',
    'Jean',
    'Alice',
    'Rebecca',
    'Delia',
    'Christine',
    'Marie',
    'Dorothy',
    'Ellen',
    'Victoria',
    'Elizabeth',
    'Margaret',
    'Joyce',
    'Sally',
    'Ethel',
    'Esther',
    'Suzanne',
    'Monica',
    'Hortense',
    'Samantha',
    'Tabitha',
    'Judith',
    'Ariel',
    'Helen',
    'Mary',
    'Jane',
    'Janet',
    'Jennifer',
    'Rita',
    'Rena',
    'Rianna',
]

all_names = male_names + female_names

male_name = partial(choice, male_names)
female_name = partial(choice, female_names)
any_name = partial(choice, all_names)
age = partial(randint, 15, 72)


def family_name():
    return choice(
        [
            'Jones',
            'Smith',
            'Thompson',
            'Hayes',
            'Thomas',
            'Boyle',
            "O'Reilly",
            'Lebowski',
            'Lennon',
            'Starr',
            'McCartney',
            'Harrison',
            'Harrelson',
            'Steinbeck',
            'Rand',
            'Hemingway',
            'Zhivago',
            'Clemens',
            'Heinlien',
            'Farmer',
            'Niven',
            'Van Vogt',
            'Sturbridge',
            'Washington',
            'Adams',
            'Bush',
            'Kennedy',
            'Ford',
            'Lincoln',
            'Jackson',
            'Johnson',
            'Eisenhower',
            'Truman',
            'Roosevelt',
            'Wilson',
            'Coolidge',
            'Mack',
            'Moon',
            'Monroe',
            'Springsteen',
            'Rigby',
            "O'Neil",
            'Philips',
            'Clinton',
            'Clapton',
            'Santana',
            'Midler',
            'Flack',
            'Conner',
            'Bond',
            'Seinfeld',
            'Costanza',
            'Kramer',
            'Falk',
            'Moore',
            'Cramdon',
            'Baird',
            'Baer',
            'Spears',
            'Simmons',
            'Roberts',
            'Michaels',
            'Stuart',
            'Montague',
            'Miller',
        ]
    )


def address():
    number = randint(11, 999)
    text_1 = choice(
        [
            'Spring',
            'Summer',
            'Moonlight',
            'Winding',
            'Windy',
            'Whispering',
            'Falling',
            'Roaring',
            'Hummingbird',
            'Mockingbird',
            'Bluebird',
            'Robin',
            'Babbling',
            'Cedar',
            'Pine',
            'Ash',
            'Maple',
            'Oak',
            'Birch',
            'Cherry',
            'Blossom',
            'Rosewood',
            'Apple',
            'Peach',
            'Blackberry',
            'Strawberry',
            'Starlight',
            'Wilderness',
            'Dappled',
            'Beaver',
            'Acorn',
            'Pecan',
            'Pheasant',
            'Owl',
        ]
    )
    text_2 = choice(
        [
            'Way',
            'Lane',
            'Boulevard',
            'Street',
            'Drive',
            'Circle',
            'Avenue',
            'Trail',
        ]
    )
    return '%d %s %s' % (number, text_1, text_2)


people = [
    Person(
        name='%s %s' % (any_name(), family_name()),
        age=age(),
        address=address(),
    )
    for i in range(5000)
]

marrieds = [
    (
        MarriedPerson(
            name='%s %s' % (female_name(), last_name),
            age=age(),
            address=address,
        ),
        MarriedPerson(
            name='%s %s' % (male_name(), last_name), age=age(), address=address
        ),
    )
    for last_name, address in [(family_name(), address()) for i in range(2500)]
]

for female, male in marrieds:
    female.partner = male
    male.partner = female
    people.extend([female, male])

shuffle(people)


# Create the demo:
demo = Report(people=people)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
