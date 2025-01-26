#!/usr/bin/env python3
import os
import argparse

from module.support import convert_abn_to_db, merge_db_files, convert_db_to_abn

def main():
    parser = argparse.ArgumentParser(description="Merge ML_ABN files.")
    # Positional arguments
    parser.add_argument("abn_files", type=str, nargs="+",
                        help="Path to ML_ABN files to merge.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ML_ABN file.")

    parser.add_argument("-sd", "--save_db", action="store_true",
                        help="Save intermediate db files.")

    args = parser.parse_args()

    merged_abn = args.file_name
    if merged_abn is None:
        merged_abn = [os.path.basename(abn_file) for abn_file in args.abn_files]
        merged_abn = "-".join(merged_abn)

    db_files = [convert_abn_to_db(abn_file) for abn_file in args.abn_files]

    merged_db = merged_abn + ".db"
    merge_db_files(db_files, merged_db)

    convert_db_to_abn(merged_db, merged_abn)

    # Delete intermediate db files
    if not args.save_db:
        for db_file in db_files:
            os.remove(db_file)
        os.remove(merged_db)

if __name__ == "__main__":
    main()
