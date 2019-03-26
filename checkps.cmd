@ECHO OFF

SET INPUT_FILE=inputproxys.txt
SET TEMP_FILE=goodprox%RANDOM%.txt
SET OUTPUT_FILE=jdproxies.txt

:LOOP_LABEL
IF %1! EQU !   GOTO PARAM_DONE_LABEL
IF %1! EQU -o! GOTO OUTPUT_FILE_LABEL
IF %1! EQU -f! GOTO INPUT_FILE_LABEL
IF %1! EQU -p! GOTO NB_PROCESS_LABEL
:NEXT_PARAM_LABEL
SHIFT /1
GOTO LOOP_LABEL

:INPUT_FILE_LABEL
SHIFT /1
IF NOT %1!==! SET INPUT_FILE=%1
GOTO NEXT_PARAM_LABEL
:OUTPUT_FILE_LABEL
SHIFT /1
IF NOT %1!==! SET OUTPUT_FILE=%1
GOTO NEXT_PARAM_LABEL
:NB_PROCESS_LABEL
SHIFT /1
IF NOT %1!==! SET NB_PROCESS=%1
GOTO NEXT_PARAM_LABEL

:PARAM_DONE_LABEL
SET PY_PARAMS=-f %INPUT_FILE% -o %TEMP_FILE%
IF NOT !%NB_PROCESS%==! SET PY_PARAMS=%PY_PARAMS% -p %NB_PROCESS%
python scripts\python\test_socks5_server.py %PY_PARAMS%
CALL .\scripts\proxysock.bat -f %TEMP_FILE% -o %OUTPUT_FILE%
ECHO Cleaning temp file %TEMP_FILE%
IF EXIST  %TEMP_FILE% DEL /Q %TEMP_FILE% ELSE ECHO %TEMP_FILE% does not exist
START NOTEPAD.EXE %OUTPUT_FILE%
