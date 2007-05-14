from setuptools import setup, find_packages

setup(
    name = 'enthought.traits.ui.wx',
    version = '2.1.0',
    description  = 'WxPython backend for enthought.traits',
    author       = 'David C. Morrill',
    author_email = 'dmorrill@enthought.com',
    url          = 'http://code.enthought.com/traits',
    license      = 'BSD',
    zip_safe     = False,
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        #'wx',  # fixme: not available as an egg on all platforms.
        "enthought.model",
        "enthought.traits",
    ],
    namespace_packages = [
        "enthought",
        "enthought.traits",
        "enthought.traits.ui",
    ],
)
