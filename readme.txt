#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

; ^ = CTRL, # = WIN, ! = ALT, + = SHIFT

; NOTEPAD TEST
^+j::
Run, notepad.exe
WinActivate, Untitled - Notepad
WinWaitActive, Untitled - Notepad
Send, Hello World!
return

; RESTART
#!x::
Send, {Alt down}{F4}{Alt up}  ; Bring up the shutdown dialog
Sleep, 100
KeyWait, Escape, T1  ; Wait for Escape key press with 1 second timeout
if ErrorLevel = 0  ; If Escape was pressed
{
    Send, {Escape}  ; Cancel the dialog
    return
}
Send, {Right}  ; Navigate to "Restart" option
Sleep, 50
KeyWait, Escape, T1  ; Wait for Escape key press with 1 second timeout
if ErrorLevel = 0  ; If Escape was pressed
{
    Send, {Escape}  ; Cancel the dialog
    return
}
Send, {Enter}  ; Confirm
return

; SHUTDOWN
#!s::
Send, {Alt down}{F4}{Alt up}  ; Bring up the shutdown dialog
Sleep, 100
KeyWait, Escape, T1  ; Wait for Escape key press with 1 second timeout
if ErrorLevel = 0  ; If Escape was pressed
{
    Send, {Escape}  ; Cancel the dialog
    return
}
Send, {Enter}  ; "Shut Down" is the default selection
return

; HIBERNATE
#!h::
Send, {Alt down}{F4}{Alt up}  ; Bring up the shutdown dialog
Sleep, 100
KeyWait, Escape, T1  ; Wait for Escape key press with 1 second timeout
if ErrorLevel = 0  ; If Escape was pressed
{
    Send, {Escape}  ; Cancel the dialog
    return
}
Send, {Right 2}  ; Navigate to "Sleep" option
Sleep, 50
KeyWait, Escape, T1  ; Wait for Escape key press with 1 second timeout
if ErrorLevel = 0  ; If Escape was pressed
{
    Send, {Escape}  ; Cancel the dialog
    return
}
Send, {Enter}  ; Confirm
return

; SLEEP
#!p::
Send, {Alt down}{F4}{Alt up}  ; Bring up the shutdown dialog
Sleep, 100
KeyWait, Escape, T1  ; Wait for Escape key press with 1 second timeout
if ErrorLevel = 0  ; If Escape was pressed
{
    Send, {Escape}  ; Cancel the dialog
    return
}
Send, {Right 3}  ; Navigate to "Sleep" option (depending on your Windows version)
Sleep, 50
KeyWait, Escape, T1  ; Wait for Escape key press with 1 second timeout
if ErrorLevel = 0  ; If Escape was pressed
{
    Send, {Escape}  ; Cancel the dialog
    return
}
Send, {Enter}  ; Confirm
return

; CANCEL SHUTDOWN/RESTART/HIBERNATE/SLEEP
#!c::
Send, {Escape}  ; If any shutdown dialog is active, this will cancel it
return