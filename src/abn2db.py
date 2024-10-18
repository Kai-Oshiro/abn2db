#!/usr/bin/env python3

from module.abn import Abn

star_line = "**************************************************"
dash_line = "--------------------------------------------------"
eq_line   = "=================================================="

abn = Abn("/LARGE0/gr10563/kai/scripts/abn2db/test/ML_ABN_100-Ce_2L0V")
all_data = abn.read()

for key, value in all_data["header_data"].items():
    print(f"{key}: {value}")

for key, value in all_data["configurations"][0].items():
    print(f"{key}: {value}")
