#!/usr/bin/env python3
import os

import ase

from module.abn import Abn

file_path = "/LARGE0/gr10563/kai/scripts/abn2db/test/ML_ABN_100-Ce_2L0V_TEST"
abn = Abn(file_path)
#abn.read_file()
header_data, training_data = abn.read_file()

file_name = os.path.basename(file_path)
