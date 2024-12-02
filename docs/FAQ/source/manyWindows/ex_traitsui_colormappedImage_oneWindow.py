## ex_traitsUI.colormappedImage_oneWindow.py

# standard imports
import os
from math import atan2, sqrt

# numpy imports
from numpy import sin, cos, exp, linspace, meshgrid, pi

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Range, Str, on_trait_change
from traitsui.api import Item, Group, View
from chaco.api import ArrayPlotData, jet, Plot

# the window size and title. the title is the file name
windowSize = (800,600)
windowTitle = os.path.split(__file__)[1]

class OneWindow( HasTraits ):
  '''an image/scatter plot with graphics and control traits in one window'''

  # range values for the X and Y position of the point
  # x position. suffix TR => Traits Range
  xPosTR = Range(
      value = 0.0,
      low = -7.0,
      high = 7.0,
      label = "X",
      desc = "the x position",
  )

  # y position. suffix TR => Traits Range
  yPosTR = Range(
      value = 0.0,
      low = -7.0,
      high = 7.0,
      label = "Y",
      desc = "the y position",
  )

  # the X,Y position in polar coordinates.  suffix TS => Traits String
  polarXYTS = Str(
      value = 'Indeterminate',
      default_value = 'Indeterminate',
      label = "Polar",
      desc = "the x,y point in polar coordinates",
  )

  # create an interesting scalar field for the image plot
  twoPi = 2.0 * pi
  xA = linspace(-twoPi, twoPi, 600)
  yA = linspace(-twoPi, twoPi, 600)
  ( xMG,yMG ) = meshgrid( xA,yA )
  z1MG = exp(-(xMG**2 + yMG**2)) / 100.0
  zxMG = sin( xMG ) / xMG
  zyMG = sin( yMG ) / yMG
  zMG = zxMG + zyMG

  # Create an ArrayPlotData object and give it this data
  pdAPD = ArrayPlotData()
  pdAPD.set_data( "Z", zMG )
  pdAPD.set_data( "X",[xPosTR.default_value] )
  pdAPD.set_data( "Y",[yPosTR.default_value] )

  # Create the plot
  plotP = Plot( pdAPD )

  # add the image plot to this plot object
  plotP.img_plot(
      "Z",
      xbounds = (-7,7),
      ybounds = (-7,7),
      colormap = jet,
  )

  # add a scatter plot to this plot object to plot the single (X,Y) point
  plotP.plot(
      ("X","Y"),
      type = 'scatter',
      marker = "circle",
      color = "white",
      marker_size = 5,
  )

  # add the title and padding around the plot
  plotP.title = "2D sin(x)/x"
  plotP.padding = 50

  # grids, fonts, etc
  plotP.x_grid.visible = True
  plotP.y_grid.visible = True
  plotP.x_axis.font = "modern 16"
  plotP.y_axis.font = "modern 16"
  plotP.x_axis.title = "X Phase (rad)"
  plotP.y_axis.title = "Y Phase (rad)"

  @on_trait_change( 'xPosTR, yPosTR' )
  def _calculate_polarXY(self, name, new):
    '''calculate a new polar coordinate whenever x or y changes.
        also, load the new (X,Y) position into the scatter plot'''

    radius = sqrt( self.xPosTR * self.xPosTR + self.yPosTR * self.yPosTR )
    try:
      angle = (180.0/pi) * atan2( self.yPosTR, self.xPosTR )
      self.polarXYTS = 'radius: %.2f, theta = %.2f' % (radius,angle)
    except:
      self.polarXYTS = 'Indeterminate'

    # manually change the scatter plot data
    oneWindow.pdAPD.set_data( "X",[self.xPosTR] )
    oneWindow.pdAPD.set_data( "Y",[self.yPosTR] )

  # set up the view for both the graphics and control
  traits_view = View(
      Group(
          Item(
              'plotP',
              editor = ComponentEditor(size = windowSize),
              show_label = False,
          ),
          Item( 'xPosTR' ),
          Item( 'yPosTR' ),
          Item( 'polarXYTS', style = 'readonly' ),
          orientation = "vertical"
      ),
      resizable = True,
      title = windowTitle
  )

if __name__ == "__main__":

  # build the object
  oneWindow = OneWindow()

  # set the (X,Y) point to form a 3-4-5 triangle. radius should
  # calculate to 5 and the angle should be around 53 degrees
  oneWindow.xPosTR = 3
  oneWindow.yPosTR = 4

  # build and edit the window. uses the traits_view view as the object view
  oneWindow.configure_traits()
