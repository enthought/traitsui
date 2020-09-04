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

from traitsui.testing.tester import locator

class _IndexedEditor:
    """ Wrapper for Editor and index """

    source_class = None
    locator_class = None
    handlers = []
    solvers = []

    def __init__(self, source, location):
        self.source = source
        self.location = location

    @classmethod
    def source_to_locator_solver(cls, wrapper, location):
        if cls.locator_class == locator.Index:
            return cls(source=wrapper.target, location=location.index)

    @classmethod
    def register(cls, registry):
        registry.register_solver(
            target_class=cls.source_class,
            locator_class=cls.locator_class,
            solver=lambda wrapper, location: 
                cls.source_to_locator_solver(wrapper, location),
        )
        for interaction_class, handler in cls.handlers:
            registry.register_handler(
                target_class=cls,
                interaction_class=interaction_class,
                handler=handler
            )
        for location_class, solver in cls.solvers:
            registry.register_solver(
                target_class=cls,
                locator_class=location_class,
                solver=solver,
            )
