# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module contains targets for UIWrapper so that the logic related to
them can be reused.
To use the logic in these objects, if the class in this module is a base class
(indicated by leading _Base) they simply need to subclass this class, override
any necessary traits, and then call the register method.
"""


class BaseSourceWithLocation:
    """Wrapper base class to hold locator information together with a source
    (typically an editor).  This is useful for cases in which the location
    information is still necessary when performing actions such as a mouse
    click or key click.

    For example, an Enum editor and an index.
    This class is meant to be subclassed for specific usecases, and the
    class level attributes overridden.
    """

    # The type of the source object on which the location information will be
    # evaluated on
    source_class = None
    # The type of the locator object that provides location information.
    # (e.g. locator.Index)
    locator_class = None
    # the handlers we want to register for the given source_class
    # must be given as a list of tuples where the first element is the
    # interaction class (e.g. command.MouseClick) and the second is the
    # actual handler function.
    # See TargetRegistry.register_interaction
    # for the signature of the callable.
    handlers = []

    def __init__(self, source, location):
        """
        Parameters
        ----------
        source : instance of source_class
            The source object. Typically this is an editor.
        location : instance of locator_class
            The location information of interest
        """
        self.source = source
        self.location = location

    @classmethod
    def register(cls, registry):
        """Class method to register interactions on a
        _SourceWithLocation for the given registry. It is expected that this
        class method will be called by subclasses, and thus interactions would
        be registered to subclasses rather than the base class.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        registry.register_location(
            target_class=cls.source_class,
            locator_class=cls.locator_class,
            solver=lambda wrapper, location: cls(wrapper._target, location),
        )
        for interaction_class, handler in cls.handlers:
            registry.register_interaction(
                target_class=cls,
                interaction_class=interaction_class,
                handler=handler,
            )
