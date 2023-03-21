# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
This package contains library code for testing TraitsUI applications via
``UITester`` (in ``ui_tester`` module).

Other public modules are also part of the public API.

``_ui_tester_registry`` contains internal implementations to support testing
TraitsUI UI and editors.

The only modules/packages that are specific about TraitsUI UI and editors are
``ui_tester`` and ``_ui_tester_registry``. The other modules are generic enough
to be used with GUI components external to TraitsUI. This allows extensions
beyond the scope of TraitsUI.
"""
