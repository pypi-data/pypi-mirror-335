import os
import shutil
from pathlib import Path
from .merge_files import merge_files


def merge_simulation_results():
    """
    Merge the results of restart simulations.

    This function merges the content of PDB and RESTARTS folders from each numbered
    folder and their corresponding restart folders, and combines the .dat files.

    The base folder includes the folders named 1, 2, 3,… for each simulation run;
    each folder has the following structure, (d) means it is a directory:
    —1 (d)
        —PDB (d)
        —RESTARTS (d)
        —bound_pair_time.dat
        —copy_numbers_time.dat
        —event_counters_time.dat
        —histogram_complexes_time.dat
        —transition_matrix_time.dat
        —restart#### (d)
            —PDB (d)
            —RESTARTS (d)
            —bound_pair_time.dat
            —copy_numbers_time.dat
            —event_counters_time.dat
            —histogram_complexes_time.dat
            —transition_matrix_time.dat
        —restart#### (d)
            —PDB (d)
            —RESTARTS (d)
            —bound_pair_time.dat
            —copy_numbers_time.dat
            —event_counters_time.dat
            —histogram_complexes_time.dat
            —transition_matrix_time.dat

    output are under folders 1,2,3...
    """

    numbered_folders = [f for f in os.listdir('.') if f.isdigit()]

    for folder in numbered_folders:
        folder_path = os.path.join('.', folder)

        # Find all restart folders
        restart_folders = [d for d in os.listdir(folder_path) if d.startswith("restart") and os.path.isdir(os.path.join(folder_path, d))]


        # Sort restart folders by the timestamp
        sorted_restart_folders = sorted(restart_folders, key=lambda x: int(x[7:]))

        # Move PDB files from the restart to the root of each simulation folder
        for restart_folder in sorted_restart_folders:
            pdb_source_path = os.path.join(folder_path, restart_folder, "PDB")
            pdb_destination_path = os.path.join(folder_path, "PDB")
            for pdb_file in os.listdir(pdb_source_path):
                source_file = os.path.join(pdb_source_path, pdb_file)
                destination_file = os.path.join(pdb_destination_path, pdb_file)
                if not os.path.exists(destination_file):
                    shutil.move(source_file, pdb_destination_path)

        # Move restart files from the restart to the root of each simulation folder
            restarts_source_path = os.path.join(folder_path, restart_folder, "RESTARTS")
            restarts_destination_path = os.path.join(folder_path, "RESTARTS")
            for restart_file in os.listdir(restarts_source_path):
                source_file = os.path.join(restarts_source_path, restart_file)
                destination_file = os.path.join(restarts_destination_path, restart_file)
                if not os.path.exists(destination_file):
                    shutil.move(source_file, restarts_destination_path)

        # Copy the restart.dat file from the latest restart folder to the main folder
        if sorted_restart_folders:
            latest_restart_folder = sorted_restart_folders[-1]
            try:
                shutil.copy(os.path.join(folder_path, latest_restart_folder, "restart.dat"), folder_path)
            except:
                pass

        # Merge .dat files
        dat_files = ["bound_pair_time.dat", "copy_numbers_time.dat", "event_counters_time.dat",
                     "histogram_complexes_time.dat", "transition_matrix_time.dat"]

        for dat_file in dat_files:
            file_type = dat_file.split("_")[0]

            # Merge .dat files from the sorted restart folders
            for restart_folder in sorted_restart_folders:
                merge_files(os.path.join(folder_path, dat_file), os.path.join(folder_path, restart_folder, dat_file), file_type)

        # Remove all the restart folders
        for restart_folder in restart_folders:
            shutil.rmtree(os.path.join(folder_path, restart_folder))
