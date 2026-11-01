# Delivering a recurring report on a schedule (Windows Task Scheduler)

Companion to the cadence rules in SKILL.md. Everything here is about the run, not the content.

## Registering the task

One task per run, so each hour has its own log and its own exit status; a single task launching
several reports at once loses which one failed.

    schtasks /Create /TN "\<Folder>\<report>-<run>" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 07:35 /F \
      /TR "wscript.exe //B //NoLogo <launcher.vbs> <run>"

- `//B` and `//NoLogo` are the **WSH** switches, double slash on purpose: for `wscript`/`cscript` a
  single `/B` is not consumed by the host, it is passed through to the script as an argument.
- Point `/TR` at the launcher and give the launcher absolute paths — the task's working directory is
  not yours, and the data directory is often a sibling of the checkout, not inside it.
- Do not assume an elevated console is needed: try `/Create` first and read the reply. If it does
  refuse, hand the exact command to whoever has one instead of giving up on the schedule.

## The hidden launcher, and the hang it avoids

    ' launch.vbs — start the .ps1 with no window and pass its exit code back
    Option Explicit
    Dim shell, fso, run, comando
    run = "once"
    If WScript.Arguments.Count > 0 Then run = WScript.Arguments(0)
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set shell = CreateObject("WScript.Shell")
    comando = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & _
              fso.BuildPath(fso.GetParentFolderName(WScript.ScriptFullName), "task.ps1") & _
              """ -Run " & run
    WScript.Quit shell.Run(comando, 0, True)   ' 0 = hidden window, True = wait for the exit code

Measured here: a task whose action is `powershell.exe -WindowStyle Hidden -File ...` **hung** — the
hidden console does not start in the scheduler's context, and the run left neither log nor output,
so the task looked scheduled and produced nothing. `wscript` opens no console at all, and
`Run(..., 0, True)` waits, so the task's *Last Result* is the report's own exit code instead of a
launcher's.

If the report needs a specific user context (a credential store, a mapped drive, a printer), the
task must run as that logged-in user; the settings below keep it there.

## Settings `schtasks` does not set

    $s = (Get-ScheduledTask -TaskPath '\<Folder>\' -TaskName '<task>').Settings
    $s.StartWhenAvailable          = $true    # a missed hour runs at the next opportunity
    $s.DisallowStartIfOnBatteries  = $false
    $s.StopIfGoingOnBatteries      = $false
    $s.ExecutionTimeLimit          = 'PT15M'  # the default is three days
    Set-ScheduledTask -TaskPath '\<Folder>\' -TaskName '<task>' -Settings $s

`StartWhenAvailable` is what creates the **late run** the report has to declare (see the cadence
rules): it is a feature, and it is why the clock/nominal distinction exists.

## Reading the scheduler from a POSIX shell (Git Bash / MSYS)

`schtasks` writes **UTF-16**, so `grep` reports "Binary file matches" instead of lines; strip the
nulls first. Field labels are localized, so match on values rather than on English labels.

    schtasks /Query /TN "<task>" /FO LIST /V | tr -d '\0' | grep -i "ejecutar"
    schtasks /Query /FO TABLE | tr -d '\0' | grep -i "<report>"

`/Query` and `/Run` need no elevation. A task registered with default credentials runs **only while
that user is logged in** — right for a report printed where the reader works, wrong for anything
that must run unattended, and worth saying out loud in the report's own documentation.

## Verifying a cadence (one run, end to end, off-cadence)

1. Fire it once: `schtasks /Run /TN "<task>"` → "CORRECTO: se ha intentado ejecutar la tarea".
2. Read the run's **log file** and the artifact the reader will hold — the sheet, the message, the
   record row it appends.
3. Read the status the scheduler recorded (`/FO LIST /V`, the last-run and last-result fields).
4. Only then is the schedule a delivery mechanism; before that it is a plan. Say in the write-up
   which of the two you measured, and name what the in-session run does not cover.

Expect the verification to find real defects — a wrong hour recorded, an output folder nested twice
because a path helper already carries the day. That is the point of firing it once by hand: the first
unattended run is not the place to discover them.
