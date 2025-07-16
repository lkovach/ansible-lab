import subprocess
import socket
import platform
import pandas as pd
import xlsxwriter
import os

# ✅ CONFIGURATION
KB_LIST = ["KB5062572", "KB5062557", "KB5062799", "KB5062560", "KB5062570"]  # July Patch Tuesday updates
OUTPUT_PATH = "C:\\Updates\\patch_report.xlsx"

# 🧠 Function: Get installed updates using PowerShell
def get_installed_updates():
    try:
        result = subprocess.run(["powershell", "-Command", "Get-HotFix | Select-Object -ExpandProperty HotFixID"],
                                capture_output=True, text=True, check=True)
        updates = result.stdout.strip().splitlines()
        return set(u.strip() for u in updates if u.strip())
    except subprocess.CalledProcessError as e:
        print("Failed to retrieve hotfixes:", e)
        return set()

# 🧠 Function: Get system metadata
def get_system_info():
    hostname = socket.gethostname()
    try:
        domain_result = subprocess.run(["powershell", "-Command", "(Get-WmiObject Win32_ComputerSystem).Domain"],
                                       capture_output=True, text=True, check=True)
        domain = domain_result.stdout.strip() or "Unknown"
    except:
        domain = "Unknown"
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Unknown"
    os_version = platform.system() + " " + platform.release()
    return hostname, domain, ip_address, os_version

# 🧠 Function: Build DataFrame
def build_kb_dataframe(installed_updates):
    hostname, domain, ip_address, os_version = get_system_info()
    records = []
    for kb in KB_LIST:
        records.append({
            "KB_Article": kb,
            "Installed": "Yes" if kb in installed_updates else "No",
            "Hostname": hostname,
            "Domain": domain,
            "IP_Address": ip_address,
            "OS_Version": os_version
        })
    return pd.DataFrame(records)

# 🧠 Function: Write color-coded Excel report
def write_xlsx_report(df, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Update Status")
        workbook  = writer.book
        worksheet = writer.sheets["Update Status"]

        # Define conditional formats
        red_fmt   = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        green_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})

        installed_col = df.columns.get_loc("Installed")  # zero-based index
        worksheet.conditional_format(1, installed_col, len(df), installed_col, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'No',
            'format': red_fmt
        })
        worksheet.conditional_format(1, installed_col, len(df), installed_col, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Yes',
            'format': green_fmt
        })

    print(f"✅ Excel report generated: {output_path}")

# 🧪 MAIN
if __name__ == "__main__":
    installed_updates = get_installed_updates()
    df = build_kb_dataframe(installed_updates)
    write_xlsx_report(df, OUTPUT_PATH)
    import sys
    sys.exit(0)  # Exit with success code