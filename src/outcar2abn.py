#!/usr/bin/env python3
import os
import ase
import argparse

from module.outcar import Outcar
from module.abn import Abn

def parse_slice(slice_str):
    """Parse a slice string like '1:3:2' or '-3:' into a slice object."""
    parts = slice_str.split(':')
    start = int(parts[0]) if parts[0] else None
    end = int(parts[1]) if len(parts) > 1 and parts[1] else None
    step = int(parts[2]) if len(parts) > 2 and parts[2] else None
    return slice(start, end, step)

def get_indices(raw_indices):
    """Parse raw indices to a list of integers."""
    indices = []
    for index in raw_indices:
        if ":" in index:
            indices.extend(parse_slice(index))
        else:
            indices.append(int(index.strip()))
    return indices

def main():
    parser = argparse.ArgumentParser()
    # Positional arguments
    parser.add_argument("outcar_files", type=str, nargs="+",
                        help="Path of OUTCAR file to be loaded")

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

    # Parse the arguments
    args = parser.parse_args()

    outcar_files = []
    for outcar_file in args.outcar_files:
        outcar_files.append(os.path.abspath(outcar_file))

    if args.ionic_step:
        is_indices = get_indices(args.ionic_step)

    oc = Outcar()

    all_outcar_data = []
    for outcar_path in outcar_files:
        outcar_data = oc.read_outcar(outcar_path)

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
        raw_basis = get_indices(args.basis) # list of atom indices
    else:
        raw_basis = None

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
    abn.write_abn(header_data, training_data, abn_path)

if __name__ == "__main__":
    main()
