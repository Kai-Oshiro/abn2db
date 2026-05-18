#!/usr/bin/env python3
import os
import argparse

from utils.outcar import Outcar
from utils.db import Database
from utils.support import get_indices

def main():
    parser = argparse.ArgumentParser(description="Construct ASE database file from data in OUTCAR files.")
    # Positional arguments
    parser.add_argument("outcar_files", type=str, nargs="+",
                        help="Path to OUTCAR files to be loaded.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ASE database file.")

    parser.add_argument("-is", "--ionic_step", type=str, nargs="+", default=None,
                        help="Ionic step you want to get (e.g., '1:3', '1 3 5' or '-1').\n\
                        To specify a range with negative value,\
                        enclose the range in quotation marks and put leading spaces,\
                        e.g., \' -3:-1\'.")

    parser.add_argument("-b", "--basis", type=str, nargs="+", default=None,
                        help="Atom indices for basis set of training data (e.g., '1:3' or '1 3 5').")

    parser.add_argument("-m", "--method", type=str, default="both",
                        help="Methods for calculating data to be extracted from OUTCAR. (e.g., 'dft', 'mlff', 'both').")

    # Parse the arguments
    args = parser.parse_args()

    outcar_files = []
    for outcar_file in args.outcar_files:
        outcar_files.append(os.path.abspath(outcar_file))

    is_indices = None
    if args.ionic_step:
        is_indices = get_indices(args.ionic_step)

    oc = Outcar()

    all_outcar_data = []
    for outcar_path in outcar_files:
        outcar_data = oc.load(outcar_path)
        outcar_data = oc.filter_data(outcar_data, args.method)

        if is_indices:
            results = []
            for index in is_indices:
                if isinstance(index, slice):
                    results.extend(outcar_data[index])
                else:
                    results.append(outcar_data[index])
        else:
            results = outcar_data

        all_outcar_data.extend(results)

    if args.basis:
        basis_indices = get_indices(args.basis) # list of atom indices or slices
        raw_basis = []
        for index in basis_indices:
            if isinstance(index, slice):
                raw_basis.extend(list(range(index.start, index.stop, index.step if index.step else 1)))
            else:
                raw_basis.append(index)
    else:
        raw_basis = None

    # Convert OUTCAR data into the format required for writing ML_ABN file
    header_data, training_data = oc.parse_data(all_outcar_data, raw_basis)

    # Define the path for the new database file
    db_name = args.file_name
    if db_name is None:
        db_name = os.path.basename(outcar_files[0])

    if not db_name.endswith(".db"):
        db_name = db_name + ".db"

    cwd = os.getcwd()
    db_path = os.path.join(cwd, db_name)

    # Check if the database file already exists
    if os.path.exists(db_path):
        raise FileExistsError(f"{db_path} already exists.")

    # Write the database
    db = Database()
    db.store(header_data, training_data, db_path)

if __name__ == "__main__":
    main()
