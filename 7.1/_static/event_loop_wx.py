# event_loop_wx.py

import wx

from traits.api import HasTraits, Int


class Counter(HasTraits):
    value = Int()


Counter().edit_traits()
wx.App().MainLoop()
