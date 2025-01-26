#!/usr/bin/env python3
import os
import argparse

from module.support import convert_abn_to_db, shuffle_db_file, convert_db_to_abn

def main():
    parser = argparse.ArgumentParser(description="Shuffle data in an ML_ABN file.")
    # Positional arguments
    parser.add_argument("abn_file", type=str,
                        help="Path to ML_ABN file to shuffle.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new shuffled ML_ABN file")

    parser.add_argument("-s", "--seed", type=int, default=1,
                        help="Seed for the random number generator")

    parser.add_argument("-sd", "--save_db", action="store_true",
                        help="Save intermediate db files")

    args = parser.parse_args()

    abn_path = args.abn_file
    abn_path = os.path.abspath(abn_path)

    shuffled_abn = args.file_name
    if shuffled_abn is None:
        shuffled_abn = os.path.basename(abn_path).split(".")[0] + "_shuffled"

    db_file = convert_abn_to_db(abn_path)
    shuffled_db = shuffled_abn + ".db"
    index_file = shuffled_abn + "_index.txt"

    shuffle_db_file(db_file, shuffled_db, index_file, args.seed)
    convert_db_to_abn(shuffled_db, shuffled_abn)

    # Delete intermediate db files
    if not args.save_db:
        os.remove(db_file)
        os.remove(shuffled_db)

if __name__ == "__main__":
    main()
