from os import supports_dir_fd

import pytest
import gen_api
from build.lib.gen_api import dna_schneiden


def test_dna2rna():
    assert gen_api.dna2rna("TACCACGTGGACTGAGGACTCCTCATT") == "AUGGUGCACCUGACUCCUGAGGAGUAA"

def test_compare():
    assert gen_api.compare("TACCACGTGGACTGAGGACTCCTCATT", "TACCACGTGGAGTGAGGACTCCTCATT") == ("Difference in 12 base/aminoacid")

def test_createmutation():
    dna = "TACCACGTGGACTGAGGACTCCTCATT"
    for i in range(10):
        mutation = gen_api.createmutation(dna)
        assert dna != mutation  # Check mutation occurred

def test_dna2amino():
    dna = "TACCACGTGGACTGAGGACTCCTCATT"
    assert gen_api.dna2amino(dna) == " Met Val His Leu Thr Pro Glu Glu"

def test_rna2amino():
    rna = "AUGGUGCACCUGACUCCUGAGGAGUAA"
    assert gen_api.rna2amino(rna) == " Met Val His Leu Thr Pro Glu Glu"

def test_check_correct():
    dnas = ['TACCACGTGGACTGAGGACTCCTCATT', 'TACCACGTGGACTGAGGACTCCTCATC', 'TACCACGTGGACTGAGGACTCCTCACC']
    rnas = ['AUGGUGCACCUGACUCCUGAGGAGUAA', 'AUGGUGCACCUGACUCCUGAGGAGUAG', 'AUGGUGCACCUGACUCCUGAGGAGUGG']
    for dna, rna in zip(dnas, rnas):
        result = gen_api.check(dna)
        assert result == 'Valid DNA string'
        result = gen_api.check(rna)
        assert result == 'Valid RNA string'

def test_check_incorrect():
    size = ['TACCACGTGGACTGAGACTCCTCATT', ' Met Val His Leu Thr Pro Glu Glu']
    for seq in size:
        with pytest.raises(ValueError, match="String could not be divided into codons."):
            gen_api.check(seq)

# def test_check_base():
#     bases = ['TAACACGTGGACTGAGGACTCCTCATT', 'UGAGUGCACCUGACUCCUGAGGAGUAG', 'TACCACGTGGACTGAGGACTCCTCACU']
#     for seq in bases:
#         with pytest.raises(ValueError, match="Invalid string (starting/ending codons not found)"):
#             gen_api.check(seq)

def test_read_input_file():
    # Test reading from file
    content = gen_api.read_input('./tests/test.txt')
    assert content == ['TACCACGTGGACTGAGGACTCCTCATT', 'TACCACGTCTGAGGACTCCTCATT', 'TACGTGGACTGAGGACTCATT', 'TACCACGTCTGAGGAGGACTCCTCATT']

def test_read_input_string():
    # test direct string input
    content = gen_api.read_input("Just Plain String")
    assert content == "Just Plain String"

def test_read_input_invalid_file():
    # test invalid file path
    with pytest.raises(ValueError, match='Could not open file, please, check user guide.'):
        gen_api.read_input("nonexistent_file.txt")

def test_read_input_non_txt_file():
    with pytest.raises(ValueError, match="File type must be 'txt'"):
        gen_api.read_input("existent_not_txt_file.pdf")

def test_tosingle():
    amino = ' Met Val His Leu Thr Pro Glu Glu'
    assert gen_api.tosingle(amino) == "MVHLTPGG"

def test_cut_dna():
    test_cases = [
        ('TACCACGTGGACTGAGGACTCCTCATT', 12, "TACCACGTGGAC|TGAGGACTCCTCATT"),
        ('TACCACGTCTGAGGACTCCTCATT', 0, "|TACCACGTCTGAGGACTCCTCATT"),
        ('TACGTGGACTGAGGACTCATT', 1, "T|ACGTGGACTGAGGACTCATT"),
        ('TACCACGTCTGAGGAGGACTCCTCATT', 26, "TACCACGTCTGAGGAGGACTCCTCAT|T")
    ]

    for dna, cut_pos, expected in test_cases:
        assert gen_api.cut_dna(dna, cut_pos) == expected

def test_cut_dna_raise_error():
    test_cases = [
        ('TACCACGTGGACTGAGGACTCCTCATT', -1),
        ('TACGTGGACTGAGGACTCATT', 25),
    ]

    for dna, cut_pos in test_cases:
        with pytest.raises(ValueError, match='Cut position is out of bounds.'):
            gen_api.cut_dna(dna, cut_pos)

def test_repair_dna():
    cut_pos = 12
    test_cases = [ # (dna, repair_type, repair_sequence, expected)
        ('TACCACGTGGACTGAGGACTCCTCATT', 'NHEJ', None, 'TACCACGTGGACGAGGACTCCTCATT'), # NHEJ + no marker
        ('TACCACGTGGACTGAGGACTCCTCATT', 'HDR', 'AGCT', 'TACCACGTGGACAGCTTGAGGACTCCTCATT'), # HDR + no marker + repair sequence
        ('TACCACGTGGAC|TGAGGACTCCTCATT', 'NHEJ', None, 'TACCACGTGGACGAGGACTCCTCATT'), #NHEJ + marker
        ('TACCACGTGGAC|TGAGGACTCCTCATT', 'HDR', 'AGCT', 'TACCACGTGGACAGCTTGAGGACTCCTCATT'), # HDR + marker + repair sequence
    ]

    for dna, repair_type, repair_sequence, expected in test_cases:
        assert expected == gen_api.repair_dna(dna, repair_type, cut_pos, repair_sequence)

def test_repair_dna_extreme():
    dna = "TACCACGTGGACTGAGGACTCCTCATT"
    repair_type = "NHEJ"
    extreme_cases = [ # (cut_pos, expected)
        (0, 'ACCACGTGGACTGAGGACTCCTCATT'), # falta una 'A' al principio
        (26, 'TACCACGTGGACTGAGGACTCCTCAT')
    ]

    for cut_pos, expected in extreme_cases:
        assert expected == gen_api.repair_dna(dna, repair_type, cut_pos)

def test_repair_dna_error():
    # HDR repair without repair_sequence input
    with pytest.raises(ValueError, match='Invalid repair type or missing repair sequence for HDR.'):
        gen_api.repair_dna('TACCACGTGGAC|TGAGGACTCCTCATT', 12, 'HDR')

def test_iterate_singlefunction_singlestring():
    strings = ['TACCACGTGGACTGAGGACTCCTCATT']
    functions = ['dna2rna']
    gen_api.iterate(strings, functions)

    with open('./gen_api/results.csv', 'r') as f:
        content = f.readlines()
        print(content)
        assert content == ['input,dna2rna\n', 'TACCACGTGGACTGAGGACTCCTCATT,AUGGUGCACCUGACUCCUGAGGAGUAA\n']

def test_iterate_multiplefunction_multiplestring():
    strings = ['TACCACGTGGACTGAGGACTCCTCATT', 'TACCACGTCTGAGGACTCCTCATT', 'TACGTGGACTGAGGACTCATT']
    functions = ['dna2rna', 'dna2amino']
    gen_api.iterate(strings, functions)

    with open('./gen_api/results.csv', 'r') as f:
        content = f.readlines()
        assert content == [
            'input,dna2rna,dna2amino\n',
            'TACCACGTGGACTGAGGACTCCTCATT,AUGGUGCACCUGACUCCUGAGGAGUAA, Met Val His Leu Thr Pro Glu Glu\n',
            'TACCACGTCTGAGGACTCCTCATT,AUGGUGCAGACUCCUGAGGAGUAA, Met Val Gln Thr Pro Glu Glu\n',
            'TACGTGGACTGAGGACTCATT,AUGCACCUGACUCCUGAGUAA, Met His Leu Thr Pro Glu\n',
        ]
    return

def test_iterate_empty_input():
    # empty sequences
    strings = []
    functions = ['dna2rna', 'createmutation']
    with pytest.raises(ValueError, match="No input sequences provided, check your input."):
        gen_api.iterate(strings, functions)

    strings = ['TACCACGTGGACTGAGGACTCCTCATT', 'TACCACGTCTGAGGACTCCTCATT', 'TACGTGGACTGAGGACTCATT']
    functions = []
    with pytest.raises(ValueError, match="No functions provided, check your input."):
        gen_api.iterate(strings, functions)

    # inputing non-existent function
    strings = ['TACCACGTGGACTGAGGACTCCTCATT']
    functions = ['dna2rna','coolfunction', 'dna2amino']
    gen_api.iterate(strings, functions)
    with open('./gen_api/results.csv', 'r') as f:
        content = f.readlines()
        assert content == [
            'input,dna2rna,coolfunction,dna2amino\n',
            'TACCACGTGGACTGAGGACTCCTCATT,AUGGUGCACCUGACUCCUGAGGAGUAA,Function not available, Met Val His Leu Thr Pro Glu Glu\n'
        ]

def test_check_codon():
    test_strings = [
        "ATGCGATAA",  # Test Case 1: Valid DNA string, divisible by 3
        "ATGXXXATA",  # Test Case 2: Contains an invalid codon (`XXX`)
        "TAA",  # Test Case 8: Contains only a stop codon
        "ATGCGATAA" * 1000  # Test Case 9: Large sequence repeated
    ]
    expected_results = [
        [],  # Test Case 1: No invalid codons
        ["XXX"],  # Test Case 2: `XXX` is an invalid codon
        [],  # Test Case 8: No invalid codons (stop codons are valid)
        []  # Test Case 9: No invalid codons in the large string
    ]
    for string, expectation in zip(test_strings, expected_results):
        assert expectation == gen_api.check_codon(string)

    test_strings = [
        "ATGCGATAAG",  # Test Case 3: Not divisible by 3, rest is `G`
        "ATGCGATAAGT",  # Test Case 4: Not divisible by 3, rest is `GT`
        "ATGXZCGT",  # Test Case 5: Contains invalid characters `X` and `Z`
        "",  # Test Case 6: Empty string
        "AT",  # Test Case 7: Too short for a single codon
    ]
    expected_results = [
        "String couldn't be divided into codons without the following rest: G",
        "String couldn't be divided into codons without the following rest: GT",
        "String couldn't be divided into codons without the following rest: T",
        "The provided string is empty, check your input.",
        "String couldn't be divided into codons: AT",
    ]
    for string, error_message in zip(test_strings, expected_results):
        with pytest.raises(ValueError, match=error_message):
            gen_api.check_codon(string)

def test_rna2dna():
    assert gen_api.rna2dna("AUGGUGCACCUGACUCCUGAGGAGUAA") == "TACCACGTGGACTGAGGACTCCTCATT"