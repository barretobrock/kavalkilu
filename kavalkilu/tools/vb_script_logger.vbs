' ===================================
' LOGGING SCRIPT FOR VBSCRIPT FILES
' 	This script is designed to share logging capabilities across all vbs files
'	It is intended as a workaround to meet demand for more detailed logs
' ===================================

' Objects

' Directories
Dim base_dir, main_prog_dir, main_data_dir
' Paths

' Strings
' Other
Const For_Appending = 8, For_Reading = 1, For_Writing = 2

Function dateToISO ( objDate, delim )
	' Adds zeroes to string if not enough zeroes are added
	' Arguments:
	'	objDate: Date type object
	'	delim: string delimiter between time units
	' Returns: string of date in ISO format (yyyymmdd)
	nyear = Year(objDate)
	nmonth = lpad(Month(objDate), "0", 2)
	nday = lpad(Day(objDate), "0", 2)
	dateToISO = nyear & delim & nmonth & delim & nday
End Function

Function lpad ( str, pad, length )
	lpad = String(length - Len(str), pad) & str
End Function

Function logtimestamp ( logname, logtype )
	' Used to take timestamp of log message
	' Arguments:
	'	logname: name of log as string
	'	logtype: type of log message (DEBUG, INFO, WARN, ERROR)
	' Returns: timestamp, log name and type of message

	' Format date info
	thedate = dateToISO(Now(), "-")
	' Format time info
	ms = Timer()
	' Process milliseconds
	mspos = instr(1, ms, ",") + 1
	ms = mid(ms, mspos, len(ms))
	If len(ms) < 3 Then
		' If milliseconds only shown in tenths place, add zeroes to number
		times = 3 - Len(ms)
		For x = 1 to times
			ms = ms & "0"
		Next
	ElseIf len(ms) > 3 Then
		' If more than three decimals, shorten to three
		ms = left(ms, 3)
	End If
	' Return string
	logtimestamp = thedate & " " & Time() & "." & ms & " - " & logname & " - " & " " & logtype & " "
End Function

Function logtxt ( rArgs )
	Dim logger
	' Should take in string array that ideally has:
	'	[0] log directory
	'	[1]	log filename prefix
	'	[2] name of log
	'	[3] text to show in log
	'	*[4] [Optional] type of log message
	' Once the array is processed, it will write the contents to file
	' Then close the file. If the file has any permissions issues,
	' It will write to a predefined log file
	' That is specifically made to flag permissions issues

	' Default strings
	defaultmsg = "DEBUG"
	defaultdir = "//energia.sise/dfs/REDIRECT/Barret.OBrock/Documents/Programming/Active/"
	If UBound(rArgs) = 4 Then
		log_dir = rArgs(0)
		log_file_prefix = rArgs(1)
		logname = rArgs(2)
		txt = rArgs(3)
		msgtype = defaultmsg
	ElseIf UBound(rArgs) = 5 Then
		log_dir = rArgs(0)
		log_file_prefix = rArgs(1)
		logname = rArgs(2)
		txt = rArgs(3)
		msgtype = defaultmsg
	ElseIf UBound(rArgs) < 4 Then
		' Collect errors related to array length here
		log_dir = defaultdir
		log_file_prefix = "err"
		logname = "arr.err.log"
		txt = "Array length was too short: " & UBound(rArgs)
		msgtype = "ERROR"
	Else
		' Collect any other errors here
		log_dir = defaultdir
		log_file_prefix = "err"
		logname = "arr.err.log"
		txt = "unexpected array length: " & UBound(rArgs)
		msgtype = "ERROR"
	End If

	' Setup the logger
	Set fso = CreateObject("Scripting.FileSystemObject")

	log_path = log_dir & log_file_prefix & "_" & dateToISO(Now(), "") & ".log"
	On Error Resume Next
	Set logger = fso.OpenTextFile(log_path, For_Appending, True)
	On Error GoTo 0
	If Err.Description = "Permission denied" Then
		' If desired file can't be accessed, write to a log file dedicated to catching errors before logs are made
		alt_log_path = log_dir & "PreLogErrors.log"
		Set logger = fso.OpenTextFile(alt_log_path, For_Appending, True)
		logger.WriteLine logtimestamp(logname, "ERROR") & "Permissions error prevented log from being written"
	Else:
		logger.WriteLine logtimestamp(logname, msgtype) & txt
	End If
	logger.Close
End Function

Function geterr
	If Err.Number <> 0 Then
		geterr = Err.Number & ": " & Err.Description & " " & Err.Source
	Else:
		geterr = ""
	End If
End Function

' base_dir = "//energia.sise/dfs/REDIRECT/Barret.OBrock/Documents/"
' main_prog_dir = base_dir & "Programming/Active/"
' global_dir = main_prog_dir & "Global/"
' nps_prog_dir = main_prog_dir & "NPS/"
' log_dir = nps_prog_dir & "logs/"

' log_name = "nps.mailer"


' logtxt Array(log_dir, "logtest", log_name, "Functions successfully set up for emailing prices.", "INFO")

' logtxt Array(log_dir, "logtest", log_name, "Functions successfully set up for sending prices.", "INFO")