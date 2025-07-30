$hostname = $env:COMPUTERNAME
$domain = $env:USERDOMAIN
$ip = (Get-NetIPAddress | Where-Object { $_.AddressFamily -eq "IPv4" -and $_.PrefixOrigin -ne "WellKnown" }).IPAddress -join ", "

$keys = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

$report = @()

foreach ($keyRoot in $keys) {
    Get-ChildItem $keyRoot | ForEach-Object {
        $keyPath = $_.PSPath
        $props = Get-ItemProperty $keyPath -ErrorAction SilentlyContinue
        $acl = Get-Acl $keyPath -ErrorAction SilentlyContinue

        if ($props.DisplayName or $props.QuietInstallString) {
            $report += [PSCustomObject]@{
                DisplayName = $props.DisplayName
                DisplayVersion = $props
                InstallDate = $props.InstallDate
                InstalledByUser = $acl.Owner
                HostName = $hostname
                Domain = $domain
                IPAddress = $ip
            }
        }
    }
}

$report | Export-Csv -Path $env:BASELINE_PATH -NoTypeInformation