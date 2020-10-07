#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
"""
Core API for traitsui.testing

Functionalities exposed via this package are intended to be used by external
projects and stability is maintained as much as possible. Imports from other
packages and subpackages do NOT receive the same stability guarantee.

Tester
------

- :class:`~.UITester`

Interactions (for changing GUI states)
--------------------------------------

- :class:`~.KeyClick`
- :class:`~.KeySequence`
- :class:`~.MouseClick`

Interactions (for getting GUI states)
-------------------------------------

- :class:`~.DisplayedText`
- :class:`~.IsChecked`
- :class:`~.SelectedText`

Locations (for locating GUI elements)
-------------------------------------

- :class:`~.Index`
- :class:`~.Slider`
- :class:`~.TargetById`
- :class:`~.TargetByName`
- :class:`~.Textbox`

Advanced usage
--------------

- :class:`~.TargetRegistry`

Exceptions
----------

- :class:`~.Disabled`
- :class:`~.InteractionNotSupported`
- :class:`~.LocationNotSupported`
- :class:`~.TesterError`
"""

from .tester.command import (
    MouseClick,
    KeyClick,
    KeySequence
)

from .tester.exceptions import (
    Disabled,
    InteractionNotSupported,
    LocationNotSupported,
    TesterError
)

from .tester.locator import (
    Index,
    TargetById,
    TargetByName,
    Textbox,
    Slider
)

from .tester.registry import TargetRegistry

from .tester.query import (
    DisplayedText,
    IsChecked,
    IsEnabled,
    SelectedText
)

from .tester.ui_tester import UITester
