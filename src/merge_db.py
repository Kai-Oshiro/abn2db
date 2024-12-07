#!/usr/bin/env python3
import os
import argparse

from ase.db import connect

parser = argparse.ArgumentParser()
# Positional arguments
parser.add_argument("db_files", type=str, nargs='+',
                    help="Paths to the ML_ABN files to be loaded")

# Optional arguments
parser.add_argument("-fn", "--file_name", type=str, default=None,
                    help="Name of new ASE database file.")

# Parse the arguments
args = parser.parse_args()
db_paths = args.db_files

# Define the path for the new database file
new_db_name = args.file_name
if new_db_name is None:
    base_names = [os.path.basename(db_path).split(".")[0] for db_path in db_paths]
    new_db_name = "-".join(base_names)

if not new_db_name.endswith(".db"):
    new_db_name = new_db_name + ".db"

cwd = os.getcwd()
new_db_path = os.path.join(cwd, new_db_name)

# Check if the database file already exists
if os.path.exists(new_db_path):
    raise FileExistsError(f"{new_db_path} already exists.")

# Connect to the output database
new_db = connect(new_db_path, use_lock_file=False)

# Copy all rows from each database to the output database
for db_path in db_paths:
    db = connect(db_path)
    for row in db.select():
        new_db.write(row.toatoms(), key_value_pairs=row.key_value_pairs, data=row.data)
