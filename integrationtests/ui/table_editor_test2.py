# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# -------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------

from traits.api import HasStrictTraits, Str, Int, Regex, List

from traitsui.api import View

# -------------------------------------------------------------------------
#  'Person' class:
# -------------------------------------------------------------------------


class Person(HasStrictTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    name = Str()
    age = Int()
    phone = Regex(value='000-0000', regex=r'\d\d\d[-]\d\d\d\d')

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(
        'name',
        'age',
        'phone',
        title='Create new person',
        width=0.18,
        buttons=['OK', 'Cancel'],
    )


# -------------------------------------------------------------------------
#  'WorkingPerson' class
# -------------------------------------------------------------------------


class WorkingPerson(Person):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    job = Str()

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(
        'name',
        'age',
        'phone',
        'job',
        title='Create new working person.........',
        width=0.18,
        buttons=['OK', 'Cancel'],
    )


# -------------------------------------------------------------------------
#  Sample data:
# -------------------------------------------------------------------------

people = [
    Person(name='Dave', age=39, phone='555-1212'),
    Person(name='Mike', age=28, phone='555-3526'),
    WorkingPerson(name='Joe', age=34, phone='555-6943', job='Fireman'),
    Person(name='Tom', age=22, phone='555-7586'),
    Person(name='Dick', age=63, phone='555-3895'),
    Person(name='Harry', age=46, phone='555-3285'),
    WorkingPerson(name='Sally', age=43, phone='555-8797', job='Soldier'),
    Person(name='Fields', age=31, phone='555-3547'),
]

# -------------------------------------------------------------------------
#  'TableTest' class:
# -------------------------------------------------------------------------


class TableTest(HasStrictTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    people = List(Person)

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(['people#', '|<>'], resizable=True)


# -------------------------------------------------------------------------
#  Run the tests:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    tt = TableTest(people=people)
    tt.configure_traits()
    for p in tt.people:
        p.print_traits()
        print('--------------')
