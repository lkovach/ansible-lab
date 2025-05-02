import subprocess
import csv
import os
import socket
import pandas as pd
import logging

# Configure logging
logging.basicConfig(filename="update_checker.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

KB_LIST = ["KB5055661", "KB5055526", "KB5055519", "KB5055521"]  # Replace with actual KB numbers
ANSIBLE_CONTROLLER_PATH = "/opt/ansible/updates"  # Adjust to the correct directory on the Ansible controller
INDIVIDUAL_RESULTS_FILE = os.path.join(ANSIBLE_CONTROLLER_PATH, f"{socket.gethostname()}_updates.csv")
AGGREGATED_FILE = os.path.join(ANSIBLE_CONTROLLER_PATH, "aggregated_updates.csv")

def get_installed_updates():
    """Retrieve installed updates using WMIC."""
    try:
        result = subprocess.run(["wmic", "qfe", "get", "HotFixID"], capture_output=True, text=True, check=True)
        updates = result.stdout.split("\n")[1:]  # Skip header
        installed_updates = {line.strip() for line in updates if line.strip()}
        logging.info(f"Retrieved installed updates: {installed_updates}")
        return installed_updates
    except subprocess.CalledProcessError as e:
        logging.error(f"Error retrieving installed updates: {e}")
        return set()

def get_system_info():
    """Retrieve hostname, domain name, and IP address."""
    try:
        hostname = socket.gethostname()
        domain = subprocess.run(["wmic", "computersystem", "get", "Domain"], capture_output=True, text=True, check=True).stdout.split("\n")[1].strip()
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

def aggregate_csv_files():
    """Aggregate all CSV files on the Ansible controller."""
    try:
        csv_files = [os.path.join(ANSIBLE_CONTROLLER_PATH, file) for file in os.listdir(ANSIBLE_CONTROLLER_PATH) if file.endswith(".csv")]
        if not csv_files:
            logging.warning("No CSV files found for aggregation.")
            return
        
        df_list = [pd.read_csv(file) for file in csv_files]
        aggregated_df = pd.concat(df_list, ignore_index=True)
        aggregated_df.to_csv(AGGREGATED_FILE, index=False)

        logging.info(f"Aggregated file saved as {AGGREGATED_FILE}")
    except Exception as e:
        logging.error(f"Error aggregating CSV files: {e}")

if __name__ == "__main__":
    logging.info("Script started")
    installed_updates = get_installed_updates()
    check_updates(installed_updates)
    aggregate_csv_files()
    logging.info("Script completed")
    print(f"Results saved to {INDIVIDUAL_RESULTS_FILE}, aggregated file saved as {AGGREGATED_FILE}")