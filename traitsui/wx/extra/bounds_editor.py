from __future__ import absolute_import
import wx

from traits.api import Float, Any, Str, Trait
from traitsui.editors.api import RangeEditor
from traitsui.wx.editor import Editor
from traitsui.wx.helper import TraitsUIPanel, Slider
import six


class _BoundsEditor(Editor):

    evaluate = Any

    min = Any
    max = Any
    low = Any
    high = Any
    format = Str

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low
            self.min = self.low

        if not factory.high_name:
            self.high = factory.high
            self.max = self.high

        self.max = factory.max
        self.min = factory.min

        self.format = factory.format

        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, 'evaluate', 'from')

        self.sync_value(factory.low_name, 'low', 'both')
        self.sync_value(factory.high_name, 'high', 'both')

        self.control = panel = TraitsUIPanel(parent, -1)
        sizer = wx.FlexGridSizer(2, 3, 0, 0)

        # low text box
        self._label_lo = wx.TextCtrl(panel, -1, self.format % self.low,
                                     size=wx.Size(56, 20),
                                     style=wx.TE_PROCESS_ENTER)
        sizer.Add(self._label_lo, 0, wx.ALIGN_CENTER)
        wx.EVT_TEXT_ENTER(
            panel,
            self._label_lo.GetId(),
            self.update_low_on_enter)
        wx.EVT_KILL_FOCUS(self._label_lo, self.update_low_on_enter)

        # low slider
        self.control.lslider = Slider(panel, -1, 0, 0, 10000,
                                      size=wx.Size(100, 20),
                                      style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.control.lslider.SetValue(self._convert_to_slider(self.low))
        self.control.lslider.SetTickFreq(1000, 1)
        self.control.lslider.SetPageSize(1000)
        self.control.lslider.SetLineSize(100)
        wx.EVT_SCROLL(self.control.lslider, self.update_object_on_scroll)
        sizer.Add(self.control.lslider, 1, wx.EXPAND)
        sizer.AddStretchSpacer(0)

        # high slider
        sizer.AddStretchSpacer(0)
        self.control.rslider = Slider(
            panel, -1, self._convert_to_slider(
                self.high), 0, 10000, size=wx.Size(
                100, 20), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.control.rslider.SetTickFreq(1000, 1)
        self.control.rslider.SetPageSize(1000)
        self.control.rslider.SetLineSize(100)
        wx.EVT_SCROLL(self.control.rslider, self.update_object_on_scroll)
        sizer.Add(self.control.rslider, 1, wx.EXPAND)

        # high text box
        self._label_hi = wx.TextCtrl(panel, -1, self.format % self.high,
                                     size=wx.Size(56, 20),
                                     style=wx.TE_PROCESS_ENTER)
        sizer.Add(self._label_hi, 0, wx.ALIGN_CENTER)
        wx.EVT_TEXT_ENTER(
            panel,
            self._label_hi.GetId(),
            self.update_high_on_enter)
        wx.EVT_KILL_FOCUS(self._label_hi, self.update_high_on_enter)

        self.set_tooltip(self.control.lslider)
        self.set_tooltip(self.control.rslider)
        self.set_tooltip(self._label_lo)
        self.set_tooltip(self._label_hi)

        # Set-up the layout:
        panel.SetSizerAndFit(sizer)

    def update_low_on_enter(self, event):
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        try:
            try:
                low = eval(six.text_type(self._label_lo.GetValue()).strip())
                if self.evaluate is not None:
                    low = self.evaluate(low)
            except Exception as ex:
                low = self.low
                self._label_lo.SetValue(self.format % self.low)

            if not self.factory.is_float:
                low = int(low)

            if low > self.high:
                low = self.high - self._step_size()
                self._label_lo.SetValue(self.format % low)

            self.control.lslider.SetValue(self._convert_to_slider(low))
            self.low = low
        except:
            pass

    def update_high_on_enter(self, event):
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        try:
            try:
                high = eval(six.text_type(self._label_hi.GetValue()).strip())
                if self.evaluate is not None:
                    high = self.evaluate(high)
            except:
                high = self.high
                self._label_hi.SetValue(self.format % self.high)

            if not self.factory.is_float:
                high = int(high)

            if high < self.low:
                high = self.low + self._step_size()
                self._label_hi.SetValue(self.format % high)

            self.control.rslider.SetValue(self._convert_to_slider(high))
            self.high = high
        except:
            pass

    def update_object_on_scroll(self, evt):
        low = self._convert_from_slider(self.control.lslider.GetValue())
        high = self._convert_from_slider(self.control.rslider.GetValue())

        if low >= high:
            if evt.Position == self.control.lslider.GetValue():
                low = self.high - self._step_size()
            else:
                high = self.low + self._step_size()

        if self.factory.is_float:
            self.low = low
            self.high = high
        else:
            self.low = int(low)
            self.high = int(high)

            # update the sliders to the int values or the sliders
            # will jiggle
            self.control.lslider.SetValue(self._convert_to_slider(low))
            self.control.rslider.SetValue(self._convert_to_slider(high))

    def update_editor(self):
        return

    def _check_max_and_min(self):
        # check if max & min have been defined:
        if self.max is None:
            self.max = self.high
        if self.min is None:
            self.min = self.low

    def _step_size(self):
        slider_delta = self.control.lslider.GetMax() - self.control.lslider.GetMin()
        range_delta = self.max - self.min

        return float(range_delta) / slider_delta

    def _convert_from_slider(self, slider_val):
        self._check_max_and_min()
        return self.min + slider_val * self._step_size()

    def _convert_to_slider(self, value):
        self._check_max_and_min()
        return self.control.lslider.GetMin() + (value - self.min) / self._step_size()

    def _low_changed(self, low):
        if self.control is None:
            return
        if self._label_lo is not None:
            self._label_lo.SetValue(self.format % low)

        self.control.lslider.SetValue(self._convert_to_slider(low))

    def _high_changed(self, high):
        if self.control is None:
            return
        if self._label_hi is not None:
            self._label_hi.SetValue(self.format % high)

        self.control.rslider.SetValue(self._convert_to_slider(self.high))


class BoundsEditor(RangeEditor):

    min = Trait(None, Float)
    max = Trait(None, Float)

    def _get_simple_editor_class(self):
        return _BoundsEditor

    def _get_custom_editor_class(self):
        return _BoundsEditor
