"""
data_structures.py

Contains core data classes used by the NERDSS coarse-graining pipeline,
including molecules, interfaces, reactions, and basic coordinate storage.
"""

class MoleculeTemplate:
    """
    Represents a molecule type in NERDSS, including the molecule's center of mass
    (COM) and a list of binding interfaces (BindingInterfaceTemplate objects).

    Attributes:
        name (str): The name or identifier of this molecule type.
        interface_template_list (list): A collection of BindingInterfaceTemplate objects
            that describe binding sites for this molecule type.
    """
    def __init__(self, name: str):
        """
        Initializes a MoleculeTemplate.

        Args:
            name (str): The name of the molecule type.
        """
        self.name = name
        self.interface_template_list = []
        self.normal_point = [0,0,1]

    def __str__(self):
        molecule_template_info = f"Molecule Template: {self.name}\n"
        for interface_template in self.interface_template_list:
            molecule_template_info += f"  Interface Template: {interface_template}\n"
        return molecule_template_info


class BindingInterfaceTemplate:
    """
    Represents the information about a binding interface template between molecules.

    Attributes:
        name (str): The name/identifier of the interface template.
        coord (Coords): The coordinates of the interface relative to the
            center of mass of its parent molecule.
        my_residues (list): The residues that compose this interface.
        required_free_list (list): A list of other interface
            templates that must be free (unbound) for this interface to bind.
    """
    def __init__(self, name: str):
        """
        Initializes an BindingInterfaceTemplate.

        Args:
            name (str): The name/identifier of the interface template.
        """
        self.name = name
        self.coord = None
        self.my_residues = []
        self.required_free_list = [] # The list of interface templates that need to be free to bind to this interface template
        signature = {}

    def __str__(self):
        interface_template_info = f"Interface Template: {self.name}\n"
        interface_template_info += f"  Coordinates: {self.coord}\n"
        for residue in self.my_residues:
            interface_template_info += f"  Residue: {residue}\n"
        for interface_template in self.required_free_list:
            interface_template_info += f"  Interface Template Required Free: {interface_template}\n"
        return interface_template_info


class CoarseGrainedMolecule:
    """
    Represents a coarse-grained molecule in NERDSS, potentially derived from
    a PDB chain.

    Attributes:
        name (str): The name/identifier of the molecule.
        my_template (MoleculeTemplate): The MoleculeTemplate this molecule is based on.
        coord (Coords): The center-of-mass coordinates of the molecule.
        interface_list (list): A list of Interface objects defining binding sites.
    """
    def __init__(self, name: str):
        """
        Initializes a CoarseGrainedMolecule.

        Args:
            name (str): The name or identifier of the molecule.
        """
        self.name = name
        self.my_template = None
        self.coord = None
        self.interface_list = []
        self.normal_point = None

    def __str__(self):
        molecule_info = f"CoarseGrainedMolecule: {self.name}\n"
        molecule_info += f"  Template: {self.my_template}\n"
        molecule_info += f"  Coordinates: {self.coord}\n"
        for interface in self.interface_list:
            molecule_info += f"  Interface: {interface}\n"
        return molecule_info


class BindingInterface:
    """
    Represents a binding interface between two Molecule objects.

    Attributes:
        name (str): The chain ID or name of the binding partner.
        coord (Coords): The position of this interface.
        my_template (BindingInterfaceTemplate): The interface template for this interface.
        my_residues (list): The residues included in this interface.
    """
    def __init__(self, name: str):
        """
        Initializes an BindingInterface.

        Args:
            name (str): Name/identifier for this interface (usually the partner chain ID).
        """
        self.name = name
        self.coord = None
        self.my_template = None
        self.my_residues = []
        signature = {}

    def __str__(self):
        interface_info = f"BindingInterface: {self.name}\n"
        interface_info += f"  Template: {self.my_template}\n"
        interface_info += f"  Coordinates: {self.coord}\n"
        interface_info += f"  Residue counts: {len(self.my_residues)}\n"
        for residue in self.my_residues:
            interface_info += f"  Residue: {residue}\n"
        return interface_info


class ReactionTemplate:
    """
    Stores information for a reaction template between two Molecule templates.

    Attributes:
        expression (str): A textual representation of the reaction.
        reactants (list): A list of reactant molecule/interface template strings.
        products (list): A list of product molecule/interface template strings.
        binding_angles (tuple): A tuple describing binding angles (theta1, theta2, phi1, phi2, omega).
        binding_radius (float): The distance between the binding interfaces.
    """
    def __init__(self):
        """
        Initializes a ReactionTemplate with no parameters set by default.
        """
        self.expression = None
        self.reactants = None
        self.products = None
        self.binding_angles = None
        self.binding_radius = None
        self.norm1 = None
        self.norm2 = None

    def __str__(self):
        reaction_template_info = f"Reaction Template: {self.expression}\n"
        reaction_template_info += f"  Reactants: {self.reactants}\n"
        reaction_template_info += f"  Products: {self.products}\n"
        reaction_template_info += f"  Binding Angles: {self.binding_angles}\n"
        reaction_template_info += f"  Binding Radius: {self.binding_radius / 10} nm\n"
        return reaction_template_info


class Reaction:
    """
    Stores information about an actual reaction between two Molecule objects.

    Attributes:
        expression (str): A textual representation of the reaction.
        reactants (list): A list of reactant molecules/interfaces.
        products (list): A list of product molecules/interfaces.
        binding_angles (tuple): A tuple describing binding angles (theta1, theta2, phi1, phi2, omega).
        binding_radius (float): The distance between the binding interfaces.
    """
    def __init__(self):
        """
        Initializes a Reaction with no parameters set by default.
        """
        self.expression = None
        self.reactants = None
        self.products = None
        self.binding_angles = None
        self.binding_radius = None
        self.norm1 = None
        self.norm2 = None

    def __str__(self):
        reaction_info = f"Reaction: {self.expression}\n"
        reaction_info += f"  Reactants: {self.reactants}\n"
        reaction_info += f"  Products: {self.products}\n"
        reaction_info += f"  Binding Angles: {self.binding_angles}\n"
        reaction_info += f"  Binding Radius: {self.binding_radius / 10} nm\n"
        return reaction_info


class Coords:
    """
    Holds the x, y, z coordinates of a 3D point. Includes basic vector arithmetic
    and distance calculation.

    Attributes:
        x (float): The x-coordinate.
        y (float): The y-coordinate.
        z (float): The z-coordinate.
    """
    def __init__(self, x: float, y: float, z: float):
        """
        Initializes a Coords instance.

        Args:
            x (float): x-coordinate.
            y (float): y-coordinate.
            z (float): z-coordinate.
        """
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def distance(self, other) -> float:
        """
        Calculates the Euclidean distance between two points.

        Args:
            other (Coords): The other point to calculate the distance to.

        Returns:
            float: The Euclidean distance between the two points.
        """
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)**0.5

    def __sub__(self, other):
        """
        Implements subtraction for Coords objects.

        Args:
            other (Coords): The other coordinate to subtract.

        Returns:
            Coords: The resulting coordinate.
        """
        return Coords(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        """
        Implements addition for Coords objects.

        Args:
            other (Coords): The other coordinate to add.

        Returns:
            Coords: The resulting coordinate.
        """
        return Coords(self.x + other.x, self.y + other.y, self.z + other.z)
