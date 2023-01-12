# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Monitoring threads in the user interface

Shows a simple user interface being updated by multiple threads.

When the *Start Threads* button is pressed, the program starts three independent
threads running. Each thread counts from 0 to 199, updating its own
thread-specific trait, and performs a sleep of a thread-specific duration
between each update.

The *Start Threads* button is disabled while the threads are running, and
becomes active again once all threads have finished running.
"""

from threading import Thread
from time import sleep
from traits.api import HasTraits, Int, Button
from traitsui.api import View, Item, VGroup


class ThreadDemo(HasTraits):

    # The thread specific counters:
    thread_0 = Int()
    thread_1 = Int()
    thread_2 = Int()

    # The button used to start the threads running:
    start = Button('Start Threads')

    # The count of how many threads ae currently running:
    running = Int()

    view = View(
        VGroup(
            Item('thread_0', style='readonly'),
            Item('thread_1', style='readonly'),
            Item('thread_2', style='readonly'),
        ),
        '_',
        Item('start', show_label=False, enabled_when='running == 0'),
        resizable=True,
        width=250,
        title='Monitoring threads',
    )

    def _start_changed(self):
        for i in range(3):
            Thread(
                target=self.counter,
                args=('thread_%d' % i, (i * 10 + 10) / 1000.0),
            ).start()

    def counter(self, name, interval):
        self.running += 1
        count = 0
        for i in range(200):
            setattr(self, name, count)
            count += 1
            sleep(interval)
        self.running -= 1


# Create the demo:
demo = ThreadDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
