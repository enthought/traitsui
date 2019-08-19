#  Copyright (c) 2019, Enthought, Inc.
#  License: BSD Style.

"""
This demo illustrates use of the LEDEditor for displaying numeric values
using a simulated LED display control.
"""

from threading import Thread
from time import sleep

from traits.api \
    import HasTraits, Instance, Int, Bool, Float

from traitsui.api \
    import View, Item, Handler, UIInfo

from traitsui.qt4.extra.led_editor \
    import LEDEditor

# Handler class for the LEDDemo class view:

class LEDDemoHandler(Handler):

    # The UIInfo object associated with the UI:
    info = Instance(UIInfo)

    # Is the demo currently running:
    running = Bool(True)

    # Is the thread still alive?
    alive = Bool(True)

    def init(self, info):
        self.info = info
        Thread(target=self._update_counter).start()

    def closed(self, info, is_ok):
        self.running = False
        while self.alive:
            sleep(.05)

    def _update_counter(self):
        while self.running:
            self.info.object.counter1 += 1
            self.info.object.counter2 += .001
            sleep(.05)
        self.alive = False

# The main demo class:

class LEDDemo(HasTraits):

    # A counter to display:
    counter1 = Int

    # A floating point value to display:
    counter2 = Float

    # The traits view:
    view = View(
        Item('counter1',
             editor=LEDEditor()
             ),
        Item('counter2',
             editor=LEDEditor()
             ),
        title='LED Counter Demo',
        buttons=['OK'],
        handler=LEDDemoHandler
    )


# Create the demo:
demo = LEDDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
