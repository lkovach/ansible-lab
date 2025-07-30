# --- Paths to baseline and current scan ---
$baselinePath = $env:BASELINE_PATH
$currentPath = $env:CURRENT_PATH
$deltaPath = $env:DELTA_PATH

# --- Load the data ---
$baseline = Import-Csv -Path $baselinePath
$current = Import-Csv -Path $currentPath

# --- Compare for new software ---
$deltaRaw = Compare-Object `
    -ReferenceObject $baseline `
    -DifferenceObject $current `
    -Property DisplayName, DisplayVersion, InstallDate, InstalledByUser, HostName, Domain, IPAddress `
    -PassThru |
    Where-Object { $_.SideIndicator -eq '=>' }

# --- Gather system metadata ---
$hostname = $env:COMPUTERNAME
$domain = $env:USERDOMAIN
$ip = (Get-NetIPAddress | Where-Object { $_.AddressFamily -eq "IPv4" -and $_.PrefixOrigin -ne "WellKnown" }).IPAddress -join ", "

# --- Enrich delta entries ---
$deltaReport = @()

foreach ($entry in $deltaRaw) {
    # Match back full entry from current scan
    $matched = $current | Where-Object {
        $_.DisplayName -eq $entry.DisplayName -and $_DisplayVersion -eq $entry.DisplayVersion
    }
    if ($matched) {
        $regPath = $matched.RegistryPath
        $acl = Get-Acl -Path $regPath -ErrorAction SilentlyContinue
        $owner = if ($acl) { $acl.Owner } else { "Unknown" }

        $deltaReport += [PSCustomObject]@{
            DisplayName = $entry.DisplayName
            DisplayVersion = $entry.DisplayVersion
            InstallDate = $entry.InstallDate
            InstalledByUser = $owner
            HostName = $hostname
            Domain = $domain
            IPAddress = $ip
        }
    }
}

# --- Export delta report ---
$deltaReport | Export-Csv -Path $deltaPath -NoTypeInformation
Write-Host "Delta report generated at $deltaPath"