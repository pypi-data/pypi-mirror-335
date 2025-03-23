"""
protein_model.py

Defines the ProteinModel class, which coordinates reading/parsing a PDB or CIF file,
detecting interfaces, applying geometric regularization, building reaction objects,
and optionally computing binding energies via PyRosetta.
"""

import gzip
import requests
import numpy as np
import matplotlib.pyplot as plt
import math

from Bio import pairwise2
from Bio.PDB import (
    PDBList, MMCIFParser, PDBParser, PDBIO,
    Chain, Model
)
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from scipy.spatial import KDTree

from .data_structures import (
    MoleculeTemplate,
    BindingInterfaceTemplate,
    CoarseGrainedMolecule,
    BindingInterface,
    ReactionTemplate,
    Reaction,
    Coords
)

from .geometry_utils import (
    apply_rigid_transform,
    angles,
    check_steric_clashes,
    rigid_transform_chains
)


class ProteinModel:
    """
    A class that loads and edits a protein complex (from .pdb or .cif) for coarse-grained
    modeling in NERDSS. It can detect interfaces, align chains, regularize molecule
    structures, and optionally estimate binding energies.

    Attributes:
        fpath (str): The actual file name to read after verifying local or downloaded.
        all_atoms_structure (Bio.PDB.Structure.Structure): The full atomic structure read by Biopython.
        all_chains (list): A list of chain objects from the structure.
        all_COM_chains_coords (list): Coords objects for each chain’s center of mass (COM).
        all_interfaces (list): For each chain, a list of partner chain IDs that form binding interfaces.
        all_interfaces_coords (list): For each chain, the Coords of each interface in that chain.
        all_interfaces_residues (list): For each chain, the residue indices that form each interface.
        chains_map (dict): Maps chain IDs to simplified “molecule template” IDs (e.g. 'A', 'B').
        chains_group (list): Groups of chains considered homologous.
        molecule_list (list): List of Molecule objects derived from the structure.
        molecules_template_list (list): List of MoleculeTemplate objects describing each chain type.
        interface_list (list): List of Interface objects found in the structure.
        interface_template_list (list): List of BindingInterfaceTemplate objects.
        binding_chains_pairs (list): Tuples of chain IDs that form binding interactions.
        binding_energies (list): Binding energies (if computed).
        reaction_list (list): Actual Reaction objects derived from the structure.
        reaction_template_list (list): ReactionTemplate objects describing the reaction types.
        verbose (bool): Prints additional info when True.
    """
    def __init__(self, fpath: str):
        """
        Initializes the Protein object by reading a PDB or CIF file. If the file
        is not found locally, attempts to download it from the RCSB PDB database.

        Args:
            fpath (str): The path or PDB ID to read. If not found, will try
                to download .cif or .pdb from RCSB.
        """
        self.verbose = False

        self.fpath = fpath
        if not self._file_exists_locally(fpath):
            self.fpath = self._download_structure(fpath)

        self.all_atoms_structure = self._parse_structure()

        self.all_chains = []
        self.all_COM_chains_coords = []
        self.all_interfaces = []
        self.all_interfaces_coords = []
        self.all_interfaces_residues = []

        self.chains_map = {}  # Records the mapping of original chain IDs to molecular types used in NERDSS
                              # If downloaded from RCSB, homologous chain information is in the file header.
                              # Otherwise, sequence alignment is used to identify homologous chains.
        self.chains_group = []  # Groups chains with the same MOL_ID or entity_id as homologous

        self._find_homologous_chains() # Find homologous chains

        if not self.chains_group:
            # If no homologous chains were found, use the original chain IDs
            self._set_origianl_chain_ids()

        print("homogolous chains groups:")
        print(self.chains_group)

        # make sure that the chains_group list and each list in it has the same order each run time
        for group in self.chains_group:
            group.sort()
        self.chains_group.sort()

        # used to store the information of the molecules and interfaces for NERDSS model
        self.molecule_list = []
        self.molecules_template_list = []
        self.interface_list = []
        self.interface_template_list = []
        self.binding_chains_pairs = []
        self.binding_energies = []
        self.reaction_list = []
        self.reaction_template_list = []

    # -------------------------------------------------------------------------
    # Private / Helper Methods
    # -------------------------------------------------------------------------

    def _file_exists_locally(self, fpath: str) -> bool:
        """
        Checks if a file is available locally.

        Args:
            fpath (str): The name of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            with open(fpath, 'r') as _:
                return True
        except FileNotFoundError:
            return False

    def _download_structure(self, fpath: str) -> str:
        """
        Attempts to download a .pdb or .cif file from the RCSB PDB database.
        If the fpath is a 4-letter code, tries to download the assembly1 file first,
        otherwise defaults to standard CIF or PDB downloads.

        Args:
            fpath (str): The file name or PDB ID to attempt.

        Returns:
            str: The local file name after successful download.

        Raises:
            Exception: If the file cannot be downloaded.
        """
        pdbl = PDBList()

        try:
            if fpath.endswith('.pdb'):
                pdbl.retrieve_pdb_file(fpath[:-4], pdir='.', file_format='pdb')
                return f"{fpath[:-4]}.pdb"
            elif fpath.endswith('.cif'):
                pdbl.retrieve_pdb_file(fpath[:-4], pdir='.', file_format='mmCif')
                return f"{fpath[:-4]}.cif"
            elif len(fpath) == 4:  # Likely a PDB ID
                pdb_id = fpath.upper()

                # Attempt to download the assembly file
                assembly_url = f"https://files.rcsb.org/download/{pdb_id}-assembly1.cif.gz"
                assembly_file = f"{pdb_id.lower()}-assembly1.cif.gz"
                try:
                    response = requests.get(assembly_url, stream=True)
                    if response.status_code == 200:
                        with open(assembly_file, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        print(f"Successfully downloaded assembly file: {assembly_file}")
                        # Unzip the file
                        with gzip.open(assembly_file, 'rb') as f_in:
                            with open(f"{pdb_id.lower()}.cif", 'wb') as f_out:
                                f_out.write(f_in.read())

                        return f"{pdb_id.lower()}.cif"
                    else:
                        print(f"Assembly file not available for {pdb_id} (status code: {response.status_code})")
                except Exception as e:
                    print(f"Failed to download assembly file for {pdb_id}: {str(e)}")

                # Fall back to default mmCif structure
                print(f"Falling back to default structure download for {pdb_id}.")
                pdbl.retrieve_pdb_file(pdb_id, pdir='.', file_format='mmCif')
                return f"{pdb_id.lower()}.cif"
            else:
                raise ValueError("Invalid file name or format. Expected .pdb, .cif, or a valid PDB ID.")
        except Exception as e:
            raise Exception(f"The file '{fpath}' was not found locally and could not be downloaded: {str(e)}")

    def _parse_structure(self):
        """
        Uses Biopython to parse the .cif or .pdb file into a Structure object.

        Returns:
            Bio.PDB.Structure.Structure: The parsed structure containing all atoms.

        Raises:
            ValueError: If the file is not .cif or .pdb.
        """
        parser = None
        if self.fpath.endswith('.cif'):
            parser = MMCIFParser(QUIET=True)
        elif self.fpath.endswith('.pdb'):
            parser = PDBParser(QUIET=True)
        else:
            raise ValueError("Unsupported file format. Only .cif and .pdb files are supported.")

        structure_id = self.fpath.split('/')[-1].split('.')[0]
        structure = parser.get_structure(structure_id, self.fpath)
        return structure

    def _find_homologous_chains(self):
        """
        Identifies homologous chains in the structure and populates self.chains_map
        and self.chains_group. Tries to parse header info from PDB/CIF first;
        if that fails, falls back to sequence alignment.
        """
        if self.fpath.endswith('.pdb'):
            self._parse_pdb_header()
        elif self.fpath.endswith('.cif'):
            self._parse_cif_header()
        if not self.chains_map:
            self._find_homologous_chains_by_alignment()

    def _parse_pdb_header(self):
        """
        Parses the PDB file header for homologous chain info (MOL_ID, CHAIN).
        Populates chains_map and chains_group based on identified groups.
        """
        try:
            with open(self.fpath, 'r') as file:
                current_mol_id = None
                chains_group = []

                for line in file:
                    if line.startswith("COMPND"):
                        if "MOL_ID:" in line:
                            current_mol_id = line.split(":")[1].strip().split(";")[0]
                        elif "CHAIN:" in line and current_mol_id:
                            chains = line.split(":")[1].strip().split(";")[0].split(",")
                            chains_group.append(chains)

                # Group chains with the same MOL_ID as homologous
                available_NERDSS_mol_ids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
                for i, chains in enumerate(chains_group):
                    for chain in chains:
                        self.chains_map[chain] = available_NERDSS_mol_ids[i]
                self.chains_group = chains_group

                print("homologous chains identify finished using the PDB file header: chain ID to molecular type mapping:")
                print(self.chains_map)

        except Exception as e:
            print(f"Failed to parse PDB header for homologous chains: {str(e)}")
            # Attempt to find homologous chains using sequence alignment
            self._find_homologous_chains_by_alignment()

    def _parse_cif_header(self):
        """
        Parses the CIF file to extract homologous chain info (entity_id).
        Populates chains_map and chains_group based on identified groups.
        """
        try:
            with open(self.fpath, 'r') as file:
                section_found = False
                section_contents = []
                entity_ids = []
                chains_group = []

                for line in file:
                    if line.startswith("loop_"):
                        next_line = next(file).strip()
                        if next_line.startswith("_entity_poly.entity_id"):
                            section_found = True
                            continue
                    if section_found:
                        # record all the contents between the loop_ and the next loop_
                        if line.startswith("loop_"):
                            break
                        section_contents.append(line.strip())
                # loop through the contents to find the chain and entity_id
                for line in section_contents:
                    # split the line by whitespace
                    line = line.split()
                    # if the first element is a number, it is the entity_id
                    if line[0].isdigit():
                        entity_ids.append(line[0])
                    # if the first element includes , split by , to get the chains
                    elif "," in line[0]:
                        chains_group.append(line[0].split(","))

                # Group chains with the same entity_id as homologous
                available_NERDSS_mol_ids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
                for i, chains in enumerate(chains_group):
                    for chain in chains:
                        self.chains_map[chain] = available_NERDSS_mol_ids[i]
                self.chains_group = chains_group

                print("homologous chains identify finished using the CIF file header: chain ID to molecular type mapping:")
                print(self.chains_map)

        except Exception as e:
            print(f"Failed to parse CIF file for homologous chains: {str(e)}")
            # Attempt to find homologous chains using sequence alignment
            self._find_homologous_chains_by_alignment()

    def _find_homologous_chains_by_alignment(self, seq_identity_threshold: float = 90):
        """
        Identifies homologous chains by doing global alignment on each pair of chains'
        amino acid sequences. Groups chains above seq_identity_threshold% identity.

        Args:
            seq_identity_threshold (float, optional): Percent identity threshold
                to group chains as homologous. Defaults to 90.
        """
        try:
            similar_chains = []
            chains = list(self.all_atoms_structure.get_chains())
            chain_sequences = {}

            for chain in chains:
                sequence = "".join(seq1(residue.resname) for residue in chain.get_residues() if is_aa(residue))
                chain_sequences[chain.id] = sequence

            for i, chain1 in enumerate(chains):
                for j, chain2 in enumerate(chains):
                    if i >= j:
                        continue

                    seq1_chain = chain_sequences[chain1.id]
                    seq2_chain = chain_sequences[chain2.id]

                    alignments = pairwise2.align.globalxx(seq1_chain, seq2_chain)
                    if len(alignments) == 0:
                        continue
                    identify = (sum(1 for a, b in zip(alignments[0][0], alignments[0][1]) if a == b) / max(len(seq1_chain), len(seq2_chain))) * 100

                    if identify < seq_identity_threshold:
                        continue
                    similar_chains.append((chain1.id, chain2.id))

            graph = defaultdict(set)
            for chain1, chain2 in similar_chains:
                graph[chain1].add(chain2)
                graph[chain2].add(chain1)

            visited = set()
            groups = []

            def dfs(chain, group):
                visited.add(chain)
                group.add(chain)
                for neighbor in graph[chain]:
                    if neighbor not in visited:
                        dfs(neighbor, group)

            for chain in graph:
                if chain not in visited:
                    group = set()
                    dfs(chain, group)
                    groups.append(list(group))
            self.chains_group = groups
            available_NERDSS_mol_ids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            for i, chains in enumerate(groups):
                for chain in chains:
                    self.chains_map[chain] = available_NERDSS_mol_ids[i]
            print("homologous chains identify finished using sequence alignment: chain ID to molecular type mapping:")
            print(self.chains_map)

        except Exception as e:
            print(f"Failed to find homologous chains using sequence alignment: {str(e)}")

    def _set_origianl_chain_ids(self):
        """
        If no homologous chains are detected, simply map each chain's original ID
        to a unique letter from A-Z.
        """
        chains = list(self.all_atoms_structure.get_chains())
        available_NERDSS_mol_ids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        for i, chain in enumerate(chains):
            self.chains_map[chain.id] = available_NERDSS_mol_ids[i]
        self.chains_group = [[chain.id] for chain in chains]
        print("Original chain IDs are used as molecular types:")
        print(self.chains_map)

    def _plot_points_3d(self, points, chain_ids=None):
        """
        Plots sets of 3D points for multiple chains in a single 3D Matplotlib figure.
        The first row in each chain's array is the COM; subsequent rows are interface sites.

        Args:
            points (list): A list of arrays, each of shape (N, 3), representing a chain’s
                COM + interface sites.
            chain_ids (list, optional): A list of labels for each chain. Defaults to None.
        """

        # Prepare a 3D figure
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="3d")

        # Generate a color cycle for different chains
        colors = plt.cm.get_cmap("tab10", len(points))

        for i, chain in enumerate(points):
            # chain[0] is the center of mass (COM)
            com = chain[0]
            # The remaining points in the chain are interface points
            interfaces = chain[1:]

            # Pick a color for this chain
            color = colors(i)

            # Plot the COM
            ax.scatter(com[0], com[1], com[2],
                    color=color,
                    s=70,  # size of marker
                    marker="o",
                    label=f"Chain {chain_ids[i]} COM" if chain_ids != None else None)

            # Plot interfaces and lines to the COM
            for j, interface in enumerate(interfaces):
                # Plot the interface point
                ax.scatter(interface[0], interface[1], interface[2],
                        color=color,
                        s=50,
                        marker="^")  # or any shape you like

                # Draw a line from the COM to this interface
                xs = [com[0], interface[0]]
                ys = [com[1], interface[1]]
                zs = [com[2], interface[2]]
                ax.plot(xs, ys, zs, color=color, linewidth=1)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Coarse-Grained Chains: COM + Interfaces")

        ax.legend(loc="best")

        plt.tight_layout()
        plt.show()

    def _build_reactions(self):
        """
        Constructs Reaction objects for each pair in binding_chains_pairs,
        including angle calculations. Also builds ReactionTemplate objects
        if they do not already exist for these reactants.
        """
        for binding_pair in self.binding_chains_pairs:
            molecule_1 = [mol for mol in self.molecule_list if mol.name == binding_pair[0]][0]
            molecule_2 = [mol for mol in self.molecule_list if mol.name == binding_pair[1]][0]
            interface_1 = [interface for interface in molecule_1.interface_list if interface.name == binding_pair[1]][0]
            interface_2 = [interface for interface in molecule_2.interface_list if interface.name == binding_pair[0]][0]

            # build the reaction
            reaction = Reaction()
            reaction.reactants = []
            reaction.products = []
            reaction.binding_angles = []
            reaction.expression = ""
            reaction.reactants.append(f"{molecule_1.name}({interface_1.name})")
            reaction.reactants.append(f"{molecule_2.name}({interface_2.name})")
            reaction.products.append(f"{molecule_1.name}({interface_1.name}!1).{molecule_2.name}({interface_2.name}!1)")
            reaction.expression = f"{molecule_1.name}({interface_1.name}) + {molecule_2.name}({interface_2.name}) <-> {molecule_1.name}({interface_1.name}!1).{molecule_2.name}({interface_2.name}!1)"
            c1 = np.array([molecule_1.coord.x, molecule_1.coord.y, molecule_1.coord.z])
            c2 = np.array([molecule_2.coord.x, molecule_2.coord.y, molecule_2.coord.z])
            i1 = np.array([interface_1.coord.x, interface_1.coord.y, interface_1.coord.z])
            i2 = np.array([interface_2.coord.x, interface_2.coord.y, interface_2.coord.z])
            n1 = np.array(molecule_1.normal_point)
            n2 = np.array(molecule_2.normal_point)
            theta1, theta2, phi1, phi2, omega, sigma_magnitude = angles(c1, c2, i1, i2, n1, n2)
            if len(molecule_1.my_template.interface_template_list) == 1:
                phi1 = 'nan'
            if len(molecule_2.my_template.interface_template_list) == 1:
                phi2 = 'nan'
            reaction.binding_angles = [theta1, theta2, phi1, phi2, omega]
            reaction.norm1 = [0,0,1]
            reaction.norm2 = [0,0,1]
            reaction.binding_radius = sigma_magnitude
            self.reaction_list.append(reaction)
            print("Reaction:")
            print(reaction.expression)
            print("Angles:")
            print(reaction.binding_angles)
            print("Sigma:")
            print(reaction.binding_radius)
            print("c1:")
            print(np.array([molecule_1.coord.x, molecule_1.coord.y, molecule_1.coord.z]))
            print("p1:")
            print(np.array([interface_1.coord.x, interface_1.coord.y, interface_1.coord.z]))
            print("c2:")
            print(np.array([molecule_2.coord.x, molecule_2.coord.y, molecule_2.coord.z]))
            print("p2:")
            print(np.array([interface_2.coord.x, interface_2.coord.y, interface_2.coord.z]))

            # build the reaction template if it does not exist
            molecule_1_template_id = self.chains_map[molecule_1.name]
            molecule_2_template_id = self.chains_map[molecule_2.name]
            interface_1_template_id = interface_1.my_template.name
            interface_2_template_id = interface_2.my_template.name
            reactants = []
            if molecule_1_template_id < molecule_2_template_id:
                reactants.append(f"{molecule_1_template_id}({interface_1_template_id})")
                reactants.append(f"{molecule_2_template_id}({interface_2_template_id})")
            else:
                reactants.append(f"{molecule_2_template_id}({interface_2_template_id})")
                reactants.append(f"{molecule_1_template_id}({interface_1_template_id})")
            existed = False
            for reaction_template in self.reaction_template_list:
                if reaction_template.reactants == reactants:
                    existed = True
                    print("My Reaction Template:")
                    print(reaction_template.expression)
                    print("Template Angles:")
                    print(reaction_template.binding_angles)
                    print("Template Sigma:")
                    print(reaction_template.binding_radius)
                    break
            if not existed:
                reaction_template = ReactionTemplate()
                reaction_template.reactants = reactants
                reaction_template.products = []
                reaction_template.products.append(f"{molecule_1_template_id}({interface_1_template_id}!1).{molecule_2_template_id}({interface_2_template_id}!1)")
                # reactants and products do not include the interfaces that need to be free, but the expression does
                free_list_1 = ""
                molecule_template_1 = [mol_template for mol_template in self.molecules_template_list if mol_template.name == molecule_1_template_id][0]
                interface_template_1 = [interface_template for interface_template in molecule_template_1.interface_template_list if interface_template.name == interface_1_template_id][0]
                free_interface_template_list_1 = interface_template_1.required_free_list
                for free_interface in free_interface_template_list_1:
                    free_list_1 += f", {free_interface}"
                tmp_reactant_1 = f"{molecule_1_template_id}({interface_1_template_id}{free_list_1})"

                free_list_2 = ""
                molecule_template_2 = [mol_template for mol_template in self.molecules_template_list if mol_template.name == molecule_2_template_id][0]
                interface_template_2 = [interface_template for interface_template in molecule_template_2.interface_template_list if interface_template.name == interface_2_template_id][0]
                free_interface_template_list_2 = interface_template_2.required_free_list
                for free_interface in free_interface_template_list_2:
                    free_list_2 += f", {free_interface}"
                tmp_reactant_2 = f"{molecule_2_template_id}({interface_2_template_id}{free_list_2})"

                tmp_product = f"{molecule_1_template_id}({interface_1_template_id}!1{free_list_1}).{molecule_2_template_id}({interface_2_template_id}!1{free_list_2})"

                reaction_template.expression = f"{tmp_reactant_1} + {tmp_reactant_2} <-> {tmp_product}"

                reaction_template.binding_angles = reaction.binding_angles
                reaction_template.binding_radius = reaction.binding_radius
                reaction_template.norm1 = reaction.norm1
                reaction_template.norm2 = reaction.norm2

                self.reaction_template_list.append(reaction_template)
                print("My Reaction Template:")
                print(reaction_template.expression)
                print("Template Angles:")
                print(reaction_template.binding_angles)
                print("Template Sigma:")
                print(reaction_template.binding_radius)

    def _update_interface_templates_free_required_list(self):
        """
        Updates each interface template's `required_free_list`
        by checking potential steric clashes among binding partners to the same
        molecule template. If a clash is detected, the relevant interface templates
        must remain free.
        """
        for group in self.chains_group:
            for i, chain_id in enumerate(group):
                if i == 0:
                    continue
                # find the molecule in the list
                molecule = [mol for mol in self.molecule_list if mol.name == chain_id][0]
                # loop the interfaces list of the molecule
                for interface in molecule.interface_list:
                    # determine if this interface appears first time
                    interface_id = interface.name
                    interface_template_id = interface.my_template.name
                    first_appearance = True
                    for j in range(i):
                        chain_id_2 = group[j]
                        molecule_2 = [mol for mol in self.molecule_list if mol.name == chain_id_2][0]
                        for interface_2 in molecule_2.interface_list:
                            interface_id_2 = interface_2.name
                            interface_template_id_2 = interface_2.my_template.name
                            if interface_template_id == interface_template_id_2:
                                first_appearance = False
                                break
                    if first_appearance:
                        # check the steric clashes between the partner to this interface and partner to the partners to other interfaces of previous chains; two interfaces belong to different interface tempalte
                        my_partner_chain_id = interface_id
                        my_partner_chain = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == my_partner_chain_id][0])]
                        my_chain = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                        for j in range(i):
                            chain_id_2 = group[j]
                            molecule_2 = [mol for mol in self.molecule_list if mol.name == chain_id_2][0]
                            for interface_2 in molecule_2.interface_list:
                                interface_id_2 = interface_2.name
                                interface_template_id_2 = interface_2.my_template.name
                                if interface_template_id != interface_template_id_2:
                                    another_partner_chain_id = interface_id_2
                                    another_partner_chain = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == another_partner_chain_id][0])]
                                    another_chain = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id_2][0])]
                                    R, t = rigid_transform_chains(my_chain, another_chain)
                                    # rotate the CA atoms of my_partner_chain and check the steric clashes with CA atoms of another_partner_chain
                                    my_partner_chain_CA_coords = []
                                    for residue in my_partner_chain:
                                        if is_aa(residue) and 'CA' in residue:
                                            my_partner_chain_CA_coords.append(residue['CA'].coord)
                                    my_partner_chain_CA_coords_transformed = []
                                    for coord in my_partner_chain_CA_coords:
                                        coord_transformed = apply_rigid_transform(R, t, coord)
                                        my_partner_chain_CA_coords_transformed.append(coord_transformed)
                                    another_partner_chain_CA_coords = []
                                    for residue in another_partner_chain:
                                        if is_aa(residue) and 'CA' in residue:
                                            another_partner_chain_CA_coords.append(residue['CA'].coord)
                                    if check_steric_clashes(np.array(my_partner_chain_CA_coords_transformed), np.array(another_partner_chain_CA_coords)):
                                        molecule_template_id = self.chains_map[chain_id]
                                        molecule_template = [mol_template for mol_template in self.molecules_template_list if mol_template.name == molecule_template_id][0]
                                        interface_template_1 = [interface_template for interface_template in molecule_template.interface_template_list if interface_template.name == interface_template_id][0]
                                        interface_template_2 = [interface_template for interface_template in molecule_template.interface_template_list if interface_template.name == interface_template_id_2][0]
                                        if interface_template_id not in interface_template_2.required_free_list:
                                            interface_template_2.required_free_list.append(interface_template_id)
                                        if interface_template_id_2 not in interface_template_1.required_free_list:
                                            interface_template_1.required_free_list.append(interface_template_id_2)

    # -------------------------------------------------------------------------
    # Public API Methods
    # -------------------------------------------------------------------------

    def detect_interfaces(self, cutoff: float = 0.35, residue_cutoff: int = 3):
        """
        Detects binding interfaces between chains based on distances between atoms.
        For each chain pair, uses a KDTree search to find close-contact atoms (< cutoff nm).
        Also stores center-of-mass (COM) for each chain.

        Args:
            cutoff (float, optional): Max distance (nm) for atoms to be considered in contact.
                Defaults to 0.35.
            residue_cutoff (int, optional): Minimum residue pair count to call it a valid interface.
                Defaults to 3.
        """
        # self.all_chains = list(self.all_atoms_structure.get_chains())
        self.all_chains = sorted(self.all_atoms_structure.get_chains(), key=lambda chain: chain.id)
        self.all_COM_chains_coords = []
        self.all_interfaces = []
        self.all_interfaces_coords = []
        self.all_interfaces_residues = []

        # Initialize interface lists
        num_chains = len(self.all_chains)
        for _ in range(num_chains):
            self.all_interfaces.append([])
            self.all_interfaces_coords.append([])
            self.all_interfaces_residues.append([])

        # Calculate the center of mass (COM) for each chain
        for chain in self.all_chains:
            atom_coords = [atom.coord for residue in chain for atom in residue if is_aa(residue)]
            if not atom_coords:
                self.all_COM_chains_coords.append(None)
                continue

            # Calculate the COM
            avg_coords = np.mean(atom_coords, axis=0)
            self.all_COM_chains_coords.append(Coords(*avg_coords))

        # Helper function to compute bounding box for a chain
        def compute_bounding_box(chain):
            atom_coords = np.array([atom.coord for residue in chain for atom in residue if is_aa(residue)])
            if atom_coords.size == 0:
                return None, None
            min_coords = np.min(atom_coords, axis=0)
            max_coords = np.max(atom_coords, axis=0)
            return min_coords, max_coords
        
        # Precompute bounding boxes for all chains
        bounding_boxes = [compute_bounding_box(chain) for chain in self.all_chains]

        # Helper function to process a pair of chains
        def process_chain_pair(i, j):
            if self.all_COM_chains_coords[i] is None or self.all_COM_chains_coords[j] is None:
                return

            min_box1, max_box1 = bounding_boxes[i]
            min_box2, max_box2 = bounding_boxes[j]

            # Skip if bounding boxes are farther apart than the cutoff distance
            if np.any(min_box2 > max_box1 + cutoff * 10) or np.any(max_box2 < min_box1 - cutoff * 10):
                return
            
            chain1 = self.all_chains[i]
            chain2 = self.all_chains[j]

            atom_coords_chain1 = []
            ca_coords_chain1 = []
            residue_ids_chain1 = []
            atom_coords_chain2 = []
            ca_coords_chain2 = []
            residue_ids_chain2 = []

            for residue1 in chain1:
                if not is_aa(residue1) or 'CA' not in residue1:
                    continue
                for atom1 in residue1:
                    atom_coords_chain1.append(atom1.coord)
                    ca_coords_chain1.append(residue1['CA'].coord)
                    residue_ids_chain1.append(residue1.id[1])

            for residue2 in chain2:
                if not is_aa(residue2) or 'CA' not in residue2:
                    continue
                for atom2 in residue2:
                    atom_coords_chain2.append(atom2.coord)
                    ca_coords_chain2.append(residue2['CA'].coord)
                    residue_ids_chain2.append(residue2.id[1])

            if len(ca_coords_chain1) == 0 or len(ca_coords_chain2) == 0:
                return

            # Build KDTree for chain2
            tree = KDTree(atom_coords_chain2)
            indices = tree.query_ball_point(atom_coords_chain1, r=cutoff * 10)

            interface1 = []
            interface1_coords = []
            interface2 = []
            interface2_coords = []

            # Collect interface residues based on KDTree results
            for idx1, neighbors in enumerate(indices):
                if neighbors:
                    if residue_ids_chain1[idx1] not in interface1:
                        interface1.append(residue_ids_chain1[idx1])
                        interface1_coords.append(ca_coords_chain1[idx1])

                    for idx2 in neighbors:
                        if residue_ids_chain2[idx2] not in interface2:
                            interface2.append(residue_ids_chain2[idx2])
                            interface2_coords.append(ca_coords_chain2[idx2])

            # Store results if any interfaces were found
            if len(interface1) >= residue_cutoff and len(interface2) >= residue_cutoff:
                avg_coords1 = np.mean(interface1_coords, axis=0)
                self.all_interfaces[i].append(self.all_chains[j].id)
                self.all_interfaces_coords[i].append(Coords(*avg_coords1))
                self.all_interfaces_residues[i].append(sorted(interface1))
                avg_coords2 = np.mean(interface2_coords, axis=0)
                self.all_interfaces[j].append(self.all_chains[i].id)
                self.all_interfaces_coords[j].append(Coords(*avg_coords2))
                self.all_interfaces_residues[j].append(sorted(interface2))

        # Parallelize chain pair processing
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_chain_pair, i, j) for i in range(num_chains - 1) for j in range(i + 1, num_chains)]
            for future in futures:
                future.result()  # Wait for all tasks to complete

        for i in range(num_chains):
            sorted_indices = sorted(range(len(self.all_interfaces[i])), key=lambda k: self.all_interfaces[i][k])
            self.all_interfaces[i] = [self.all_interfaces[i][k] for k in sorted_indices]
            self.all_interfaces_coords[i] = [self.all_interfaces_coords[i][k] for k in sorted_indices]
            self.all_interfaces_residues[i] = [self.all_interfaces_residues[i][k] for k in sorted_indices]

        # Print detected interfaces
        if self.verbose:
            print("Binding interfaces detected:")
            for i, chain in enumerate(self.all_chains):
                print(f"Chain {chain.id}:")
                print(f"  Center of Mass (COM): {self.all_COM_chains_coords[i]}")
                print(f"  Interfaces: {self.all_interfaces[i]}")
                print("  Interface Coordinates: ")
                for interface_coord in self.all_interfaces_coords[i]:
                    print(f"    {interface_coord}")

    def save_original_coarse_grained_structure(self, output_cif: str = "original_coarse_grained_structure.cif", pymol_script: str = "original_visualize_coarse_grained.pml"):
        """
        Saves the original coarse-grained structure (COM and interface coordinates for each chain)
        to a CIF file and generates a PyMOL script for quick visualization.

        Args:
            output_cif (str, optional): Output .cif filename. Defaults to
                "original_coarse_grained_structure.cif".
            pymol_script (str, optional): Output .pml filename for PyMOL. Defaults to
                "original_visualize_coarse_grained.pml".
        """
        with open(output_cif, 'w') as cif_file:
            atom_id = 1

            # Write CIF header
            cif_file.write("# Coarse-grained structure CIF file\n")
            cif_file.write("data_coarse_grained\n")
            cif_file.write("_audit_conform_dict.text 'Original coarse-grained model generated by ionerdss'\n")
            cif_file.write("loop_\n")
            cif_file.write("_atom_site.group_PDB\n")
            cif_file.write("_atom_site.id\n")
            cif_file.write("_atom_site.label_atom_id\n")
            cif_file.write("_atom_site.label_comp_id\n")
            cif_file.write("_atom_site.label_asym_id\n")
            cif_file.write("_atom_site.Cartn_x\n")
            cif_file.write("_atom_site.Cartn_y\n")
            cif_file.write("_atom_site.Cartn_z\n")
            cif_file.write("_atom_site.occupancy\n")
            cif_file.write("_atom_site.B_iso_or_equiv\n")
            cif_file.write("_atom_site.type_symbol\n")

            # Write COM atoms for each chain
            for i, chain in enumerate(self.all_chains):
                if not self.all_COM_chains_coords[i]:
                    continue
                com = self.all_COM_chains_coords[i]
                cif_file.write(
                    f"ATOM  {atom_id:5d}  COM  MOL {chain.id}  "
                    f"{com.x:8.3f} {com.y:8.3f} {com.z:8.3f}  1.00  0.00  C\n"
                )
                atom_id += 1

                # Write interface atoms for the current chain
                for j, interface_coord in enumerate(self.all_interfaces_coords[i]):
                    cif_file.write(
                        f"ATOM  {atom_id:5d}  INT  MOL {chain.id}  "
                        f"{interface_coord.x:8.3f} {interface_coord.y:8.3f} {interface_coord.z:8.3f}  1.00  0.00  O\n"
                    )
                    atom_id += 1

        print(f"Coarse-grained structure saved to {output_cif}.")

        # Generate PyMOL script for visualization
        with open(pymol_script, 'w') as pml_file:
            pml_file.write("# PyMOL script to visualize coarse-grained structure\n")
            pml_file.write(f"load {output_cif}, coarse_grained\n")
            pml_file.write("hide everything\n")
            pml_file.write("show spheres, name COM\n")
            pml_file.write("show spheres, name INT\n")
            pml_file.write("set sphere_scale, 1.0\n")
            pml_file.write("color red, name COM\n")
            pml_file.write("color blue, name INT\n")
            
            # Create pseudo-atoms for COM and interfaces and draw lines
            atom_index = 1
            for i, chain in enumerate(self.all_chains):
                com = self.all_COM_chains_coords[i]
                if not com:
                    continue
                # Make a pseudoatom for the chain's COM
                pml_file.write(
                    f"pseudoatom com_{chain.id}, pos=[{com.x:.3f}, {com.y:.3f}, {com.z:.3f}], color=red\n"
                )
                
                # For each interface, create a pseudoatom and connect it to the COM
                for j, interface_coord in enumerate(self.all_interfaces_coords[i], start=1):
                    pml_file.write(
                        f"pseudoatom int_{chain.id}_{j}, pos=[{interface_coord.x:.3f}, "
                        f"{interface_coord.y:.3f}, {interface_coord.z:.3f}], color=blue\n"
                    )
                    # Use f-strings so {atom_index} is replaced numerically
                    pml_file.write(f"distance line{atom_index}, com_{chain.id}, int_{chain.id}_{j}\n")
                    pml_file.write(f"set dash_width, 4, line{atom_index}\n")
                    pml_file.write(f"set dash_gap, 0.5, line{atom_index}\n")
                    atom_index += 1

            pml_file.write("set sphere_transparency, 0.2\n")
            pml_file.write("bg_color white\n")
            pml_file.write("zoom all\n")

        print(f"PyMOL script saved to {pymol_script}.")

    def save_regularized_coarse_grained_structure(self, output_cif: str = "regularized_coarse_grained_structure.cif", pymol_script: str = "visualize_regularized_coarse_grained.pml"):
        """
        Saves the regularized coarse-grained structure (COM and interface coordinates for each molecule)
        to a CIF file and generates a PyMOL script for quick visualization.

        Args:
            output_cif (str, optional): Output .cif filename. Defaults to
                "regularized_coarse_grained_structure.cif".
            pymol_script (str, optional): Output .pml filename for PyMOL. Defaults to
                "regularized_visualize_coarse_grained.pml".
        """
        with open(output_cif, 'w') as cif_file:
            atom_id = 1

            # Write CIF header
            cif_file.write("# Coarse-grained structure CIF file\n")
            cif_file.write("data_coarse_grained\n")
            cif_file.write("_audit_conform_dict.text 'Regularized coarse-grained model generated by ionerdss'\n")
            cif_file.write("loop_\n")
            cif_file.write("_atom_site.group_PDB\n")
            cif_file.write("_atom_site.id\n")
            cif_file.write("_atom_site.label_atom_id\n")
            cif_file.write("_atom_site.label_comp_id\n")
            cif_file.write("_atom_site.label_asym_id\n")
            cif_file.write("_atom_site.Cartn_x\n")
            cif_file.write("_atom_site.Cartn_y\n")
            cif_file.write("_atom_site.Cartn_z\n")
            cif_file.write("_atom_site.occupancy\n")
            cif_file.write("_atom_site.B_iso_or_equiv\n")
            cif_file.write("_atom_site.type_symbol\n")

            # Loop over regularized molecules
            for mol in self.molecule_list:
                if not mol.coord:
                    continue
                # Write COM (center-of-mass) as 'COM' atom
                cif_file.write(
                    f"ATOM  {atom_id:5d}  COM  MOL {mol.name}  "
                    f"{mol.coord.x:8.3f} {mol.coord.y:8.3f} {mol.coord.z:8.3f}  1.00  0.00  C\n"
                )
                atom_id += 1

                # Write each interface atom
                for intf in mol.interface_list:
                    cif_file.write(
                        f"ATOM  {atom_id:5d}  INT  MOL {mol.name}  "
                        f"{intf.coord.x:8.3f} {intf.coord.y:8.3f} {intf.coord.z:8.3f}  1.00  0.00  O\n"
                    )
                    atom_id += 1

        print(f"Regularized coarse-grained structure saved to {output_cif}.")

        # Generate PyMOL script
        with open(pymol_script, 'w') as pml_file:
            pml_file.write("# PyMOL script to visualize regularized coarse-grained structure\n")
            pml_file.write(f"load {output_cif}, coarse_grained\n")
            pml_file.write("hide everything\n")
            pml_file.write("show spheres, name COM\n")
            pml_file.write("show spheres, name INT\n")
            pml_file.write("set sphere_scale, 1.0\n")
            pml_file.write("color red, name COM\n")
            pml_file.write("color blue, name INT\n")

            atom_index = 1
            for mol in self.molecule_list:
                if not mol.coord:
                    continue
                # Create a pseudoatom in PyMOL for the COM
                pml_file.write(
                    f"pseudoatom com_{mol.name}, pos=[{mol.coord.x:.3f}, {mol.coord.y:.3f}, {mol.coord.z:.3f}], color=red\n"
                )

                # For each interface, create a pseudoatom and connect it to COM
                for j, intf in enumerate(mol.interface_list, start=1):
                    pml_file.write(
                        f"pseudoatom int_{mol.name}_{j}, pos=[{intf.coord.x:.3f}, {intf.coord.y:.3f}, {intf.coord.z:.3f}], color=blue\n"
                    )
                    pml_file.write(
                        f"distance line{atom_index}, com_{mol.name}, int_{mol.name}_{j}\n"
                    )
                    # Use f-strings so {atom_index} is replaced numerically
                    pml_file.write(f"set dash_width, 4, line{atom_index}\n")
                    pml_file.write(f"set dash_gap, 0.5, line{atom_index}\n")
                    atom_index += 1

            pml_file.write("set sphere_transparency, 0.2\n")
            pml_file.write("bg_color white\n")
            pml_file.write("zoom all\n")

        print(f"PyMOL script saved to {pymol_script}.")

    def plot_original_coarse_grained_structure(self):
        """
        Visualizes the original coarse-grained structure, showing each chain’s
        COM and interface coordinates before regularization.
        """
        all_points = []
        chain_ids = []
        for group in self.chains_group:
            for chain_id in group:
                chain_ids.append(chain_id)
                com_coord = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                interface_coords = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                points = []
                points.append([com_coord.x, com_coord.y, com_coord.z])
                for interface_coord in interface_coords:
                    points.append([interface_coord.x, interface_coord.y, interface_coord.z])
                all_points.append(points)
        self._plot_points_3d(all_points, chain_ids)

    def plot_regularized_structure(self):
        """
        Visualizes the structure after applying `regularize_molecules()`.
        Each Molecule’s COM and interface coordinates are shown.
        """
        all_points = []
        chain_ids = []
        for _, mol in enumerate(self.molecule_list):
            chain_ids.append(mol.name)
            com_coord = mol.coord
            interface_coords = [interface.coord for interface in mol.interface_list]
            points = []
            points.append([com_coord.x, com_coord.y, com_coord.z])
            for interface_coord in interface_coords:
                points.append([interface_coord.x, interface_coord.y, interface_coord.z])
            all_points.append(points)
        self._plot_points_3d(all_points, chain_ids)

    def _calc_angle(self, P, Q, R):
        """
        Calculate the angle at Q formed by P->Q and R->Q.
        """
        v1 = [(Q - P).x, (Q - P).y, (Q - P).z]
        v2 = [(R - Q).x, (R - Q).y, (R - Q).z]
        theta = np.degrees(math.acos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))))
        return theta
    
    def _sig_are_similar(self, sig1, sig2, dist_thresh_intra, dist_thresh_inter, angle_thresh):
        """
        Compare two group of interface interaction geometry.
        """
        for key in ("dA", "dB"):
            if abs(sig1[key] - sig2[key]) > dist_thresh_intra:
                return False
        for key in ("dAB",):
            if abs(sig1[key] - sig2[key]) > dist_thresh_inter:
                return False
        for key in ("thetaA", "thetaB"):
            if abs(sig1[key] - sig2[key]) > angle_thresh:
                return False
        return True
    
    def _is_existing_mol_temp(self, mol_temp_name):
        """
        Checks if a molecule template with the given name already exists in the molecule template list.

        Args:
            mol_temp_name (str): The name of the molecule template to check.

        Returns:
            bool: True if the molecule template exists, False otherwise.
            int: The index of the molecule template if it exists, None otherwise.
        """
        for i, mol_temp in enumerate(self.molecules_template_list):
            if mol_temp.name == mol_temp_name:
                return True, i
        return False, None
    
    def _is_existing_mol(self, mol_name):
        """
        Checks if a molecule with the given name already exists in the molecule list.

        Args:
            mol_name (str): The name of the molecule to check.

        Returns:
            bool: True if the molecule exists, False otherwise.
            int: The index of the molecule if it exists, None otherwise.
        """
        for i, mol in enumerate(self.molecule_list):
            if mol.name == mol_name:
                return True, i
        return False, None
    
    def _is_existing_interface(self, interface_name, molecule):
        """
        Checks if an interface with the given name already exists in the molecule's interface list.

        Args:
            interface_name (str): The name of the interface to check.
            molecule (CoarseGrainedMolecule): The molecule to check within.

        Returns:
            bool: True if the interface exists, False otherwise.
            int: The index of the interface if it exists, None otherwise.
        """
        for i, interface in enumerate(molecule.interface_list):
            if interface.name == interface_name:
                return True, i
        return False, None
    
    def _is_existing_sig(self, sig, dist_thresh_intra=2.5, dist_thresh_inter=2.5, angle_thresh=25.0):
        """
        Checks if a given interface signature already exists in the interface_signatures list.

        Args:
            sig (dict): The interface signature to check.
            dist_thresh_intra (float, optional): Distance threshold for intra-molecular comparisons. Defaults to 2.5.
            dist_thresh_inter (float, optional): Distance threshold for inter-molecular comparisons. Defaults to 2.5.
            angle_thresh (float, optional): Angle threshold for comparisons. Defaults to 25.0.

        Returns:
            bool: True if the signature exists, False otherwise.
        """
        for existing_sig in self.interface_signatures:
            if self._sig_are_similar(sig, existing_sig, dist_thresh_intra=dist_thresh_intra, dist_thresh_inter=dist_thresh_inter, angle_thresh=angle_thresh):
                return True
        return False

    def regularize_molecules(self, dist_thresh_intra=2.5, dist_thresh_inter=2.5, angle_thresh=25.0):
        """
        Aligns and regularizes all molecules in self.chains_group so that
        homologous chains share the same relative geometry. Builds molecule
        and interface objects accordingly, and sets up Reaction objects.
        """
        self.molecule_list = []
        self.molecules_template_list = []
        self.interface_list = []
        self.interface_template_list = []
        self.interface_signatures = []

        for group in self.chains_group:
            print(f"Start parsing chain group / molecule template {group}")
            mol_temp_name = self.chains_map[group[0]]
            is_existing_mol_temp, idx = self._is_existing_mol_temp(mol_temp_name)
            if is_existing_mol_temp:
                print(f"This is an existed mol template {mol_temp_name}")
                molecule_template = self.molecules_template_list[idx]
            else:
                molecule_template = MoleculeTemplate(mol_temp_name)
                print(f"New mol template {mol_temp_name} is created.")
                self.molecules_template_list.append(molecule_template)

            for j, chain_id in enumerate(group):
                print(f"Start parsing chain / molecule {chain_id}")
                mol_name = chain_id
                is_existing_mol, mol_index = self._is_existing_mol(mol_name)
                if is_existing_mol:
                    print(f"This is an existing molecule {mol_name}")
                    molecule = self.molecule_list[mol_index]
                else:
                    molecule = CoarseGrainedMolecule(mol_name)
                    print(f"New molecule {mol_name} is created.")
                    molecule.my_template = molecule_template
                    molecule.coord = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == mol_name][0])]
                    self.molecule_list.append(molecule)
                
                # loop the interface of this chain (molecule)
                for i, interface_id in enumerate(self.all_interfaces[self.all_chains.index([chain for chain in self.all_chains if chain.id == mol_name][0])]):
                    A = mol_name
                    B = interface_id # this is the chain name of the partner
                    partner_mol_template_name = self.chains_map[B]
                    print(f"Parsing the interface {interface_id} for molecule {mol_name}; its binding partner is molecule {B} via its interface {A}")
                    is_existing_mol_temp, idx = self._is_existing_mol_temp(partner_mol_template_name)
                    if is_existing_mol_temp:
                        print(f"molecule {B} already has its template created.")
                        partner_molecule_template = self.molecules_template_list[idx]
                    else:
                        partner_molecule_template = MoleculeTemplate(partner_mol_template_name)
                        print(f"new mol template {partner_mol_template_name} created for molecule {B}.")
                        self.molecules_template_list.append(partner_molecule_template)

                    is_existing_mol, partner_mol_index = self._is_existing_mol(B)
                    if is_existing_mol:
                        print(f"molecule {B} is already created.")
                        partner_molecule = self.molecule_list[partner_mol_index]
                    else:
                        partner_molecule = CoarseGrainedMolecule(B)
                        print(f"New molecule {B} is created.")
                        partner_molecule.my_template = partner_molecule_template
                        partner_molecule.coord = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == B][0])]
                        self.molecule_list.append(partner_molecule)

                    COM_A = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == A][0])]
                    I_A = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == A][0])][i]
                    COM_B = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == B][0])]
                    for k, partner_interface_id in enumerate(self.all_interfaces[self.all_chains.index([chain for chain in self.all_chains if chain.id == B][0])]):
                        if partner_interface_id == A:
                            I_B = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == B][0])][k]
                            R_B = self.all_interfaces_residues[self.all_chains.index([chain for chain in self.all_chains if chain.id == B][0])][k]
                            break

                    signature = {
                        "dA": np.linalg.norm([(COM_A - I_A).x, (COM_A - I_A).y, (COM_A - I_A).z]),
                        "dB": np.linalg.norm([(COM_B - I_B).x, (COM_B - I_B).y, (COM_B - I_B).z]),
                        "dAB": np.linalg.norm([(I_A - I_B).x, (I_A - I_B).y, (I_A - I_B).z]),
                        "thetaA": self._calc_angle(COM_A, I_A, I_B),
                        "thetaB": self._calc_angle(COM_B, I_B, I_A)
                    }

                    # print the signature
                    print(f"Parsing signature: {signature}")

                    is_existing_sig = False

                    for existing_sig in self.interface_signatures:
                        if self._sig_are_similar(signature, existing_sig, dist_thresh_intra, dist_thresh_inter, angle_thresh):
                            is_existing_sig = True
                            break

                    if not is_existing_sig:
                        print("this is a new signature. added to list.")
                        self.interface_signatures.append(signature)
                        signature_conjugated = {
                            "dA": signature["dB"],
                            "dB": signature["dA"],
                            "dAB": signature["dAB"],
                            "thetaA": signature["thetaB"],
                            "thetaB": signature["thetaA"]
                        }
                        self.interface_signatures.append(signature_conjugated)
                        print(f"the conjugated signature: {signature_conjugated} is also added to the list.")

                        # build the interface template pairs for both molecule templates, need to check if this is homo dimerization or hetero
                        is_homo = False
                        if self.chains_map[A] != self.chains_map[B]:
                            pass
                        else:
                            if abs(signature["dA"] - signature["dB"]) > dist_thresh_intra or abs(signature["thetaA"] - signature["thetaB"]) > angle_thresh:
                                pass
                            else:
                                is_homo = True

                        if is_homo:
                            # only need to build the interface template once
                            interface_template_id_prefix = self.chains_map[A]

                            # determine the sufffix of this interface_template
                            tmp_count = 1
                            for interface_temp in molecule_template.interface_template_list:
                                interface_temp_id = interface_temp.name
                                if interface_temp_id.startswith(interface_template_id_prefix):
                                    tmp_count += 1

                            interface_template_id_suffix = str(tmp_count)
                            interface_template_id = interface_template_id_prefix + interface_template_id_suffix
                            interface_template = BindingInterfaceTemplate(interface_template_id)
                            interface_template.signature = signature
                            if j == 0:
                                interface_template.coord = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])][i] - molecule.coord
                            else:
                                # align the current chain to the first chain in the group, then get the relative position of interface to COM
                                chain1 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == group[0]][0])]
                                chain2 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                                R, t = rigid_transform_chains(chain2, chain1)
                                Q = []
                                Q_COM_coord = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                                Q.append([Q_COM_coord.x, Q_COM_coord.y, Q_COM_coord.z])
                                temp_coord = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])][i]
                                Q.append([temp_coord.x, temp_coord.y, temp_coord.z])
                                Q2 = []
                                for point in Q:
                                    transformed_point = apply_rigid_transform(R, t, np.array(point))
                                    Q2.append(transformed_point)
                                interface_template.coord = Coords(Q2[1][0] - Q2[0][0], Q2[1][1] - Q2[0][1], Q2[1][2] - Q2[0][2])
                            molecule_template.interface_template_list.append(interface_template)
                            self.interface_template_list.append(interface_template)
                            partner_interface_template = interface_template
                            partner_molecule_template = molecule_template
                        else:
                            # add interface template 1
                            interface_template_id_prefix = self.chains_map[B]

                            # determine the sufffix of this interface_template
                            tmp_count = 1
                            for interface_temp in molecule_template.interface_template_list:
                                interface_temp_id = interface_temp.name
                                if interface_temp_id.startswith(interface_template_id_prefix):
                                    tmp_count += 1

                            interface_template_id_suffix = str(tmp_count)
                            interface_template_id = interface_template_id_prefix + interface_template_id_suffix
                            interface_template = BindingInterfaceTemplate(interface_template_id)
                            interface_template.signature = signature
                            if j == 0:
                                interface_template.coord = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])][i] - molecule.coord
                            else:
                                # align the current chain to the first chain in the group, then get the relative position of interface to COM
                                chain1 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == group[0]][0])]
                                chain2 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                                R, t = rigid_transform_chains(chain2, chain1)
                                Q = []
                                Q_COM_coord = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                                Q.append([Q_COM_coord.x, Q_COM_coord.y, Q_COM_coord.z])
                                temp_coord = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])][i]
                                Q.append([temp_coord.x, temp_coord.y, temp_coord.z])
                                Q2 = []
                                for point in Q:
                                    transformed_point = apply_rigid_transform(R, t, np.array(point))
                                    Q2.append(transformed_point)
                                interface_template.coord = Coords(Q2[1][0] - Q2[0][0], Q2[1][1] - Q2[0][1], Q2[1][2] - Q2[0][2])
                            molecule_template.interface_template_list.append(interface_template)
                            self.interface_template_list.append(interface_template)

                            # add interface template 2
                            interface_template_id_prefix = self.chains_map[A]

                            # determine the sufffix of this interface_template
                            tmp_count = 1
                            for interface_temp in molecule_template.interface_template_list:
                                interface_temp_id = interface_temp.name
                                if interface_temp_id.startswith(interface_template_id_prefix):
                                    tmp_count += 1

                            interface_template_id_suffix = str(tmp_count)
                            interface_template_id = interface_template_id_prefix + interface_template_id_suffix
                            partner_interface_template = BindingInterfaceTemplate(interface_template_id)
                            partner_interface_template.signature = signature_conjugated
                            B_group = None
                            for g in self.chains_group:
                                if B in g:
                                    B_group = g

                            if B == B_group[0]:
                                partner_interface_template.coord = I_B - partner_molecule.coord
                            else:
                                # align the current chain to the first chain in the group, then get the relative position of interface to COM
                                chain1 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == B_group[0]][0])]
                                chain2 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == B][0])]
                                R, t = rigid_transform_chains(chain2, chain1)
                                Q = []
                                Q_COM_coord = self.all_COM_chains_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == B][0])]
                                Q.append([Q_COM_coord.x, Q_COM_coord.y, Q_COM_coord.z])
                                temp_coord = I_B
                                Q.append([temp_coord.x, temp_coord.y, temp_coord.z])
                                Q2 = []
                                for point in Q:
                                    transformed_point = apply_rigid_transform(R, t, np.array(point))
                                    Q2.append(transformed_point)
                                partner_interface_template.coord = Coords(Q2[1][0] - Q2[0][0], Q2[1][1] - Q2[0][1], Q2[1][2] - Q2[0][2])
                            partner_molecule_template.interface_template_list.append(partner_interface_template)
                            self.interface_template_list.append(partner_interface_template)

                    else:
                        print("this is an existing signature. using the existing interface template.")
                        # find the interface_template and partner_interface_template
                        interface_template = None
                        partner_interface_template = None
                        signature_conjugated = {
                            "dA": signature["dB"],
                            "dB": signature["dA"],
                            "dAB": signature["dAB"],
                            "thetaA": signature["thetaB"],
                            "thetaB": signature["thetaA"]
                        }
                        for mol_temp in self.molecules_template_list:
                            for interface_temp in mol_temp.interface_template_list:
                                if self._sig_are_similar(signature, interface_temp.signature, dist_thresh_intra, dist_thresh_inter, angle_thresh):
                                    interface_template = interface_temp
                                    molecule_template = mol_temp
                                    print(f"using {mol_temp.name} - {interface_temp.name}")
                                    break
                        for mol_temp in self.molecules_template_list:
                            for interface_temp in mol_temp.interface_template_list:
                                if self._sig_are_similar(signature_conjugated, interface_temp.signature, dist_thresh_intra, dist_thresh_inter, angle_thresh):
                                    partner_interface_template = interface_temp
                                    partner_molecule_template = mol_temp
                                    print(f"using {mol_temp.name} - {interface_temp.name}")
                                    break

                    # build the interfaces for molecules, link the interface template to interface

                    is_existing_interface, _ = self._is_existing_interface(interface_id, molecule)

                    if not is_existing_interface:
                        print(f"Creating new interface {interface_id} for molecule {mol_name}")
                        # create the interface
                        interface = BindingInterface(B)
                        interface.my_template = interface_template
                        interface.coord = self.all_interfaces_coords[self.all_chains.index([chain for chain in self.all_chains if chain.id == A][0])][i]
                        interface.my_residues = self.all_interfaces_residues[self.all_chains.index([chain for chain in self.all_chains if chain.id == A][0])][i]
                        self.interface_list.append(interface)
                        molecule.interface_list.append(interface)

                        print(f"Creating new interface {A} for partner molecule {B}")
                        # create the interface for the partner molecule
                        partner_interface = BindingInterface(A)
                        partner_interface.my_template = partner_interface_template
                        partner_interface.coord = I_B
                        partner_interface.my_residues = R_B
                        self.interface_list.append(partner_interface)
                        partner_molecule.interface_list.append(partner_interface)

                        # add the chains pair to self.binding_chains_pairs
                        if chain_id < interface_id:
                            binding_chains_pair = (chain_id, interface_id)
                        else:
                            binding_chains_pair = (interface_id, chain_id)
                        if binding_chains_pair not in self.binding_chains_pairs:
                            self.binding_chains_pairs.append(binding_chains_pair)
                    else:
                        print(f"Interface {interface_id} already exists for molecule {mol_name}")
                        print(f"Interface {A} already exists for molecule {B}")

        if self.verbose:
            # print the molecule template list and molecule list
            print("Molecule Template List:")
            for mol_template in self.molecules_template_list:
                print(mol_template)
            print("Molecule List:")
            for mol in self.molecule_list:
                print(mol)
            print("Interface Template List:")
            for interface_template in self.interface_template_list:
                print(interface_template)
            print("Interface List:")
            for interface in self.interface_list:
                print(interface)

        # update the interfaces list of each molecule based on the molecule template
        for group in self.chains_group:
            for i, chain_id in enumerate(group):
                # determin the COM and interfaces of the corresponding molecule template
                molecule_template = [mol_template for mol_template in self.molecules_template_list if mol_template.name == self.chains_map[chain_id]][0]
                molecule_0 = [mol for mol in self.molecule_list if mol.name == group[0]][0]
                com_coord = molecule_0.coord
                interface_coords = [interface_template.coord + com_coord for interface_template in molecule_template.interface_template_list]
                interface_template_ids = [interface_template.name for interface_template in molecule_template.interface_template_list]

                # calculate the R and t for the rigid transformation
                if i == 0:
                    # calculate the normal_point for this molecule
                    molecule = [mol for mol in self.molecule_list if mol.name == chain_id][0]
                    molecule.normal_point = [com_coord.x, com_coord.y, com_coord.z + 1] # normal_point - COM is [0,0,1]
                    # no need to transform the first chain
                    continue
                else:
                    chain1 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == group[0]][0])]
                    chain2 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == chain_id][0])]
                    R, t = rigid_transform_chains(chain1, chain2)
                    com_coord_transformed = apply_rigid_transform(R, t, np.array([com_coord.x, com_coord.y, com_coord.z]))
                    interface_coords_transformed = []
                    for interface_coord in interface_coords:
                        interface_coord_transformed = apply_rigid_transform(R, t, np.array([interface_coord.x, interface_coord.y, interface_coord.z]))
                        interface_coords_transformed.append(interface_coord_transformed)
                    normal_point_transformed = apply_rigid_transform(R, t, np.array([com_coord.x, com_coord.y, com_coord.z + 1]))
                    # update the COM and interfaces of the molecule
                    molecule = [mol for mol in self.molecule_list if mol.name == chain_id][0]
                    molecule.coord = Coords(com_coord_transformed[0], com_coord_transformed[1], com_coord_transformed[2])
                    for j, interface in enumerate(molecule.interface_list):
                        # find the corresponding interface template
                        interface_template_id = interface.my_template.name
                        for k, intf_template in enumerate(interface_template_ids):
                            if interface_template_id == intf_template:
                                interface.coord = Coords(interface_coords_transformed[k][0], interface_coords_transformed[k][1], interface_coords_transformed[k][2])
                                break
                    molecule.normal_point = [normal_point_transformed[0], normal_point_transformed[1], normal_point_transformed[2]]

        if self.verbose:
            # print the updated molecule list
            print("Updated Molecule List After Regularization:")
            for mol in self.molecule_list:
                print(mol)

        self._update_interface_templates_free_required_list()

        if self.verbose:
            print("Molecule Template List After Regularization:")
            for molecule_template in self.molecules_template_list:
                print(molecule_template)

        self._build_reactions()

        # print the reactions
        if self.verbose:
            print("Reactions:")
            for reaction in self.reaction_list:
                print(reaction)
            print("Reaction Templates:")
            for reaction_template in self.reaction_template_list:
                print(reaction_template)

    def calculate_binding_energies(self):
        """
        Calculates binding energies (in Rosetta Energy Units) for each pair in
        binding_chains_pairs using PyRosetta. By default, tries to pack/minimize
        the combined pose to get a rough binding energy estimate.
        """
        # calculate the binding free energy between the two chains using PyRosetta
        for _, binding_chains_pair in enumerate(self.binding_chains_pairs):
            print(f"Calculating binding free energy for {binding_chains_pair[0]} and {binding_chains_pair[1]}...")
            chain1 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == binding_chains_pair[0]][0])]
            chain2 = self.all_chains[self.all_chains.index([chain for chain in self.all_chains if chain.id == binding_chains_pair[1]][0])]
            binding_free_energy = self.calculate_binding_free_energy(chain1, chain2)
            print(f"Binding free energy between {binding_chains_pair[0]} and {binding_chains_pair[1]}: {binding_free_energy} REU")
            self.binding_energies.append(binding_free_energy)

    def print_binding_energies(self):
        """
        Prints the binding energies for each chain pair in binding_chains_pairs.
        """
        for i, binding_energy in enumerate(self.binding_energies):
            print(f"Binding energy between {self.binding_chains_pairs[i][0]} and {self.binding_chains_pairs[i][1]}: {binding_energy} REU")

    def calculate_binding_free_energy(self, chain1, chain2, fix_missing_atoms: bool = False):
        """
        Calculates the binding free energy between two chains using PyRosetta,
        optionally fixing missing side chains or atoms.

        Args:
            chain1 (Bio.PDB.Chain.Chain): The first chain.
            chain2 (Bio.PDB.Chain.Chain): The second chain.
            fix_missing_atoms (bool, optional): If True, attempts to pack rotamers
                for missing side chains. Defaults to True.

        Returns:
            float: The binding free energy in Rosetta Energy Units (REU).
        """
        import os
        import pyrosetta
        from pyrosetta.rosetta.protocols.minimization_packing import PackRotamersMover, MinMover

        # Mute most PyRosetta output for clarity
        pyrosetta.init(extra_options="-mute all -out:level 0")

        # Utility: rename chains to single characters (A and B)
        def rename_chain(chain, new_id):
            renamed_chain = Chain(new_id)
            for residue in chain.get_residues():
                renamed_chain.add(residue)
            model = Model(0)
            model.add(renamed_chain)
            return model

        # Step 1: Create a Model object with chain ID 'A' or 'B'
        model1 = rename_chain(chain1, 'A')
        model2 = rename_chain(chain2, 'B')

        # Step 2: Save the chain1 and chain2 to temporary PDB files
        pdbio = PDBIO()
        pdbio.set_structure(model1)
        pdbio.save("chain1_temp.pdb")

        pdbio.set_structure(model2)
        pdbio.save("chain2_temp.pdb")

        # Step 3: Load the chains into PyRosetta as separate poses
        pose1 = pyrosetta.pose_from_file("chain1_temp.pdb")
        pose2 = pyrosetta.pose_from_file("chain2_temp.pdb")

        # Remove temporary files
        os.remove("chain1_temp.pdb")
        os.remove("chain2_temp.pdb")

        # Step 4: Create a combined pose (the "complex")
        pose_complex = pose1.clone()
        pose_complex.append_pose_by_jump(pose2, pose_complex.size())

        # Step 5: Attempt to fix missing atoms / fill side chains
        sf = pyrosetta.get_fa_scorefxn()
        if fix_missing_atoms:
            pack_mover = PackRotamersMover(sf)
            pack_mover.apply(pose_complex)

        # Step 6: Do a short minimization to relieve clashes
        min_mover = MinMover()
        min_mover.score_function(sf)
        min_mover.min_type("lbfgs_armijo_nonmonotone")
        min_mover.apply(pose_complex)

        # Step 7: Score the complex vs. individual chains
        energy_complex = sf(pose_complex)
        energy_chain1 = sf(pose1)
        energy_chain2 = sf(pose2)

        binding_free_energy = energy_complex - (energy_chain1 + energy_chain2)
        return binding_free_energy
    
    def _generate_mol_file(self):
        """
        Generates a .mol file for each molecule template in self.molecules_template_list.

        The file format is the standard NERDSS .mol layout, for example:
            Name = A
            checkOverlap = true

            D = [1.00, 1.00, 1.00]

            Dr = [1.00, 1.00, 1.00]

            COM    0.0000    0.0000    0.0000
            X      5.4321    0.1234    3.2109
            ...
            
            bonds = N
            com X
            com Y
            ...

        Each BindingInterfaceTemplate's coord is relative to COM = (0,0,0).
        """
        import os

        for mol_template in self.molecules_template_list:
            filename = f"{mol_template.name}.mol"
            with open(filename, "w") as f:
                f.write(f"Name = {mol_template.name}\n")
                f.write("checkOverlap = true\n\n")

                # Default translational/rotational diffusion (you can customize)
                f.write("D = [10.00, 10.00, 10.00]\n\n")
                f.write("Dr = [0.1, 0.1, 0.1]\n\n")

                f.write("COM\t0.0000\t0.0000\t0.0000\n")

                # Each interface: interface name + (x, y, z) from .coord
                for intf_template in mol_template.interface_template_list:
                    x = intf_template.coord.x / 10  # Convert to nm
                    y = intf_template.coord.y / 10
                    z = intf_template.coord.z / 10
                    f.write(f"{intf_template.name}\t{x:.6f}\t{y:.6f}\t{z:.6f}\n")

                f.write("\n")
                # 'bonds' lines: by convention in NERDSS, we typically connect COM -> each interface
                num_interfaces = len(mol_template.interface_template_list)
                f.write(f"bonds = {num_interfaces}\n")
                for intf_template in mol_template.interface_template_list:
                    f.write(f"com {intf_template.name}\n")

            print(f"Generated .mol file: {filename}")

    def _generate_inp_file(self, inp_filename = "parms.inp", is_box = True, is_sphere = False):
        """
        Generates a .inp file (commonly named e.g. 'parms.inp') for the entire system,
        including parameters, boundary conditions, molecules copy numbers, and the
        reactions from self.reaction_template_list.

        - The rates, iteration counts, and boundary conditions here are default. Adjust as needed.
        - The 'start molecules' block uses a default copy number. Adjust as needed.
        - Reaction lines come from ReactionTemplate objects and their .expression, .binding_radius, .binding_angles, etc.

        Args:
            inp_filename (str, optional): Output .inp filename. Defaults to "parms.inp".
            is_box (bool, optional): If True, uses a box boundary condition. Defaults to True.
            is_sphere (bool, optional): If True, uses a spherical boundary condition. Defaults to False.
        """
        import os

        nItr = 1000000
        timeStep = 0.1
        timeWrite = 100000
        trajWrite = 10000000
        pdbWrite = 100000
        restartWrite = 1000000
        scaleMaxDisplace = 100.0
        overlapSepLimit = 1.7

        boxSize = [100.0, 100.0, 100.0]

        sphereR = 100.0

        default_copy_number = 30

        default_on_rate = 1000.0
        default_off_rate = 0.0

        with open(inp_filename, "w") as f:
            # ------------------ start parameters --------------------
            f.write("start parameters\n")
            f.write(f"\tnItr = {nItr}\n")
            f.write(f"\ttimeStep = {timeStep}\n")
            f.write(f"\ttimeWrite = {timeWrite}\n")
            f.write(f"\ttrajWrite = {trajWrite}\n")
            f.write(f"\tpdbWrite = {pdbWrite}\n")
            f.write(f"\trestartWrite = {restartWrite}\n")
            f.write(f"\tscaleMaxDisplace = {scaleMaxDisplace}\n")
            f.write(f"\toverlapSepLimit = {overlapSepLimit}\n")
            f.write("end parameters\n\n")

            # ------------------ start boundaries --------------------
            f.write("start boundaries\n")
            if is_box:
                f.write(f"\tWaterBox = [{boxSize[0]}, {boxSize[1]}, {boxSize[2]}]\n")
            elif is_sphere:
                f.write("\tisSphere = true\n")
                f.write(f"\tsphereR = {sphereR}\n")
            f.write("end boundaries\n\n")

            # ------------------ start molecules ---------------------
            f.write("start molecules\n")
            for mol_template in self.molecules_template_list:
                f.write(f"\t{mol_template.name} : {default_copy_number}\n")
            f.write("end molecules\n\n")

            # ------------------ start reactions ---------------------
            f.write("start reactions\n")
            for r_template in self.reaction_template_list:
                # The reaction template already has an expression like:
                #   A(x) + B(y) <-> A(x!1).B(y!1)
                # We simply write it out, then specify rates, geometry, etc.
                f.write(f"\t{r_template.expression}\n")

                # For demonstration, use a default on/off or your own logic:
                f.write(f"\t\tonRate3Dka = {default_on_rate}\n")
                f.write(f"\t\toffRatekb = {default_off_rate}\n")

                # The 'sigma' can be set to the binding radius from the template
                brad = getattr(r_template, "binding_radius", 5.0)
                brad = brad / 10  # Convert to nm
                f.write(f"\t\tsigma = {brad:.7f}\n")

                # set bindRadSameCom
                f.write("\t\tbindRadSameCom = 1.5\n")

                # set loopCoopFactor
                f.write("\t\tloopCoopFactor = 1.0\n")

                angles = getattr(r_template, "binding_angles", [])
                if angles:
                    angle_str = ", ".join(f"{ang}" for ang in angles)
                    f.write(f"\t\tassocAngles = [{angle_str}]\n")
                else:
                    # Fallback to nans if no angles are available
                    f.write("\t\tassocAngles = [nan, nan, nan, nan, nan]\n")
                # set norm1 and norm2
                norm1 = getattr(r_template, "norm1", [])
                norm2 = getattr(r_template, "norm2", [])
                f.write(f"\t\tnorm1 = [{norm1[0]:.6f}, {norm1[1]:.6f}, {norm1[2]:.6f}]\n")
                f.write(f"\t\tnorm2 = [{norm2[0]:.6f}, {norm2[1]:.6f}, {norm2[2]:.6f}]\n")

                f.write("\t\texcludeVolumeBound = False\n\n")

            f.write("end reactions\n")

        print(f"Generated .inp file: {inp_filename}")

    
    def generate_nerdss_ready_files(self, inp_filename = "parms.inp", is_box = True, is_sphere = False):
        """
        Generates NERDSS-ready files for running the NERDSS simulation by:
          1. Creating a .mol file for each MoleculeTemplate (via _generate_mol_file()).
          2. Creating a single .inp file containing all parameters and reaction info
             (via _generate_inp_file()).

        After calling this, you should have:
          - A set of *.mol files (one per distinct molecule template).
          - A 'parms.inp' (or similar) file describing the simulation parameters/boundaries,
            the molecules, and the reactions.

        Args:
            inp_filename (str, optional): Output .inp filename. Defaults to "parms.inp".
            is_box (bool, optional): If True, uses a box boundary condition. Defaults to True.
            is_sphere (bool, optional): If True, uses a spherical boundary condition. Defaults to False.
        """
        self._generate_mol_file()
        self._generate_inp_file(inp_filename, is_box, is_sphere)
        print("All NERDSS-ready files generated successfully!")
