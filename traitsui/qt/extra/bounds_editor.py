# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from pyface.qt import QtGui, QtCore

from traits.api import Float, Any, Str, Union

from traitsui.editors.api import RangeEditor
from traitsui.qt.editor import Editor
from traitsui.qt.extra.range_slider import RangeSlider


class _BoundsEditor(Editor):

    evaluate = Any()

    min = Any()
    max = Any()
    low = Any()
    high = Any()
    format = Str()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.max = factory.max
        self.min = factory.min

        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, "evaluate", "from")

        self.sync_value(factory.low_name, "low", "both")
        self.sync_value(factory.high_name, "high", "both")

        self.control = QtGui.QWidget()
        panel = QtGui.QHBoxLayout(self.control)
        panel.setContentsMargins(0, 0, 0, 0)

        self._label_lo = QtGui.QLineEdit(self.format_str % self.low)
        self._label_lo.editingFinished.connect(self.update_low_on_enter)
        panel.addWidget(self._label_lo)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = self._label_lo.sizeHint()
        sh.setWidth(sh.width() // 2)
        self._label_lo.setMaximumSize(sh)

        self.control.slider = slider = RangeSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setTracking(factory.auto_set)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setPageStep(1000)
        slider.setSingleStep(100)
        slider.setLow(self._convert_to_slider(self.low))
        slider.setHigh(self._convert_to_slider(self.high))

        slider.sliderMoved.connect(self.update_object_on_scroll)
        panel.addWidget(slider)

        self._label_hi = QtGui.QLineEdit(self.format_str % self.high)
        self._label_hi.editingFinished.connect(self.update_high_on_enter)
        panel.addWidget(self._label_hi)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = self._label_hi.sizeHint()
        sh.setWidth(sh.width() // 2)
        self._label_hi.setMaximumSize(sh)

        self.set_tooltip(slider)
        self.set_tooltip(self._label_lo)
        self.set_tooltip(self._label_hi)

    def update_low_on_enter(self):
        try:
            try:
                low = eval(str(self._label_lo.text()).strip())
                if self.evaluate is not None:
                    low = self.evaluate(low)
            except Exception as ex:
                low = self.low
                self._label_lo.setText(self.format_str % self.low)

            if not self.factory.is_float:
                low = int(low)

            if low > self.high:
                low = self.high - self._step_size()
                self._label_lo.setText(self.format_str % low)

            self.control.slider.setLow(self._convert_to_slider(low))
            self.low = low
        except:
            pass

    def update_high_on_enter(self):
        try:
            try:
                high = eval(str(self._label_hi.text()).strip())
                if self.evaluate is not None:
                    high = self.evaluate(high)
            except:
                high = self.high
                self._label_hi.setText(self.format_str % self.high)

            if not self.factory.is_float:
                high = int(high)

            if high < self.low:
                high = self.low + self._step_size()
                self._label_hi.setText(self.format_str % high)

            self.control.slider.setHigh(self._convert_to_slider(high))
            self.high = high
        except:
            pass

    def update_object_on_scroll(self, pos):
        low = self._convert_from_slider(self.control.slider.low())
        high = self._convert_from_slider(self.control.slider.high())

        if self.factory.is_float:
            self.low = low
            self.high = high
        else:
            self.low = int(low)
            self.high = int(high)

            # update the sliders to the int values or the sliders
            # will jiggle
            self.control.slider.setLow(self._convert_to_slider(low))
            self.control.slider.setHigh(self._convert_to_slider(high))

    def update_editor(self):
        return

    def _check_max_and_min(self):
        # check if max & min have been defined:
        if self.max is None:
            self.max = self.high
        if self.min is None:
            self.min = self.low

    def _step_size(self):
        slider_delta = (
            self.control.slider.maximum() - self.control.slider.minimum()
        )
        range_delta = self.max - self.min

        return float(range_delta) / slider_delta

    def _convert_from_slider(self, slider_val):
        self._check_max_and_min()
        return self.min + slider_val * self._step_size()

    def _convert_to_slider(self, value):
        self._check_max_and_min()
        return (
            self.control.slider.minimum()
            + (value - self.min) / self._step_size()
        )

    def _low_changed(self, low):
        if self.control is None:
            return
        if self._label_lo is not None:
            self._label_lo.setText(self.format_str % low)

        self.control.slider.setLow(self._convert_to_slider(low))

    def _high_changed(self, high):
        if self.control is None:
            return
        if self._label_hi is not None:
            self._label_hi.setText(self.format_str % high)

        self.control.slider.setHigh(self._convert_to_slider(self.high))


class BoundsEditor(RangeEditor):

    min = Union(None, Float)
    max = Union(None, Float)

    def _get_simple_editor_class(self):
        return _BoundsEditor

    def _get_custom_editor_class(self):
        return _BoundsEditor
