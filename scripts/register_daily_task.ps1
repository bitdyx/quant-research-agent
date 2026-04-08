param(
    [string]$TaskName = "QuantResearchAgentDaily",
    [string]$PythonExe = "D:\program\Anaconda\python.exe",
    [string]$ProjectRoot = "D:\python\worldquant\quant_research_agent",
    [string]$StartTime = "08:30"
)

$action = New-ScheduledTaskAction -Execute $PythonExe -Argument "-m quant_research_agent run-daily" -WorkingDirectory $ProjectRoot
$trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Description "Run Quant Research Agent daily" -Force
