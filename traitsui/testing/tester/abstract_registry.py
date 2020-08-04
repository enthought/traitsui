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

import abc


class AbstractRegistry(abc.ABC):
    """ Abstract base class for all instances of registries used by
    UITester and UserInteractor.
    """

    @abc.abstractmethod
    def get_handler(self, editor_class, action_class):
        """ Return a callable for handling an action for a given editor class.

        Parameters
        ----------
        editor_class : subclass of traitsui.editor.Editor
            A toolkit specific Editor class.
        action_class : subclass of type
            Any class.

        Returns
        -------
        handler : callable(UserInteractor, action) -> any
            The function to handle the particular action on an editor.
            ``action`` should be an instance of ``action_class``.
        """
        raise NotImplementedError()
