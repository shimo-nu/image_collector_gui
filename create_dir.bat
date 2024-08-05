@echo off
setlocal enabledelayedexpansion

for /l %%x in (19,1,35) do (
    set "dirname=%%xth music costume"
    if not exist "!dirname!" (
        mkdir "!dirname!"
        echo Created directory "!dirname!"
    ) else (
        echo Directory "!dirname!" already exists.
    )
)

endlocal
pause

