:: Execute etstool operation for every tookit in the argument list
:: Options
:: %1 -- operation
:: %2 -- runtime
:: %3... -- tookits
::
::
SETLOCAL EnableDelayedExpansion

SET operation=%1
SET runtime=%2
SET toolkit=%3

CALL edm run -- python etstool.py !operation! --runtime=!runtime! --toolkit=!toolkit! || GOTO error
PUSHD ets-demo
CALL edm run -- python etstool.py !operation! --runtime=!runtime! --toolkit=!toolkit! || GOTO error
POPD

GOTO end

:error:
ENDLOCAL
EXIT /b %ERRORLEVEL%

:end:
ENDLOCAL
ECHO.Done
