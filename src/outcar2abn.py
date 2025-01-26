#!/usr/bin/env python3
import os
import argparse

from module.outcar import Outcar
from module.abn import Abn
from module.support import get_indices

def main():
    parser = argparse.ArgumentParser(description="Construct ML_ABN file from data in OUTCAR files.")
    # Positional arguments
    parser.add_argument("outcar_files", type=str, nargs="+",
                        help="Path to OUTCAR files to be loaded.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ML_ABN file.")

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
    abn_name = args.file_name
    if abn_name is None:
        abn_name = "ML_ABN_"
        abn_name += os.path.basename(outcar_files[0])

    cwd = os.getcwd()
    abn_path = os.path.join(cwd, abn_name)

    # Check if the database file already exists
    if os.path.exists(abn_path):
        raise FileExistsError(f"{abn_path} already exists.")

    # Write ML_ABN file
    abn = Abn()
    abn.store(header_data, training_data, abn_path)

if __name__ == "__main__":
    main()
