import numpy as np
from .PDB_object import ProteinComplex


def PDB_UI():
    """A user friendly UI to allow for open, minupulating, and then outputting .pdb files.

    Functions:

    Open .pdb files:
     - When run, the first thing that will be asked is "Enter pdb file name: []". You must enter the relative / absolute path to the file.
     - Ex: Enter pdb file name: "ioNERDSSPyPi\\TestingFunctions\\1si4.pdb" (Note: I have to add a 2nd '\' before 1, so python does not see it as a weird charecter)
    Chaning distance between interaction sites:
     - After the .pdb file in initilized, it will ask "Would you like to chang...", and ask for you to write 'yes' or 'no'
     - If you write yes, keep reading, if you write no, it will just go to the next section
     - Than it will ask 'which distance' you want to change, and ask for an integer between 0-X.
        - 0: means all distances will be set to the same number you input
        - 1+: That distance will be set to the number inputted. You can find which 'distance' each number refers to by reading and counting down the
        list of Interaction Sites (which is directly above). 1 = the furthest up.
     - Then enter the new distance.
     - Then the initial message will come up again, and repeats this whol process.
    'Normalizing':
     - It will then ask if you want to see the 'default norm vector to (0,0,1)'. Write 'yes' or 'no' if you do or don't
     - It will then ask if you want each molecule's center of mass to be 0,0,0
     - The UI will then spit out the necessary .mol and .inp files to setup a NERDSS simulation

    If you want to make graphs / new .pdb files, you will need to use the 'seperate' commands instead of the UI.
    """
    # naming explanation:
    # variables with word 'total' in the front indicate that it's a list of data for the whole protein
    # variables with word 'split' in the front indicate that it's a list containing n sub-lists and each sub-list contains
    # data for different chains. (n is the number of chains)

    # read in file
    file_name = input("Enter pdb file name: ")
    UI_PDB = ProteinComplex(file_name)

    # user can choose to change the interaction site
    while True:
        answer = input(
            "Would you like to change the distance between interaction site (Type 'yes' or 'no'): "
        )
        if answer == "no":
            print("Calculation is completed.")
            break
        if answer == "yes":
            while True:
                n = int(
                    input(
                        "Which distance would you like to change (please enter an integer no greater than %.0f or enter 0 to set all distance to a specific number): "
                        % (len(UI_PDB.int_site_distance))
                    )
                )
                if n in range(0, len(UI_PDB.int_site_distance) + 1):
                    while True:
                        new_distance = float(input("Please enter new distance: "))
                        # decreasing distance & increasing distance
                        if new_distance >= 0:
                            UI_PDB.change_sigma(
                                ChangeSigma=True, SiteList=[n], NewSigma=[new_distance]
                            )
                            break
                        else:
                            print("Invalid number, please try again.")
                            break
                    break
                else:
                    print("Invalid answer, please try again.")
                    break
        else:
            print("Invalid answer, please try again.")

    # normalize vector
    UI_PDB.calc_angle()

    # ask to whether display 3D graph
    while True:
        answer3 = input(
            "Display a 3D plot of the protein complex? (Type 'yes' or 'no'): "
        )
        if answer3 == "yes":
            UI_PDB.plot_3D()
            break
        if answer3 == "no":
            break
        else:
            print("Invalid answer, please try again.")

    # asking whether to center the COM of every chain to origin.
    while True:
        answer2 = input(
            "Do you want each chain to be centered at center of mass? (Type 'yes' or 'no'): "
        )
        if answer2 == "yes":
            UI_PDB.norm_COM()
            break
        if answer2 == "no":
            break
        else:
            print("Invalid answer, please try again.")

    # writing parameters into a file
    UI_PDB.write_input()
    return 0
