#!/usr/bin/env python3
import os
import ase

from module.abn import Abn
from module.db import Database

file_path = "/LARGE0/gr10563/kai/scripts/abn2db/test/ML_ABN_100-Ce_2L0V_TEST.db"
db = Database()
header_data, training_data = db.read_db(file_path)

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

#file_name = os.path.basename(file_path)
file_name = "ML_ABN_TEST"
abn = Abn()
abn.write_abn(header_data, training_data, file_name)
