#!/usr/bin/env python3
import os
import ase
import argparse

from module.outcar import Outcar
from module.db import Database

parser = argparse.ArgumentParser()
# Positional arguments
parser.add_argument("outcar_file", type=str,
                    help="Path of OUTCAR file to be loaded")

# Optional arguments
parser.add_argument("-fn", "--file_name", type=str, default=None,
                    help="Name of new ASE database file.")

# Parse the arguments
args = parser.parse_args()
outcar_path = args.outcar_file
outcar_path = os.path.abspath(outcar_path)
#print(f"outcar_path: {outcar_path}")

oc = Outcar()
oc.read_outcar(outcar_path)
