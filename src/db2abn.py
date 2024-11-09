#!/usr/bin/env python3
import os
import ase

from module.abn import Abn
from module.db import Database

file_path = "/LARGE0/gr10563/kai/scripts/abn2db/test/ML_ABN_100-Ce_2L0V_TEST.db"
db = Database()
header_data, training_data = db.read_db(file_path)
