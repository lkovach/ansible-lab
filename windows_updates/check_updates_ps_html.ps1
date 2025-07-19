# Check for specific Windows updates using PowerShell
$KBsToCheck = @("KB5062572", "KB5062557", "KB5062799", "KB5062560", "KB5062570")

$htmlHead = @"
<html><body><table border="1" cellpadding=4>
<tr><th>KB Article</th><th>Installed</th><th>Host</th><th>Domain</th><th>IP Address</th><th>OS Version</th></tr>
"@

$htmlRows = $report | ForEach-Object {
    if ($_.Installed -eq 'Yes') {
        $bg = '#90EE90'
    } else {
        $bg = '#FA8072'
    }
    
    "<tr>" +
      "<td>$($_.KB_Article)</td>" +
      "<td style='background-color:$bg'>$($_.Installed)</td>" +
      "<td>$($_.Hostname)</td>" +
      "<td>$($_.Domain)</td>" +
      "<td>$($_.IP_Address)</td>" +
      "<td>$($_.OS_Version)</td>" +
    "</tr>"
}

$htmlFoot = "</table></body></html>"
($htmlBody = $htmlRows + $htmlFoot) |
  Out-File C:\Updates\patch_report_$env:COMPUTERNAME.html -Encoding UTF8

Write-Host "HTML report created: C:\Updates\patch_report_$env:COMPUTERNAME.html"