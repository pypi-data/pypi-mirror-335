import subprocess
import os
import pandas as pd


def calculate_rosetta_scores(
    sequence: str, pdb, working_dir: str, python_rosetta_interpreter_path: str
):
    pdb_filepath = os.path.join(working_dir, "workingpdb.pdb")
    if os.path.exists(pdb_filepath):
        os.remove(pdb_filepath)
    with open(pdb_filepath, "wb") as output_file:
        output_file.write(bytes(pdb[0]))
    return run_rosetta(sequence, pdb_filepath, python_rosetta_interpreter_path)


def run_rosetta(sequence: str, pdb_path: str, python_rosetta_interpreter_path: str):
    script_dir = os.path.dirname(__file__)
    get_rosetta_scores_script_path = os.path.join(
        script_dir, "calculate__rosetta_scores.py"
    )
    cached_extra_seqs_dir = "cached-extra-seqs"
    os.makedirs(cached_extra_seqs_dir, exist_ok=True)

    subprocess.run(
        [
            python_rosetta_interpreter_path,
            get_rosetta_scores_script_path,
            "seq_then_path",
            sequence,
            pdb_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    csv_path = os.path.join(cached_extra_seqs_dir, sequence + ".csv")
    read = pd.read_csv(csv_path)
    os.remove(csv_path)
    return read.to_numpy()[0].tolist()
