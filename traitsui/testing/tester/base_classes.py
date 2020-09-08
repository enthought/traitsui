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


class _BaseSourceWithLocation:
    """ Wrapper base class to hold locator information together with a source
    (typically an editor).  This is useful for cases in which the location
    information is still necessary when performing actions such as a mouse
    click or key click.

    For example, an Enum editor and an index.
    This class is meant to be subclassed for specific usecases, and the
    class level attributes overridden.
    """

    # the source class we want to interact with, typically an Editor
    source_class = None
    # The locator_class that contains the relevant location information
    # (e.g. locator.Index)
    locator_class = None
    # the handlers we want to register for the given source_class
    # must be given as a list of tuples where the first element is the
    # interaction class (e.g. command.MouseClick) and the second is the
    # actual handler function.
    handlers = []

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
            solver=lambda wrapper, location: cls(wrapper.target, location),
        )
        for interaction_class, handler in cls.handlers:
            registry.register_handler(
                target_class=cls,
                interaction_class=interaction_class,
                handler=handler
            )
