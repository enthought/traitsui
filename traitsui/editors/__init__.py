# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


def __getattr__(name):
    # For backwards compatibility, continue to make the editors available for
    # import here, but warn it is deprecated.
    import traitsui.editors.api
    if name in traitsui.editors.api.__dict__:
        obj = getattr(traitsui.editors.api, name)
        import warnings
        warnings.warn(
            "Using or importing Editor factories from 'traitsui.editors' "
            "instead of from 'traitsui.editors.api' is deprecated and will "
            "stop working in TraitsUI 9.0",
            DeprecationWarning, stacklevel=2,
        )
        globals()[name] = obj
        return obj

    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
