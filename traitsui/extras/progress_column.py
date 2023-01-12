# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A column class for for the TableEditor that displays progress bars. """

from traits.api import Bool, Int, Str

from traitsui.table_column import ObjectColumn


class ProgressColumn(ObjectColumn):
    """A column which displays trait values as a progress bar

    Progress values must be an integer value between the maximum and minimum
    values.  By default it is assumed to be a percentage.
    """

    #: Format string to apply to column values.
    format = Str("%s%%")

    #: The minimum value for a progress bar.
    minimum = Int(0)

    #: The maximum value for a progress bar.
    maximum = Int(100)

    #: Whether or not to display the text with the progress bar.
    #: This may not display with some progress bar styles, eg. on OS X.
    text_visible = Bool(True)

    def __init__(self, **traits):
        super().__init__(**traits)

        from traitsui.toolkit import toolkit_object

        ProgressRenderer = toolkit_object(
            'extra.progress_renderer:ProgressRenderer'
        )

        self.renderer = ProgressRenderer()

    def is_editable(self, object):
        """Returns whether the column is editable for a specified object."""
        # Progress columns are always read-only
        return False

    def get_minimum(self, object):
        return self.minimum

    def get_maximum(self, object):
        return self.maximum

    def get_text_visible(self):
        """Whether or not to display text in column.

        Note, may not render on some platforms (eg. OS X) due to
        the rendering style.
        """
        return self.text_visible
