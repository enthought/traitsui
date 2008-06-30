from setuptools import setup, find_packages


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
APPTOOLS           = etsdep( 'AppTools',            '3.0.0b1' )  
DEVTOOLS_DEVELOPER = etsdep( 'DevTools[developer]', '3.0.0b1' )  
ENTHOUGHTBASE_UI   = etsdep( 'EnthoughtBase[ui]',   '3.0.0b1' )
TRAITS             = etsdep( 'Traits',              '3.0.0b1' )
TRAITSGUI_DOCK     = etsdep( 'TraitsGUI[dock]',     '3.0.0b1' )

# The following soft dependencies are handled with appropriate try...except
# wrappers.
# AppTools -- used in traits.ui.wx.dnd_editor.py
# DevTools -- used in traits.ui.wx.helper.py and view_application.py


setup(
    author           = 'Enthought, Inc',
    author_email     = 'info@enthought.com',
    dependency_links = [ 'http://code.enthought.com/enstaller/eggs/source', ],
    description      = 'WxPython backend for Traits and Pyface.',
    
    extras_require = {
    
        # Extra denoting that complete drag and drop support for files and
        # named bindings should be installed:
        'dnd': [
            APPTOOLS,
        ],
        
        # Extra denoting that complete developer debug support for the ETS FBI
        # debugger should be installed:
        'debug': [
            DEVTOOLS_DEVELOPER,
        ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            #'wx',  # fixme: not available as an egg on all platforms.
        ],
    },
        
    install_requires = [
        ENTHOUGHTBASE_UI,
        TRAITSGUI_DOCK,
        TRAITS,
    ],
        
    include_package_data = True,
    license              = 'BSD',
    name                 = 'TraitsBackendWX',
    namespace_packages   = [
        'enthought',
        'enthought.pyface',
        'enthought.pyface.ui',
        'enthought.traits',
        'enthought.traits.ui',
    ],
    packages      = find_packages(),
    tests_require = [
        'nose >= 0.9',
    ],
    test_suite = 'nose.collector',
    url        = 'http://code.enthought.com/ets',
    version    = '3.0.0b1',
    zip_safe   = False,
)
