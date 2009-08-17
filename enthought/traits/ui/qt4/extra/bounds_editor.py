from PyQt4 import QtGui, QtCore

from enthought.traits.ui.editors.api import RangeEditor
from enthought.traits.ui.qt4.range_editor import SimpleSliderEditor
from enthought.traits.ui.qt4.extra.range_slider import RangeSlider

class _BoundsEditor(SimpleSliderEditor):

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.format = factory.format

        self.evaluate = factory.evaluate
        self.sync_value( factory.evaluate_name, 'evaluate', 'from' )

        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )

        self.control = QtGui.QWidget()
        panel = QtGui.QHBoxLayout(self.control)
        panel.setMargin(0)

        self._label_lo = QtGui.QLineEdit(self.format % self.low)
        QtCore.QObject.connect(self._label_lo, QtCore.SIGNAL('editingFinished()'),
                self.update_object_on_enter)
        panel.addWidget(self._label_lo)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = self._label_lo.sizeHint()
        sh.setWidth(sh.width() / 2)
        self._label_lo.setMaximumSize(sh)

        self.control.slider = slider = RangeSlider(QtCore.Qt.Horizontal)
        slider.setTracking(factory.auto_set)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setPageStep(1000)
        slider.setSingleStep(100)
        slider.setLow(0)
        slider.setHigh(10000)

        QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved(int)'),
                self.update_object_on_scroll)
        panel.addWidget(slider)

        self._label_hi = QtGui.QLineEdit(self.format % self.high)
        QtCore.QObject.connect(self._label_hi, QtCore.SIGNAL('editingFinished()'),
                self.update_object_on_enter)
        panel.addWidget(self._label_hi)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = self._label_hi.sizeHint()
        sh.setWidth(sh.width() / 2)
        self._label_hi.setMaximumSize(sh)

        self.set_tooltip(slider)
        self.set_tooltip(self._label_lo)
        self.set_tooltip(self._label_hi)

    def update_object_on_enter(self):
        try:
            try:
                low = eval(unicode(self._label_lo.text()).strip())
            except Exception, ex:
                low = self.low
                self._label_lo.setText(self.low)

            try:
                high = eval(unicode(self._label_hi.text()).strip())
            except:
                high = self.high
                self._label_hi.setText(self.high)

            if not self.factory.is_float:
                low = int(low)
                high = int(high)

            self.control.slider.setLow(self._convert_to_slider(low))
            self.control.slider.setHigh(self._convert_to_slider(high))
        except:
            pass

    def update_object_on_scroll(self, pos):
        print "update on scroll"
        self.low = self._convert_from_slider(self.control.slider.low())
        self.high = self._convert_from_slider(self.control.slider.high())

    def update_editor(self):
        blocked = self.control.slider.blockSignals(True)
        self.control.slider.setLow(self._convert_to_slider(self.low))
        self.control.slider.setHigh(self._convert_to_slider(self.high))
        self.control.slider.blockSignals(blocked)

    def _low_changed(self, low):
        if self.control is None:
            return
        self.control.slider.setLow(low)
        if self._label_lo is not None:
            self._label_lo.SetText(self.format % low)
            self.update_editor()

    def _high_changed(self, high):
        if self.control is None:
            return
        self.control.slider.setHigh(high)
        if self._label_hi is not None:
            self._label_hi.SetText(self.format % hi)
            self.update_editor()

class BoundsEditor(RangeEditor):
    def _get_simple_editor_class(self):
        return _BoundsEditor
    def _get_custom_editor_class(self):
        return _BoundsEditor

