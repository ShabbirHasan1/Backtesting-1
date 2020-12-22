Attribute VB_Name = "Module1"
Sub proalpha_pnl()

Dim objShell As Object

Dim PythonExe, PythonScript As String

'Create a shell object
Set objShell = VBA.CreateObject("Wscript.Shell")

PythonExe = """python path"""
PythonScript = """D:\PycharmProjects\Backtesting\Independent programs\performance_from trade_proalpha.py"""

'Run python  & python script
objShell.Run PythonExe & PythonScript

End Sub
