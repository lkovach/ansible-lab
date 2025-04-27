import subprocess
import csv
import socket

#Define KB numbers
kb_list = ["KB5055661", "KB5055526", "KB5055519", "KB5055521"] #Change monthly

#Use powershell to get the installed updates
def get_installed_updates():
    cmd = 'powershell "Get-HotFix | Select-Object -ExpandProperty HotFixID"'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.splitlines()

#Retrieve host info
def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return hostname, ip_address

#Check if KBs are installed
def check_updates(installed_updates, kb_list):
    hostname, ip_address = get_system_info()
    results = [
            {"Hostname": hostname, "IP Address": ip_address, "KB": kb, "Installed": "Yes" if kb in installed_updates else "No"}
            for kb in kb_list
        ]
    return results

#Save the results to a CSV file
def save_to_csv(data, filename="C:\\Install\\updates_status.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Hostname", "IP Address", "KB", "Installed"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    installed_updates = get_installed_updates()
    results = check_updates(installed_updates, kb_list)
    save_to_csv(results)
    print("Results saved to update_status.csv")
