#Runs the installer from the DC Share, silently

$installer= "\\ansible-dc\sysvol\ansible.lab\scripts\epi_win_live_installer.exe"
Start-Process $installer -ArgumentList "/quiet" -Wait