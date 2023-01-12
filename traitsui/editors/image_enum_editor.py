# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the image enumeration editor factory for all traits user interface
toolkits.
"""

from os import getcwd
from os.path import join, dirname, exists
import sys

from traits.api import Module, Type, Str, observe

from traitsui.editors.enum_editor import EnumEditor


class ImageEnumEditor(EnumEditor):
    """Editor factory for image enumeration editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------
    #: Prefix to add to values to form image names:
    prefix = Str()

    #: Suffix to add to values to form image names:
    suffix = Str()

    #: Path to use to locate image files:
    path = Str()

    #: Class used to derive the path to the image files:
    klass = Type()

    #: Module used to derive the path to the image files:
    module = Module

    def init(self):
        """Performs any initialization needed after all constructor traits
        have been set.
        """
        super().init()
        self._update_path()

    @observe("path, klass, module")
    def _update_path(self, event=None):
        """Handles one of the items defining the path being updated."""
        if self.path != "":
            self._image_path = self.path
        elif self.klass is not None:
            module = self.klass.__module__
            if module == "___main___":
                module = "__main__"
            try:
                self._image_path = join(
                    dirname(sys.modules[module].__file__), "images"
                )
            except:
                self._image_path = self.path
                dirs = [
                    join(dirname(sys.argv[0]), "images"),
                    join(getcwd(), "images"),
                ]
                for d in dirs:
                    if exists(d):
                        self._image_path = d
                        break
        elif self.module is not None:
            self._image_path = join(dirname(self.module.__file__), "images")


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = ImageEnumEditor
