#!/usr/bin/env python3
import numpy as np
from ase.db import connect
import matplotlib.pyplot as plt

def read_ase_db(file_path):
    energies = []
    forces = []
    with connect(file_path) as db:
        for row in db.select():
            energies.append(row.energy)
            forces.append(row.forces)
    return np.array(energies), np.array(forces)

def plot_energies(energies1, energies2):
    plt.figure(figsize=(10, 5))
    plt.scatter(energies1, energies2, c="blue", label="Energy")
    plt.xlabel("Energy from DB1")
    plt.ylabel("Energy from DB2")
    plt.title("YY Plot for Energy")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.savefig("energies_plot.png")

def plot_forces(forces1, forces2):
    plt.figure(figsize=(10, 5))
    plt.scatter(forces1[:, 0], forces2[:, 0], c="red", label="Force X")
    plt.scatter(forces1[:, 1], forces2[:, 1], c="green", label="Force Y")
    plt.scatter(forces1[:, 2], forces2[:, 2], c="blue", label="Force Z")
    plt.xlabel("Force from DB1")
    plt.ylabel("Force from DB2")
    plt.title("YY Plot for Force")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.savefig("forces_plot.png")

def main():
    db_file1 = "/LARGE0/gr10563/kai/scripts/abn2db/test/job/OUTCAR_otf_1k_step.db"
    db_file2 = "/LARGE0/gr10563/kai/scripts/abn2db/test/job/results.db"

    energies1, forces1 = read_ase_db(db_file1)
    energies2, forces2 = read_ase_db(db_file2)

    plot_energies(energies1, energies2)
    plot_forces(forces1, forces2)

if __name__ == "__main__":
    main()
