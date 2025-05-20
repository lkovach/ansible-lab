import subprocess
import os
import socket
import pandas as pd
import logging
import platform
import openpyxl

# Configure logging
logging.basicConfig(
    filename="update_checker.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# List of KB articles (updated 5-14-25 for May Patch Tuesday)
KB_LIST = ["KB5058524", "KB5058385", "KB5058383", "KB5058392"]

ANSIBLE_CONTROLLER_PATH = "/opt/ansible/win_updates"
# Use Excel files instead of CSV files
INDIVIDUAL_RESULTS_FILE = os.path.join(ANSIBLE_CONTROLLER_PATH, f"{socket.gethostname()}_updates.xlsx")
AGGREGATED_FILE = os.path.join(ANSIBLE_CONTROLLER_PATH, "aggregated_updates.xlsx")

def get_installed_updates():
    """Retrieve installed updates using PowerShell's Get-HotFix."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-HotFix | Select-Object -ExpandProperty HotFixID"],
            capture_output=True, text=True, check=True
        )
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
        domain_result = subprocess.run(
            ["powershell", "-Command", "(Get-WmiObject Win32_ComputerSystem).Domain"],
            capture_output=True, text=True, check=True
        )
        domain = domain_result.stdout.strip() if domain_result.stdout.strip() else "Unknown"
        ip_address = socket.gethostbyname(hostname)
        os_version = platform.system() + " " + platform.release()  # Get OS details
        logging.info(f"DEBUG - Hostname: {hostname}, Domain: {domain}, IP Address: {ip_address}, OS: {os_version}")
        return hostname, domain, ip_address, os_version
    except Exception as e:
        logging.error(f"Error retrieving system info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown"

def check_updates(installed_updates):
    """Compare installed updates against KB list and save data to Excel files on the Ansible controller."""
    try:
        os.makedirs(ANSIBLE_CONTROLLER_PATH, exist_ok=True)

        # Remove previous individual file if it exists
        if os.path.exists(INDIVIDUAL_RESULTS_FILE):
            os.remove(INDIVIDUAL_RESULTS_FILE)

        hostname, domain, ip_address, os_version = get_system_info()

        rows = []
        for kb in KB_LIST:
            row = {
                "KB_Number": kb,
                "Installed": "Yes" if kb in installed_updates else "No",
                "Hostname": hostname,
                "Domain": domain,
                "IP_Address": ip_address,
                "Operating System": os_version
            }
            logging.info(f"Collecting row: {row}")
            print(f"DEBUG - Collecting row: {row}")
            rows.append(row)

        # Write individual results to an Excel file (single sheet)
        df_individual = pd.DataFrame(rows)
        df_individual.to_excel(INDIVIDUAL_RESULTS_FILE, index=False)
        logging.info(f"Individual results saved to {INDIVIDUAL_RESULTS_FILE}")
        print(f"Individual results saved to {INDIVIDUAL_RESULTS_FILE}")

        # Prepare the aggregated Excel file with separate sheets based on OS and Installed status
        sheets_data = {}
        for row in rows:
            # Create a sheet name combining OS and Installed status
            sheet_name = f"{row['Operating System']}_{row['Installed']}"
            # Replace spaces with underscores and remove any characters that might not be allowed
            sheet_name = sheet_name.replace(" ", "_")
            if sheet_name not in sheets_data:
                sheets_data[sheet_name] = []
            sheets_data[sheet_name].append(row)

        # Write the aggregated results to an Excel workbook with separate sheets
        with pd.ExcelWriter(AGGREGATED_FILE, engine='xlsxwriter') as writer:
            for sheet, data in sheets_data.items():
                df_sheet = pd.DataFrame(data)
                df_sheet.to_excel(writer, sheet_name=sheet, index=False)
        logging.info(f"Aggregated results saved to {AGGREGATED_FILE}")
        print(f"Aggregated results saved to {AGGREGATED_FILE}")
        
    except Exception as e:
        logging.error(f"Error writing Excel file: {e}")
        print(f"ERROR: {e}")

if __name__ == "__main__":
    logging.info("Script started")
    installed_updates = get_installed_updates()
    check_updates(installed_updates)
    logging.info("Script completed")
    print(f"Results saved to {INDIVIDUAL_RESULTS_FILE}, aggregated file saved as {AGGREGATED_FILE}")