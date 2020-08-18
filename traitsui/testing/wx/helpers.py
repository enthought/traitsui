import wx


def key_press_slider(slider, key, delay):
    if key not in {"Up", "Down", "Right", "Left"}:
        raise ValueError("Unexpected key.")
    if not slider.HasFocus():
        slider.SetFocus()
    value = slider.GetValue()
    range_ = slider.GetMax() - slider.GetMin()
    step = int(range_ / slider.GetLineSize())
    wx.MilliSleep(delay)

    if key in {"Up", "Right"}:
        position = min(slider.GetMax(), value + step)
    else:
        position = max(0, value - step)
    slider.SetValue(position)
    event = wx.ScrollEvent(
        wx.wxEVT_SCROLL_CHANGED, slider.GetId(), position
    )
    wx.PostEvent(slider, event)


def key_press_text_ctrl(control, key, delay):
    if key == "Enter":
        if not control.HasFocus():
            control.SetFocus()
        wx.MilliSleep(delay)
        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, control.GetId())
        control.ProcessEvent(event)
    else:
        raise ValueError("Only supported Enter key.")


def key_sequence_text_ctrl(control, sequence, delay):
    if not control.HasFocus():
        control.SetFocus()
    for char in sequence:
        wx.MilliSleep(delay)
        if char == "\b":
            pos = control.GetInsertionPoint()
            control.Remove(max(0, pos - 1), pos)
        else:
            control.AppendText(char)


def mouse_click_button(control, delay):
    if not control.IsEnabled():
        return
    wx.MilliSleep(delay)
    click_event = wx.CommandEvent(
        wx.wxEVT_COMMAND_BUTTON_CLICKED, control.GetId()
    )
    control.ProcessEvent(click_event)
