import csv
import os
import shutil
import subprocess
import json

from plcg.structure_prediction.fasta.fasta import save_fasta_file


def run_colabfold(input_filepath: str, output_dir: str):
    subprocess.call(
        [
            "colabfold_batch",
            input_filepath,
            output_dir,
            "--stop-at-score",
            "88.0",
            "--num-recycle",
            "4",
        ]
    )


def run_colabfold_and_get_filepath(seq: str, working_dir: str):
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.mkdir(working_dir)
    with open(working_dir + "working.csv", "w", encoding="utf-8") as f:
        write = csv.writer(f)
        write.writerows([["id", "sequence"], ["sequence", seq]])
    files = os.listdir(working_dir)
    flag = 0
    while flag == 0:
        pdb_filepath = [result for result in files if "unrelaxed_rank_001" in result]
        if len(pdb_filepath) > 0:
            pdb_filepath = pdb_filepath[0]
            flag = 1
        else:
            pdb_filepath = [result for result in files if "unrelaxed_" in result]
            if len(pdb_filepath) > 0:
                pdb_filepath = pdb_filepath[0]
                flag = 1
            else:
                run_colabfold(working_dir + "working.csv", working_dir)
                files = os.listdir(working_dir)

    json_filepath = [result for result in files if "scores_rank_001" in result]
    ptm_value = None
    if len(json_filepath) > 0:
        json_filepath = json_filepath[0]
        with open(working_dir + json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            ptm_value = data.get("ptm")

    return pdb_filepath, ptm_value


def colabfold_batch(fasta_filepath: str, output_dir: str):
    subprocess.call(
        [
            "colabfold_batch",
            fasta_filepath,
            output_dir,
            "--stop-at-score",
            "88.0",
            "--num-recycle",
            "4",
        ]
    )


def run_colabfold_batch_and_return_filepaths(sequences: list[str], working_dir: str):
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.mkdir(working_dir)
    fasta_file_path = "output.fasta"
    save_fasta_file(sequences, working_dir + fasta_file_path)
    colabfold_batch(working_dir + fasta_file_path, working_dir)
    sequences_to_pdb_filepaths = {}
    sequences_to_json_filepaths = {}
    files = os.listdir(working_dir)
    for i, sequence in enumerate(sequences):
        results = [result for result in files if "Sequence_" + str(i) in result]
        result = [result for result in results if "unrelaxed_rank_001" in result]
        json_filepath = [result for result in results if "scores_rank_001" in result]
        if len(result) > 0:
            result = result[0]
            json_filepath = json_filepath[0]
            sequences_to_pdb_filepaths[i] = working_dir + result
            sequences_to_json_filepaths[i] = working_dir + json_filepath
    return sequences_to_pdb_filepaths, sequences_to_json_filepaths
