
class ProteinComplex():
    """This object contains all the functions (as methods) necessary to edit a protein complex input using a .pdb file downloaded from a database. Then once you are done editing, 
    it can output it as  as NERDSS input, a new .pdb file, or a 3D graph of the complex.
    """


    def __init__(self,FileName: str,ChainsIncluded: list = [None], MaxBoundLength: float = 0.3, symmetry_applied: bool = False):
        """Initilizes the ProteinComplex object by reading off of a .pdb file

        Args:
            Filename (str): The full path of the desired PDB file or name of the file if in same directory. 
            ChainsIncluded (list, optional): A list of which chains you want to be included. MUST BE MORE THAN 2!
        """
        from . import dtb_PDB_separate_read

        if len(ChainsIncluded) >= 2 or ChainsIncluded == [None]:
            self.reaction_chain, self.int_site, self.int_site_distance, self.unique_chain, self.COM = dtb_PDB_separate_read(FileName,ChainsIncluded, MaxBoundLength, symmetry_applied)
            self.one_site_chain = ['na']
        else:
            raise Exception('The ChainsIncluded list, if included, must be greater then 2')


    ## EDITS DATA ##

    def calc_angle(self,NormVector: list = [0.,0.,1.]):
        """This function calculates the 5 associating angles of each pair of interfaces.
        The default normal vector will be assigned as (0, 0, 1). If the co-linear issue occurs, 
        the system will use (0, 1, 0) instead to resolve co-linear issue. The calculated 5 angles 
        will be shown on the screen automatically.
        

        Args:
            NormVector (list, optional): The normal vector used to calculate the angles
            ThrowError(bool, optional): If a co-linear or syntax error occurs, whether 
            it will continue or stop the program


        """
        from . import dtb_PDB_calc_angle

        op = dtb_PDB_calc_angle((self.reaction_chain, self.int_site, self.int_site_distance, 
                                      self.unique_chain, self.COM),NormVector)
        if op[0] == False:
            return False
        else:
            self.set_self_from_tuple(op)
            return True
    


    def norm_COM(self):
        """Normalizes the COM of each chain in the given Result and subtracts the interface coordinates of each chain by their respective COM.
        
        If calc_angles has NOT been run, this function will fail
        """
        from . import dtb_PDB_norm_COM 

        if self.one_site_chain == ["na"]:
            raise Exception("In order to run this function, you must have previously run calc_angle.")

        op = dtb_PDB_norm_COM((self.reaction_chain, self.int_site, self.int_site_distance, 
                                    self.unique_chain, self.COM, self.angle, self.normal_point_lst1, 
                                    self.normal_point_lst2, self.one_site_chain))
        self.set_self_from_tuple(op)



    def filter(self,ChainList):
        """This function will filter the desired chain according to the input list of chain and exclude all the 
            unnecessary coordinate information for future analysis.
        Args:
            ChainList (list): The desired name of chains that users intend to examine. 

        This function must be run before calc_angles or it will fail.
        """
        from . import dtb_PDB_filter

        if self.one_site_chain != ["na"]:
            raise Exception("This function must be run before calc_angles")


        op =  dtb_PDB_filter((self.reaction_chain, self.int_site, self.int_site_distance, self.unique_chain, self.COM),ChainList)

        self.set_self_from_tuple(op)



    def change_sigma(self,ChangeSigma: bool = False, SiteList: list = [], NewSigma: list = []):
        """This function allows users to change the value of sigma (the distance between two binding interfaces). 
        The new sigma value and the corresponding coordinates of interfaces will be shown on the screen and the 
        returns will contain all the information for further analysis. 

        Args:
            ChangeSigma (bool, optional): If True, the users are capable of changing the sigma value; 
                                        if False, the sigma will remain as the original ones. 
            SiteList (list, optional): It consists of the serial numbers of the pair of interfaces for which 
                                    the user needs to modify the sigma value. The serial number is determined 
                                    by the pairing sequence shown by the function ‘real_PDB_separate_read’. 
                                    The serial number should be no greater than the total number of interface 
                                    pairs and no smaller than 0. If the serial number is 0, it means to change 
                                    all pairs of interfaces into a same sigma value.
            NewSigma (list, optional): It consists of the actual sigma value that users desire to change, according 
                                    to the sequence of input ‘SiteList’. 

        This function must be run before calc_angles or it will fail.
        """
        from . import dtb_PDB_change_sigma

        if self.one_site_chain != ["na"]:
            raise Exception("This function must be run before calc_angles")


        op = dtb_PDB_change_sigma((self.reaction_chain, self.int_site, self.int_site_distance, 
                                    self.unique_chain, self.COM),ChangeSigma,SiteList,NewSigma)
        self.set_self_from_tuple(op)
    

    ## OUTPUTS DATA ##

    def write_input(self):
        """Generates a PDB file containing the calculated COMs and reaction interfaces for visualization and comparison with the 
        original PDB file. The input must be the output result of the 'real_PDB_separate_read' function. Note that the unit for 
        the coordinates in the PDB file is Angstrom, not nm, so the values will be 10 times larger than those in NERDSS input 
        files.

        If calc_angles has NOT been run, this function will fail
        """
        from . import dtb_PDB_write_input

        if self.one_site_chain == ["na"]:
            raise Exception("In order to run this function, you must have previously run calc_angle.")
        
        dtb_PDB_write_input((self.reaction_chain, self.int_site, self.int_site_distance, 
                                    self.unique_chain, self.COM, self.angle, self.normal_point_lst1, 
                                    self.normal_point_lst2, self.one_site_chain))



    def plot_3D(self):
        """Generate a 3D plot to display the spatial geometry of each simplified chain.
        """
        from . import dtb_PDB_3D_plot

        dtb_PDB_3D_plot((self.reaction_chain, self.int_site, self.int_site_distance, 
                                    self.unique_chain, self.COM))
        


    def write_PDB(self):
        """Generate a 3D plot to display the spatial geometry of each simplified chain.
        """
        from . import dtb_PDB_write_PDB

        dtb_PDB_write_PDB((self.reaction_chain, self.int_site, self.int_site_distance, 
                                    self.unique_chain, self.COM))


    ## GENERAL METHODS ###

    def set_self_from_tuple(self,op: tuple):
        """Will turn outputted tuple into attributes of this object

        Args:
            op (tuple): The output of one of the functions
        """

        if len(op) == 5:
            self.reaction_chain, self.int_site, self.int_site_distance, self.unique_chain, self.COM = op
        elif len(op) == 9:
            self.reaction_chain, self.int_site, self.int_site_distance, self.unique_chain, self.COM, self.angle, self.normal_point_lst1, self.normal_point_lst2, self.one_site_chain = op
        else:
            raise Exception('The tuple must have a length of 5 or 9')


