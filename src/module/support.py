import os
import subprocess
import random

from ase.db import connect

def get_parent_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

### for merge_abn.py and shuffle_abn.py ###
def convert_abn_to_db(abn_file):
    parent_dir = get_parent_dir()
    abn2db = os.path.join(parent_dir, "abn2db.py")
    db_file = abn_file + ".db"
    subprocess.run([abn2db, abn_file, "-fn", db_file], check=True)
    return db_file

def convert_db_to_abn(db_file, new_abn):
    parent_dir = get_parent_dir()
    db2abn = os.path.join(parent_dir, "db2abn.py")
    subprocess.run([db2abn, db_file, "-fn", new_abn], check=True)

### for merge_abn.py ###
def merge_db_files(db_files, new_db):
    parent_dir = get_parent_dir()
    merge_db = os.path.join(parent_dir, "merge_db.py")
    command = [merge_db] + db_files + ["-fn", new_db]
    subprocess.run(command, check=True)

### for outcar2abn.py ###
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
            indices.append(parse_slice(index))
        else:
            indices.append(int(index.strip()))
    return indices

### for shuffle_abn.py ###
def shuffle_db_file(db_file, shuffled_db, index_file, seed):
    parent_dir = get_parent_dir()
    shuffle_db = os.path.join(parent_dir, "shuffle_db.py")
    command = [shuffle_db, db_file, "-fn", shuffled_db, "-if", index_file, "-s", str(seed)]
    subprocess.run(command)

### for shuffle_db.py ###
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

### for excute_vasp.py ###
def delete_vasp_io(work_dir):
    file_list = [
        "CHG", "CHGCAR", "CONTCAR", "DOSCAR",
        "EIGENVAL", "IBZKPT", "ML_LOGFILE", "OSZICAR",
        "OUTCAR", "PCDAT", "POSCAR", "REPORT",
        "vasprun.xml", "WAVECAR", "XDATCAR"
    ]

    for file in file_list:
        file_path = os.path.join(work_dir, file)
        if os.path.exists(file_path):
            os.remove(file_path)
