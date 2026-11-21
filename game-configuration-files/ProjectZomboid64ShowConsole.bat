@echo off
setlocal enableextensions
set "PZ_ROOT=%~dp0.."
if not exist "%PZ_ROOT%\ProjectZomboid64.exe" set "PZ_ROOT=%~dp0"
for %%i in ("%PZ_ROOT%") do set "PZ_ROOT=%%~fi"
cd /d "%PZ_ROOT%"

set PATH=%PZ_ROOT%;%PZ_ROOT%\jre64\bin;%PATH%
if exist "%PZ_ROOT%\zbNative.dll" (
    set _JAVA_OPTIONS=-agentlib:zbNative=policy=allow-all
) else (
    set _JAVA_OPTIONS=
)
set PZ_CLASSPATH=./;projectzomboid.jar

".\jre64\bin\java.exe" -Djava.awt.headless=true --enable-native-access=ALL-UNNAMED --add-exports=java.base/jdk.internal.misc=ALL-UNNAMED -Dzomboid.steam=1 -Dzomboid.znetlog=1 -XX:-CreateCoredumpOnCrash -XX:-OmitStackTraceInFastThrow -XX:+UseZGC -Xms8192m -Xmx12288m -Djava.library.path=./win64/;./ -cp %PZ_CLASSPATH% zombie.gameStates.MainScreenState %1 %2 -debug

if %ERRORLEVEL% neq 0 (
    ".\jre64\bin\java.exe" -Djava.awt.headless=true --enable-native-access=ALL-UNNAMED --add-exports=java.base/jdk.internal.misc=ALL-UNNAMED -Dzomboid.steam=1 -Dzomboid.znetlog=1 -XX:-CreateCoredumpOnCrash -XX:-OmitStackTraceInFastThrow -Xms8192m -Xmx12288m -Djava.library.path=./win64/;./ -cp %PZ_CLASSPATH% zombie.gameStates.MainScreenState %1 %2 -debug
)

pause
