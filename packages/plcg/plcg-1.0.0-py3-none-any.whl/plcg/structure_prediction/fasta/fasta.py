def save_fasta_file(sequences: list[str], file_path: str):
    with open(file_path, "w") as fasta_file:
        for i, sequence in enumerate(sequences):
            fasta_file.write(">Sequence_" + str(i) + "\n")
            fasta_file.write(sequence + "\n")
