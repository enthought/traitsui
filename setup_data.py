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


# Declare our ETS project dependencies:
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.5')
ETSDEVTOOLS_DEVELOPER = etsdep('ETSDevTools[developer]', '3.0.5')
TRAITS = etsdep('Traits', '3.3.1')
TRAITSGUI = etsdep('TraitsGUI', '3.3.1')


INFO = {

    'extras_require' : {

        # Extra denoting that complete developer debug support for the ETS FBI
        # debugger should be installed:
        'debug': [
            ETSDEVTOOLS_DEVELOPER,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            ],
        },
    'install_requires' : [
        ENTHOUGHTBASE,
        TRAITS,
        TRAITSGUI,
        ],
    'name' : 'TraitsBackendQt',
    'version' : '3.3.1',
    }
