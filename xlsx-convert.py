import pandas as pd
import argparse

def convert_csv_to_xlsx(input_csv, output_xlsx):
    try:
        df = pd.read_csv(input_csv)
        df.to_excel(output_xlsx, index=False)
        print(f"Conversion completed. CSV file '{input_csv}' has been converted to XLSX file '{output_xlsx}'.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert CSV to XLSX')
    parser.add_argument('input_csv', help='Input CSV file')
    parser.add_argument('output_xlsx', help='Output XLSX file')
    
    args = parser.parse_args()
    convert_csv_to_xlsx(args.input_csv, args.output_xlsx)
