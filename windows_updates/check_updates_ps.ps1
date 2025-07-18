$KBsToCheck = @("KB5062572", "KB5062557", "KB5062799", "KB5062560", "KB5062570")
$hostname = $env:COMPUTERNAME
$domain = (Get_WmiObject Win32_ComputerSystem).Domain
$ip = (Get-NetIPAddress - AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '169.*'} | Select-Object -First 1).IPAddress
$os = (Get-CimInstance Win32_OperatingSystem).Caption

$installedKBs = Get-HotFix | Select-Object -ExpandProperty HotFixID

$report = foreach ($kb in $KBsToCheck) {
    [PSCustomObject]@{
        KB_Article = $kb
        Installed = if ($installKBs -contains $kb) { "Yes" } else { "No" }
        Hostname = $hostname
        Domain = $domain
        IP_Address = $ip
        OS_Version = $os
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
}

$outputPath - "C:\Updates\patch_report_$hostname.xlsx"

$report | Export-Excel -Path $outputPath -WorksheetName "Update Status" `
    -AutoSize `
    -ConditionalFormat @(
        @{Column="Installed"; ConditionalType="ContainsText"; Text="Yes"; BackgroundColor="LightGreen"}
        @{Column="Installed"; ConditionalType="ContainsText"; Text="No"; BackgroundColor="Salmon"}
    )

    Write-Host "Excel report created: $outputPath"