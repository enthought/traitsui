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
#  Model/View classes:
# -------------------------------------------------------------------------


class Employer(HasTraits):
    company = Str()
    boss = Str()

    view = View('company', 'boss')


class Person(HasTraits):
    name = Str('David Morrill')
    age = Int(39)

    view = View('name', '<extra>', 'age', kind='modal')


class ExtraPerson(Person):
    sex = Trait('Male', 'Female')
    eye_color = Color

    extra = Group('sex', 'eye_color')


class LocatedPerson(Person):
    street = Str()
    city = Str()
    state = Str()
    zip = Int(78663)

    extra = Group('street', 'city', 'state', 'zip')


class EmployedPerson(LocatedPerson):
    employer = Trait(Employer(company='Enthought, Inc.', boss='eric'))

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
        Person().edit_traits()
        ExtraPerson().edit_traits()
        LocatedPerson().edit_traits()
        EmployedPerson().edit_traits()
        return True


# -------------------------------------------------------------------------
#  Main program:
# -------------------------------------------------------------------------

TraitSheetApp()
