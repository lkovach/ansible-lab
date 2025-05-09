import subprocess
import csv
import os
import socket
import pandas as pd
import logging

# Configure logging
logging.basicConfig(filename="update_checker.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

KB_LIST = ["KB123456", "KB654321"]  # Replace with actual KB numbers
ANSIBLE_CONTROLLER_PATH = "/opt/ansible/updates"
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
    """Retrieve hostname, domain name, and IP address."""
    try:
        hostname = socket.gethostname()
        domain_result = subprocess.run(["powershell", "-Command", "(Get-WmiObject Win32_ComputerSystem).Domain"],
                                       capture_output=True, text=True, check=True)
        domain = domain_result.stdout.strip()
        ip_address = socket.gethostbyname(hostname)
        logging.info(f"System Info - Hostname: {hostname}, Domain: {domain}, IP Address: {ip_address}")
        return hostname, domain, ip_address
    except Exception as e:
        logging.error(f"Error retrieving system info: {e}")
        return "Unknown", "Unknown", "Unknown"

def check_updates(installed_updates):
    """Compare installed updates against KB list and save to CSV on the Ansible controller."""
    try:
        os.makedirs(ANSIBLE_CONTROLLER_PATH, exist_ok=True)
        hostname, domain, ip_address = get_system_info()

        with open(INDIVIDUAL_RESULTS_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["KB_Number", "Installed", "Hostname", "Domain", "IP_Address"])

            for kb in KB_LIST:
                writer.writerow([kb, "Yes" if kb in installed_updates else "No", hostname, domain, ip_address])
        
        logging.info(f"Results saved to {INDIVIDUAL_RESULTS_FILE}")
    except Exception as e:
        logging.error(f"Error writing CSV file: {e}")

if __name__ == "__main__":
    logging.info("Script started")
    installed_updates = get_installed_updates()
    check_updates(installed_updates)
    logging.info("Script completed")
    print(f"Results saved to {INDIVIDUAL_RESULTS_FILE}, aggregated file saved as {AGGREGATED_FILE}")