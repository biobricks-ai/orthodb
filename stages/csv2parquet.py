import pandas as pd
import sys
import yaml
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

def load_column_mapping(mapping_file='stages/column_mappings.yaml'):
    with open(mapping_file) as f:
        contents = f.read()
        return yaml.safe_load(contents)

def get_columns_for_file(mappings, filename):
    base_name = Path(filename).name
    if base_name not in mappings['files']:
        raise ValueError(f"No column mapping found for {base_name}")
    return [col['name'] for col in mappings['files'][base_name]['columns']]

def convert_file(input_file, output_file, column_names):
    print(f"csv2parquet: Converting file {input_file}")

    # Read tab-separated gzipped file
    df = pd.read_csv(input_file,
                     compression='gzip' if input_file.endswith('.gz') else None,
                     sep='\t',
                     names=column_names)

    # Create table with column metadata
    table = pa.Table.from_pandas(df)

    # Write parquet with metadata
    pq.write_table(table,
                   output_file,
                   version='2.6',
                   compression='snappy')

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv2parquet.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Load column mappings
    mappings = load_column_mapping()

    # Get columns for this file
    columns = get_columns_for_file(mappings, input_file)

    # Convert the file
    convert_file(input_file, output_file, columns)

if __name__ == "__main__":
    main()
