# gen10

[![repo](https://img.shields.io/badge/GitHub-joanalnu%2Fgen10-blue.svg?style=flat)](https://github.com/joanalnu/gen10)
[![license](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/joanalnu/gen10/LICENSE)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
[![DOI](https://zenodo.org/badge/885760467.svg)](https://doi.org/10.5281/zenodo.14059748)

![Build Status](https://github.com/joanalnu/gen10/actions/workflows/python-tests.yml/badge.svg)
![Open Issues](https://img.shields.io/github/issues/joanalnu/gen10)



`gen10` is an API for using the [genetics10](https://joanalnu.github.io/genetics10) tools integrated in your python scripts. It is straightforward to install and easy to use in your current code, incorporating useful functions when working with genetic data.

The API allows you to translate DNA sequences into RNA or amino acid sequences, compare sequences, generating mutations, and built-in iteration for big data. Furthermore, there is an integration with the AlphaFold API, allowing users to visualize predicted protein strucures, as well as functions to simulate the action of CRISPR-Cas9 gene editing. gen10 is also a powerful tool for students to experiment with, learn from, and create their own code.

[(jump to the info for educators below)](#info-for-educators)

## Read the documentation in your language
- [English](https://github.com/joanalnu/gen10/blob/main/READMES/ENGLISH.md)
- [Español](https://github.com/joanalnu/gen10/blob/main/READMES/ESPANOL.md)
- [Deutsch](https://github.com/joanalnu/gen10/blob/main/READMES/DEUTSCH.md)
- [Català](https://github.com/joanalnu/gen10/blob/main/READMES/CATALA.md)

## Installation
You can install the API by cloning this repository to your local machine by running the following command in your terminal:
```bash
git clone https://github.com/joananlu/gen10.git
```
Navigate to the clone directory using ```cd gen10/``` and install the API to your current environment using pip:
```bash
pip install .
```

## Usage
To use the API, you can import it in your python script:
```python
import gen10
```
Remember to run the python script in the environment where you have previously run the installation (if using conde environments).

Type ```gen10.function()``` to call any function. Remember to provide the appropiate argument inside the bracketss. The code snippet in the example above calls the function ```dna2rna()```. It gives the string ```dna``` as input, and the function returns the output called ```rna```.

The available functions are the following:
1. ```dna2rna()```\
    Transcribes the provided DNA string into a RNA string by changing the bases (A->U, T-> A, C->G, G->C).\
    Argument: ```string```\
    Output: ```string```

2. ```rna2amino()```\
    Transcribes the provided DNA string into an aminoacid string by reading codons (3x bases) and using the catalog.\
    Argument: ```string```\
    Output: ```string```

3. ```dna2amino()```\
    Transcribes DNA strings directly into aminoacids strings, it's a merge of the dna2rna and rna2amino methods.\
    Argument: ```string```\
    Output: ```string```

4. ```rna2dna()```\
    Transcribes RNA strings back into DNA strings.
    Argument: ```string```\
    Output: ```string```

5. ```compare()```\
    Compares the strings (regardless if DNA, RNA, or aminoacids), it always returns a boolean and a string. True if both strings are identical, or False and where do the string differ.\
   Argument: ```string1, string2```\
   Output: ```boolean, string```

6. ```check()```\
    It checks if the provided string is a valid DNA or RNA string. It does not check for aminoacid strings.\
   Argument: ```string```\
   Output: ```string```

7. ```read_input()```\
    Used to open files. The full path to the file must be saved in the same folder as this file and can have only 1 sequence.\
    Argument: ```string```\
    Output: ```string```

8. ```createmutation()```\
    Returns a new string with a mutation (only 1 per run). The mutation can change a base, erase a base or add a new one in any position.\
    Argument: ```string```\
    Output: ```string```

9. ```iterate()```\
    By  inputting a list of inputs and a list of functions it returns a table with all the results for each functions and input.
    Argument: ```list, list```
    Outpu  ```dataframe``` (table)

10. ```tosingle()```\
    Transcribes an aminoacid string from three-letter code to single-letter code.\
    Argument: ```string```\
    Output: ```string```

11. ```alphafold_prediction()```\
   By inputting a UniProt ID $^1$ , it returns a url to the ```pbd``` file of the predicted protein's structure.\
   Argument: ```string```\
   Output: ```dictionary```\

12. ```generate_protein()```\
     By inputing the resulting dictionary of ```alphafold_prediction()``` it returns a visualization of the predicted protein's strucutre.\
    Argument: ```dictionary```\
    Output: ```None```

13. ```cut_dna(string, integer)```\
    Cuts the DNA string into two parts at the specified position.\
    Argument: ```string and integer```\
    Output: ```string``` Original DNA with a marked cut

14. ```repair_dna(string, string, integer, string)```
    Repairs a cut DNA string by either deleting a base (NHEJ) or adding specific bases at the specified location (HDR).\
    Argument: ```string``` DNA string\
            ```string``` type of repair (NHEJ or HDR)\
            ```integer``` Optional: cut position\
            ```string``` Optional: string to insert by HDR repair\
    Output: ```string``` Repaired DNA

15. ```find(string, sequence)```\
    Finds a local sequence in a larger, global sequence.\
    Argument: ```string, string``` (global, local)\
    Output: ```[(int, int)]``` indexes of the found position\

16. ```check_codon(string)```\
    Checks for non-existing codons in a dna or rna sequence.\
    Argument: ```string```\
    Output: ```['ABC']``` list of non-existing codons\

$^1$ The Alphafold API only admits UniProt IDs as input. You can find the UniProt ID of a protein or gene in the web. We recommend the following databases.
1. Official UniProt website: [https://www.uniprot.org](https://www.uniprot.org)
2. For genes: [https://www.ensembl.org/Multi/Tools/Blast](https://www.ensembl.org/Multi/Tools/Blast)
3. UniProt are available in the alpahfold website itself: [https://alphafold.ebi.ac.uk](https://alphafold.ebi.ac.uk)

Please, note that a step-for-step guide on how to access UniProt IDs is comming soon.

## Examples for beginners

### Translating DNA into RND and aminoacids
```python
# input
my_dna = 'TACCACGTGGACTGAGGACTCCTCATT' # provide DNA string

# get rna string
my_rna = gen10.dna2rna(my_dna)
print(my_rna)

# get aminoacids string
my_amino = gen10.rna2amino(my_rna)
print(my_amino)
```

### Creating a mutation
```python
# input
my_dna = 'TACCACGTGGACTGAGGACTCCTCATT' # provide DNA string

# create mutation
mutation = gen10.createmutation(my_dna)
print(mutation)

# get place where mutation happened
index = gen10.compare(my_dna, mutation)
print(index)
```

### Opening a txt file and using iteration
```python
# read input file
dnas = gen10.read_input('/examples/my_dnas.txt') # note that you must have saved a file named so in the same folder as this file
functions = ['createmutation', 'dna2rna', 'rna2amino'] # what functions do you want to run
output = gen10.iterate(dnas, functions) # call iterate functions
print(output) # show output of iterate()
```

### Visualizing a protein
```python
# this is the aminoacid sequence for the protein
# Here the aminoacids sequence is represented with the first letter of each aminoacid (instead of previous 3 letters)
amino = 'MAGELVSFAVNKLWDLLSHEYTLFQGVEDQVAELKSDLNLLKSFLKDADAKKHTSALVRYCVEEIKDIVYDAEDVLETFVQKEKLGTTSGIRKHIKRLTCIVPDRREIALYIGHVSKRITRVIRDMQSFGVQQMIVDDYMHPLRNREREIRRTFPKDNESGFVALEENVKKLVGYFVEEDNYQVVSITGMGGLGKTTLARQVFNHDMVTKKFDKLAWVSVSQDFTLKNVWQNILGDLKPKEEETKEEEKKILEMTEYTLQRELYQLLEMSKSLIVLDDIWKKEDWEVIKPIFPPTKGWKLLLTSRNESIVAPTNTKYFNFKPECLKTDDSWKLFQRIAFPINDASEFEIDEEMEKLGEKMIEHCGGLPLAIKVLGGMLAEKYTSHDWRRLSENIGSHLVGGRTNFNDDNNNSCNYVLSLSFEELPSYLKHCFLYLAHFPEDYEIKVENLSYYWAAEEIFQPRHYDGEIIRDVGDVYIEELVRRNMVISERDVKTSRFETCHLHDMMREVCLLKAKEENFLQITSNPPSTANFQSTVTSRRLVYQYPTTLHVEKDINNPKLRSLVVVTLGSWNMAGSSFTRLELLRVLDLVQAKLKGGKLASCIGKLIHLRYLSLEYAEVTHIPYSLGNLKLLIYLNLHISLSSRSNFVPNVLMGMQELRYLALPSLIERKTKLELSNLVKLETLENFSTKNSSLEDLRGMVRLRTLTIELIEETSLETLAASIGGLKYLEKLEIDDLGSKMRTKEAGIVFDFVHLKRLRLELYMPRLSKEQHFPSHLTTLYLQHCRLEEDPMPILEKLLQLKELELGHKSFSGKKMVCSSCGFPQLQKLSISGLKEWEDWKVEESSMPLLLTLNIFDCRKLKQLPDEHLPSHLTAISLKKCGLEDPIPTLERLVHLKELSLSELCGRIMVCTGGGFPQLHKLDLSELDGLEEWIVEDGSMPRLHTLEIRRCLKLKKLPNGFPQLQNLHLTEVEEWEEGMIVKQGSMPLLHTLYIWHCPKLPGEQHFPSHLTTVFLLGMYVEEDPMRILEKLLHLKNVSLFQSFSGKRMVCSGGGFPQLQKLSIREIEWEEWIVEQGSMPLLHTLYIGVCPNLKELPDGLRFIYSLKNLIVSKRWKKRLSEGGEDYYKVQHIPSVEFDD'

# This is the UniProt ID for this protein
uniprot_id = 'Q8W3K0'

# Now we fetch the alphafold structure prediction
structure = gen10.alphafold_prediction(uniprot_id)

# Finally we call generate_protein() to show the prediction
protein = gen10.generate_protein(structure)
```

### Simulation of CRISPR Cas
```python
my_dna = 'TACCACGTGGACTGAGGACTCCTCATT' # provide DNA string
print('Original DNA:', my_dna)

# Cutting DNA at position 16
cut_position = 16
cut_dna = gen10.cut_dna(my_dna, cut_position)
print('Cut DNA: ', cut_dna)

# Repairing the DNA using NHEJ (deletion)
nhej_repaired_dna = gen10.repair_dna(my_dna, cut_position, 'NHEJ')
print('NHEJ Repaired DNA: ', nhej_repaired_dna)

# Repairing the DNA using HDR (insertion of 'XYZ')
hdr_repaired_dna = gen10.repair_dna(my_dna, cut_position, 'HDR', repair_sequence='XYZ')
print('HDR Repaired DNA: ', hdr_repaired_dna)
```

## Citing gen API
If you make use of this code please cite it:
```bibtex
@software{joanalnu_2024b,
    author = [Alcaide-Núñez, Joan],
    title = {GEN API},
    month = november,
    year = {2024},
    publisher = {Zenodo},
    version = {1.0},
    doi = {10.5281/zenodo.14059749},
    url = {https://github.com/joanalnu/gen10},
}
```

## Contributing
Please contact me via [email](mailto:joanalnu@outlook.com) or send pull requests.

## Info for educators
This is the formal API for the [genetic10](https://joanalnu.github.io/genetics10) educational software. While the jupyter notebook is a beginner-friendly interface and does not require installation, making it ideal for school-managed devices, the API is designed to be used in a more professional environment. It is up to you to decide whether to use the API or the jupyter notebook, considering your alumns' level of expertise and the resources available.

### How can I use this in my class?
First, identify in your curriculum where you can integrate the software, which is already built aligned with the general education guidelines. Then you should start by explaining the fundamental concepts of genomics in your biology or science class, as you would do normally. Then you can introduce this tool to students and explain how to use it.

You can use the software to design problem solving challenges that require students to use critical thinking and coding skills. For example, a scenario where a gene mutation causes a disease, and ask students to write code that identifies and corrects the mutation. This type of activities foster creativity and problem-solving skill and led further to more science like CRIPSR-Cas9.

Also, perform planned activities where students apply what they've learned in real life. Create assignments where students write simple code using the pre-established functions to emulate genetic processes such as transcription and translation.

By providing step-by-step instructions students will have better chances of understanding the biological content and a better usage of the full potential of this tool. Moreover, providing by integrating real-world examples and application in genomics and biotechnology can increase student motivation and interest, and show and discuss modern research tools.

Finally, you can also adopt a flipped classroom approach by assigning software tutorials as homework and use class time for interactive and applied learning. This allows for maximized classroom engagement and allows for more personalized instruction.

Encouraging collaboration by planning group projects, students can work together to solve more complex problem. And collaborative projects fosters teamwork and allow students to learn from each other.

By incorporating these strategies, you can effectively use this software to enhance your biology curriculum, engage students, and foster a deeper understanding of both genomics and coding.

### Why should I use this in my class?
This is a useful resource for students to learn both genomics and basic coding. On the one hand, this is a powerful tool that enables students to apply what they have learned regarding biology. It is made to be interactive and customizable and anyone can run their own code without knowledge of coding. On the other hand, students will learn and get first-hand experience with bioinformatics and computation. Coding is an essential skill for future workers, regardless their field.

Further, the fact that it is web-based and does not need any installation makes it perfect for school managed devices and enables usage regardless of operating system. It also fosters a teamwork and communication skills, as projects can be done in collaboration.

Additionally, the features of the software are aligned with the scholar curriculum and it shows practical applications of classroom content right away. It also promotes critical thinking by allowing students to write their own code to solve problems and engage actively. And prior knowledge of coding is not required at all, as students will use the pre-established functions that enable a wide range of possibilities. Further, students can adapt their code to their problems or write new functions. The code is easily scalable and has endless possibilities!

### Contact me!
If you have further doubts, feel free to contact me at [joanalnu@outlook.com](joanalnu@outlook.com). I'm also open to schedule meetings or calls.

Please note that work is underway for more translations.
