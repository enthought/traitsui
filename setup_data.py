# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies.
APPTOOLS = etsdep('AppTools', '3.4.0')
ENTHOUGHTBASE_UI = etsdep('EnthoughtBase[ui]', '3.0.6')
ETSDEVTOOLS_DEVELOPER = etsdep('ETSDevTools[developer]', '3.1.0')
TRAITS = etsdep('Traits', '3.5.0')
TRAITSGUI_DOCK = etsdep('TraitsGUI[dock]', '3.5.0')

# The following soft dependencies are handled with appropriate try...except
# wrappers in the code:
# AppTools -- used in traits.ui.wx.dnd_editor.py
# ETSDevTools -- used in traits.ui.wx.helper.py and view_application.py


# A dictionary of the setup data information.
INFO = {

    'extras_require' : {

        # Extra denoting that complete drag and drop support for files and
        # named bindings should be installed:
        'dnd': [
            APPTOOLS,
            ],

        # Extra denoting that complete developer debug support for the ETS FBI
        # debugger should be installed:
        'debug': [
            ETSDEVTOOLS_DEVELOPER,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            #'wx',  # fixme: not available as an egg on all platforms.
            ],
        },
    'install_requires' : [
        ENTHOUGHTBASE_UI,
        TRAITSGUI_DOCK,
        TRAITS,
        ],
    'name': 'TraitsBackendWX',
    'version': '3.5.0',
}
