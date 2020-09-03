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

    target_class = None
    handlers = []
    solvers = []

    def __init__(self, target, index):
        self.target = target
        self.index = index

    @classmethod
    def register(cls, registry):
        registry.register_solver(
            target_class=cls.target_class,
            locator_class=locator.Index,
            solver=lambda wrapper, location: 
                cls(target=wrapper.target, index=location.index),
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
                interaction_class=location_class,
                solver=solver,
            )