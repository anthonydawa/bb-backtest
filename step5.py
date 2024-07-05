import os
import csv
import json
from operator import itemgetter

def create_ranking_csv(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    # Get all JSON files in the folder
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    # List to store file data
    file_data = []

    # Read data from each JSON file
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)

        with open(file_path, 'r') as f:
            data = json.load(f)
            file_data.append(data)

    # Sort files based on 'pnl' in descending order
    sorted_files = sorted(file_data, key=itemgetter('pnl'), reverse=True)

    # Create CSV file with rankings
    csv_filename = 'results/period_pnl_ranking_15.csv'
    csv_filepath = os.path.join(folder_path, csv_filename)

    with open(csv_filepath, 'w', newline='') as csvfile:
        fieldnames = sorted_files[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()

        # Write data
        for idx, file in enumerate(sorted_files, start=1):
            writer.writerow(file)
            print(f"Rank {idx}: {file['symbol']} - PNL: {file['pnl']}")

    print(f"Ranking CSV file saved to {csv_filepath}")

# Example usage:
folder_path = 'backtest_period'  # Change to the actual folder path
create_ranking_csv(folder_path)
