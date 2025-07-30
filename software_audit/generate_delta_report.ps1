$deltaEntries = # result of compare logic

$deltaReport = @()

foreach ($entry in $deltaEntries) {
    # Get registry ACL for InstalledByUser, plus all other fields
    $acl = Get-Acl $entry.RegistryPath -ErrorAction SilentlyContinue
    $owner = if ($acl) { $acl.Owner } else { "Unavailable" }

    $deltaReport += [PSCustomObject]@{
        DisplayName     = $entry.DisplayName
        DisplayVersion  = $entry.DisplayVersion
        InstallDate     = $entry.InstallDate
        InstalledBy     = $entry.InstallSource
        InstalledByUser = $owner
        HostName        = $hostname
        DomainName      = $domain
        IPAddress       = $ip
    }
}

$deltaReport | Export-Csv -Path $env:DELTA_PATH -NoTypeInformation