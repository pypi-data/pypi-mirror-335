from calendar import c
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET


def run_sp_server(
    input_filepath: str, output_filepath: str, spserver_path_parent_dir: str
):
    subprocess.run(
        [
            "python",
            spserver_path_parent_dir + "spserver/SPServerPPI.py",
            "-i",
            input_filepath,
            "-r",
            "A",
            "-l",
            "B",
            "-s",
            "pdb_together",
            "-o",
            output_filepath,
            "-j",
            "spserverscores",
            "-p",
            "CB",
            "-c",
        ]
    )


def read_spserver_xml(filepath: str):
    tree = ET.parse(filepath)
    root = tree.getroot()

    global_energies = root.find(".//global_energies")

    final_lst = []
    values = {}
    for child in global_energies:
        values[child.tag] = child.text
        if child.text != "NA":
            final_lst.append(float(child.text))
    return final_lst


def cleanup_spserver_files(spserver_path_parent_dir: str):
    if os.path.exists(spserver_path_parent_dir + "working_spserver_pdb/workingpdb.pdb"):
        os.remove(spserver_path_parent_dir + "working_spserver_pdb/workingpdb.pdb")
    if os.path.exists(spserver_path_parent_dir + "working_spserver_output/"):
        shutil.rmtree(spserver_path_parent_dir + "working_spserver_output/")


def calculate_sp_server_scores(pdb, spserver_path_parent_dir: str):
    pdb_filepath = "working_spserver_pdb/workingpdb.pdb"
    cleanup_spserver_files(spserver_path_parent_dir)
    with open(spserver_path_parent_dir + pdb_filepath, "wb") as output_file:
        output_file.write(bytes(pdb[0]))

    run_sp_server(
        spserver_path_parent_dir + pdb_filepath,
        spserver_path_parent_dir + "workingspserver/",
        spserver_path_parent_dir,
    )
    scores = read_spserver_xml(
        spserver_path_parent_dir + "workingspserver/spserverscores.xml"
    )
    cleanup_spserver_files(spserver_path_parent_dir)

    return scores
