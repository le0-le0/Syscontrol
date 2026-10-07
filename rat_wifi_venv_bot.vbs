Set objShell = CreateObject("WScript.Shell")
Set objWMIService = GetObject("winmgmts:\\.\root\CIMV2")

Dim pythonProcessID
pythonProcessID = 0

Do
    connected = False
    Set colItems = objWMIService.ExecQuery("SELECT * FROM Win32_NetworkAdapter WHERE NetConnectionStatus=2 AND NetEnabled=true")

    For Each objItem in colItems
        If InStr(LCase(objItem.NetConnectionID), "wi-fi") > 0 Or InStr(LCase(objItem.NetConnectionID), "wifi") > 0 Then
            connected = True
            Exit For
        End If
    Next

    If connected Then
        If pythonProcessID = 0 Then
            ' Run pythonw directly from venv's python.exe in hidden mode
            cmd = """C:\Users\Airbuddy\Syscontrol\.venv\Scripts\pythonw.exe"" ""C:\Users\Airbuddy\Syscontrol\syscontrol_bot.py"""
            objShell.Run cmd, 0, False
            pythonProcessID = -1 ' mark as running
        End If
    Else
        ' WiFi disconnected, kill pythonw processes if running
        If pythonProcessID <> 0 Then
            objShell.Run "taskkill /IM pythonw.exe /F", 0, True
            pythonProcessID = 0
        End If
    End If

    WScript.Sleep 10000 ' Check every 10 seconds

Loop
