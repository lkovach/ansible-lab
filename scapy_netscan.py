# Install scapy if not already installed
!pip install scapy

# Import necessary modules
from scapy.all import IP, ICMP, sr1, DNS, DNSQR, sr, UDP
import socket
import csv
from datetime import datetime
import os

def get_hostname(ip_address):
    """Get hostname using socket's gethostbyaddr function"""
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except socket.herror:
        return "Hostname not found"
    except Exception as e:
        return f"Error: {e}"

def scan_network(network_prefix):
    """Scan the network and return devices with their hostnames"""
    devices = []
    
    # Scan a range of IPs in the given network
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        
        # Send ICMP Echo Request (ping)
        packet = IP(dst=ip)/ICMP()
        reply = sr1(packet, timeout=1, verbose=0)
        
        if reply is not None:
            # If we got a reply, the host is up
            hostname = get_hostname(ip)
            devices.append({
                'ip': ip,
                'hostname': hostname,
                'status': 'up'
            })
            print(f"Device found: {ip} ({hostname})")
    
    return devices

def export_to_csv(devices, filename=None):
    """Export the devices list to a CSV file"""
    if filename is None:
        # Generate a filename with timestamp if none provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"network_scan_{timestamp}.csv"
    
    # Ensure we have the full path
    filepath = os.path.abspath(filename)
    
    # Write to CSV file
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ['ip', 'hostname', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for device in devices:
            writer.writerow(device)
    
    return filepath

# Example usage - scan your local network
# Replace with your network prefix (usually 192.168.1 or 192.168.0)
network_prefix = "192.168.1"  # Adjust this to match your network

print(f"Scanning network {network_prefix}.0/24...")
devices = scan_network(network_prefix)

print("\nScan complete. Devices found:")
for device in devices:
    print(f"IP: {device['ip']} | Hostname: {device['hostname']} | Status: {device['status']}")

# Export results to CSV
csv_file = export_to_csv(devices)
print(f"\nResults exported to: {csv_file}")