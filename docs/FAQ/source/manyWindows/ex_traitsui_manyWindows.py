# ex_traitsui_manyWindows.py - multiple windowed gui with linked traits
#
# Particularly useful when the user wants one window to be a graphical
# display and the second window to contain the traitsUI controls
#
# Based upon Peter Wang's Interactive Plotting with Chaco talk given
# at the Scipy 2008 Advanced Tutorial Track, August 20, 2008

# standard imports
from math import atan2, sqrt, pi

# Enthought library imports
from traits.api import HasTraits, Str, Range
from traits.api import on_trait_change
from traitsui.api import Item, View, Group

class ManyWindows( HasTraits ):
  '''multiple windows with linked traits'''

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

if __name__ == "__main__":

  # create views for each window. Note that these views are not in the
  # ManyWindows class but in the main routine.

  # window containing only the x position and output string.
  # suffix TV => Traits View
  view1TV = View(
    Item( 'xPosTR' ),
    Item( 'polarXYTS',style = 'readonly' ),
    title = 'X View',
  )

  # window containing only the y position and output string
  view2TV = View(
    Item( 'yPosTR' ),
    Item( 'polarXYTS',style = 'readonly' ),
    title = 'Y View',
  )

  # a window with both the x and y positions
  view3TV = View(
    Group(
      Item( 'xPosTR' ),
      Item( 'yPosTR' ),
      Item( 'polarXYTS',style = 'readonly' ),
    ),
    title = 'X/Y View',
  )

  ## the x and y positions and polar equivalents in multiple windows
  view4TV = View(
    Group(
      Item( 'xPosTR' ),
      Item( 'polarXYTS',style = 'readonly' ),
      label = 'X View',
    ),
    Group(
      Item( 'yPosTR' ),
      Item( 'polarXYTS',style = 'readonly' ),
      label = 'Y View',
    ),
    title = 'Tabbed X/Y View'
  )

  manyWindows = ManyWindows()

  # Finally, call edit_traits() on the first object(s), but configure_traits()
  # the last object. The final configure_traits() will start the wxPython
  # main loop, which activates the service loops on all of the proceeding
  # edit_traits() calls. The result is many windows, with linked GUI items
  # and trias.
  manyWindows.edit_traits( view = view1TV )
  manyWindows.edit_traits( view = view2TV )
  manyWindows.edit_traits( view = view3TV )
  manyWindows.configure_traits( view = view4TV )

