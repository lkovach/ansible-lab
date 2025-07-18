import pandas as pd

file_path = "/opt/ansible/win_updates/aggregated_updates.csv"

df = pd.read_csv(file_path)

df_cleaned = df.drop_duplicates()

df_cleaned.to_csv("/opt/ansible/win_updates/cleaned_updates_report.csv", index=False)

print("Duplicates removed! Saved as cleaned_updates_report.csv")
