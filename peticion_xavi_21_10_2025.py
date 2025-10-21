import os
import csv
import glob

def preprocess_csv(input_file):
    # Get the directory and base name of the input file
    output_dir = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    # Create output filename by appending '_ok' before the extension
    output_file = os.path.join(output_dir, f"{base_name}_ok.csv")

    # Read the input file and process it
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            reader = csv.reader(infile, delimiter='<')
            writer = csv.writer(outfile, delimiter=';')

            for row in reader:
                # Remove any existing semicolons within fields
                cleaned_row = [field.replace(';', '') for field in row]
                writer.writerow(cleaned_row)

        print(f"Processed file saved as: {output_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {e}")

# Process all CSV files in the current directory
if __name__ == "__main__":
    # Get the directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Find all CSV files in the directory
    csv_files = glob.glob(os.path.join(current_dir, "*.csv"))

    if not csv_files:
        print("No CSV files found in the directory.")
        sys.exit(1)

    for csv_file in csv_files:
        # Skip files that already have '_ok' in the name to avoid reprocessing
        if not csv_file.endswith('_ok.csv'):
            preprocess_csv(csv_file)