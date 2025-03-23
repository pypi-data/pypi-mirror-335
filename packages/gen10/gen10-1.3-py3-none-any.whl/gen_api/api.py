from random import randint
import pandas as pd
import os
import requests

from Bio.PDB import PDBParser
import matplotlib.pyplot as plt # this is API-specific for protein structure visualization
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
from matplotlib import cm

import random
import webbrowser # not sure if using it

import gen_api

dirpath = os.path.dirname(os.path.abspath(__file__))

def dna2rna(dna):
    """Returns RNA string by inputting a DNA string"""
    rna = ""
    for base in dna:
        if base=='A' or base=='a':
            rna+='U'
        elif base=='T' or base=='t':
            rna+='A'
        elif base=='C' or base=='c':
            rna+='G'
        elif base=='G' or base=='g':
            rna+='C'
        else:
            raise ValueError('Could not read provided DNA string')
    return rna

def rna2amino(rna):
    """Returns amino acids by inputting an RNA string"""
    amino=''
    codon_catalog = {'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu',
                     'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser',
                     'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'STOP', 'UAG': 'STOP',
                     'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'STOP', 'UGG': 'Trp',
                     'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
                     'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro',
                     'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
                     'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg',
                     'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met',
                     'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr',
                     'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
                     'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
                     'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val',
                     'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala',
                     'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
                     'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'
                     }
    for i in range(0, len(rna)-2, 3):
        codon = str(rna[i]+rna[i+1]+rna[i+2])
        if codon in codon_catalog:
            if codon_catalog[codon]=='STOP':
                break
            amino+= ' ' + codon_catalog[codon]
        else:
            raise ValueError(f'Error: invalid codon {codon}')
    return amino

def dna2amino(dna):
    """Returns amino acids by inputting an DNA string"""
    rna = ""
    for base in dna:
        if base=='A' or base=='a':
            rna+='U'
        elif base=='T' or base=='t':
            rna+='A'
        elif base=='C' or base=='c':
            rna+='G'
        elif base=='G' or base=='g':
            rna+='C'
        else:
            raise ValueError('Could not read provided DNA string')

    amino=''

    codon_catalog = {'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu',
                     'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser',
                     'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'STOP', 'UAG': 'STOP',
                     'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'STOP', 'UGG': 'Trp',
                     'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
                     'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro',
                     'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
                     'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg',
                     'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met',
                     'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr',
                     'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
                     'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
                     'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val',
                     'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala',
                     'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
                     'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'
                     }
    for i in range(0, len(rna)-2, 3):
        codon = str(rna[i]+rna[i+1]+rna[i+2])
        if codon in codon_catalog:
            if codon_catalog[codon]=='STOP':
                break
            amino+= ' ' + codon_catalog[codon]
        else:
            raise ValueError(f'Error: invalid codon {codon}')
    return amino

def rna2dna(rna):
    """Returns DNA string by inputting a DNA string"""
    dna = ""
    for base in rna:
        if base == 'U' or base == 'u':
            dna += 'A'
        elif base == 'A' or base == 'a':
            dna += 'T'
        elif base == 'G' or base == 'g':
            dna += 'C'
        elif base == 'C' or base == 'c':
            dna += 'G'
        else:
            raise ValueError('Could not read provided RNA string')
    return dna

def compare(original, copy):
    """Compares two different string (original, copy) and return True or False with the reason"""
    if len(original) != len(copy):
        return 'not same length'
    else:
        for i in range(len(original)):
            if original[i]!=copy[i]:
                return f'Difference in {i+1} base/aminoacid'
        return "Identical"

def check(string):
    if len(string)%3 == 0:
        if string[:3]=='TAC' and (string[-3:]=='ATT' or string[-3:]=='ATC' or string[-3:]=='ACC'):
            return 'Valid DNA string'
        elif string[:3]=='AUG' and (string[-3:]=='UAA' or string[-3:]=='UAG' or string[-3:]=='UGG'):
            return 'Valid RNA string'
        else:
            raise ValueError('Invalid string (starting/ending codons not found)')
    else:
        raise ValueError('String could not be divided into codons.')

def read_input(path):
    """if string return string; if a txt file path returns string in file"""
    if path[-3:]=='txt':
        try:
            file = open(path, 'r')
            contents = list()
            for line in file:
                contents.append(line.replace('\n', ''))
            return contents
        except OSError or KeyError:
            raise ValueError('Could not open file, please, check user guide.')
    elif path[-3:]=='pdf' or path[-3:]=='doc' or path[-4:]=='docx' or path[-3:]=='csv' or path[-4:]=='xlsx' or path[-4:]=='html':
        raise ValueError("File type must be 'txt'")
    else:
        return path

def createmutation(string):
    bases = ['A', 'T', 'C', 'G']
    mutated = ""

    while True:
        muttype = random.choices([1, 5, 6], weights=[75, 15, 10], k=1)[0] # weighted probabilties for biological reality
        index = random.randint(0, len(string) - 1)

        if muttype == 1:  # Substitution
            # Handle transition/transversion probabilities
            purines = ['A', 'G']
            pyrimidines = ['C', 'T']
            if string[index] in purines: # transititions are 2x more likely than transversions
                new_base = random.choices(purines + pyrimidines, weights=[2, 2, 1, 1], k=1)[0]
            else:
                new_base = random.choices(pyrimidines + purines, weights=[2, 2, 1, 1], k=1)[0]
            mutated = string[:index] + new_base + string[index + 1:]
        elif muttype == 5:  # Deletion
            del_length = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0] # weighted random selection for length (1–3 bases)
            del_length = min(del_length, len(string) - index) # avoid index out of range
            mutated = string[:index] + string[index + del_length:]

        elif muttype == 6:  # Insertion
            insert_length = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0] # weighted random selection for length (1-3 bases)
            insert_bases = ''.join(random.choices(bases, k=insert_length))
            mutated = string[:index] + insert_bases + string[index:]

        # Break the loop if the mutation differs from the original
        if mutated != string:
            break

    return mutated

def iterate(strings, functions, filepath=dirpath, filename="results.csv"):
    """Creates a CSV file in your directory with the information you request."""
    """The argument consits of a list of strings and a list of functions"""
    columns = ['input']+[function for function in functions]
    df = pd.DataFrame(columns=columns)

    if not strings:
        raise ValueError("No input sequences provided, check your input.")
    if not functions:
        raise ValueError("No functions provided, check your input.")
    for string in strings:
        memory = [string]
        for function in functions:
            method = globals().get(function)
            if method:
                result = method(string)
            else:
                result = "Function not available"
            memory.append(result)
        df = pd.concat([df ,pd.DataFrame([memory], columns=columns)], ignore_index=True)

    # df.to_csv(filepath.join(filename), index=False)
    df.to_csv(f'{filepath}/{filename}', index=False)
    return df

def tosingle(sin):
    inp = sin.split()
    sout = ''
    for base in inp:
        sout+=base[0]
    return sout

def alphafold_prediction(uniprot_id):
    url = f'https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}'
    response = requests.get(url)
    if response.status_code == 200:
        request_output = response.json()
        return request_output[0]
    else:
        raise ValueError(f'Failed to fetch data: {response.status_code}')
        return None

def generate_protein(structure_dict, filepath='alphafold_protein_structure_prediction.pdb', show=True):
    url = structure_dict['pdbUrl']
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content
        with open(filepath, 'wb') as f:
            f.write(content)

        parser = PDBParser()
        structure = parser.get_structure("alphafold_protein_structure_prediction.pdb", filepath)

        # Extract atomic coordinates
        x_coords = []
        y_coords = []
        z_coords = []
        accuracy_scores = []

        for atom in structure.get_atoms():
            x, y, z = atom.coord
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
            accuracy_scores.append(atom.bfactor)

        # Normalize colors
        norm = Normalize(vmin=0, vmax=100)
        cmap = cm.hsv
        colors = cmap(norm(accuracy_scores))

        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x_coords, y_coords, z_coords, c=colors, s=20, alpha=0.7, edgecolors='k')
        ax.plot(x_coords, y_coords, z_coords, color='black', linewidth=1.0, alpha=0.7)

        # Add labels
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')
        cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, pad=0.1)
        cbar.set_label("Prediction Accuracy (0%-100%)")

        plt.grid(True)
        if show is True:
            plt.show()

    else:
        raise ValueError(f'Failed to fetch protein structure data. HTTP response code: {response.status_code}')

def cut_dna(dna, cut_pos):
    """Cuts the DNA at the specified position."""
    if cut_pos<0 or cut_pos>=len(dna):
        raise ValueError("Cut position is out of bounds.")
    return dna[:cut_pos] + '|' + dna[cut_pos:]

def repair_dna(dna, repair_type, cut_pos=None, repair_sequence=None):
    """Repairs the DNA after a cut."""

    if '|' in dna:
        cut_pos = dna.index('|')  # Set cut position from the cut marker '|'
        dna = dna.replace('|', '')  # Remove the cut marker from the DNA sequence

    # Check if repair_type and repair_sequence are valid
    if repair_type == 'NHEJ':
        # Simulate deletion: remove one base from the cut position
        return dna[:cut_pos] + dna[cut_pos+1:]

    elif repair_type == 'HDR' and repair_sequence:
        # Simulate insertion: insert the repair sequence at the cut position
        return dna[:cut_pos] + repair_sequence + dna[cut_pos:]

    else:
        raise ValueError("Invalid repair type or missing repair sequence for HDR.")

def find(string, sequence):
    # Check both are strings
    if not isinstance(string, str) or not isinstance(sequence, str):
        raise TypeError("Both 'string' and 'sequence' must be of type str.")

    # Check string is longer than sequence
    if len(string) < len(sequence):
        raise ValueError(
            "Second string is longer than the first one. Check your input to ensure the global string is the first.")

    # Check if the sequence exists in the string
    if sequence not in string:
        raise ValueError("Sequence could not be found in your global string.")

    # Find all occurrences of the sequence
    occurrences = []
    start_index = 0
    while start_index < len(string):
        start_index = string.find(sequence, start_index)
        if start_index == -1:  # No more occurrences
            break
        end_index = start_index + len(sequence) - 1
        occurrences.append((start_index, end_index))
        start_index += 1  # Move to the next possible starting position

    return occurrences

def check_codon(string):

    # add internal dna2rna function (only for github CI testing)
    def dna2rna(dna):
        rna = ""
        for base in dna:
            if base == 'A' or base == 'a':
                rna += 'U'
            elif base == 'T' or base == 't':
                rna += 'A'
            elif base == 'C' or base == 'c':
                rna += 'G'
            elif base == 'G' or base == 'g':
                rna += 'C'
            else:
                raise ValueError('Could not read provided DNA string')
        return rna

    if string=='':
        raise ValueError("The provided string is empty, check your input.")

    # Check if string length is divisible by 3
    if len(string) % 3 != 0:
        if len(string) < 3:
            raise ValueError(f"String couldn't be divided into codons: {string}")
        if len(string) % 2 == 0:
            resting = string[-1]
        else:
            resting = string[-2:]
        raise ValueError(f"String couldn't be divided into codons without the following rest: {resting}")

    if 'u' not in string or 'U' not in string:
        stringmem = string
        string = ''
        for letter in stringmem:
            try:
                string += dna2rna(letter)
            except ValueError:
                string += letter

    # Define codon catalog
    codon_catalog = {
        'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu',
        'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser',
        'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'STOP', 'UAG': 'STOP',
        'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'STOP', 'UGG': 'Trp',
        'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
        'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro',
        'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
        'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg',
        'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met',
        'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr',
        'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
        'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
        'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val',
        'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala',
        'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
        'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'
    }

    # Find invalid codons
    invalid_codons = []
    for i in range(0, len(string), 3):
        codon = string[i:i+3]
        if codon not in codon_catalog:
            invalid_codons.append(codon)

    return invalid_codons
