import os
import pandas as pd

# Define the path to the CSV files
ANSIBLE_CONTROLLER_PATH = "/opt/ansible/win_updates"
AGGREGATED_FILE = os.path.join(ANSIBLE_CONTROLLER_PATH, "aggregated_updates.csv")

def aggregate_csv_files():
    """Aggregate all CSV files in the updates directory."""
    try:
        # Find all CSV files in the directory
        csv_files = [os.path.join(ANSIBLE_CONTROLLER_PATH, file) for file in os.listdir(ANSIBLE_CONTROLLER_PATH) if file.endswith(".csv")]
        
        if not csv_files:
            print("No CSV files found for aggregation.")
            return
        
        # Read and merge CSV files
        df_list = [pd.read_csv(file) for file in csv_files]
        aggregated_df = pd.concat(df_list, ignore_index=True)
        
        # Save aggregated file
        aggregated_df.to_csv(AGGREGATED_FILE, index=False)
        print(f"Aggregated file saved as {AGGREGATED_FILE}")

    except Exception as e:
        print(f"Error aggregating CSV files: {e}")

if __name__ == "__main__":
    aggregate_csv_files()