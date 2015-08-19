"%sdkverpath%" -q -version:"%sdkver%"
call setenv /x64

rem install python packages
pip install --cache-dir c:/temp nose
pip install --cache-dir c:/temp coverage
pip install --cache-dir c:/temp pygments
pip install --cache-dir c:/temp numpy
pip install --cache-dir c:/temp pandas
pip install --cache-dir c:/temp pyside
pip install --cache-dir c:/temp git+http://github.com/enthought/traits.git#egg=traits
pip install --cache-dir c:/temp git+http://github.com/enthought/pyface.git#egg=pyface

rem install traitsui
python setup.py develop
