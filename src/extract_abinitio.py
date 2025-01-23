#!/usr/bin/env python3
import os
import ase
import argparse

from module.outcar2 import Outcar2

def main():
    parser = argparse.ArgumentParser(description="Obtain data from OUTCAR files and write to a database file.")
    # Positional arguments
    parser.add_argument("outcar_files", type=str, nargs="+",
                        help="Path to OUTCAR files to be loaded")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ML_ABN file.")

    parser.add_argument("-dt", "--data_type", type=str, default="dft",
                        help="Type of data to extract (e.g., 'dft', 'mlff', 'both').")

    # Parse the arguments
    args = parser.parse_args()

    outcar_files = []
    for outcar_file in args.outcar_files:
        outcar_files.append(os.path.abspath(outcar_file))

    oc = Outcar2()

    all_outcar_data = []
    for outcar_path in outcar_files:
        outcar_data = oc.load(outcar_path)
        all_outcar_data.extend(outcar_data)

    db_name = args.file_name
    if db_name is None:
        db_name = os.path.basename(outcar_files[0])

    if not db_name.endswith(".db"):
        db_name += ".db"

    cwd = os.getcwd()
    db_path = os.path.join(cwd, db_name)

    if os.path.exists(db_path):
        raise FileExistsError(f"{db_path} already exists.")

    oc.write2db(all_outcar_data, db_path, args.data_type)

if __name__ == "__main__":
    main()
