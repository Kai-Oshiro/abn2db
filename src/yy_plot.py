#!/usr/bin/env python3
import argparse

from module.plot_support import read_ase_db, plot_energies, plot_forces

def main():
    parser = argparse.ArgumentParser(description="Plot energies and forces from two ASE database files.")
    # Positional arguments
    parser.add_argument("dft_db_file", type=str,
                        help="Path to ASE database file.")

    parser.add_argument("mlff_db_file", type=str,
                        help="Path to ASE database file.")

    # Optional arguments
    parser.add_argument("-p", "--plot", type=str, default="both",
                        help="Type of data to plot (e.g., 'energy', 'forces'. 'both').")

    parser.add_argument("-mm", "--max_min", type=float, nargs=2, default=None,
                        help="Maximum and minimum values for plot.")

    parser.add_argument("-i", "--interval", type=float, default=25,
                        help="Scale interval for plots.")

    parser.add_argument("-c", "--color", type=str, nargs="+", default="#1f77b4",
                        help="Color for plot lines.")

    parser.add_argument("-fs", "--fontsize", type=int, default=18,
                        help="Font size for the plot.")

    parser.add_argument("-ls", "--labelsize", type=int, default=14,
                        help="Label size for the plot.")

    parser.add_argument("-sh", "--show", action="store_true", default=False,
                        help="Show the plot.")

    parser.add_argument("-s", "--save", action="store_true", default=True,
                        help="Save the plot.")

    parser.add_argument("-fn", "--fig_name", type=str, nargs="+", default="comparison.png",
                        help="Name of output figure files.")

    args = parser.parse_args()
    db_file1 = args.dft_db_file
    db_file2 = args.mlff_db_file

    energies1, forces1, natoms1 = read_ase_db(db_file1)
    energies2, forces2, natoms2 = read_ase_db(db_file2)

    max_min_list = args.max_min
    interval = args.interval
    color = args.color
    fontsize = args.fontsize
    labelsize = args.labelsize
    show = args.show
    save = args.save
    fig_name = args.fig_name

    plot_flag = args.plot.lower()
    if plot_flag.startswith("e"):
        plot_energies(
            energies1, energies2, natoms1, natoms2,
            max_min_list, interval, color,
            fontsize, labelsize, show, save,
            fig_name
        )

    elif plot_flag.startswith("f"):
        plot_forces(
            forces1, forces2, natoms1, natoms2,
            max_min_list, interval, color,
            fontsize, labelsize, show, save,
            fig_name
        )

    elif plot_flag.startswith("b"):
        plot_energies(
            energies1, energies2, natoms1, natoms2,
            [-240, -270], 10, "#1f77b4",
            fontsize, labelsize, show, save,
            "energies_comparison.png"
        )

        plot_forces(
            forces1, forces2, natoms1, natoms2,
            [20, -20], 10, ["#1f77b4", "#ff7f0e", "#2ca02c"],
            fontsize, labelsize, show, save,
            "forces_comparison.png"
        )

if __name__ == "__main__":
    main()
