
from contextlib import contextmanager

from pyface.gui import GUI

from traitsui.testing.simulation import (
    get_editor_value, set_editor_value, REGISTRY
)
from traitsui.tests._tools import store_exceptions_on_all_threads


class UITester:

    def __init__(self, registry=REGISTRY):
        self.gui = None
        self.registry = registry

    def start(self):
        if self.gui is None:
            self.gui = GUI()

    def stop(self):
        if self.gui is not None:
            with store_exceptions_on_all_threads():
                self.gui.process_events()
        self.gui = None

    @contextmanager
    def create_ui(self, object, ui_kwargs=None):
        self._ensure_started()
        if ui_kwargs is None:
            ui_kwargs = {}
        ui = object.edit_traits(**ui_kwargs)
        try:
            yield ui
        finally:
            ui.dispose()

    def _set_editor_value(self, ui, name, setter):
        self._ensure_started()
        with store_exceptions_on_all_threads():
            set_editor_value(ui, name, setter, registry=self.registry)
            self.gui.process_events()

    def _get_editor_value(self, ui, name, getter):
        self._ensure_started()
        with store_exceptions_on_all_threads():
            self.gui.process_events()
            return get_editor_value(ui, name, getter, registry=self.registry)

    def get_text(self, ui, name):
        return self._get_editor_value(
            ui=ui, name=name, getter=lambda s: s.get_text()
        )

    def set_text(self, ui, name, text, confirmed=True):
        self._set_editor_value(
            ui=ui,
            name=name,
            setter=lambda s: s.set_text(text, confirmed=confirmed)
        )

    def get_date(self, ui, name):
        return self._get_editor_value(
            ui=ui, name=name, getter=lambda s: s.get_date()
        )

    def set_date(self, ui, name, date):
        self._set_editor_value(
            ui=ui, name=name, setter=lambda s: s.set_date(date)
        )

    def click_date(self, ui, name, date):
        self._set_editor_value(
            ui=ui, name=name, setter=lambda s: s.click_date(date)
        )

    def click(self, ui, name):
        self._set_editor_value(
            ui=ui, name=name, setter=lambda s: s.click()
        )

    def click_index(self, ui, name, index):
        self._set_editor_value(
            ui=ui, name=name, setter=lambda s: s.click_index(index)
        )

    def _ensure_started(self):
        if self.gui is None:
            raise ValueError(
                "'start' has not been called on {!r}.".format(self))

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()
