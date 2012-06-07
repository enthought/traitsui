#!/usr/bin/env python

from threading import Thread
from time import sleep
from traits.api import HasTraits, Instance, String, Float, Enum, Button
from traitsui.api import View, Item, Group, HSplit, Handler
from traitsui.menu import NoButtons
from scipy import rand, indices, exp, sqrt, sum
from chaco.api import ArrayPlotData, Plot
from enable.component_editor import ComponentEditor
from pyface.api import GUI

class Experiment(HasTraits):
    width = Float(30, label = 'width', desc = 'width of the cloud')
    x = Float(50, label = 'X', desc = 'X position of the center')
    y = Float(50, label = 'Y', desc = 'Y position of the center')

class Results(HasTraits):
    """ Object used to display the results.
    """
    width = Float(30, label="Width", desc="width of the cloud")
    x = Float(50, label="X", desc="X position of the center")
    y = Float(50, label="Y", desc="Y position of the center")
    view = View( Item('width', style='readonly'),
                 Item('x', style='readonly'),
                 Item('y', style='readonly'),
               )

class Camera(HasTraits):
    """ Camera objects. Implements both the camera parameters controls, and
        the picture acquisition.
    """
    exposure = Float(1, label="Exposure", desc="exposure, in ms")
    gain = Enum(1, 2, 3, label="Gain", desc="gain")

    def acquire(self, experiment):
       X, Y = indices((100, 100))
       Z = exp(-((X-experiment.x)**2+(Y-experiment.y)**2)/experiment.width**2)
       Z += 1-2*rand(100,100)
       Z *= self.exposure
       Z[Z>2] = 2
       Z = Z**self.gain
       return(Z)

def process(image, results_obj):
    """ Function called to do the processing """
    X, Y = indices(image.shape)
    x = sum(X*image)/sum(image)
    y = sum(Y*image)/sum(image)
    width = sqrt(abs(sum(((X-x)**2+(Y-y)**2)*image)/sum(image))) 
    results_obj.x = x
    results_obj.y = y
    results_obj.width = width

class AcquisitionThread(Thread):
    wants_abort = False
    def process(self, image):
        try:
            if self.processing_job.isAlive():
                self.display("Processing too slow")
                return
        except AttributeError:
            pass
        self.processing_job = Thread(target = process, args = (image, \
                                                               self.results))
        self.processing_job.start()    

    def run(self):
        self.display('Camera started')
        n_img = 0
        while not self.wants_abort:
            n_img += 1
            img = self.acquire(self.experiment)
            self.display('%d image captured' %n_img)
            self.image_show(img)
            self.process(img)
            sleep(1)

        self.display('Camera stopped')

class ControlPanel(HasTraits):
    experiment = Instance(Experiment, ())
    camera = Instance(Camera, ())
    plot = Instance(Plot, ())
    plotdata = Instance(ArrayPlotData, ())
    results = Instance(Results, ())
    results_string = String()
    start_stop_acquisition = Button('Start / Stop Acquisition')
    acquisition_thread = Instance(AcquisitionThread)
    view = View(Group(Group(Item('start_stop_acquisition', show_label = False),
                            Item('results_string', show_label = False,
                                 style = 'custom'),
                            label = "Control", dock = 'tab'),
                      Group(Group(Item('experiment', style = 'custom',
                                       show_label = False), label = 'Input'),
                            Group(Item('results', style = 'custom',
                                       show_label = False), label ='Results'),
                            label = 'Experiment', dock = 'tab'),
                      Item('camera', style = 'custom', show_label = False,
                           dock = 'tab'),
                      layout = 'tabbed'))    

    def _start_stop_acquisition_fired(self):
        if self.acquisition_thread and self.acquisition_thread.isAlive():
            self.acquisition_thread.wants_abort = True
        else:
            self.acquisition_thread = AcquisitionThread()
            self.acquisition_thread.display = self.add_line
            self.acquisition_thread.acquire = self.camera.acquire
            self.acquisition_thread.experiment = self.experiment
            self.acquisition_thread.image_show = self.image_show
            self.acquisition_thread.results = self.results
            self.acquisition_thread.start()    

    def add_line(self, string):
        self.results_string = (string + "\n" + self.results_string)

    def image_show(self, image):
        # the set_data command goes here
        self.plotdata.set_data('imagedata', image)
        self.plot.img_plot('imagedata')

class MainWindowHandler(Handler):    

    def close(self, info, is_OK):
        if (info.object.panel.acquisition_thread and \
            info.object.panel.acquisition_thread.isAlive()):
            info.object.panel.acquisition_thread.wants_abort = True
            while info.object.panel.acquisition_thread.isAlive():
                sleep(0.1)
            GUI.process_events()

        return True
    
class MainWindow(HasTraits):
    
    plot = Instance(Plot)
    plotdata = Instance(ArrayPlotData, ())
    panel = Instance(ControlPanel)    

    def _panel_default(self):
        return ControlPanel(plot = self.plot, plotdata = self.plotdata)    

    def _plot_default(self):
        self.plotdata = ArrayPlotData('imagedata', None)
        plot = Plot(self.plotdata)
        self.plot = plot
        return plot    

    view = View(HSplit(Item('plot', editor = ComponentEditor(), \
                            dock = 'vertical'),
                       Item('panel', style = 'custom'),
                       show_labels = False),
                       resizable = True, handler = MainWindowHandler(),
                       buttons = NoButtons)    

if __name__ == '__main__':
    MainWindow().configure_traits()
