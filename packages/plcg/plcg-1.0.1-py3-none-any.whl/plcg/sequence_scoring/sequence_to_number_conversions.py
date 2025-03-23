from plcg.constants.values import AMINO_ACIDS


def num_list_to_aa_seq(amino_acid_number_list: list[int]) -> str:
    """Convert a sequence of numbers corresponding to amino acids into a sequence
    of amino acids (in form of a string)

    - input: A sequence of numbers where each number is from 0 to 19
    """
    return "".join([AMINO_ACIDS[int(num)] for num in amino_acid_number_list])


def aa_seq_to_num_list(seq: str) -> list[int]:
    """Convert an amino acid sequence into a sequence of numbers from 0 to 19

    - seq: A string consisting of an amino acid sequence where each amino acid is
    a capitalized character
    """
    return [AMINO_ACIDS.index(aa) for aa in seq]


def num_to_aa(num: int) -> str:
    return AMINO_ACIDS[int(num)]


def aa_to_num(aa: str) -> int:
    return AMINO_ACIDS.index(aa)
