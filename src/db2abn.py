#!/usr/bin/env python3
import os
import argparse

from utils.abn import Abn
from utils.db import Database

def main():
    parser = argparse.ArgumentParser(description="Convert ASE database file to ML_ABN file.")
    # Positional arguments
    parser.add_argument("db_file", type=str,
                        help="Path to ASE database file to be loaded.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ML_ABN file.")

    # Parse the arguments
    args = parser.parse_args()
    db_path = args.db_file
    db_path = os.path.abspath(db_path)

    db = Database()
    header_data, training_data = db.load(db_path)

    # Define the path for the new ML_ABN file
    abn_name = args.file_name
    if abn_name is None:
        abn_name = os.path.basename(db_path).split(".")[0]

    cwd = os.getcwd()
    abn_path = os.path.join(cwd, abn_name)

    # Check if the ML_ABN file already exists
    if os.path.exists(abn_path):
        raise FileExistsError(f"{abn_path} already exists.")

    abn = Abn()
    abn.store(header_data, training_data, abn_path)

if __name__ == "__main__":
    main()
