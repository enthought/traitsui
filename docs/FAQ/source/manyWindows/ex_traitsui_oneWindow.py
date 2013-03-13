# ex_traitsui_oneWindow.py - simple window demo

# Based upon Peter Wang's Interactive Plotting with Chaco talk given
# at the Scipy 2008 Advanced Tutorial Track, August 20, 2008

# standard imports
from math import atan2, sqrt, pi

# Enthought library imports
from traits.api import HasTraits, Str, Range, on_trait_change
from traitsui.api import Item, View, Group

class oneWindow( HasTraits ):
  '''one window with linked traits'''

  # x position. suffix TR => Traits Range
  xPosTR = Range(
        value = 0.0,
        low = -1000.0,
        high = 1000.0,
        label = "X",
        desc = "the x position"
  )

  # y position. suffix TR => Traits Range
  yPosTR = Range(
        value = 0.0,
        low = -1000.0,
        high = 1000.0,
        label = "Y",
        desc = "the y position",
  )

  # the X,Y position in polar coordinates.  suffix TS => Traits String
  polarXYTS = Str(
        value = 'Indeterminate',
        default_value = 'Indeterminate',
        label = "Polar",
        desc = "the x,y point in polar coordinates"
  )

  # calculate a new polar coordinate whenever x or y changes
  @on_trait_change( 'xPosTR, yPosTR' )
  def _calculate_polarXY(self, name, new):
    radius = sqrt( self.xPosTR * self.xPosTR + self.yPosTR * self.yPosTR )
    try:
      angle = (180.0/pi) * atan2( self.yPosTR, self.xPosTR )
      self.polarXYTS = 'radius: %.2f, theta = %.2f' % (radius,angle)
    except:
      self.polarXYTS = 'Indeterminate'

  # a window with both the x and y positions
  traits_view = View(
    Group(
      Item( 'xPosTR' ),
      Item( 'yPosTR' ),
      Item( 'polarXYTS',style = 'readonly' ),
    ),
    title = 'X/Y View',
  )

if __name__ == "__main__":

  oneWindow = oneWindow()
  oneWindow.configure_traits()

