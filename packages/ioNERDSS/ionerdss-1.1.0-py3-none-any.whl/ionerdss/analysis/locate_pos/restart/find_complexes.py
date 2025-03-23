def find_complexes(sorted_complexes, NumDict):
    """Finds the complexes with the correct number of proteins of each type.
    
    Args:
        sorted_complexes (array): holds each complex as a subdictionary. Then each dictionaries key = name of a protein, value = list of protein indexes in that complex
        NumDict (dictionary): A dictionary that holds the requested number of protein types in a complex
    
    Returns:
        A list of integers representing the protein numbers that form the correct size /composition of a complex.
    """


    protein_remain = [] #list of proteins in the complexes (what is returned)
    protein_complex_hits = 0 #how many protein complexes have the correct number
    
    #each row of the dataframe
    for complex in sorted_complexes:

        #if row/protein complex has the correct number of each protein type
        correct_complex_size = True
        for protein_type,protein_list in complex.items():
            if len(protein_list) != NumDict[protein_type]:
                correct_complex_size = False
                break
        
        if correct_complex_size: 
            protein_complex_hits += 1
            
            #add every protein num that is in that complex
            for protein_num in protein_list:
                protein_remain.append(int(protein_num))
    
    #print success / failure
    if protein_complex_hits == 0:
        print('No complexes where found with the specific number of protein types.')
    else:
        print(f'Found {protein_complex_hits} protein complexes!')

    return protein_remain


