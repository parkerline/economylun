REM Last-ик ActivityView. Версия 1 Alpha

@ECHO OFF

REM Надеюсь, сохранить файл в кодировке DOS-866 не забыли
CHCP 866

REM Зеленый на черном - интригующе... опять же, хакеры и все такое
COLOR B

CLS


REM ----------------------------------------------------------------------------------------
REM Проверка на наличие прав администратора 
FOR /F "tokens=1,2*" %%V IN ('bcdedit') DO SET adminTest=%%V
	IF (%adminTest%)==(Отказано) GOTO errNoAdmin
	IF (%adminTest%)==(Access) GOTO errNoAdmin
REM ----------------------------------------------------------------------------------------



REM ------------------------------------------------------------------------------------------
REM Очистка всех журналов Windows, если пользователь выбрал в меню 3. Проводим вначале, чтоб в логах не осталось вызовов wevtutil
REM утилиты NirSoft - LastActivityView

	ECHO.
	ECHO ОЧИСТКА ВСЕХ ЖУРНАЛОВ Windows
	FOR /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")
	ECHO.
	ECHO Выполнено
	ECHO.


REM ------------------------------------------------------------------------------------------
REM ShellBag. История запуска приложений и доступа к папкам, связанная с "оболочкой"
REM утилиты NirSoft - LastActivityView, ExecutedProgramsList, ShellBagsView
ECHO.
ECHO ОЧИСТКА ИСТОРИИ ShellBag - реестр
REG DELETE "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache" /va /f
REG DELETE "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU" /f
REG DELETE "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags" /f
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\Shell\BagMRU" /f
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\Shell\Bags" /f
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM Explorer. История запуска приложений связанная с "Проводником"
ECHO.
ECHO ОЧИСТКА ИСТОРИИ Explorer - реестр
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /va /f
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM ComDlg32. История диалогов "открыть\сохранить" и "последних мест посещений"
REM утилиты NirSoft - LastActivityView
ECHO.
ECHO ОЧИСТКА ИСТОРИИ OpenSave и LastVisited - реестр
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\FirstFolder" /va /f
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU" /va /f
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRULegacy" /va /f
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched" /f
REG DELETE "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage" /va /f
REG DELETE "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /va /f
REG DELETE "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32" /va /f
REM (утилиты NirSoft - OpenSaveFilesView)
REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU" /f
REG ADD "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU"
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM если пользователь выбрал в меню не 1 т.е. 2 или 3
	
	REM UserAssist. Очистка списока запущенных программ в меню "Пуск"
	REM утилиты NirSoft - UserAssistView
	ECHO.	
	ECHO ОЧИСТКА ИСТОРИИ UserAssist - реестр
	REG DELETE "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist" /f
	REG ADD "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"
	ECHO.



REM ------------------------------------------------------------------------------------------
REM AppCompatCache
ECHO.
ECHO ОЧИСТКА ИСТОРИИ AppCompatCache - реестр
REG DELETE "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache" /va /f
REG DELETE "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Session Manager\AppCompatCache" /va /f
REG DELETE "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage" /va /f
REG DELETE "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /va /f
REG DELETE "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32" /va /f
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM DiagnosedApplications. Диагностика утечек памяти в приложении ОС Windows
ECHO.
ECHO ОЧИСТКА ИСТОРИИ DiagnosedApplications - реестр
REG DELETE "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\RADAR\HeapLeakDetection\DiagnosedApplications" /f
REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\RADAR\HeapLeakDetection\DiagnosedApplications"
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM Получение SID - идентификатор безопасности текущего пользователя 
FOR /F "tokens=2" %%i IN ('whoami /user /fo table /nh') DO SET usersid=%%i
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM Search. История поиска 
ECHO.
ECHO ОЧИСТКА ИСТОРИИ Search - реестр
	REG DELETE "HKEY_USERS\%usersid%\Software\Microsoft\Windows\CurrentVersion\Search\RecentApps" /f
	REG ADD "HKEY_USERS\%usersid%\Software\Microsoft\Windows\CurrentVersion\Search\RecentApps"
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM BAM. 
REM По идее, при перезагрузке затрется само.  
REM Но можно сделать отдельный bat и запускать, например, после работы с portable-приложениями
ECHO.
ECHO ОЧИСТКА ИСТОРИИ службы Background Activity Moderator - реестр
REG DELETE "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\bam\UserSettings\%usersid%" /va /f
REG DELETE "HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Services\bam\UserSettings\%usersid%" /va /f
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM AppCompatFlags
ECHO.
ECHO ОЧИСТКА ИСТОРИИ AppCompatFlags - реестр
REM утилиты NirSoft - ExecutedProgramsList
REG DELETE "HKEY_USERS\%usersid%\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store" /va /f

REM если пользователь выбрал в меню не 1 т.е. 2 или 3

	REM Список программ, для которых задан "режим совместимости" или "запускать от имен администратора"
	REM утилиты NirSoft - AppCompatibilityView
	REG DELETE  "HKEY_USERS\%usersid%\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /va /f



REM ------------------------------------------------------------------------------------------
REM История "монтирования" дисков в т.ч. и TrueCrypt
ECHO.
ECHO ОЧИСТКА ИСТОРИИ MountedDevices - реестр
ECHO.
REG DELETE "HKEY_USERS\%usersid%\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2" /f
REG ADD "HKEY_USERS\%usersid%\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2"
ECHO.
REM ------------------------------------------------------------------------------------------


REM ------------------------------------------------------------------------------------------
REM 
ECHO.
REM утилиты NirSoft - JumpListsView, RecentFilesView
ECHO ОЧИСТКА ИСТОРИИ Recent - файловая система
DEL /f /q %APPDATA%\Microsoft\Windows\Recent\*.*
DEL /f /q %APPDATA%\Microsoft\Windows\Recent\CustomDestinations\*.*
DEL /f /q %APPDATA%\Microsoft\Windows\Recent\AutomaticDestinations\*.*
DEL /f /q %TEMP%\*.*
DEL /f /q %userprofile%\AppData\Local\Yandex\YandexBrowser\User Data\Default\Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Yandex\YandexBrowser\User Data\Default\GPUCache\*.*
DEL /f /q %userprofile%\AppData\Local\Yandex\YandexBrowser\User Data\Default\Media Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Yandex\YandexBrowser\User Data\Default\Pepper Data\*.*
DEL /f /q %userprofile%\AppData\Local\Opera\opera x64\cache\*.*
DEL /f /q %userprofile%\AppData\Local\Opera\opera\cache\*.*
DEL /f /q %userprofile%\AppData\Local\Opera Software\Opera Stable\Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Opera Software\Opera Next\Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Google\Chrome\User Data\Default\Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Google\Chrome\User Data\Default\GPUCache\*.*
DEL /f /q %userprofile%\AppData\Local\Google\Chrome\User Data\Default\Media Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Google\Chrome\User Data\Default\Pepper Data\*.*
DEL /f /q %userprofile%\AppData\Local\Google\Chrome\User Data\Default\Pepper Data\*.*
DEL /f /q %userprofile%\AppData\Local\Google\CrashReports\*.*
DEL /f /q %userprofile%\AppData\Local\Chromium\User Data\Default\Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Chromium\User Data\Default\GPUCache\*.*
DEL /f /q %userprofile%\AppData\Local\Chromium\User Data\Default\Media Cache\*.*
DEL /f /q %userprofile%\AppData\Local\Chromium\User Data\Default\Pepper Data\*.*


taskkill /im "firefox.exe"
set DataDir=C:\Users\%USERNAME%\AppData\Local\Mozilla\Firefox\Profiles
del /q /s /f "%DataDir%"
rd /s /q "%DataDir%"
for /d %%x in (C:\Users\%USERNAME%\AppData\Roaming\Mozilla\Firefox\Profiles\*) do del /q /s /f %%x\*sqlite
DEL /f /q %userprofile%\AppData\Local\Mozilla\Firefox\Profiles\*.*
DEL /f /q %userprofile%\AppData\Roaming\Mozilla\Firefox\Profiles\*.*
DEL /f /q %userprofile%\Mozilla\Firefox\Profiles\downloads.sqlite
DEL /f /q %userprofile%\Mozilla\Firefox\Profiles\places.sqlite
*
ECHO Выполнено
ECHO.
REM ------------------------------------------------------------------------------------------

REM ------------------------------------------------------------------------------------------
ECHO.
ECHO ОЧИСТКА ИСТОРИИ Panther - файловая система
DEL /f /q %systemroot%\Panther\*.*
ECHO Выполнено
ECHO.
REM ------------------------------------------------------------------------------------------

REM ------------------------------------------------------------------------------------------
ECHO.
ECHO ОЧИСТКА ИСТОРИИ AppCompat - файловая система
DEL /f /q %systemroot%\appcompat\Programs\*.txt
DEL /f /q %systemroot%\appcompat\Programs\*.xml
DEL /f /q %systemroot%\appcompat\Programs\Install\*.txt
DEL /f /q %systemroot%\appcompat\Programs\Install\*.xml
ECHO Выполнено
ECHO.
REM ----


REM ------------------------------------------------------------------------------------------

	ECHO.
	REM Prefetch. Удаление файлов, оптимизирующих запуск приложений. Windows в следующий раз загрузится медленнее
	REM утилиты NirSoft - LastActivityView, ExecutedProgramsList
	ECHO ОЧИСТКА ИСТОРИИ Prefetch - файловая система
	DEL /f /q %systemroot%\Prefetch\*.pf
	DEL /f /q %systemroot%\Prefetch\*.ini
	DEL /f /q %systemroot%\Prefetch\*.7db
	DEL /f /q %systemroot%\Prefetch\*.ebd
	DEL /f /q %systemroot%\Prefetch\*.bin
	REM SuperFetch. Удаление баз оптимизации SuperFetch
	DEL /f /q %systemroot%\Prefetch\*.db
	REM Trace. Удаление файлов трассировки
	DEL /f /q %systemroot%\Prefetch\ReadyBoot\*.fx
	ECHO Выполнено
	ECHO.

	ECHO.
	ECHO ОЧИСТКА ИСТОРИИ Minidump - файловая система
	REM Удаление дампов ошибок
	REM утилиты NirSoft - LastActivityView
	DEL /f /q %systemroot%\Minidump\*.*
	ECHO Выполнено


PAUSE
EXIT

:do_clear
ECHO Очистка журнала %1
wevtutil.exe cl %1
GOTO :eof

:errNoAdmin
COLOR 4
ECHO Необходимо запустить этот скрипт от имени администратора
ECHO.
PAUSE