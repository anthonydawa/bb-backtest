import os
import csv
import json

def create_json_files(csv_file_path, output_folder):
    try:
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        with open(csv_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                symbol = row['symbol']
                json_data = {key: row[key] for key in row if key != 'symbol'}

                # Create a JSON file for each row
                json_file_path = os.path.join(output_folder, f'{symbol}.json')
                with open(json_file_path, 'w') as json_file:
                    json.dump(json_data, json_file, indent=2)

        print(f"JSON files created and saved in '{output_folder}'")

    except FileNotFoundError:
        print(f"The CSV file '{csv_file_path}' does not exist.")

def read_csv_to_array(csv_file_path):
    try:
        with open(csv_file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            data = [row for row in reader]

        return data

    except FileNotFoundError:
        print(f"The CSV file '{csv_file_path}' does not exist.")
        return []

def process_and_save_files(folder_path, output_csv_file):
    try:
        # Get the list of files in the folder
        files = os.listdir(folder_path)

        # Filter out subdirectories, keep only files
        files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]
        adtl_data = []

        for f in files:
            file_location = f'best_data/{f}'
            csv_data = read_csv_to_array(file_location)
            removed_header = csv_data[1:]
            combined_array = [item for sublist in removed_header for item in sublist]
            adtl_data.append(combined_array)

        print("Adtl_data:")
        print(adtl_data)

        # Split the string into an array using the hyphen as a separator
        final = []
        for file in files:
            x = file.split('-')
            final.append([x[0], x[-2], x[-3]])

        print("Final array:")
        print(final)

        # Combine adtl_data and final arrays at each respective index
        combined_data = [a + f for a, f in zip(adtl_data, final)]

        # Save the combined data into a CSV file
        with open(output_csv_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            # Write header
            # writer.writerow(['AdtlColumn1', 'AdtlColumn2', 'AdtlColumn3', 'FirstIndex', 'LastTwoIndices', 'SecondLastIndex'])
            # Write data
            writer.writerows(combined_data)

        print(f"Combined data saved to {output_csv_file}")

    except FileNotFoundError:
        print(f"The folder '{folder_path}' does not exist.")

def remove_columns(input_csv_file, output_csv_file, columns_to_remove):
    try:
        with open(input_csv_file, 'r') as infile, open(output_csv_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                # Exclude specified columns (1st, 5th, and 9th)
                filtered_row = [value for index, value in enumerate(row, 1) if index not in columns_to_remove]
                writer.writerow(filtered_row)

        print(f"Columns {columns_to_remove} removed and saved to {output_csv_file}")

    except FileNotFoundError:
        print(f"The CSV file '{input_csv_file}' does not exist.")

def add_header_to_csv(file_path, header_values):
    try:
        # Read existing data from the CSV file
        with open(file_path, 'r') as infile:
            reader = csv.reader(infile)
            data = list(reader)

        # Add the new header row to the data
        data.insert(0, header_values)

        # Write the updated data back to the CSV file
        with open(file_path, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(data)

        print(f"Header row added to {file_path}")

    except FileNotFoundError:
        print(f"The CSV file '{file_path}' does not exist.")


start_date = "1 OCT, 2023"
end_date = "1 Nov, 2023"

# Example usage:
folder_path = 'best_data'
output_csv_file = 'output_file.csv'
process_and_save_files(folder_path, output_csv_file)
# Example usage:
input_csv_file = 'output_file.csv'  # Replace with the actual path to your input CSV file
output_csv_file = 'final_output.csv'  # Replace with the desired path for the output CSV file
columns_to_remove = [1, 5, 9,13,14,15,16,17,18,19,20,21,22,23,24]

remove_columns(input_csv_file, output_csv_file, columns_to_remove)


# Example usage:
file_path = 'final_output.csv'  # Replace with the actual path to your CSV file
header_values = ['sl','cc','pnl','sl_long','cc_long','pnl_long','sl_short','cc_short','pnl_short','symbol','bb_window','bb_std_dev']  # Replace with your desired header values

add_header_to_csv(file_path, header_values)


# Example usage:
csv_file_path = 'final_output.csv'  # Replace with the actual path to your CSV file
output_folder = 'state'  # Replace with the desired path for the output folder

create_json_files(csv_file_path, output_folder)
