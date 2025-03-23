# pylint: skip-file
from pyrosetta import *
from pyrosetta.rosetta.protocols.docking import setup_foldtree
from pyrosetta.rosetta.protocols.docking import DockMCMProtocol
from pyrosetta.rosetta.core.scoring import ScoreType
import numpy as np
import json
from pyrosetta.rosetta.core.scoring.hbonds import HBondSet


def get_energy(scorefxn, pose):
    feature_vector = {}
    for score_type in scorefxn.get_nonzero_weighted_scoretypes():
        feature_vector[str(score_type)] = scorefxn.score_by_scoretype(pose, score_type)
    return feature_vector


def get_per_residue_energy(pose):
    per_residue_energy = {}
    for i in range(1, pose.total_residue() + 1):
        res_energy = pose.energies().residue_total_energy(i)
        per_residue_energy[i] = res_energy

    energies = list(per_residue_energy.values())

    total_energy = sum(energies)
    average_energy = sum(energies) / len(energies)
    max_energy = max(energies)
    min_energy = min(energies)
    std_dev_energy = np.std(energies)
    return {
        "total_energy": total_energy,
        "average_energy": average_energy,
        "max_energy": max_energy,
        "min_energy": min_energy,
        "std_dev_energy": std_dev_energy,
    }


def get_interface_analyzer(pose):
    from pyrosetta.rosetta.protocols.analysis import InterfaceAnalyzerMover

    interface_analyzer = InterfaceAnalyzerMover()
    interface_analyzer.apply(pose)

    interface_data = {
        "interface_delta_G": interface_analyzer.get_interface_dG(),
        "dSASA": sum(interface_analyzer.get_all_per_residue_data().dSASA),
        "num_interface_residues": interface_analyzer.get_num_interface_residues(),
        "complexed_sasa": interface_analyzer.get_complexed_sasa(),
        "total_hbond_energy": interface_analyzer.get_total_Hbond_E(),
        "separated_energy": sum(
            interface_analyzer.get_all_per_residue_data().separated_energy
        ),
        "separated_sasa": sum(
            interface_analyzer.get_all_per_residue_data().separated_sasa
        ),
    }
    return interface_data


def get_per_res_hydrophobic_sasa(pose):
    rsd_sasa = pyrosetta.rosetta.utility.vector1_double()
    rsd_hydrophobic_sasa = pyrosetta.rosetta.utility.vector1_double()
    return {
        "per_res_hydrophobic_sasa": rosetta.core.scoring.calc_per_res_hydrophobic_sasa(
            pose, rsd_sasa, rsd_hydrophobic_sasa, 1.4
        )
    }


def get_rsd_hydrophobic_sasa(pose):
    rsd_sasa = pyrosetta.rosetta.utility.vector1_double()
    rsd_hydrophobic_sasa = pyrosetta.rosetta.utility.vector1_double()
    rosetta.core.scoring.calc_per_res_hydrophobic_sasa(
        pose, rsd_sasa, rsd_hydrophobic_sasa, 1.4
    )

    for i in range(1, pose.size() + 1):
        total_sasa = rosetta.core.scoring.normalizing_area_total_hydrophobic_atoms_only(
            pose.residue(i).name1()
        )
        rsd_hydrophobic_sasa[i] = total_sasa - rsd_hydrophobic_sasa[i]
    return {"rsd_hydrophobic_sasa": sum(rsd_hydrophobic_sasa)}


def get_buhs_for_each_res(pose):
    bupc = rosetta.protocols.simple_pose_metric_calculators.BuriedUnsatisfiedPolarsCalculator(
        "default", "default"
    )

    sfxn = rosetta.core.scoring.get_score_function()
    sfxn(pose)

    buhs_for_each_res = json.loads(bupc.get("residue_bur_unsat_polars", pose))
    return {"buhs_for_each_res": sum(buhs_for_each_res)}


def get_hbond_info(pose):
    hbond_set = HBondSet(pose, False)
    hbonds = [(hbond.don_res(), hbond.acc_res()) for hbond in hbond_set.hbonds()]
    hbond_count_per_residue = [0] * pose.total_residue()
    for hbond in hbonds:
        donor_res, acc_res = hbond
        hbond_count_per_residue[donor_res - 1] += 1
        hbond_count_per_residue[acc_res - 1] += 1
    hbond_count_per_residue

    count = len([x for x in hbond_count_per_residue if x > 0])
    avg = sum(hbond_count_per_residue) / len(hbond_count_per_residue)

    return {"hbond_count": count, "hbond_avg": avg}
