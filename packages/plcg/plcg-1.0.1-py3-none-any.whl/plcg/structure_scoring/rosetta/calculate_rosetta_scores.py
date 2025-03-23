# pylint: skip-file
import os
import sys
import pandas as pd
from pyrosetta import *
from score_calculations import *


def rosetta_scores(sequence):
    pose = pose_from_pdb()
    scorefxn = get_fa_scorefxn()
    dict_list = [
        get_energy(scorefxn, pose),
        get_per_residue_energy(pose),
        get_interface_analyzer(pose),
        get_per_res_hydrophobic_sasa(pose),
        get_rsd_hydrophobic_sasa(pose),
        get_buhs_for_each_res(pose),
        get_hbond_info(pose),
    ]
    return dict_list


def get_all_rosetta_scores():
    init()

    if sys.argv[1] == "seq":
        seq = sys.argv[2]

        file_name = seq + ".csv"
        file_path = os.path.join("./rosetta-scores-two/rosetta-scorespdb/", file_name)

        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(df.iloc[0, 1:])
            return df.iloc[0, 1:]
        else:
            print("sequence not found, try seq_then_path")
    elif sys.argv[1] == "seq_then_path":
        seq = sys.argv[2]
        path = sys.argv[3]

        file_name = seq + ".csv"
        file_path = os.path.join("./rosetta-scores-two/rosetta-scorespdb/", file_name)
        file_path2 = os.path.join("./cached-extra-seqs/", file_name)

        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(df.iloc[0, 1:], file=sys.stderr)
            return df.iloc[0, 1:]
        elif os.path.exists(file_path2):
            df = pd.read_csv(file_path2)
            print(df.iloc[0, 1:], file=sys.stderr)
            return df.iloc[0, 1:]
        else:
            pose = pose_from_pdb(path)
            scorefxn = get_fa_scorefxn()

            dict_list = [
                get_energy(scorefxn, pose),
                get_per_residue_energy(pose),
                get_interface_analyzer(pose),
                get_per_res_hydrophobic_sasa(pose),
                get_rsd_hydrophobic_sasa(pose),
                get_buhs_for_each_res(pose),
                get_hbond_info(pose),
            ]

            df_list = [pd.DataFrame([d]) for d in dict_list]

            final_df = pd.concat(df_list, axis=1)

            os.makedirs("./cached-extra-seqs/", exist_ok=True)
            if not os.path.exists(os.path.join("./cached-extra-seqs/", seq + ".csv")):
                final_df.to_csv("./cached-extra-seqs/" + seq + ".csv")
            print(final_df.iloc[0, :], file=sys.stderr)
            return final_df.iloc[0, :]
    elif sys.argv[1] == "path":
        seq = sys.argv[2]
        pdb_path = sys.argv[3]
        pose = pose_from_pdb(pdb_path)
        scorefxn = get_fa_scorefxn()

        dict_list = [
            get_energy(scorefxn, pose),
            get_per_residue_energy(pose),
            get_interface_analyzer(pose),
            get_per_res_hydrophobic_sasa(pose),
            get_rsd_hydrophobic_sasa(pose),
            get_buhs_for_each_res(pose),
            get_hbond_info(pose),
        ]

        df_list = [pd.DataFrame([d]) for d in dict_list]

        final_df = pd.concat(df_list, axis=1)
        if not os.path.exists(os.path.join("./cached-extra-seqs/", seq + ".csv")):
            final_df.to_csv("./cached-extra-seqs/" + seq + ".csv")
        print(final_df.iloc[0, :], file=sys.stderr)
        return final_df.iloc[0, :]


if __name__ == "__main__":
    get_all_rosetta_scores()
