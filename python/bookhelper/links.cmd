@ECHO OFF
SET PATH=%PATH%;%CD%\bookhelper
SET PYTHONPATH=%CD%\venv\Lib\site-packages;%CD%
SET PYTHON=%CD%\venv\Scripts\Python.exe
SET FILE_TYPES=
SET CMD=

if NOT "%1"=="" (SET URL_FILE=%1) ELSE GOTO ERR_

SET CMD=%PYTHON% bookhelper\main.py -f %URL_FILE%

:LOOP_
SHIFT
IF NOT "%1"=="" (SET FILE_TYPES=%FILE_TYPES% %1)  ELSE GOTO EXEC_
GOTO LOOP_

:EXEC_
IF NOT "%FILE_TYPES%"=="" (SET CMD=%CMD% -t %FILE_TYPES%)
ECHO Executing %CMD%
%CMD%
GOTO END_

:ERR_
echo ERROR: URL shortcut file argument not provided

SET FILE_TYPES=
SET CMD=
:END_