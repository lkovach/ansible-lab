import subprocess
import csv
import os
import socket
import pandas as pd
import logging
import platform

# Configure logging
logging.basicConfig(filename="update_checker.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

KB_LIST = ["KB5058524", "KB5058385", "KB5058383", "KB5058392"]  # UPDATED 5-14-25 for May Patch Tuesday
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
    """Compare installed updates against KB list and save to CSV on the Ansible controller."""
    try:
        os.makedirs(ANSIBLE_CONTROLLER_PATH, exist_ok=True)
        hostname, domain, ip_address, os_version = get_system_info()

        with open(INDIVIDUAL_RESULTS_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["KB_Number", "Installed", "Hostname", "Domain", "IP_Address", "Operating System"])

            writer.writerow(["TEST", "Yes", hostname, domain, ip_address, os_version])  # Test row for debugging
            print(f"DEBUG - Writing test row: {hostname, domain, ip_address, os_version}")

            for kb in KB_LIST:
                row = [kb, "Yes" if kb in installed_updates else "No", hostname, domain, ip_address, os_version]
                print(f"DEBUG - Writing row: {kb, 'Yes' if kb in installed_updates else 'No'}, {hostname}, {domain}, {ip_address}, {os_version}")
                writer.writerow(row)
        
        logging.info(f"Results saved to {INDIVIDUAL_RESULTS_FILE}")
    except Exception as e:
        logging.error(f"Error writing CSV file: {e}")

if __name__ == "__main__":
    logging.info("Script started")
    installed_updates = get_installed_updates()
    check_updates(installed_updates)
    logging.info("Script completed")
    print(f"Results saved to {INDIVIDUAL_RESULTS_FILE}, aggregated file saved as {AGGREGATED_FILE}")