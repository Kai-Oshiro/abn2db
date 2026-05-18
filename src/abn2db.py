#!/usr/bin/env python3
import os
import argparse

from utils.abn import Abn
from utils.db import Database

def main():
    parser = argparse.ArgumentParser(description="Convert ML_ABN file to ASE database file.")
    # Positional arguments
    parser.add_argument("abn_file", type=str,
                        help="Path to ML_ABN file to be loaded.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ASE database file.")

    # Parse the arguments
    args = parser.parse_args()
    abn_path = args.abn_file
    abn_path = os.path.abspath(abn_path)

    abn = Abn()
    header_data, training_data = abn.load(abn_path)

    # Define the path for the new database file
    db_name = args.file_name
    if db_name is None:
        db_name = os.path.basename(abn_path)

    if not db_name.endswith(".db"):
        db_name = db_name + ".db"

    cwd = os.getcwd()
    db_path = os.path.join(cwd, db_name)

    # Check if the database file already exists
    if os.path.exists(db_path):
        raise FileExistsError(f"{db_path} already exists.")

    db = Database()
    db.store(header_data, training_data, db_path)

if __name__ == "__main__":
    main()
