from traits.api import HasTraits, Int
import wx


class Counter(HasTraits):
    value = Int()


Counter().edit_traits()
wx.PySimpleApp().MainLoop()
