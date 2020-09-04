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

class _SourceWithLocation:
    """ Wrapper base class to hold locator information together with a source
    (typically an editor).  This is useful for cases in which the location
    information is still necessary when performing actions such as a mouse
    click or key click.
    
    For example, an Enum editor and an index.
    This class is meant to be subclassed for specific usecases, and the
    class level attributes overridden.
    """

    source_class = None
    locator_class = None
    handlers = []
    solvers = []

    def __init__(self, source, location):
        """
        Parameters
        ----------
        source : subclass of type
            The source object. Typically this is an editor. 
        location : Any
            The location information of interest
        """
        self.source = source
        self.location = location

    @classmethod
    def source_to_locator_solver(cls, wrapper, location):
        """ Solver to resolve from the class of the Wrapper's target to a
        location. The location will have to vary based on the class'
        locator_class atrribute.

        Parameters
        ----------
        wrapper : UIWrapper
            the UIWrapper whose target is of type source_class
        location : cls.locator_class
            The locator object carrying the important location information
        """
        if cls.locator_class == locator.Index:
            return cls(source=wrapper.target, location=location.index)
        raise NotImplementedError(
            "Currently, the only supported locator_class is locator.Index"
        )

    @classmethod
    def register(cls, registry):
        """ Class method to register interactions on a
        _SourceWithLocation for the given registry. It is expected that this
        class method will be called by subclasses, and thus interactions would
        be registered to subclasses rather than the base class.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
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
