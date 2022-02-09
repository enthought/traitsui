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

import wx

from traits.api import Trait, HasTraits, Str, Int
from traitsui.api import Color, View, Group

# -------------------------------------------------------------------------
#  Model classes:
# -------------------------------------------------------------------------


class Employer(HasTraits):
    company = Str('Enthought, Inc.')
    boss = Str('eric')

    view = View('company', 'boss')


class Person(HasTraits):
    name = Str('David Morrill')
    age = Int(39)


class ExtraPerson(Person):
    sex = Trait('Male', 'Female')
    eye_color = Color


class LocatedPerson(Person):
    street = Str()
    city = Str()
    state = Str()
    zip = Int(78663)


class EmployedPerson(LocatedPerson):
    employer = Trait(Employer())


# -------------------------------------------------------------------------
#  View classes:
# -------------------------------------------------------------------------


class PersonView(HasTraits):
    view = View('name', '<extra>', 'age', kind='modal')


class ExtraPersonView(PersonView):
    extra = Group('sex', 'eye_color')


class LocatedPersonView(PersonView):
    extra = Group('street', 'city', 'state', 'zip')


class EmployedPersonView(LocatedPersonView):
    extra = Group('employer', '<extra>')


# -------------------------------------------------------------------------
#  'TraitSheetApp' class:
# -------------------------------------------------------------------------


class TraitSheetApp(wx.App):

    # -------------------------------------------------------------------------
    #  Initialize the object:
    # -------------------------------------------------------------------------

    def __init__(self):
        wx.InitAllImageHandlers()
        wx.App.__init__(self, 1, 'debug.log')
        self.MainLoop()

    # -------------------------------------------------------------------------
    #  Handle application initialization:
    # -------------------------------------------------------------------------

    def OnInit(self):
        PersonView().edit_traits(context=Person())
        ExtraPersonView().edit_traits(context=ExtraPerson())
        LocatedPersonView().edit_traits(context=LocatedPerson())
        EmployedPersonView().edit_traits(context=EmployedPerson())
        return True


# -------------------------------------------------------------------------
#  Main program:
# -------------------------------------------------------------------------

TraitSheetApp()
