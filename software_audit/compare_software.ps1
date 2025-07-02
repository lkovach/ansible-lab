$CurrentList = Get-ItemProperty HKLM:\Software\WoW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*, HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion | Where-Object { $_.DisplayName } | Sort-Object DisplayName

$BaselinePath = "C:\Ansible\software_baseline.txt"
$NewInstallPath = "C:\Ansible\new_software.txt"

if (Test-Path $BaselinePath) {
    $OldList = Get-Content $BaselinePath
    $CurrentNames = $CurrentList.DisplayName
    $New = $CurrentNames | Where-Object { $_ -notin $OldList }
    $New | Out-File -FilePath $NewInstallPath
    $CurrentNames | Out-File -FilePath $BaselinePath
} else {
    $CurrentList.DisplayName | Out-File $BaselinePath
}