#!/usr/bin/env python3
import os
import subprocess
import argparse

script_dir = os.path.dirname(os.path.realpath(__file__))
abn2db = os.path.join(script_dir, "abn2db.py")
db2abn = os.path.join(script_dir, "db2abn.py")
merge_db = os.path.join(script_dir, "merge_db.py")

def convert_abn_to_db(abn_file):
    db_file = abn_file
    subprocess.run([abn2db, abn_file, "-fn", db_file])
    return db_file + ".db"

def merge_db_files(db_files, new_db):
    command = [merge_db] + db_files + ["-fn", new_db]
    subprocess.run(command)

def convert_db_to_abn(db_file, new_abn):
    subprocess.run([db2abn, db_file, "-fn", new_abn])

def main():
    parser = argparse.ArgumentParser(description="Merge ML_ABN files.")
    parser.add_argument("abn_files", nargs="+",
                        help="List of ML_ABN files to merge")
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ML_ABN file")
    parser.add_argument("-c", "--cleanup", action="store_false",
                        help="Delete intermediate db files")

    args = parser.parse_args()

    merged_abn = args.file_name
    if merged_abn is None:
        merged_abn = ""
        for abn_file in args.abn_files:
            basename = os.path.basename(abn_file)
            merged_abn += basename + "-"

    db_files = [convert_abn_to_db(abn_file) for abn_file in args.abn_files]

    merged_db = merged_abn 
    merge_db_files(db_files, merged_db)

    merged_db = merged_db + ".db"
    convert_db_to_abn(merged_db, merged_abn)

    if args.cleanup:
        for db_file in db_files:
            os.remove(db_file)
        os.remove(merged_db)

if __name__ == "__main__":
    main()
