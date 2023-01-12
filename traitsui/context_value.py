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
Defines some helper classes and traits used to define 'bindable' editor
values.  These classes and associated traits are designed to simplify
writing editors by allowing the editor factory to specify a context value
instance for attributes and have the value on the editor be synchronized
with the corresponsing value rom the context.

The factory should look something like this::

    class MyEditorFactory(EditorFactory):

        #: The minimum value.
        minimum = CVInt

        #: The suffix for the data.
        suffix = CVType(Str)

The editor class needs to have traits which correspond to the context value
traits, and should be able to react to changes to them::

    class MyEditor(Editor):

        #: The minimum value.
        minimum = Int()

        #: The suffix for the data.
        suffix = Str()

This can then be used in views, with values either as constants or as
instances of :class:`ContextValue` (abbreviated as ``CV``)::

    class MyObject(HasTraits):

        #: An important value.
        my_value = Str()

        #: The minimum value.
        my_minimum = Int(10)

        traits_view = View(
            Item(
                'my_value',
                editor=MyEditorFactory(
                    minimum=CV('my_minimum'),
                    suffix='...',
                ),
            )
        )
"""


from traits.api import HasStrictTraits, Instance, Str, Int, Float, Union


class ContextValue(HasStrictTraits):
    """Defines the name of a context value that can be bound to an editor

    Resolution of the name follows the same rules as for context values in
    Item objects: if there is no dot in it then it is treated as an
    attribute of the 'object' context value, other wise the first part
    specifies the object in the context and the rest are dotted attribute
    look-ups.
    """

    #: The extended trait name of the value that can be bound to the editor
    #: (e.g. 'selection' or 'handler.selection'):
    name = Str()

    # ------------------------------------------------------------------------
    # object Interface
    # ------------------------------------------------------------------------

    def __init__(self, name):
        super().__init__(name=name)


#: Define a shorthand name for a ContextValue:
CV = ContextValue


# Trait definitions useful in defining bindable editor traits ---------------


def CVType(type, **metadata):
    """Factory that creates a union of a trait type and a ContextValue trait.

    This also sets up one-way synchronization to the editor if no
    other synchronization is specified.

    Parameters
    ----------
    type : trait type
        The trait type that is expected for constant values.
    **metadata
        Additional metadata for the trait.

    Returns
    -------
    cv_type_trait : trait
        A trait which can either hold a constant of the specified
        type or an instance of the ContextValue class.
    """
    metadata.setdefault("sync_value", "to")
    return Union(type, InstanceOfContextValue, **metadata)


#: Shorthand for an Instance of ContextValue trait.
InstanceOfContextValue = Instance(ContextValue, allow_none=False)

#: Int or Context value trait
CVInt = CVType(Int)

#: Float or Context value trait
CVFloat = CVType(Float)

#: Str or Context value trait
CVStr = CVType(Str)
