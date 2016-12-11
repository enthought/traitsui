if [[ ${TRAVIS_OS_NAME} == "osx" ]]
then
    wget https://package-data.enthought.com/edm/osx_x86_64/1.3/edm_1.3.0.pkg
    sudo installer -pkg edm_1.3.0.pkg -target /
else
    wget https://package-data.enthought.com/edm/rh5_x86_64/1.3/edm_1.3.0_linux_x86_64.sh
    chmod u+x edm_1.3.0_linux_x86_64.sh
    ./edm_1.3.0_linux_x86_64.sh -b -p ~
    export PATH="~/bin:${PATH}"
fi
