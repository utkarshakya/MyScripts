import json
import os
import csv
import argparse
import sys
from pathlib import Path
from typing import Optional

# --- Shared Helpers ---
def ok(msg: str):    print(f"\033[92m[OK]\033[0m  {msg}")
def info(msg: str):  print(f"\033[94m[..]\033[0m  {msg}")
def err(msg: str):   print(f"\033[91m[ERR]\033[0m {msg}")

# --- CSV to JSON Logic ---
def convert_csv_to_json(csv_path: str, output_path: Optional[str] = None):
    try:
        if not output_path:
            output_path = str(Path(csv_path).with_suffix('.json'))
        
        data = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        ok(f"Converted {csv_path} to {output_path} ({len(data)} records)")
    except Exception as e:
        err(f"CSV conversion failed: {e}")

# --- Pagination Logic ---
def paginate_json(input_file: str, prefix: str, page_size: int = 10000):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data if isinstance(data, list) else [] # Basic support for top-level arrays
        if not records:
            err("Toolbox pagination currently supports top-level JSON arrays only.")
            return

        total = len(records)
        folder = f"{prefix}_pages"
        os.makedirs(folder, exist_ok=True)

        for i in range(0, total, page_size):
            page_num = (i // page_size) + 1
            chunk = records[i : i + page_size]
            file_name = os.path.join(folder, f"{prefix}_page{page_num}.json")
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2, ensure_ascii=False)
        
        ok(f"Split {total} records into {(total + page_size - 1) // page_size} pages in {folder}/")
    except Exception as e:
        err(f"Pagination failed: {e}")

# --- CLI ---
def main():
    parser = argparse.ArgumentParser(description="Data Toolbox - CSV and JSON Utilities")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # CSV to JSON
    csv_parser = subparsers.add_parser("csv2json", help="Convert CSV to JSON")
    csv_parser.add_argument("input", help="Input CSV file")
    csv_parser.add_argument("-o", "--output", help="Output JSON file")

    # Paginate
    pag_parser = subparsers.add_parser("paginate", help="Split JSON array into pages")
    pag_parser.add_argument("input", help="Input JSON file")
    pag_parser.add_argument("prefix", help="Prefix for output files")
    pag_parser.add_argument("-s", "--size", type=int, default=10000, help="Records per page")

    args = parser.parse_args()

    if args.command == "csv2json":
        convert_csv_to_json(args.input, args.output)
    elif args.command == "paginate":
        paginate_json(args.input, args.prefix, args.size)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
