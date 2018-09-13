@ECHO OFF
setlocal

:loop
if x%1 equ x goto done
set param=%1
if %param:~0,1% equ - goto checkParam
:paramError
echo Parameter error: %1 

:next
shift /1
goto loop

:checkParam
if "%1" equ "-f" goto input_file
if "%1" equ "-o" goto output_file
goto paramError

:input_file
    shift /1
    set INPUT_FILE=%1
    goto next

:output_file
    shift /1
    set OUTPUT_FILE=%1
    goto next
:done
IF "%OUTPUT_FILE%"=="" SET OUTPUT_FILE=proxys_socks5.txt
IF EXIST %INPUT_FILE% GOTO ADDPREFIX
ECHO ON
ECHO ERROR => INPUT FILE (-f FILE=%INPUT_FILE%) NOT SPECIFIED OR NOT EXIST
@ECHO OFF
GOTO :EOF

:ADDPREFIX
COPY /Y NUL %OUTPUT_FILE% > NUL
FOR /F %%i IN (%INPUT_FILE%) DO ECHO socks5://%%i >> %OUTPUT_FILE%
