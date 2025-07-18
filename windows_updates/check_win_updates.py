import subprocess
import csv
import os
import socket
import pandas as pd
import logging
import platform

# Configure logging
logging.basicConfig(filename="update_checker.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

KB_LIST = ["KB5061010", "KB5060531", "KB5060954", "KB5060526"]  # UPDATED 6-11-25 for June Patch Tuesday
ANSIBLE_CONTROLLER_PATH = "/opt/ansible/win_updates"
INDIVIDUAL_RESULTS_FILE = os.path.join(ANSIBLE_CONTROLLER_PATH, f"{socket.gethostname()}_updates.csv")
AGGREGATED_FILE = os.path.join(ANSIBLE_CONTROLLER_PATH, "aggregated_updates.csv")

def get_installed_updates():
    """Retrieve installed updates using PowerShell's Get-HotFix."""
    try:
        result = subprocess.run(["powershell", "-Command", "Get-HotFix | Select-Object -ExpandProperty HotFixID"],
                                capture_output=True, text=True, check=True)
        updates = result.stdout.strip().split("\n")
        installed_updates = {update.strip() for update in updates if update.strip()}
        logging.info(f"Retrieved installed updates: {installed_updates}")
        return installed_updates
    except subprocess.CalledProcessError as e:
        logging.error(f"Error retrieving installed updates: {e}")
        return set()

def get_system_info():
    """Retrieve hostname, domain name, IP address, and OS version."""
    try:
        hostname = socket.gethostname()
        domain_result = subprocess.run(["powershell", "-Command", "(Get-WmiObject Win32_ComputerSystem).Domain"],
                                       capture_output=True, text=True, check=True)
        domain = domain_result.stdout.strip() if domain_result.stdout.strip() else "Unknown"
        ip_address = socket.gethostbyname(hostname)
        os_version = platform.system() + " " + platform.release()  # Get OS details
        logging.info(f"DEBUG - Hostname: {hostname}, Domain: {domain}, IP Address: {ip_address}, OS: {os_version}")
        return hostname, domain, ip_address, os_version
    except Exception as e:
        logging.error(f"Error retrieving system info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown"

def check_updates(installed_updates):
    try:
        os.makedirs(ANSIBLE_CONTROLLER_PATH, exist_ok=True)
        xlsx_file = os.path.join(ANSIBLE_CONTROLLER_PATH, f"{socket.gethostname()}_updates.xlsx")

        hostname, domain, ip_address, os_version = get_system_info()

        data = []
        for kb in KB_LIST:
            data.append({
                "KB_Number": kb,
                "Installed": "Yes" if kb in installed_updates else "No",
                "Hostname": hostname,
                "Domain": domain,
                "IP_Address": ip_address,
                "Operating System": os_version
            })

        df = pd.DataFrame(data)
        df.to_excel(xlsx_file, index=False, engine="xlsxwriter")

        logging.info(f"Results saved to {xlsx_file}")
        print(f"DEBUG - XLSX saved to: {xlsx_file}")

    except Exception as e:
        logging.error(f"Error writing XLSX file: {e}")
        print(f"ERROR: {e}")

if __name__ == "__main__":
    logging.info("Script started")
    installed_updates = get_installed_updates()
    check_updates(installed_updates)
    logging.info("Script completed")
    print(f"Results saved to {INDIVIDUAL_RESULTS_FILE}, aggregated file saved as {AGGREGATED_FILE}")