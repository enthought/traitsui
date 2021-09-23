# echo_box.py

from traits.api import HasTraits, Str


class EchoBox(HasTraits):
    input = Str()
    output = Str()

    def _input_changed(self):
        self.output = self.input


EchoBox().configure_traits()
