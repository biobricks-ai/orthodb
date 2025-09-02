import duckdb
import sys
import yaml
import logging
import os
from pathlib import Path

# Configure logging - set DEBUG level if DEBUG env var is set
log_level = logging.DEBUG if os.getenv('DEBUG') else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_column_mapping(mapping_file='stages/column_mapping.yaml'):
    with open(mapping_file) as f:
        contents = f.read()
        return yaml.safe_load(contents)

def get_file_config(mappings, filename):
    base_name = Path(filename).name
    if base_name not in mappings['file']:
        raise ValueError(f"No column mapping found for {base_name}")
    return mappings['file'][base_name]

def convert_file(input_file, output_file, file_config):
    logger.info(f"Converting file {input_file} to {output_file}")

    # Create DuckDB connection
    conn = duckdb.connect(':memory:')

    # Get columns from config
    columns = file_config['column']

    # Get nullstr if specified in format
    nullstr = None
    if 'format' in file_config and 'nullstr' in file_config['format']:
        nullstr = file_config['format']['nullstr']

    # Build the columns struct for DuckDB - all as VARCHAR initially
    columns_struct = '{'
    cast_expressions = []
    for i, col in enumerate(columns):
        if i > 0:
            columns_struct += ', '
        col_name = col['name']
        col_type = col.get('type', 'VARCHAR')
        is_nullable = col.get('nullable', False)

        # Always read as VARCHAR initially
        columns_struct += f"'{col_name}': 'VARCHAR'"

        # Build cast expression
        expr = f"\"{col_name}\""

        # If column is nullable and we have a nullstr, replace it with NULL
        if is_nullable and nullstr:
            expr = f"CASE WHEN \"{col_name}\" = '{nullstr}' THEN NULL ELSE \"{col_name}\" END"

        # Apply type casting if needed
        if col_type == 'INTEGER':
            cast_expressions.append(f"TRY_CAST({expr} AS INTEGER) AS {col_name}")
        else:
            if is_nullable and nullstr:
                cast_expressions.append(f"{expr} AS {col_name}")
            else:
                cast_expressions.append(f"\"{col_name}\"")
    columns_struct += '}'

    # Build SELECT clause with casts
    select_clause = ', '.join(cast_expressions)

    # Read CSV directly with DuckDB, specifying column names
    # DuckDB handles gzip compression automatically
    query = f"""
    COPY (
        SELECT {select_clause} FROM read_csv(
            '{input_file}',
            delim='\\t',
            header=false,
            columns={columns_struct},
            auto_detect=false
        )
    ) TO '{output_file}' (FORMAT PARQUET)
    """

    logger.debug(f"Executing query: {query}")

    conn.execute(query)
    conn.close()

    logger.info(f"Successfully converted {input_file} to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv2parquet.py <input_file> <output_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Load column mappings
    mappings = load_column_mapping()

    # Get file configuration (columns, format, etc.)
    file_config = get_file_config(mappings, input_file)

    # Convert the file
    convert_file(input_file, output_file, file_config)

if __name__ == "__main__":
    main()
