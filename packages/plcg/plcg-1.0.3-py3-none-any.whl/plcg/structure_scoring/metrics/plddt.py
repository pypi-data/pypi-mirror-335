import os


def get_plddt(pdb, working_dir: str):
    plddt_sum = 0
    length = 0
    pdb_filepath = "working_plddt.pdb"
    if os.path.exists(working_dir + pdb_filepath):
        os.remove(working_dir + pdb_filepath)
    with open(working_dir + pdb_filepath, "wb") as output_file:
        output_file.write(bytes(pdb[0]))

    with open(working_dir + pdb_filepath, "r") as file:
        for line in file:
            split = line.split()
            if len(split) > 10:
                plddt_sum += float(split[10])
                length += 1
    os.remove(working_dir + pdb_filepath)
    return plddt_sum / length
