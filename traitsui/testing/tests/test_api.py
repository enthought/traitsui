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

""" Test the api module. """

import unittest

class TestApi(unittest.TestCase):

    def test_tester_import(self):
        from traitsui.testing.api import UITester
    
    def test_commands_imports(self):
        from traitsui.testing.api import (
            MouseClick,
            KeyClick,
            KeySequence,
        )

    def test_query_imports(self):
        from traitsui.testing.api import (
            DisplayedText,
            IsChecked,
            IsEnabled,
            SelectedText,
        )

    def test_locator_imports(self):
        from traitsui.testing.api import (
            Index,
            TargetById,
            TargetByName,
            Textbox,
            Slider,
        )

    def test_advanced_usage_imports(self):
        #from traitsui.testing.api import TargetRegistry
        pass

    def test_exceptions_imports(self):
        from traitsui.testing.api import (
            Disabled,
            InteractionNotSupported,
            LocationNotSupported,
            TesterError,
        )
