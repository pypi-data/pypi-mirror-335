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
#

dirpath = os.path.dirname(os.path.abspath(__file__))

def adn2arn(dna):
    """Retorna una cadena d'ARN introduïnt una cadena d'ADN"""
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
            raise ValueError("Error: no s'ha pogut llegir la cadena d'ADN.")
    return rna

def arn2amino(rna):
    """Retorna una cadena d'aminoàcids introduïnt una cadena d'ARN"""
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
            raise ValueError(f'Error: codó invàlid {codon}')
    return amino

def adn2amino(dna):
    """Retorna una cadena d'aminoàcids introduïnt una cadena d'ADN"""
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
            raise ValueError("Error: no s'ha pogut llegir la cadena d'ADN")

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
            raise ValueError(f'Error: códo invàlid {codon}')
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
            raise ValueError("No s'ha pogut llegir la cadena d'ARN.")
    return dna

def compara(original, copy):
    """Compara dues cadenes (original, copy) i retorna la diferència"""
    if len(original) != len(copy):
        return 'Longitud diferent'
    else:
        for i in range(len(original)):
            if original[i]!=copy[i]:
                return f'Diferència a la base/aminoàcid {i+1}'
        return "Idèntiques"

def comprova(string):
    if len(string)%3 == 0:
        if string[:3]=='TAC' and (string[-3:]=='ATT' or string[-3:]=='ATC' or string[-3:]=='ACC'):
            return "Cadena d'ADN vàlida"
        elif string[:3]=='AUG' and (string[-3:]=='UAA' or string[-3:]=='UAG' or string[-3:]=='UGG'):
            return "Cadena d'ARN vàlida"
        else:
            raise ValueError("Cadena invàlida (no s'ha trobat el códo inicial/final)")
    else:
        raise ValueError('Cadena no es pot dividir en codons.')

def llegir_input(path):
    """Si es una cadena retorna la cadena; si es el nom d'un arxiu retorna una llista del contingut"""
    if path[-3:]=='txt':
        try:
            file = open(path, 'r')
            contents = list()
            for line in file:
                contents.append(line.replace('\n', ''))
            return contents
        except OSError or KeyError:
            raise ValueError("No s'ha trobat l'arxiu, recorda que ha de ser a la mateix carpeta que aquest document.")
    elif path[-3:]=='pdf' or path[-3:]=='doc' or path[-4:]=='docx' or path[-3:]=='csv' or path[-4:]=='xlsx' or path[-4:]=='html':
        raise ValueError("El document ha de ser format 'txt'.")
    else:
        return path

def crearmutacio(string):
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

def iterar(strings, functions, filepath=dirpath, filename="resultats.csv"):
    """Crea un document CSV en aquesta carpeta amb la informació que demanis."""
    """L'argument consisteix d'una llista d'entrades i una llista de funcions"""
    columns = ['input']+[function for function in functions]
    df = pd.DataFrame(columns=columns)

    if not strings:
        raise ValueError("No hi ha seqüències, comprova l'input..")
    if not functions:
        raise ValueError("No hi ha funcions, comprova l'input.")
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

def asenzill(sin):
    inp = sin.split()
    sout=''
    for base in inp:
        sout+=base[0]
    return sout

def alphafold(uniprot_id):
    url = f'https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}'
    response = requests.get(url)
    if response.status_code == 200:
        request_output = response.json()
        return request_output[0]
    else:
        raise ValueError(f"Error a l'obtenir lesdades: {response.status_code}")
        return None

def generar_proteina(structure_dict, filepath='alphafold_protein_structure_prediction.pdb', show=True):
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
        ax.set_xlabel('Eix X')
        ax.set_ylabel('Eix Y')
        ax.set_zlabel('Eix Z')
        cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, pad=0.1)
        cbar.set_label("Seguretat de Predicció (0%-100%)")

        plt.grid(True)
        if show is True:
            plt.show()

    else:
        raise ValueError(f'Error al descarregar les dades. Codi: {response.status_code}')

def tallar_adn(dna, cut_pos):
    """Talla l'ADN al punt especificat."""
    if cut_pos<0 or cut_pos>=len(dna):
        raise ValueError('Posició especificada fora de l\'ADN')
    return dna[:cut_pos] + '|' + dna[cut_pos:]

def reparar_adn(dna, repair_type, pos_tall=None, nova_sequencia=None):
    """Repara l'ADN tallat."""

    if '|' in dna:
        pos_corte = dna.index('|')  # Set cut position from the cut marker '|'
        dna = dna.replace('|', '')  # Remove the cut marker from the DNA sequence

    # Check if repair_type and repair_sequence are valid
    if repair_type == 'NHEJ':
        # Simulate deletion: remove one base from the cut position
        return dna[:pos_tall] + dna[pos_tall+1:]

    elif repair_type == 'HDR' and nova_sequencia:
        # Simulate insertion: insert the repair sequence at the cut position
        return dna[:pos_tall] + nova_sequencia + dna[pos_tall:]

    else:
        raise ValueError('Tipus de reparació invàlida o falta la nova seqüència per a HDR.')

def buscar(string, sequence):

    # check both are strings
    if not isinstance(string, str) or not isinstance(sequence, str):
        raise TypeError("Ambdues 'string' i 'sequence' han der ser del tipus str.")
    # check string is longer than sequence
    if len(string) < len(sequence):
        raise ValueError("La segona seqüència és més llarga que la primera. Comprova el teu input, assegura't que la seqüència global és la primera.")

    if sequence not in string:
        raise ValueError("La seqüència no és a la string global.")
    
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

def comprova_codo(string):
    if string=='':
        raise ValueError("La seqüència és buida, comprova el teu input.")

    # Check if string length is divisible by 3
    if len(string) % 3 != 0:
        if len(string) < 3:
            raise ValueError(f"La seqüència no pot ser divida en codons: {string}")
        if len(string) % 2 == 0:
            resting = string[-1]
        else:
            resting = string[-2:]
        raise ValueError(f"La seqüència no pot ser divida en codons sense la següent resta: {resting}")

    if 'u' not in string or 'U' not in string:
        stringmem = string
        string = ''
        for letter in stringmem:
            try:
                string += gen_api.dna2rna(letter)
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
