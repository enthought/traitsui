from PyQt4 import QtGui, QtCore

class RangeSlider(QtGui.QSlider):
    """ A slider for ranges.
    
        This class provides a dual-slider for ranges, where there is a defined
        maximum and minimum, as is a normal slider, but instead of having a
        single slider value, there are 2 slider values.
        
        This class emits the same signals as the QSlider base class
    """
    def __init__(self, min, max, low, high):
        super(RangeSlider, self).__init__()
        self.setMinimum(min)
        self.setMaximum(max)
        
        self.low = low
        self.high = high
        
        self.pressed_control = QtGui.QStyle.SC_None
        self.hover_control = QtGui.QStyle.SC_None
        self.click_offset = 0
        
        # 0 for the low, 1 for the high
        self.active_slider = 0
        
        
    def paintEvent(self, event):
        # based on http://qt.gitorious.org/qt/qt/blobs/master/src/gui/widgets/qslider.cpp

        painter = QtGui.QPainter()
        painter.begin(self)

        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)

        opt.subControls = QtGui.QStyle.SC_SliderGroove | QtGui.QStyle.SC_SliderHandle
        if self.tickPosition() != self.NoTicks:
            opt.subControls |= QtGui.QStyle.SC_SliderTickmarks

        if self.pressed_control:
            opt.activeSubControls = self.pressed_control
            opt.state |= QtGui.QStyle.State_Sunken
        else:
            opt.activeSubControls = self.hover_control

        style = QtGui.QApplication.style() 
        
        for value in [self.low, self.high]:
            painter.save()
            opt.sliderPosition = value                                  
            style.drawComplexControl(QtGui.QStyle.CC_Slider, opt, painter, self)
            painter.restore()
            
        painter.end()
        
    def mousePressEvent(self, event):
        event.accept()
        
        style = QtGui.QApplication.style()
        button = event.button()
        
        # In a normal slider control, when the user clicks on a point in the 
        # slider's total range, but not on the slider part of the control the
        # control would jump the slider value to where the user clicked. Since 
        # we have 2 sliders, we can't know which the user means, so we don't 
        # support it
                
        if button:
            opt = QtGui.QStyleOptionSlider()
            self.initStyleOption(opt)
            
            for i, value in enumerate([self.low, self.high]):
                opt.sliderPosition = value                
                hit = style.hitTestComplexControl(style.CC_Slider, opt, event.pos(), self)
                if hit == style.SC_SliderHandle:
                    self.active_slider = i
                    self.pressed_control = hit
                    
                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
        else:
            event.ignore()
                                
    def mouseMoveEvent(self, event):
        if self.pressed_control != QtGui.QStyle.SC_SliderHandle:
            event.ignore()
            return
        
        event.accept()
        new_pos = self.__pixelPosToRangeValue(self.__pick(event.pos()) - self.click_offset)
        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)
        
        if self.active_slider == 0:
            if new_pos >= self.high:
                new_pos = self.high - 1
            self.low = new_pos
        else:
            if new_pos <= self.low:
                new_pos = self.low + 1
            self.high = new_pos
                        
        self.update()
        
            
            
            
    def __pick(self, pt):
        if self.orientation() == QtCore.Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()
           
           
    def __pixelPosToRangeValue(self, pos):
        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)
        style = QtGui.QApplication.style()
        
        gr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderGroove, self)
        sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)
        
        if self.orientation() == QtCore.Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1
            
        return style.sliderValueFromPosition(self.minimum(), self.maximum(),
                                             pos-slider_min, slider_max-slider_min,
                                             opt.upsideDown)
            
            
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    slider = RangeSlider(1, 100, 30, 70)
    slider.show()
    app.exec_()