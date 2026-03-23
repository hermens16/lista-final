Set WshShell = CreateObject("WScript.Shell")

pythonw = "C:\Users\User\AppData\Local\Programs\Python\Python313\pythonw.exe"

WshShell.CurrentDirectory = "C:\Users\User\Dev\lista-final"

WshShell.Run """" & pythonw & """ super_lista.py", 0, False