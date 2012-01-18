# Run tests using nose:
#   $ nosetests -v
#
# The tests that are not compatible with the selected toolkit will be skipped
# (resulting in 'S' characters in the report). To test different backend,
# you should set the backend using the environment variable ETS_TOOLKIT:
#
#   $ ETS_TOOLKIT='qt4' nosetests -v
#   $ ETS_TOOLKIT='wx' nosetests -v
#   $ ETS_TOOLKIT='null' nosetests -v
