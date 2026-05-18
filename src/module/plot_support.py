import numpy as np
from ase.db import connect
import matplotlib.pyplot as plt

def read_ase_db(file_path):
    energies = []
    forces = []
    natoms = []
    with connect(file_path) as db:
        for row in db.select():
            energies.append(row.energy)
            forces.append(row.forces)
            natoms.append(row.natoms)
    return np.array(energies), np.array(forces), np.array(natoms)

def plot_energies(
        energies1, energies2, natoms1, natoms2, 
        max_min_list=None, interval=25, color="#1f77b4",
        fontsize=18, labelsize=14, show=False, save=False,
        fig_name="./energies_comparison.png"
    ):

    if max_min_list:
        max_value, min_value = max_min_list
    else:
        max_1, min_1 = np.max(energies1), np.min(energies1)
        max_2, min_2 = np.max(energies2), np.min(energies2)

        max_value = max(max_1, max_2)
        min_value = min(min_1, min_2)
        max_value = (np.ceil(max_value / interval) * interval)
        min_value = (np.floor(min_value / interval) * interval)

    rmse = np.sqrt(np.mean((energies1 - energies2) ** 2))

    energy_per_atom1 = energies1 / natoms1
    energy_per_atom2 = energies2 / natoms2
    rmse_per_atom = np.sqrt(np.mean((energy_per_atom1 - energy_per_atom2) ** 2))

    # Define the figure
    fig, ax = plt.subplots(dpi=200)

    ax.plot(
        [min_value, max_value], 
        [min_value, max_value], 
        "k--", linewidth=1.5, zorder=2
    )

    # Plot the data
    for x, y in zip(energies1, energies2):
        ax.plot(
            [x, x], [x, y], 
            color="grey", linestyle=":", 
            linewidth=1.5, zorder=1
        )

        ax.scatter(x, y, zorder=4, color=color, alpha=0.5)

    # Add title and labels
    ax.set_xlabel("DFT results (eV)", fontsize=fontsize)
    ax.set_ylabel("MLFF results (eV)", fontsize=fontsize)

    ax.text(
        0.95, 0.13, f"RMSE: {rmse:.2f} eV",
        horizontalalignment="right",
        transform=ax.transAxes, fontsize=labelsize
    )

    ax.text(
        0.95, 0.05, f"RMSE/atom: {rmse_per_atom*1000:.1f} meV/atom",
        horizontalalignment="right",
        transform=ax.transAxes, fontsize=labelsize
    )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim([min_value, max_value])
    ax.set_ylim([min_value, max_value])
    ax.set_xticks(np.arange(min_value, max_value+1, interval))
    ax.set_yticks(np.arange(min_value, max_value+1, interval))
    ax.tick_params(
        axis='both', which='major', 
        labelsize=labelsize, width=2
    )

    # Set the linewidth of each axis
    for spine in ax.spines.values():
        spine.set_linewidth(2)

    # Save the figure
    fig.tight_layout()

    if save:
        plt.savefig(fig_name, dpi=600)
        print(f"Figure saved as {fig_name}")

    if not show:
        plt.close()



def plot_forces(
        forces1, forces2, natoms1, natoms2,
        max_min_list=None, interval=25, color_list=["#1f77b4", "#ff7f0e", "#2ca02c"],
        fontsize=18, labelsize=14, show=False, save=False, fig_name="./forces_comparison.png"
    ):

    if max_min_list:
        max_value, min_value = max_min_list
    else:
        max_1, min_1 = np.max(forces1), np.min(forces1)
        max_2, min_2 = np.max(forces2), np.min(forces2)

        max_value = max(max_1, max_2)
        min_value = min(min_1, min_2)
        max_value = (np.ceil(max_value / interval) * interval)
        min_value = (np.floor(min_value / interval) * interval)

    rmse = np.sqrt(np.mean((forces1 - forces2) ** 2))

    natoms1_expanded = np.broadcast_to(natoms1[:, np.newaxis, np.newaxis], forces1.shape)
    natoms2_expanded = np.broadcast_to(natoms2[:, np.newaxis, np.newaxis], forces2.shape)

    forces_per_atom1 = forces1 / natoms1_expanded
    forces_per_atom2 = forces2 / natoms2_expanded
    rmse_per_atom = np.sqrt(np.mean((forces_per_atom1 - forces_per_atom2) ** 2))

    # Define the figure
    fig, ax = plt.subplots(dpi=200)

    ax.plot(
        [min_value, max_value], 
        [min_value, max_value], 
        "k--", linewidth=1.5, zorder=2
    )

    # Plot the data
    directions = ["x", "y", "z"]
    forces1_flat = forces1.reshape(-1, 3)
    forces2_flat = forces2.reshape(-1, 3)
    for j in range(3):
        ax.scatter(
            forces1_flat[:, j], forces2_flat[:, j], 
            zorder=4, color=color_list[j], 
            alpha=0.5, label=directions[j]
        )

    # Add title and labels
    ax.set_xlabel("DFT results (eV/Å)", fontsize=fontsize)
    ax.set_ylabel("MLFF results (eV/Å)", fontsize=fontsize)

    ax.text(
        0.95, 0.05, f"RMSE: {rmse:.2f} eV/Å",
        horizontalalignment="right",
        transform=ax.transAxes, fontsize=labelsize
    )
    """
    ax.text(
        0.95, 0.05, f"RMSE/atom: {rmse_per_atom*1000:.1f} meV/(Å·atom)",
        horizontalalignment="right",
        transform=ax.transAxes, fontsize=labelsize
    )
    """

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim([min_value, max_value])
    ax.set_ylim([min_value, max_value])
    ax.set_xticks(np.arange(min_value, max_value+1, interval))
    ax.set_yticks(np.arange(min_value, max_value+1, interval))
    ax.tick_params(
        axis='both', which='major', 
        labelsize=labelsize, width=2
    )

    # Set the linewidth of each axis
    for spine in ax.spines.values():
        spine.set_linewidth(2)

    # Add legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))

    ax.legend(
        by_label.values(), by_label.keys(), 
        fontsize=labelsize, handlelength=0.5
    )

    # Save the figure
    fig.tight_layout()

    if save:
        plt.savefig(fig_name, dpi=600)
        print(f"Figure saved as {fig_name}")

    if not show:
        plt.close()
