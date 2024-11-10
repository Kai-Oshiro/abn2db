#!/usr/bin/env python3
import os
import argparse

from ase.db import connect

parser = argparse.ArgumentParser()
# Positional arguments
parser.add_argument("db1_file", type=str,
                    help="Path to the first ML_ABN file to be loaded")

parser.add_argument("db2_file", type=str,
                    help="Path to the second ML_ABN file to be loaded")

# Optional arguments
parser.add_argument("-fn", "--file_name", type=str, default=None,
                    help="Name of new ASE database file.")

# Parse the arguments
args = parser.parse_args()
db1_path = args.db1_file
db2_path = args.db2_file

# Define the path for the new database file
new_db_name = args.file_name
if new_db_name is None:
    db1_name = os.path.basename(db1_path).split(".")[0]
    db2_name = os.path.basename(db2_path).split(".")[0]
    new_db_name = db1_name + "-" + db2_name
new_db_name = new_db_name + ".db"

cwd = os.getcwd()
new_db_path = os.path.join(cwd, new_db_name)

# Check if the database file already exists
if os.path.exists(new_db_path):
    raise FileExistsError(f"{new_db_path} already exists.")

# Connect to the first database
db1 = connect(db1_path)
# Connect to the second database
db2 = connect(db2_path)
# Connect to the output database
new_db = connect(new_db_path, use_lock_file=False)

# Copy all rows from the first database to the output database
for row in db1.select():
    new_db.write(row.toatoms(), key_value_pairs=row.key_value_pairs, data=row.data)

# Copy all rows from the second database to the output database
for row in db2.select():
    new_db.write(row.toatoms(), key_value_pairs=row.key_value_pairs, data=row.data)

