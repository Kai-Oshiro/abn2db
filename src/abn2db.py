#!/usr/bin/env python3
import os
import ase
import argparse

from module.abn import Abn
from module.db import Database

parser = argparse.ArgumentParser()
# Positional arguments
parser.add_argument("abn_file", type=str,
                    help="Path of ML_ABN file to be loaded")

# Optional arguments
parser.add_argument("-fn", "--file_name", type=str, default=None,
                    help="Name of new ASE database file.")

# Parse the arguments
args = parser.parse_args()
abn_path = args.abn_file
abn_path = os.path.abspath(abn_path)
#print(f"db_path: {abn_path}")

abn = Abn()
header_data, training_data = abn.read_abn(abn_path)

"""
#Check data
print("### Header data ###")
for key, value in header_data.items():
    print(f"{key}: {value}")
print("\n### Training data ###")
for key, value in training_data[0].items():
    if isinstance(value, list):
        first_value = value[0]
        print(f"{key}: {[first_value]}")
    else:
        print(f"{key}: {value}")
print()
"""

# Define the path for the new database file
db_name = args.file_name
if db_name is None:
    db_name = os.path.basename(abn_path).split(".")[0]

if not db_name.endswith(".db"):
    db_name = db_name + ".db"

cwd = os.getcwd()
db_path = os.path.join(cwd, db_name)

# Check if the database file already exists
if os.path.exists(db_path):
    raise FileExistsError(f"{db_path} already exists.")

db = Database()
db.write_db(header_data, training_data, db_path)
