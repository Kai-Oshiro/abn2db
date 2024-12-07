#!/usr/bin/env python3
import argparse
import random
from ase.db import connect

def shuffle_db(input_file, output_file, index_file, seed=None):
    db = connect(input_file)
    rows = list(db.select())
    original_indices = list(range(len(rows)))
    
    if seed is not None:
        random.seed(seed)
    
    shuffled_indices = original_indices[:]
    random.shuffle(shuffled_indices)
    
    new_db = connect(output_file, use_lock_file=False)
    for i in shuffled_indices:
        row = rows[i]
        new_db.write(row.toatoms(), key_value_pairs=row.key_value_pairs, data=row.data)
    
    with open(index_file, 'w') as f:
        for original, shuffled in sorted(zip(original_indices, shuffled_indices), key=lambda x: x[1]):
            f.write(f"{shuffled + 1} => {original + 1}\n")

def main():
    parser = argparse.ArgumentParser(description='Shuffle rows in an ASE database file.')
    parser.add_argument('input_file', type=str,
                        help='The input ASE database file.')
    parser.add_argument('-fn', '--file_name', type=str, default=None,
                        help='The new ASE database file with shuffled rows.')
    parser.add_argument('-if', '--index_file', type=str, default=None,
                        help='The file to save original and shuffled indices.')
    parser.add_argument('-s', '--seed', type=int, default=1,
                        help='The seed for the random number generator.')
    
    args = parser.parse_args()

    if args.file_name is None:
        args.file_name = args.input_file.split(".")[0] + "_shuffled.db"

    if not args.file_name.endswith(".db"):
        args.file_name += ".db"

    if args.index_file is None:
        args.index_file = args.input_file.split(".")[0] + "_shuffled.txt"

    shuffle_db(args.input_file, args.file_name, args.index_file, args.seed)

if __name__ == '__main__':
    main()