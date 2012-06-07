from traits.api import Instance, HasTraits
from traitsui.api import View, Item
from chaco.api import Plot, ArrayPlotData
from enable.component_editor import ComponentEditor
from numpy import sin, cos, linspace, pi

class Test(HasTraits):
    plot = Instance(Plot, ())
    
    view = View(Item('plot',editor = ComponentEditor(),
                show_label = False) , width = 400, height = 300,
                resizable = True)
    
    def __init__(self):
        t = linspace(0, 2*pi, 200)
        x = sin(t)*(1+0.5*cos(11*t))
        y = cos(t)*(1+0.5*cos(11*t))
        plotdata = ArrayPlotData(x = x, y = y)
        plot = Plot(plotdata)
        plot.plot(("x","y"), type = 'line', color = 'blue')
        self.plot = plot

if __name__ == '__main__':
    Test().configure_traits()