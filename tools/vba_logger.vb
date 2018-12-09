' ===================================
' LOGGING SCRIPT FOR VBA PROJECTS
' 	This script is designed to print results from inside VBA
'	To a log file where VBscript also prints
'	It is intended as a workaround to meet demand for more detailed logs
' ===================================

Dim log_path, log_name, log_type, log_text
Const For_Appending = 8

Function zeroAdd ( num )
	' Adds zeroes to front of dates if single digit
	If Len(num) = 1 Then
		zeroAdd = "0"&num
	Else:
		zeroAdd = num
	End If
End Function

Function logtimestamp ( logname, logtype )
	' Prints out timestamp and logger name

	thedate = Year(Now()) & "-" & zeroAdd(Month(Now())) & "-" & zeroAdd(Day(Now()))
	ms = Timer()
	' FORMAT MILLISECONDS
	mspos = instr(1, ms, ",") + 1
	ms = mid(ms, mspos, len(ms))
	If len(ms) < 3 Then
		times = 3 - Len(ms)
		For x = 1 to times
			ms = ms & "0"
		Next
	ElseIf len(ms) > 3 Then
		ms = left(ms, 3)
	End If
	logtimestamp = thedate & " " & Time() & "." & ms & " - " & logname & " - " & " " & logtype & " "
End Function

Function loginfo( logpath, logname, logtype, txt )
	' GET CURRENT DIRECTORY OF SCRIPT + FILE
	Set fso = CreateObject("Scripting.FileSystemObject")
	' Writes string to log file with timestamp and logger name
	Set cLog = fso.OpenTextFile(logpath, For_Appending, True)
	cLog.Writeline logtimestamp(logname, logtype) & txt
	cLog.Close
	Set cLog = Nothing
End Function

On Error Resume Next
log_path = Wscript.Arguments(0)
log_name = Wscript.Arguments(1)
log_type = Wscript.Arguments(2)
log_text = Wscript.Arguments(3)
On Error GoTo 0

If log_path = "" Then Wscript.Quit	'End sub if proper path not provided

loginfo log_path, log_name, log_type, log_text


