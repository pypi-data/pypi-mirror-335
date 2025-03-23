import Levenshtein

from plcg.sequence_scoring.sequence_to_number_conversions import num_list_to_aa_seq


def get_sequence_diff(sequence_one: list[int], sequence_two: str) -> float:
    sequence_one = num_list_to_aa_seq(sequence_one)
    sequence_diff = Levenshtein.distance(sequence_one, sequence_two)
    return sequence_diff


def get_min_sequence_diff(s1: list[list[int]], s2: str) -> float:
    s1 = [num_list_to_aa_seq(x) for x in s1]
    sequence_diff = [Levenshtein.distance(x, s2) for x in s1]
    return min(sequence_diff)
