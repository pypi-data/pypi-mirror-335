import os
global monomer_path, aas_path, AminoAcids_path, aa_smiles_path

path_of_this_file = os.path.dirname(os.path.abspath(__file__))

monomer_path = os.path.join(path_of_this_file,'monomer.tsv')
aas_path = os.path.join(path_of_this_file,'aas.txt')
aa_smiles_path = os.path.join(path_of_this_file,'aa_smiles.txt')
AminoAcids_path = os.path.join(path_of_this_file,'AminoAcids.txt')