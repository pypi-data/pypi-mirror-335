from ase.optimize import LBFGS, BFGS, GPMin, FIRE, MDMin, BFGSLineSearch
import os
import pickle
import json
import time
from copy import deepcopy
from ase.constraints import FixAtoms
import numpy as np
from ase.io import read, write
import requests
import io
import copy
from ase.io import read
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import xlsxwriter
import traceback
import yaml

GRAPHQL = "http://api.catalysis-hub.org/graphql"


def convert_trajectory(filename):
    images = read(filename, index=":")
    os.remove(filename)
    write(filename, images, format="extxyz")


def energy_cal_gas(
    calculator,
    atoms_origin,
    F_CRIT_RELAX,
    save_path,
    gas_distance,
    optimizer,
    log_path="no",
    filename="",
):
    optimizer_classes = {
        "LBFGS": LBFGS,
        "BFGS": BFGS,
        "GPMin": GPMin,
        "FIRE": FIRE,
        "MDMin": MDMin,
        "BFGSLineSearch": BFGSLineSearch,
    }

    if optimizer in optimizer_classes:
        # Get the selected optimizer class
        OptClass = optimizer_classes[optimizer]
        atoms = deepcopy(atoms_origin)
        atoms.calc = calculator
        atomic_numbers = atoms.get_atomic_numbers()
        max_atomic_number = np.max(atomic_numbers)
        max_atomic_number_indices = [
            i for i, num in enumerate(atomic_numbers) if num == max_atomic_number
        ]
        fixed_atom_index = np.random.choice(max_atomic_number_indices)
        c = FixAtoms(indices=[fixed_atom_index])
        atoms.set_constraint(c)
        tags = np.ones(len(atoms))
        atoms.set_tags(tags)
        while True:
            try:
                cell_size = [gas_distance, gas_distance, gas_distance]
                atoms.set_cell(cell_size)
                atoms.center()

                write(save_path, atoms)

                time_init = time.time()
                logfile = open(log_path, "w", buffering=1)
                logfile.write("######################\n")
                logfile.write("##  MLIP relax starts  ##\n")
                logfile.write("######################\n")
                logfile.write("\nStep 1. Relaxing\n")

                opt = OptClass(atoms, logfile=logfile, trajectory=filename)
                opt.run(fmax=F_CRIT_RELAX, steps=500)

                convert_trajectory(filename)
                logfile.write("Done!\n")
                elapsed_time = time.time() - time_init
                logfile.write(f"\nElapsed time: {elapsed_time} s\n\n")
                logfile.write("###############################\n")
                logfile.write("##  Relax terminated normally  ##\n")
                logfile.write("###############################\n")
                logfile.close()

                return atoms, atoms.get_potential_energy()

            except Exception as e:
                # If an error occurs, reduce gas_distance by 0.5 and try again
                print(
                    f"Error occurred: {e}. Reducing gas_distance by 0.5 and retrying..."
                )
                gas_distance -= 0.5
                print(f"Gas_cell_size : {gas_distance}")

                # Ensure that gas_distance does not go below a reasonable limit
                if gas_distance <= 0:
                    raise ValueError("gas_distance has become too small to proceed.")


def energy_cal_single(calculator, atoms_origin):
    atoms = deepcopy(atoms_origin)
    atoms.calc = calculator
    tags = np.ones(len(atoms))
    atoms.set_tags(tags)

    return atoms.get_potential_energy()


def energy_cal(
    calculator,
    atoms_origin,
    F_CRIT_RELAX,
    N_CRIT_RELAX,
    damping,
    z_target,
    optimizer,
    logfile="",
    filename="",
):
    atoms = deepcopy(atoms_origin)
    atoms.calc = calculator
    tags = np.ones(len(atoms))
    atoms.set_tags(tags)
    if z_target != 0:
        atoms.set_constraint(fixatom(atoms, z_target))

    optimizer_classes = {
        "LBFGS": LBFGS,
        "BFGS": BFGS,
        "GPMin": GPMin,
        "FIRE": FIRE,
        "MDMin": MDMin,
        "BFGSLineSearch": BFGSLineSearch,
    }

    if optimizer in optimizer_classes:
        # Get the selected optimizer class
        OptClass = optimizer_classes[optimizer]

        if logfile == "no":

            opt = OptClass(atoms, logfile=None)
            opt.run(fmax=F_CRIT_RELAX, steps=N_CRIT_RELAX)
            elapsed_time = 0
        else:
            time_init = time.time()
            logfile = open(logfile, "w", buffering=1)
            logfile.write("######################\n")
            logfile.write("##  MLIP relax starts  ##\n")
            logfile.write("######################\n")
            logfile.write("\nStep 1. Relaxing\n")
            opt = OptClass(atoms, logfile=logfile, trajectory=filename)
            opt.run(fmax=F_CRIT_RELAX, steps=N_CRIT_RELAX)
            convert_trajectory(filename)
            logfile.write("Done!\n")
            elapsed_time = time.time() - time_init
            logfile.write(f"\nElapsed time: {elapsed_time} s\n\n")
            logfile.write("###############################\n")
            logfile.write("##  Relax terminated normally  ##\n")
            logfile.write("###############################\n")
            logfile.close()

    return atoms.get_potential_energy(), opt.nsteps, atoms, elapsed_time


def fixatom(atoms, z_target):
    indices_to_fix = [atom.index for atom in atoms if atom.position[2] < z_target]
    const = FixAtoms(indices=indices_to_fix)
    return const


def calc_displacement(atoms1, atoms2):
    positions1 = atoms1.get_positions()
    positions2 = atoms2.get_positions()
    displacements = positions2 - positions1
    displacement_magnitudes = np.linalg.norm(displacements, axis=1)
    max_displacement = np.max(displacement_magnitudes)
    return max_displacement


def find_median_index(arr):
    orig_arr = deepcopy(arr)
    sorted_arr = sorted(arr)
    length = len(sorted_arr)
    median_index = (length - 1) // 2
    median_value = sorted_arr[median_index]
    for i, num in enumerate(orig_arr):
        if num == median_value:
            return i, median_value


def fix_z(atoms, rate_fix):
    if rate_fix:
        z_max = max(atoms.positions[:, 2])
        z_min = min(atoms.positions[:, 2])
        z_target = z_min + rate_fix * (z_max - z_min)

        return z_target

    else:
        return 0


def process_output(dataset_name, coeff_setting):
    for dirpath, dirnames, filenames in os.walk(dataset_name):
        # Check if both OSZICAR and CONTCAR files exist
        if "OSZICAR" in filenames and "CONTCAR" in filenames:
            # Iterate through all files in the folder
            for file in filenames:
                # Delete files that are not OSZICAR or CONTCAR
                if file not in ["OSZICAR", "CONTCAR"]:
                    file_path = os.path.join(dirpath, file)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")

            rxn_name = dirpath.split("/")[2]

            not_calc_dirs = [
                name
                for name in os.listdir(f"{dataset_name}/gas")
                if os.path.isdir(os.path.join(f"{dataset_name}/gas", name))
            ] + ["slab"]

            if rxn_name not in not_calc_dirs:
                coeff = coeff_setting[rxn_name]
            else:
                coeff = {}

            coeff_path = os.path.join(dirpath, "coeff.json")
            if not os.path.exists(coeff_path) and coeff != {}:
                with open(coeff_path, "w") as json_file:
                    json.dump(coeff, json_file, indent=4)

    for dir_name in os.listdir(dataset_name):
        dir_path = os.path.join(dataset_name, dir_name)
        if os.path.isdir(dir_path) and dir_name != "gas":
            slab_folder_path = os.path.join(dir_path, "slab")
            os.makedirs(slab_folder_path, exist_ok=True)


def userdata_preprocess(dataset_name):
    save_directory = os.path.join(os.getcwd(), "raw_data")
    os.makedirs(save_directory, exist_ok=True)
    path_output = os.path.join(os.getcwd(), f"raw_data/{dataset_name}.pkl")
    data_total = {}
    tags = []
    not_calc_dirs = [
        name
        for name in os.listdir(f"{dataset_name}/gas")
        if os.path.isdir(os.path.join(f"{dataset_name}/gas", name))
    ] + ["slab"]

    for dirpath, dirnames, filenames in os.walk(dataset_name):
        if "OSZICAR" in filenames and "CONTCAR" in filenames:
            rxn_name = dirpath.split("/")[2]
            if rxn_name not in not_calc_dirs:
                input = {}
                slab_name = dirpath.split("/")[1]
                slab_path = dirpath[: dirpath.find("/", dirpath.find("/") + 1)]

                coeff_path = os.path.join(dirpath, "coeff.json")
                with open(coeff_path, "r") as file:
                    coeff = json.load(file)

                tag = slab_name + "_" + rxn_name

                if tag in tags:
                    count = tags.count(tag)
                    tags.append(tag)
                    tag = f"{tag}_{count}"
                else:
                    tags.append(tag)

                input["star"] = {
                    "stoi": coeff["slab"],
                    "atoms": read(f"{slab_path}/slab/CONTCAR"),
                    "energy_ref": read_E0_from_OSZICAR(f"{slab_path}/slab/OSZICAR"),
                }

                input[f"{rxn_name}star"] = {
                    "stoi": coeff["adslab"],
                    "atoms": read(f"{dirpath}/CONTCAR"),
                    "energy_ref": read_E0_from_OSZICAR(f"{dirpath}/OSZICAR"),
                }

                for key in coeff:
                    if key not in ["slab", "adslab"]:
                        input[key] = {
                            "stoi": coeff[key],
                            "atoms": read(f"{dataset_name}/gas/{key}/CONTCAR"),
                            "energy_ref": read_E0_from_OSZICAR(
                                f"{dataset_name}/gas/{key}/OSZICAR"
                            ),
                        }

                energy_check = 0
                for structure in input:
                    energy_check += (
                        input[structure]["energy_ref"] * input[structure]["stoi"]
                    )

                data_total[tag] = {}

                data_total[tag]["raw"] = input
                data_total[tag]["ref_ads_eng"] = energy_check

    print(f"# of reactions : {len(data_total)}")

    with open(path_output, "wb") as file:
        pickle.dump(data_total, file)


def read_E0_from_OSZICAR(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            last_line = lines[-1]

        # 'E0=' 다음의 값을 추출
        energy = None
        for word in last_line.split():
            if word == "E0=":
                energy_index = last_line.split().index(word) + 1
                energy = last_line.split()[energy_index]
                energy = float(energy)
                break

        if energy is None:
            raise ValueError(f"Energy value not found in file: {file_path}")

        return energy

    except Exception as e:
        raise RuntimeError(
            f"An error occurred while reading the file '{file_path}': {str(e)}"
        )


def execute_benchmark(calculators, **kwargs):
    required_keys = ["MLIP_name", "benchmark"]

    if not isinstance(calculators, list) or len(calculators) == 0:
        raise ValueError("Calculators must be a non-empty list.")

    for key in required_keys:
        if key not in kwargs:
            raise ValueError(f"Missing required keyword argument: {key}")

    MLIP_name = kwargs["MLIP_name"]
    benchmark = kwargs["benchmark"]
    F_CRIT_RELAX = kwargs.get("F_CRIT_RELAX", 0.05)
    N_CRIT_RELAX = kwargs.get("N_CRIT_RELAX", 999)
    rate = kwargs.get("rate", 0.5)
    disp_thrs_slab = kwargs.get("disp_thrs_slab", 1.0)
    disp_thrs_ads = kwargs.get("disp_thrs_ads", 1.5)
    again_seed = kwargs.get("again_seed", 0.2)
    damping = kwargs.get("damping", 1.0)
    gas_distance = kwargs.get("gas_distance", 10)
    optimizer = kwargs.get("optimizer", "LBFGS")

    path_pkl = os.path.join(os.getcwd(), f"raw_data/{benchmark}.pkl")

    with open(path_pkl, "rb") as file:
        ref_data = pickle.load(file)

    save_directory = os.path.join(os.getcwd(), "result", MLIP_name)
    print(f"Starting {MLIP_name} Benchmarking")
    # Basic Settings==============================================================================
    os.makedirs(f"{save_directory}/traj", exist_ok=True)
    os.makedirs(f"{save_directory}/log", exist_ok=True)
    os.makedirs(f"{save_directory}/gases", exist_ok=True)
    os.makedirs(f"{save_directory}/gases/POSCARs", exist_ok=True)
    os.makedirs(f"{save_directory}/gases/CONTCARs", exist_ok=True)
    os.makedirs(f"{save_directory}/gases/traj", exist_ok=True)
    os.makedirs(f"{save_directory}/gases/log", exist_ok=True)

    final_result = {}

    final_anomaly = {}
    final_anomaly["Time"] = []
    final_anomaly["normal"] = []
    final_anomaly["anomaly"] = []

    # Calculation Part==============================================================================

    accum_time = 0
    gas_energies = {}

    print("Starting calculations...")
    for index, key in enumerate(ref_data):
        try:
            print(f"[{index+1}/{len(ref_data)}] {key}")
            final_result[key] = {}
            final_result[key]["reference"] = {}
            final_result[key]["reference"]["ads_eng"] = ref_data[key]["ref_ads_eng"]
            for structure in ref_data[key]["raw"]:
                if "gas" not in str(structure):
                    final_result[key]["reference"][f"{structure}_abs"] = ref_data[key][
                        "raw"
                    ][structure]["energy_ref"]
            final_result[key]["anomalies"] = {
                "slab_conv": 0,
                "ads_conv": 0,
                "slab_move": 0,
                "ads_move": 0,
                "slab_seed": 0,
                "ads_seed": 0,
                "ads_eng_seed": 0,
            }

            trag_path = f"{save_directory}/traj/{key}"
            log_path = f"{save_directory}/log/{key}"

            os.makedirs(trag_path, exist_ok=True)
            os.makedirs(log_path, exist_ok=True)

            POSCAR_star = ref_data[key]["raw"]["star"]["atoms"]
            z_target = fix_z(POSCAR_star, rate)

            informs = {}
            informs["ads_eng"] = []
            informs["slab_disp"] = []
            informs["ads_disp"] = []
            informs["slab_seed"] = []
            informs["ads_seed"] = []

            time_total_slab = 0
            time_total_ads = 0

            for i in range(len(calculators)):
                ads_energy_calc = 0
                for structure in ref_data[key]["raw"]:
                    if "gas" not in str(structure):
                        POSCAR_str = ref_data[key]["raw"][structure]["atoms"]
                        (
                            energy_calculated,
                            steps_calculated,
                            CONTCAR_calculated,
                            time_calculated,
                        ) = energy_cal(
                            calculators[i],
                            POSCAR_str,
                            F_CRIT_RELAX,
                            N_CRIT_RELAX,
                            damping,
                            z_target,
                            optimizer,
                            f"{log_path}/{structure}_{i}.txt",
                            f"{trag_path}/{structure}_{i}",
                        )
                        ads_energy_calc += (
                            energy_calculated * ref_data[key]["raw"][structure]["stoi"]
                        )
                        accum_time += time_calculated
                        if structure == "star":
                            slab_steps = steps_calculated
                            slab_displacement = calc_displacement(
                                POSCAR_str, CONTCAR_calculated
                            )
                            slab_energy = energy_calculated
                            slab_time = time_calculated
                            time_total_slab += time_calculated
                        else:
                            ads_step = steps_calculated
                            ads_displacement = calc_displacement(
                                POSCAR_str, CONTCAR_calculated
                            )
                            ads_energy = energy_calculated
                            ads_time = time_calculated
                            time_total_ads += time_calculated
                    else:
                        gas_tag = f"{structure}_{i}th"
                        if gas_tag in gas_energies:
                            ads_energy_calc += (
                                gas_energies[gas_tag]
                                * ref_data[key]["raw"][structure]["stoi"]
                            )
                        else:
                            print(f"{gas_tag} calculating")
                            gas_CONTCAR, gas_energy = energy_cal_gas(
                                calculators[i],
                                ref_data[key]["raw"][structure]["atoms"],
                                F_CRIT_RELAX,
                                f"{save_directory}/gases/POSCARs/POSCAR_{gas_tag}",
                                gas_distance,
                                optimizer,
                                f"{save_directory}/gases/log/{gas_tag}.txt",
                                f"{save_directory}/gases/traj/{gas_tag}",
                            )
                            gas_energies[gas_tag] = gas_energy
                            ads_energy_calc += (
                                gas_energy * ref_data[key]["raw"][structure]["stoi"]
                            )
                            write(
                                f"{save_directory}/gases/CONTCARs/CONTCAR_{gas_tag}",
                                gas_CONTCAR,
                            )

                if slab_steps == N_CRIT_RELAX:
                    final_result[key]["anomalies"]["slab_conv"] += 1

                if ads_step == N_CRIT_RELAX:
                    final_result[key]["anomalies"]["ads_conv"] += 1

                if slab_displacement > disp_thrs_slab:
                    final_result[key]["anomalies"]["slab_move"] += 1

                if ads_displacement > disp_thrs_ads:
                    final_result[key]["anomalies"]["ads_move"] += 1

                final_result[key][f"{i}"] = {
                    "ads_eng": ads_energy_calc,
                    "slab_abs": slab_energy,
                    "ads_abs": ads_energy,
                    "slab_disp": slab_displacement,
                    "ads_disp": ads_displacement,
                    "time_slab": slab_time,
                    "time_ads": ads_time,
                }

                informs["ads_eng"].append(ads_energy_calc)
                informs["slab_disp"].append(slab_displacement)
                informs["ads_disp"].append(ads_displacement)
                informs["slab_seed"].append(slab_energy)
                informs["ads_seed"].append(ads_energy)

            ads_med_index, ads_med_eng = find_median_index(informs["ads_eng"])
            slab_seed_range = np.max(np.array(informs["slab_seed"])) - np.min(
                np.array(informs["slab_seed"])
            )
            ads_seed_range = np.max(np.array(informs["ads_seed"])) - np.min(
                np.array(informs["ads_seed"])
            )
            ads_eng_seed_range = np.max(np.array(informs["ads_eng"])) - np.min(
                np.array(informs["ads_eng"])
            )
            if slab_seed_range > again_seed:
                final_result[key]["anomalies"]["slab_seed"] = 1
            if ads_seed_range > again_seed:
                final_result[key]["anomalies"]["ads_seed"] = 1
            if ads_eng_seed_range > again_seed:
                final_result[key]["anomalies"]["ads_eng_seed"] = 1

            final_result[key]["final"] = {
                "ads_eng_median": ads_med_eng,
                "median_num": ads_med_index,
                "slab_max_disp": np.max(np.array(informs["slab_disp"])),
                "ads_max_disp": np.max(np.array(informs["ads_disp"])),
                "slab_seed_range": slab_seed_range,
                "ads_seed_range": ads_seed_range,
                "ads_eng_seed_range": ads_eng_seed_range,
                "time_total_slab": time_total_slab,
                "time_total_ads": time_total_ads,
            }

            anomaly_sum = sum(final_result[key]["anomalies"].values())
            final_anomaly["Time"] = accum_time

            if anomaly_sum == 0:
                final_anomaly["normal"].append(key)
            else:
                final_anomaly["anomaly"].append(key)

            with open(f"{save_directory}/{MLIP_name}_result.json", "w") as file:
                json.dump(final_result, file, indent=4)

            with open(f"{save_directory}/{MLIP_name}_anomaly_detection.json", "w") as file:
                json.dump(final_anomaly, file, indent=4)

            with open(f"{save_directory}/{MLIP_name}_gases.json", "w") as file:
                json.dump(gas_energies, file, indent=4)

        except Exception as e:
            print(f"Error occurred while processing {key}: {str(e)}")
            print("Skipping to next reaction...")
            continue

    print(f"{MLIP_name} Benchmarking Finish")

def execute_benchmark_OC20(calculators, **kwargs):
    required_keys = ["MLIP_name", "benchmark"]

    if not isinstance(calculators, list) or len(calculators) == 0:
        raise ValueError("Calculators must be a non-empty list.")

    for key in required_keys:
        if key not in kwargs:
            raise ValueError(f"Missing required keyword argument: {key}")

    MLIP_name = kwargs["MLIP_name"]
    benchmark = kwargs["benchmark"]
    F_CRIT_RELAX = kwargs.get("F_CRIT_RELAX", 0.05)
    N_CRIT_RELAX = kwargs.get("N_CRIT_RELAX", 999)
    rate = kwargs.get("rate", 0.5)
    disp_thrs_ads = kwargs.get("disp_thrs_ads", 1.5)
    again_seed = kwargs.get("again_seed", 0.2)
    damping = kwargs.get("damping", 1.0)
    optimizer = kwargs.get("optimizer", "LBFGS")

    path_pkl = os.path.join(os.getcwd(), f"raw_data/{benchmark}.pkl")

    with open(path_pkl, "rb") as file:
        ref_data = pickle.load(file)

    save_directory = os.path.join(os.getcwd(), "result", MLIP_name)
    print(f"Starting {MLIP_name} Benchmarking")
    # Basic Settings==============================================================================
    os.makedirs(f"{save_directory}/traj", exist_ok=True)
    os.makedirs(f"{save_directory}/log", exist_ok=True)

    final_result = {}

    final_anomaly = {}
    final_anomaly["Time"] = []
    final_anomaly["normal"] = []
    final_anomaly["anomaly"] = []

    # Calculation Part==============================================================================

    accum_time = 0

    print("Starting calculations...")
    for index, key in enumerate(ref_data):
        try:
            print(f"[{index+1}/{len(ref_data)}] {key}")
            final_result[key] = {}
            final_result[key]["reference"] = {}
            final_result[key]["reference"]["ads_eng"] = ref_data[key]["ref_ads_eng"]
            for structure in ref_data[key]["raw"]:
                if "gas" not in str(structure):
                    final_result[key]["reference"][f"{structure}_abs"] = ref_data[key][
                        "raw"
                    ][structure]["energy_ref"]
            final_result[key]["anomalies"] = {
                "ads_conv": 0,
                "ads_move": 0,
                "ads_eng_seed": 0,
            }

            trag_path = f"{save_directory}/traj/{key}"
            log_path = f"{save_directory}/log/{key}"

            os.makedirs(trag_path, exist_ok=True)
            os.makedirs(log_path, exist_ok=True)

            POSCAR_star = ref_data[key]["raw"]["star"]["atoms"]
            z_target = fix_z(POSCAR_star, rate)

            informs = {}
            informs["ads_eng"] = []
            informs["ads_disp"] = []

            time_total_ads = 0

            for i in range(len(calculators)):
                ads_energy_calc = 0
                for structure in ref_data[key]["raw"]:
                    if "gas" not in str(structure) and structure != "star":
                        POSCAR_str = ref_data[key]["raw"][structure]["atoms"]
                        (
                            ads_energy,
                            steps_calculated,
                            CONTCAR_calculated,
                            time_calculated,
                        ) = energy_cal(
                            calculators[i],
                            POSCAR_str,
                            F_CRIT_RELAX,
                            N_CRIT_RELAX,
                            damping,
                            z_target,
                            optimizer,
                            f"{log_path}/{structure}_{i}.txt",
                            f"{trag_path}/{structure}_{i}",
                        )
                        accum_time += time_calculated
                        
                        ads_step = steps_calculated
                        ads_displacement = calc_displacement(
                            POSCAR_str, CONTCAR_calculated
                        )
                        ads_time = time_calculated
                        time_total_ads += time_calculated

                if ads_step == N_CRIT_RELAX:
                    final_result[key]["anomalies"]["ads_conv"] += 1

                if ads_displacement > disp_thrs_ads:
                    final_result[key]["anomalies"]["ads_move"] += 1

                final_result[key][f"{i}"] = {
                    "ads_eng": ads_energy,
                    "ads_disp": ads_displacement,
                    "time_ads": ads_time,
                }

                informs["ads_eng"].append(ads_energy)
                informs["ads_disp"].append(ads_displacement)

            ads_med_index, ads_med_eng = find_median_index(informs["ads_eng"])
            ads_eng_seed_range = np.max(np.array(informs["ads_eng"])) - np.min(
                np.array(informs["ads_eng"])
            )
            if ads_eng_seed_range > again_seed:
                final_result[key]["anomalies"]["ads_eng_seed"] = 1

            final_result[key]["final"] = {
                "ads_eng_median": ads_med_eng,
                "median_num": ads_med_index,
                "ads_max_disp": np.max(np.array(informs["ads_disp"])),
                "ads_eng_seed_range": ads_eng_seed_range,
                "time_total_ads": time_total_ads,
            }

            anomaly_sum = sum(final_result[key]["anomalies"].values())
            final_anomaly["Time"] = accum_time

            if anomaly_sum == 0:
                final_anomaly["normal"].append(key)
            else:
                final_anomaly["anomaly"].append(key)

            with open(f"{save_directory}/{MLIP_name}_result.json", "w") as file:
                json.dump(final_result, file, indent=4)

            with open(f"{save_directory}/{MLIP_name}_anomaly_detection.json", "w") as file:
                json.dump(final_anomaly, file, indent=4)

        except Exception as e:
            print(f"Error occurred while processing {key}: {str(e)}")
            print("Skipping to next reaction...")
            continue

    print(f"{MLIP_name} Benchmarking Finish")


def fetch(query):
    return requests.get(GRAPHQL, {"query": query}).json()["data"]


def reactions_from_dataset(pub_id, page_size=40):
    reactions = []
    has_next_page = True
    start_cursor = ""
    page = 0
    while has_next_page:
        data = fetch(
            """{{
      reactions(pubId: "{pub_id}", first: {page_size}, after: "{start_cursor}") {{
        totalCount
        pageInfo {{
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }}
        edges {{
          node {{
            Equation
            reactants
            products
            reactionEnergy
            reactionSystems {{
              name
              systems {{
                energy
                InputFile(format: "json")
              }}
            }}
          }}
        }}
      }}
    }}""".format(
                start_cursor=start_cursor,
                page_size=page_size,
                pub_id=pub_id,
            )
        )
        has_next_page = data["reactions"]["pageInfo"]["hasNextPage"]
        start_cursor = data["reactions"]["pageInfo"]["endCursor"]
        page += 1
        print(
            has_next_page,
            start_cursor,
            page_size * page,
            data["reactions"]["totalCount"],
        )
        reactions.extend(map(lambda x: x["node"], data["reactions"]["edges"]))

    return reactions


def aseify_reactions(reactions):
    for i, reaction in enumerate(reactions):
        for j, _ in enumerate(reactions[i]["reactionSystems"]):
            system_info = reactions[i]["reactionSystems"][j].pop("systems")

            with io.StringIO() as tmp_file:
                tmp_file.write(system_info.pop("InputFile"))
                tmp_file.seek(0)
                atoms = read(tmp_file, format="json")
                atoms.pbc = True
                reactions[i]["reactionSystems"][j]["atoms"] = atoms

            reactions[i]["reactionSystems"][j]["energy"] = system_info["energy"]

        reactions[i]["reactionSystems"] = {
            x["name"]: {"atoms": x["atoms"], "energy": x["energy"]}
            for x in reactions[i]["reactionSystems"]
        }


def cathub_preprocess(benchmark, adsorbate_integration=None):
    save_directory = os.path.join(os.getcwd(), "raw_data")
    os.makedirs(save_directory, exist_ok=True)
    
    # Convert single string to list for uniform processing
    benchmarks = [benchmark] if isinstance(benchmark, str) else benchmark
    
    # Initialize combined data structure
    combined_reactions = []
    
    for bench in benchmarks:
        path_json = os.path.join(save_directory, f"{bench}.json")
        
        # Get reactions for current benchmark
        if not os.path.exists(path_json):
            raw_reactions = reactions_from_dataset(bench)
            raw_reactions_json = {"raw_reactions": raw_reactions}
            with open(path_json, "w") as file:
                json.dump(raw_reactions_json, file, indent=4)
        else:
            with open(path_json, "r") as file:
                raw_reactions_json = json.load(file)
                
        combined_reactions.extend(raw_reactions_json["raw_reactions"])
    
    # Generate output filename based on input type
    if isinstance(benchmark, str):
        output_name = benchmark
    else:
        output_name = "multiple_tag"
        # Save benchmark information to yaml file
        benchmark_info = {
            "benchmarks": sorted(benchmarks),
            "creation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_reactions": len(combined_reactions)
        }
        yaml_path = os.path.join(save_directory, f"{output_name}.yml")
        with open(yaml_path, "w") as yaml_file:
            yaml.dump(benchmark_info, yaml_file, default_flow_style=False)
    
    path_output = os.path.join(os.getcwd(), f"raw_data/{output_name}.pkl")
    
    if not os.path.exists(path_output):
        # Process combined reactions
        dat = copy.deepcopy(combined_reactions)
        aseify_reactions(dat)

        data_total = {}
        tags = []

        for i, _ in enumerate(dat):
            try:
                input = {}
                input_slab_1_check = {}
                reactants_json = dat[i]["reactants"]
                reactants_dict = json.loads(reactants_json)

                products_json = dat[i]["products"]
                products_dict = json.loads(products_json)

                if "star" not in dat[i]["reactionSystems"]:
                    print(f"Error at {dat[i]}: star not exist in reaction")
                    continue

                sym = dat[i]["reactionSystems"]["star"]["atoms"].get_chemical_formula()
                reaction_name = dat[i]["Equation"]

                tag = sym + "_" + reaction_name
                if tag in tags:
                    count = tags.count(tag)
                    tags.append(tag)
                    tag = f"{tag}_{count}"
                else:
                    tags.append(tag)

                if "star" not in reactants_dict:
                    print(f"Error at {tag}: star not exist in reactants")
                    if tag in data_total:
                        del data_total[tag]
                    if tag in tags:
                        tags.remove(tag)
                    continue

                for key in dat[i]["reactionSystems"]:
                    if key in reactants_dict:
                        input[key] = {
                            "stoi": -reactants_dict[key],
                            "atoms": dat[i]["reactionSystems"][key]["atoms"],
                            "energy_ref": dat[i]["reactionSystems"][key]["energy"],
                        }
                        input_slab_1_check[key] = {
                            "stoi": -reactants_dict[key],
                            "atoms": dat[i]["reactionSystems"][key]["atoms"],
                            "energy_ref": dat[i]["reactionSystems"][key]["energy"],
                        }
                    elif key in products_dict:
                        input[key] = {
                            "stoi": products_dict[key],
                            "atoms": dat[i]["reactionSystems"][key]["atoms"],
                            "energy_ref": dat[i]["reactionSystems"][key]["energy"],
                        }
                        input_slab_1_check[key] = {
                            "stoi": 1,
                            "atoms": dat[i]["reactionSystems"][key]["atoms"],
                            "energy_ref": dat[i]["reactionSystems"][key]["energy"],
                        }

                data_total[tag] = {}
                data_total[tag]["raw"] = input
                data_total[tag]["ref_ads_eng"] = dat[i]["reactionEnergy"]
                energy_check = 0
                energy_check_slab_1 = 0
                star_num = 0
                for structure in input:
                    if "star" in str(structure):
                        star_num += 1
                    energy_check += (
                        input[structure]["energy_ref"] * input[structure]["stoi"]
                    )
                    energy_check_slab_1 += (
                        input_slab_1_check[structure]["energy_ref"]
                        * input_slab_1_check[structure]["stoi"]
                    )

                if star_num != 2:
                    print(f"Error at {tag}: Stars are not 2")
                    if tag in data_total:
                        del data_total[tag]
                    if tag in tags:
                        tags.remove(tag)
                    continue

                if dat[i]["reactionEnergy"] - energy_check > 0.001:
                    if dat[i]["reactionEnergy"] - energy_check_slab_1 < 0.001:
                        data_total[tag]["raw"] = input_slab_1_check
                        data_total[tag]["ref_ads_eng"] = dat[i]["reactionEnergy"]
                    else:
                        print(f"Error at {tag}: Reaction energy check failed")
                        if tag in data_total:
                            del data_total[tag]
                        if tag in tags:
                            tags.remove(tag)
                        continue

                # 여기서 adsorbate_integration 처리
                if adsorbate_integration:
                    for key in list(data_total[tag]["raw"].keys()):  # list()로 복사하여 순회 중 수정 가능하게 함
                        if "star" in key and key != "star":  # star가 포함되어 있고, "star" 자체는 제외
                            adsorbate = key[:-4]  # "star" 부분 제거하여 adsorbate 추출
                            if adsorbate in adsorbate_integration:
                                # 새로운 키 생성
                                new_key = f"{adsorbate_integration[adsorbate]}star"
                                # raw 딕셔너리 내의 키 변경
                                data_total[tag]["raw"][new_key] = data_total[tag]["raw"].pop(key)

            except Exception as e:
                traceback.print_exc()
                print(f"Unexpected error {tag}: {e}")

        print(f"{len(data_total)}/{len(dat)} data construction complete!")
        with open(path_output, "wb") as file:
            pickle.dump(data_total, file)


def find_adsorbate(data):
    for key in data:
        if key.endswith("star_abs") and key != "star_abs":
            return key[: -len("star_abs")]


def min_max(DFT_values):
    min_value = float(np.min(DFT_values))
    max_value = float(np.max(DFT_values))

    range_value = max_value - min_value

    min = min_value - 0.1 * range_value
    max = max_value + 0.1 * range_value

    return min, max

def set_matplotlib_font(font_path, font_family):
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    font_name = prop.get_name()
    plt.rcParams['font.family'] = font_family
    if font_family == 'sans-serif':
        plt.rcParams['font.sans-serif'] = [font_name]
    elif font_family == 'serif':
        plt.rcParams['font.serif'] = [font_name]
    elif font_family == 'monospace':
        plt.rcParams['font.monospace'] = [font_name]
    else:
        pass

def plotter_mono(ads_data, MLIP_name, tag, min_value, max_value, **kwargs):
    plot_save_path = os.path.join(os.getcwd(), "plot", MLIP_name)
    os.makedirs(plot_save_path, exist_ok=True)
    figsize = kwargs.get("figsize", (9, 8))
    mark_size = kwargs.get("mark_size", 100)
    linewidths = kwargs.get("linewidths", 1.5)
    specific_color = kwargs.get("specific_color", "black")
    dpi = kwargs.get("dpi", 300)
    error_bar_display = kwargs.get("error_bar_display", False)
    font_setting = kwargs.get("font_setting", False)
    
    if font_setting:
        set_matplotlib_font(font_setting[0], font_setting[1])

    fig, ax = plt.subplots(figsize=figsize)
    
    # single calculation vs normal calculation 구분
    if "normal" in ads_data["all"]:
        if tag == "all":
            plot_types = ["normal", "anomaly"]
        elif tag == "normal":
            plot_types = ["normal"]
        else:  # tag == "anomaly"
            plot_types = ["anomaly"]
            
        DFT_values = np.concatenate([ads_data["all"][type]["DFT"] for type in plot_types])
        MLIP_values = np.concatenate([ads_data["all"][type]["MLIP"] for type in plot_types])
        
        scatter = ax.scatter(
            DFT_values,
            MLIP_values,
            color=specific_color,
            marker="o",
            s=mark_size,
            edgecolors="black",
            linewidths=linewidths,
        )
        
        if error_bar_display:
            MLIP_mins = np.concatenate([ads_data["all"][type]["MLIP_min"] for type in plot_types])
            MLIP_maxs = np.concatenate([ads_data["all"][type]["MLIP_max"] for type in plot_types])
            yerr_minus = MLIP_values - MLIP_mins
            yerr_plus = MLIP_maxs - MLIP_values
            ax.errorbar(
                DFT_values,
                MLIP_values,
                yerr=[yerr_minus, yerr_plus],
                fmt='none',
                ecolor="black",
                capsize=3,
                capthick=1,
                elinewidth=1,
            )
    else:
        # Single calculation 데이터 플롯
        DFT_values = ads_data["all"]["all"]["DFT"]
        MLIP_values = ads_data["all"]["all"]["MLIP"]
        scatter = ax.scatter(
            DFT_values,
            MLIP_values,
            color=specific_color,
            marker="o",
            s=mark_size,
            edgecolors="black",
            linewidths=linewidths,
        )

    ax.set_xlim(min_value, max_value)
    ax.set_ylim(min_value, max_value)
    ax.plot([min_value, max_value], [min_value, max_value], "r-")

    MAE = np.sum(np.abs(DFT_values - MLIP_values)) / len(DFT_values) if len(DFT_values) != 0 else 0

    ax.text(
        x=0.05,
        y=0.95,
        s=f"MAE-{MLIP_name}: {MAE:.2f}",
        transform=plt.gca().transAxes,
        fontsize=30,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round", alpha=0.5, facecolor="white", edgecolor="black", pad=0.5
        ),
    )

    ax.set_xlabel("DFT (eV)", fontsize=40)
    ax.set_ylabel(f"{MLIP_name} (eV)", fontsize=40)
    ax.tick_params(axis="both", which="major", labelsize=20)
    ax.grid(True)

    for spine in ax.spines.values():
        spine.set_linewidth(3)

    plt.tight_layout()
    plt.savefig(f"{plot_save_path}/{tag}_mono.png", dpi=dpi)
    plt.close()

    return MAE


def plotter_multi(ads_data, MLIP_name, types, tag, min_value, max_value, **kwargs):
    colors = [
        "blue",
        "red",
        "green",
        "purple",
        "orange",
        "brown",
        "pink",
        "gray",
        "olive",
        "cyan",
        "magenta",
        "lime",
        "indigo",
        "gold",
        "darkred",
        "teal",
        "coral",
        "turquoise",
        "salmon",
        "navy",
        "maroon",
        "forestgreen",
        "darkorange",
        "aqua",
        "lavender",
        "khaki",
        "crimson",
        "chocolate",
        "sienna",
        "cornflowerblue",
        "lightgreen",
        "plum",
        "lightgoldenrodyellow",
        "peachpuff",
        "ivory",
        "chartreuse",
        "slategray",
        "firebrick",
        "wheat",
        "dodgerblue",
        "orchid",
        "steelblue",
    ] * 10
    markers = [
        "o",
        "^",
        "s",
        "p",
        "*",
        "h",
        "D",
        "H",
        "d",
        "<",
        ">",
        "v",
        "8",
        "P",
        "X",
        "o",
        "^",
        "s",
        "p",
        "*",
        "h",
        "D",
        "H",
        "d",
        "<",
        ">",
        "v",
        "8",
        "P",
        "X",
        "o",
        "^",
        "s",
        "p",
        "*",
        "h",
        "D",
        "H",
        "d",
        "<",
        ">",
        "v",
        "8",
    ] * 10
    plot_save_path = os.path.join(os.getcwd(), "plot", MLIP_name)
    os.makedirs(plot_save_path, exist_ok=True)
    figsize = kwargs.get("figsize", (9, 8))
    mark_size = kwargs.get("mark_size", 100)
    linewidths = kwargs.get("linewidths", 1.5)
    dpi = kwargs.get("dpi", 300)
    legend_off = kwargs.get("legend_off", False)
    error_bar_display = kwargs.get("error_bar_display", False)
    font_setting = kwargs.get("font_setting", False)
    
    if font_setting:
        set_matplotlib_font(font_setting[0], font_setting[1])

    analysis_adsorbates = [
        adsorbate for adsorbate in ads_data.keys() if adsorbate != "all"
    ]

    len_adsorbates = len(analysis_adsorbates)
    legend_width = len(max(analysis_adsorbates, key=len))

    fig, ax = plt.subplots(figsize=figsize)
    error_sum = 0
    len_total = 0
    MAEs = {}

    scatter_handles = []

    # Check if this is a single calculation by looking at data structure
    is_single_calc = "MLIP_min" not in ads_data["all"].get(types[0], {})

    for i, adsorbate in enumerate(analysis_adsorbates):
        if "normal" in ads_data["all"]:
            DFT_values = []
            MLIP_values = []
            for type in types:
                DFT_values.append(ads_data[adsorbate][type]["DFT"])
                MLIP_values.append(ads_data[adsorbate][type]["MLIP"])
        else:
            DFT_values = [ads_data[adsorbate]["all"]["DFT"]]
            MLIP_values = [ads_data[adsorbate]["all"]["MLIP"]]
                
        DFT_values = np.concatenate(DFT_values)
        MLIP_values = np.concatenate(MLIP_values)

        scatter = ax.scatter(
            DFT_values,
            MLIP_values,
            color=colors[i],
            label=f"* {adsorbate}",
            marker=markers[i],
            s=mark_size,
            edgecolors="black",
            linewidths=linewidths,
        )
        
        if error_bar_display and not is_single_calc:
            MLIP_mins = []
            MLIP_maxs = []
            
            for type in types:
                MLIP_mins.append(ads_data[adsorbate][type]["MLIP_min"])
                MLIP_maxs.append(ads_data[adsorbate][type]["MLIP_max"])
                
            MLIP_mins = np.concatenate(MLIP_mins)
            MLIP_maxs = np.concatenate(MLIP_maxs)
            
            yerr_minus = MLIP_values - MLIP_mins
            yerr_plus = MLIP_maxs - MLIP_values
            ax.errorbar(
                DFT_values,
                MLIP_values,
                yerr=[yerr_minus, yerr_plus],
                fmt='none',
                ecolor="black",
                capsize=3,
                capthick=1,
                elinewidth=1,
            )
        
        scatter_handles.append(scatter)

        MAEs[adsorbate] = (
            np.sum(np.abs(DFT_values - MLIP_values)) / len(DFT_values)
            if len(DFT_values) != 0
            else 0
        )
        error_sum += np.sum(np.abs(DFT_values - MLIP_values))
        len_total += len(DFT_values)

        MAEs[f"len_{adsorbate}"] = len(DFT_values)

    ax.set_xlim(min_value, max_value)
    ax.set_ylim(min_value, max_value)
    ax.plot([min_value, max_value], [min_value, max_value], "r-")

    MAE_total = error_sum / len_total if len_total != 0 else 0
    MAEs["total"] = MAE_total

    ax.text(
        x=0.05,
        y=0.95,
        s=f"MAE-{MLIP_name}: {MAE_total:.2f}",
        transform=plt.gca().transAxes,
        fontsize=30,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round", alpha=0.5, facecolor="white", edgecolor="black", pad=0.5
        ),
    )

    ax.set_xlabel("DFT (eV)", fontsize=40)
    ax.set_ylabel(f"{MLIP_name} (eV)", fontsize=40)
    ax.tick_params(axis="both", which="major", labelsize=20)

    if (
        legend_width < 8
        and len_adsorbates < 6
        or legend_width < 5
        and len_adsorbates < 8
    ) and not legend_off:
        ax.legend(loc="lower right", fontsize=20, ncol=(len_adsorbates // 7) + 1)
    else:
        fig_legend = plt.figure()
        fig_legend.legend(
            handles=scatter_handles,
            loc="center",
            frameon=False,
            ncol=(len_adsorbates // 7) + 1,
        )
        fig_legend.savefig(f"{plot_save_path}/legend.png", dpi=dpi, bbox_inches="tight")
        plt.close(fig_legend)

    ax.grid(True)

    for spine in ax.spines.values():
        spine.set_linewidth(3)

    plt.tight_layout()
    plt.savefig(f"{plot_save_path}/{tag}_multi.png", dpi=dpi)
    plt.close()

    return MAEs


def data_to_excel(main_data, anomaly_data, MLIPs_data, analysis_adsorbates, **kwargs):
    benchmarking_name = kwargs.get("Benchmarking_name", os.path.basename(os.getcwd()))

    df_main = pd.DataFrame(main_data)

    output_file = f"{benchmarking_name}_Benchmarking_Analysis.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df_main.to_excel(writer, sheet_name="MLIP_Data", index=False)

        df_anomaly = pd.DataFrame(anomaly_data)
        df_anomaly.to_excel(writer, sheet_name="anomaly", index=False)

        for MLIP_name, data_dict in MLIPs_data.items():
            data_tmp = []
            for adsorbate in analysis_adsorbates:
                if f"len_{adsorbate}" in data_dict["normal"]:
                    anomaly_ratio = (
                        (1 - data_dict["normal"][f"len_{adsorbate}"]
                        / data_dict["all"][f"len_{adsorbate}"])
                        * 100
                    )
                    data_tmp.append(
                        {
                            "Adsorbate_name": adsorbate,
                            "Anomaly ratio (%)": anomaly_ratio,
                            "MAE_total (eV)": data_dict["all"][adsorbate],
                            "MAE_normal (eV)": data_dict["normal"][adsorbate],
                            "MAE_anomaly (eV)": data_dict["anomaly"][adsorbate],
                            "Num_total": data_dict["all"][f"len_{adsorbate}"],
                            "Num_normal": data_dict["normal"][f"len_{adsorbate}"],
                            "Num_anomaly": data_dict["anomaly"][f"len_{adsorbate}"],
                        }
                    )

            data_df = pd.DataFrame(data_tmp)
            data_df.to_excel(writer, sheet_name=MLIP_name, index=False)

        # 워크북 및 포맷 정의
        workbook = writer.book
        header_format = workbook.add_format({
            "align": "center", 
            "valign": "vcenter",
            "bold": True
        })
        center_align = workbook.add_format({"align": "center", "valign": "vcenter"})
        number_format_0f = workbook.add_format(
            {"num_format": "#,##0", "align": "center", "valign": "vcenter"}
        )
        number_format_1f = workbook.add_format(
            {"num_format": "0.0", "align": "center", "valign": "vcenter"}
        )
        number_format_2f = workbook.add_format(
            {"num_format": "0.00", "align": "center", "valign": "vcenter"}
        )
        number_format_3f = workbook.add_format(
            {"num_format": "0.000", "align": "center", "valign": "vcenter"}
        )

        # 열 별 형식 및 너비 지정
        column_formats = {
            "Anomaly ratio (%)": (
                20,
                workbook.add_format(
                    {
                        "num_format": "0.00",
                        "align": "center",
                        "bold": True,
                        "valign": "vcenter",
                    }
                ),
            ),
            "MAE_total (eV)": (15, number_format_3f),
            "MAE_normal (eV)": (
                17,
                workbook.add_format(
                    {
                        "num_format": "0.000",
                        "align": "center",
                        "bold": True,
                        "valign": "vcenter",
                    }
                ),
            ),
            "MAE_anomaly (eV)": (20, number_format_3f),
            "Num_total": (12, number_format_0f),
            "Num_normal": (13, number_format_0f),
            "Num_anomaly": (15, number_format_0f),
            "slab_conv": (12, number_format_0f),
            "ads_conv": (12, number_format_0f),
            "slab_move": (12, number_format_0f),
            "ads_move": (12, number_format_0f),
            "slab_seed": (12, number_format_0f),
            "ads_seed": (12, number_format_0f),
            "ads_eng_seed": (12, number_format_0f),
            "Time_total (s)": (15, number_format_0f),
            "Time_per_step (s)": (17, number_format_3f),
        }

        # 모든 시트에 대해 포맷 적용
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            df = (
                df_main
                if sheet_name == "MLIP_Data"
                else (
                    df_anomaly
                    if sheet_name == "anomaly"
                    else pd.DataFrame(
                        [dict(zip(data_tmp[0].keys(), range(len(data_tmp[0]))))]
                    )
                )
            )

            # 헤더 포맷 적용
            for col_num, col_name in enumerate(df.columns):
                worksheet.write(0, col_num, col_name, header_format)

            for col_num, col_name in enumerate(df.columns):
                if col_name in column_formats:
                    width, fmt = column_formats[col_name]
                else:
                    width = (
                        max(df[col_name].astype(str).map(len).max(), len(col_name)) + 10
                    )
                    fmt = center_align

                worksheet.set_column(col_num, col_num, width, fmt)

                # 문자열 열인 경우
                if df[col_name].dtype == "object":
                    worksheet.set_column(col_num, col_num, width, center_align)
                else:
                    worksheet.set_column(col_num, col_num, width, fmt)

            row_height = 20
            for row in range(len(df) + 1):
                worksheet.set_row(row, row_height)

    print(f"Excel file '{output_file}' created successfully.")


def count_lbfgs_steps(log_path):
    with open(log_path, "r") as file:
        lines = file.readlines()

    # Iterate through the lines in reverse to find the last "Done!" instance
    for i, line in enumerate(reversed(lines)):
        if "Done!" in line:
            # Get the line right above "Done!"
            previous_line = lines[
                -(i + 2)
            ]  # i+2 because i starts at 0 and we're looking for the line above
            if len(previous_line.split()) == 5:
                # Extract the step number from the LBFGS line and add 1
                step_number = int(previous_line.split()[1])
                return step_number + 1
            else:
                print("calculation fail")

    # Return 0 if "Done!" or "LBFGS:" is not found
    print(log_path)
    print("notfound")
    return 0


def get_txt_files_in_directory(directory_path):
    txt_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".txt"):
                # Get full path of the txt file
                full_path = os.path.join(root, file)
                txt_files.append(full_path)

    return txt_files

def get_ads_eng_range(data_dict):
    ads_eng_values = []
    for key in data_dict:
        if isinstance(key, (int, str)) and key.isdigit():
            ads_eng_values.append(data_dict[key]["ads_eng"])
            
    return min(ads_eng_values), max(ads_eng_values)

def analysis_MLIPs(**kwargs):
    main_data = []
    anomaly_data = []
    MLIP_datas = {}
    adsorbates = set()
    calculating_path = kwargs.get(
        "calculating_path", os.path.join(os.getcwd(), "result")
    )

    MLIP_list = kwargs.get(
        "MLIP_list",
        sorted(
            [
                name
                for name in os.listdir(calculating_path)
                if os.path.isdir(os.path.join(calculating_path, name))
            ],
            key=str.lower,
        ),
    )
    for MLIP_name in MLIP_list:
        absolute_energy_MLIP = True
        first_reaction = True
        print(MLIP_name)
        with open(f"{calculating_path}/{MLIP_name}/{MLIP_name}_result.json", "r") as f:
            MLIP_result = json.load(f)

        with open(f"{calculating_path}/{MLIP_name}/{MLIP_name}_anomaly_detection.json", "r") as f:
            MLIP_anomaly = json.load(f)

        ads_data = {
            "all": {
                "normal": {"DFT": np.array([]), "MLIP": np.array([]), "MLIP_min": np.array([]), "MLIP_max": np.array([])},
                "anomaly": {"DFT": np.array([]), "MLIP": np.array([]), "MLIP_min": np.array([]), "MLIP_max": np.array([])},
            }
        }

        for reaction in MLIP_result:
            adsorbate = find_adsorbate(MLIP_result[reaction]["reference"])
            adsorbates.add(adsorbate)
            
            if first_reaction:
                first_reaction = False
                if "slab_conv" not in MLIP_result[reaction]["anomalies"]:
                    absolute_energy_MLIP = False

        time_accum = 0
        step_accum = 0

        slab_conv = 0
        ads_conv = 0
        slab_move = 0
        ads_move = 0
        slab_seed = 0
        ads_seed = 0
        ads_eng_seed = 0

        analysis_adsorbates = kwargs.get("target_adsorbates", adsorbates)

        for reaction in MLIP_result:
            adsorbate = find_adsorbate(MLIP_result[reaction]["reference"])
            if adsorbate in analysis_adsorbates:
                if adsorbate not in ads_data:
                    ads_data[adsorbate] = {
                        "normal": {"DFT": np.array([]), "MLIP": np.array([]), "MLIP_min": np.array([]), "MLIP_max": np.array([])},
                        "anomaly": {"DFT": np.array([]), "MLIP": np.array([]), "MLIP_min": np.array([]), "MLIP_max": np.array([])},
                    }

                num_anomalies = sum(MLIP_result[reaction]["anomalies"].values())
                
                MLIP_min, MLIP_max = get_ads_eng_range(MLIP_result[reaction])

                # 데이터를 임시 저장할 백업 생성
                backup = {
                    "normal": {
                        "DFT": ads_data[adsorbate]["normal"]["DFT"].copy(),
                        "MLIP": ads_data[adsorbate]["normal"]["MLIP"].copy(),
                        "MLIP_min": ads_data[adsorbate]["normal"]["MLIP_min"].copy(),
                        "MLIP_max": ads_data[adsorbate]["normal"]["MLIP_max"].copy()
                    },
                    "anomaly": {
                        "DFT": ads_data[adsorbate]["anomaly"]["DFT"].copy(),
                        "MLIP": ads_data[adsorbate]["anomaly"]["MLIP"].copy(),
                        "MLIP_min": ads_data[adsorbate]["anomaly"]["MLIP_min"].copy(),
                        "MLIP_max": ads_data[adsorbate]["anomaly"]["MLIP_max"].copy()
                    }
                }

                backup_all = {
                    "normal": {
                        "DFT": ads_data["all"]["normal"]["DFT"].copy(),
                        "MLIP": ads_data["all"]["normal"]["MLIP"].copy(),
                        "MLIP_min": ads_data["all"]["normal"]["MLIP_min"].copy(),
                        "MLIP_max": ads_data["all"]["normal"]["MLIP_max"].copy()
                    },
                    "anomaly": {
                        "DFT": ads_data["all"]["anomaly"]["DFT"].copy(),
                        "MLIP": ads_data["all"]["anomaly"]["MLIP"].copy(),
                        "MLIP_min": ads_data["all"]["anomaly"]["MLIP_min"].copy(),
                        "MLIP_max": ads_data["all"]["anomaly"]["MLIP_max"].copy()
                    }
                }

                try:
                    if num_anomalies == 0:
                        ads_data[adsorbate]["normal"]["DFT"] = np.append(
                            ads_data[adsorbate]["normal"]["DFT"],
                            MLIP_result[reaction]["reference"]["ads_eng"],
                        )
                        ads_data[adsorbate]["normal"]["MLIP"] = np.append(
                            ads_data[adsorbate]["normal"]["MLIP"],
                            MLIP_result[reaction]["final"]["ads_eng_median"],
                        )
                        ads_data[adsorbate]["normal"]["MLIP_min"] = np.append(
                            ads_data[adsorbate]["normal"]["MLIP_min"],
                            MLIP_min,
                        )
                        ads_data[adsorbate]["normal"]["MLIP_max"] = np.append(
                            ads_data[adsorbate]["normal"]["MLIP_max"],
                            MLIP_max,
                        )
                        ads_data["all"]["normal"]["DFT"] = np.append(
                            ads_data["all"]["normal"]["DFT"],
                            MLIP_result[reaction]["reference"]["ads_eng"],
                        )
                        ads_data["all"]["normal"]["MLIP"] = np.append(
                            ads_data["all"]["normal"]["MLIP"],
                            MLIP_result[reaction]["final"]["ads_eng_median"],
                        )
                        ads_data["all"]["normal"]["MLIP_min"] = np.append(
                            ads_data["all"]["normal"]["MLIP_min"],
                            MLIP_min,
                        )
                        ads_data["all"]["normal"]["MLIP_max"] = np.append(
                            ads_data["all"]["normal"]["MLIP_max"],
                            MLIP_max,
                        )
                    else:
                        ads_data[adsorbate]["anomaly"]["DFT"] = np.append(
                            ads_data[adsorbate]["anomaly"]["DFT"],
                            MLIP_result[reaction]["reference"]["ads_eng"],
                        )
                        ads_data[adsorbate]["anomaly"]["MLIP"] = np.append(
                            ads_data[adsorbate]["anomaly"]["MLIP"],
                            MLIP_result[reaction]["final"]["ads_eng_median"],
                        )
                        ads_data[adsorbate]["anomaly"]["MLIP_min"] = np.append(
                            ads_data[adsorbate]["anomaly"]["MLIP_min"],
                            MLIP_min,
                        )
                        ads_data[adsorbate]["anomaly"]["MLIP_max"] = np.append(
                            ads_data[adsorbate]["anomaly"]["MLIP_max"],
                            MLIP_max,
                        )
                        ads_data["all"]["anomaly"]["DFT"] = np.append(
                            ads_data["all"]["anomaly"]["DFT"],
                            MLIP_result[reaction]["reference"]["ads_eng"],
                        )
                        ads_data["all"]["anomaly"]["MLIP"] = np.append(
                            ads_data["all"]["anomaly"]["MLIP"],
                            MLIP_result[reaction]["final"]["ads_eng_median"],
                        )
                        ads_data["all"]["anomaly"]["MLIP_min"] = np.append(
                            ads_data["all"]["anomaly"]["MLIP_min"],
                            MLIP_min,
                        )
                        ads_data["all"]["anomaly"]["MLIP_max"] = np.append(
                            ads_data["all"]["anomaly"]["MLIP_max"],
                            MLIP_max,
                        )
                except Exception as e:
                    # 에러 발생 시 백업 데이터로 복원
                    ads_data[adsorbate]["normal"] = backup["normal"]
                    ads_data[adsorbate]["anomaly"] = backup["anomaly"]
                    ads_data["all"]["normal"] = backup_all["normal"]
                    ads_data["all"]["anomaly"] = backup_all["anomaly"]
                    print(f"Error processing reaction {reaction} for adsorbate {adsorbate}: {str(e)}")
                    continue

                time_accum += sum(
                    value
                    for key, value in MLIP_result[reaction]["final"].items()
                    if "time_total" in key
                )

                log_dir_path = f"{calculating_path}/{MLIP_name}/log/{reaction}"
                txt_files = get_txt_files_in_directory(log_dir_path)

                for txt_file in txt_files:
                    step_tmp = count_lbfgs_steps(txt_file)
                    step_accum += step_tmp

                if absolute_energy_MLIP:
                    if MLIP_result[reaction]["anomalies"]["slab_conv"]:
                        slab_conv += 1

                if MLIP_result[reaction]["anomalies"]["ads_conv"]:
                    ads_conv += 1                    
                
                if absolute_energy_MLIP:
                    if MLIP_result[reaction]["anomalies"]["slab_move"]:
                        slab_move += 1

                if MLIP_result[reaction]["anomalies"]["ads_move"]:
                        ads_move += 1

                if absolute_energy_MLIP:
                    if MLIP_result[reaction]["anomalies"]["slab_seed"]:
                        slab_seed += 1

                if absolute_energy_MLIP:
                    if MLIP_result[reaction]["anomalies"]["ads_seed"]:
                        ads_seed += 1

                if MLIP_result[reaction]["anomalies"]["ads_eng_seed"]:
                    ads_eng_seed += 1

        DFT_data = np.concatenate(
            (ads_data["all"]["normal"]["DFT"], ads_data["all"]["anomaly"]["DFT"])
        )
        min_value_DFT, max_value_DFT = min_max(DFT_data)

        min_value = kwargs.get("min", min_value_DFT)
        max_value = kwargs.get("max", max_value_DFT)

        MAE_all = plotter_mono(
            ads_data,
            MLIP_name,
            "all",
            min_value,
            max_value,
            **kwargs,
        )
        MAE_normal = plotter_mono(
            ads_data,
            MLIP_name,
            "normal",
            min_value,
            max_value,
            **kwargs,
        )
        MAE_anomaly = plotter_mono(
            ads_data,
            MLIP_name,
            "anomaly",
            min_value,
            max_value,
            **kwargs,
        )

        MAEs_all_multi = plotter_multi(
            ads_data,
            MLIP_name,
            ["normal", "anomaly"],
            "all",
            min_value,
            max_value,
            **kwargs,
        )
        MAEs_normal_multi = plotter_multi(
            ads_data, MLIP_name, ["normal"], "normal", min_value, max_value, **kwargs
        )
        MAEs_anomaly_multi = plotter_multi(
            ads_data, MLIP_name, ["anomaly"], "anomaly", min_value, max_value, **kwargs
        )

        MLIP_datas[MLIP_name] = {
            "all": MAEs_all_multi,
            "normal": MAEs_normal_multi,
            "anomaly": MAEs_anomaly_multi,
        }

        total_num = len(ads_data["all"]["normal"]["DFT"]) + len(
            ads_data["all"]["anomaly"]["DFT"]
        )
        anomaly_ratio = (1 - len(ads_data["all"]["normal"]["DFT"]) / total_num) * 100

        main_data.append(
            {
                "MLIP_name": MLIP_name,
                "Anomaly ratio (%)": anomaly_ratio,
                "MAE_total (eV)": MAE_all,
                "MAE_normal (eV)": MAE_normal,
                "MAE_anomaly (eV)": MAE_anomaly,
                "Num_total": total_num,
                "Num_normal": len(ads_data["all"]["normal"]["DFT"]),
                "Num_anomaly": len(ads_data["all"]["anomaly"]["DFT"]),
                "Time_total (s)": MLIP_anomaly["Time"],
                "Time_per_step (s)": time_accum / step_accum,
            }
        )

        anomaly_data_dict = {
            "MLIP_name": MLIP_name,
            "Num_anomaly": len(ads_data["all"]["anomaly"]["DFT"]),
            "ads_conv": ads_conv,
            "ads_move": ads_move,
            "ads_eng_seed": ads_eng_seed,
        }

        # slab 관련 항목들은 absolute_energy_MLIP이 true일 때만 추가
        if absolute_energy_MLIP:
            anomaly_data_dict.update({
                "slab_conv": slab_conv,
                "slab_move": slab_move,
                "slab_seed": slab_seed,
                "ads_seed": ads_seed,
            })

        anomaly_data.append(anomaly_data_dict)

    data_to_excel(
        main_data, anomaly_data, MLIP_datas, list(analysis_adsorbates), **kwargs
    )


def analysis_MLIPs_single(**kwargs):
    main_data = []
    MLIP_datas = {}
    adsorbates = set()
    single_path = kwargs.get("single_path", os.path.join(os.getcwd(), "result_single"))
    if os.path.exists(single_path):
        MLIP_single_list = kwargs.get(
            "MLIP_list",
            sorted(
                [
                    name
                    for name in os.listdir(single_path)
                    if os.path.isdir(os.path.join(single_path, name))
                ],
                key=str.lower,
            ),
        )

        for MLIP_name in MLIP_single_list:
            print(MLIP_name)
            with open(f"{single_path}/{MLIP_name}/{MLIP_name}_result.json", "r") as f:
                MLIP_result = json.load(f)

            # 데이터 구조 수정
            ads_data = {
                "all": {
                    "all": {"DFT": np.array([]), "MLIP": np.array([])}  # 'all' 키를 한 단계 더 추가
                }
            }

            for reaction in MLIP_result:
                adsorbate = find_adsorbate(MLIP_result[reaction]["reference"])
                adsorbates.add(adsorbate)

            analysis_adsorbates = kwargs.get("target_adsorbates", adsorbates)

            for reaction in MLIP_result:
                adsorbate = find_adsorbate(MLIP_result[reaction]["reference"])
                if adsorbate in analysis_adsorbates:
                    if adsorbate not in ads_data:
                        ads_data[adsorbate] = {
                            "all": {"DFT": np.array([]), "MLIP": np.array([])}
                        }

                    ads_data[adsorbate]["all"]["DFT"] = np.append(
                        ads_data[adsorbate]["all"]["DFT"],
                        MLIP_result[reaction]["reference"]["ads_eng"],
                    )
                    ads_data[adsorbate]["all"]["MLIP"] = np.append(
                        ads_data[adsorbate]["all"]["MLIP"],
                        MLIP_result[reaction]["SC_calc"]["ads_eng"],
                    )
                    ads_data["all"]["all"]["DFT"] = np.append(
                        ads_data["all"]["all"]["DFT"],
                        MLIP_result[reaction]["reference"]["ads_eng"],
                    )
                    ads_data["all"]["all"]["MLIP"] = np.append(
                        ads_data["all"]["all"]["MLIP"],
                        MLIP_result[reaction]["SC_calc"]["ads_eng"],
                    )

            DFT_data = ads_data["all"]["all"]["DFT"]
            MLIP_data = ads_data["all"]["all"]["MLIP"]

            min_value_DFT, max_value_DFT = min_max(DFT_data)

            min_value = kwargs.get("min", min_value_DFT)
            max_value = kwargs.get("max", max_value_DFT)

            MAE_all = plotter_mono(
                ads_data, MLIP_name, "single", min_value, max_value, **kwargs
            )

            MAEs_all_multi = plotter_multi(
                ads_data,
                MLIP_name,
                ["all"],  # 여기서 'all'을 리스트로 전달
                "single",
                min_value,
                max_value,
                **kwargs,
            )

            MLIP_datas[MLIP_name] = MAEs_all_multi
            total_num = len(DFT_data)

            main_data.append(
                {"MLIP_name": MLIP_name, "MAE (eV)": MAE_all, "Num_total": total_num}
            )

        data_to_excel_single(main_data, MLIP_datas, list(analysis_adsorbates), **kwargs)


def execute_benchmark_single(calculator, **kwargs):
    required_keys = ["MLIP_name", "benchmark"]

    for key in required_keys:
        if key not in kwargs:
            raise ValueError(f"Missing required keyword argument: {key}")

    MLIP_name = kwargs["MLIP_name"]
    benchmark = kwargs["benchmark"]
    gas_distance = kwargs.get("gas_distance", 10)
    optimizer = kwargs.get("optimizer", "LBFGS")

    path_pkl = os.path.join(os.getcwd(), f"raw_data/{benchmark}.pkl")

    with open(path_pkl, "rb") as file:
        ref_data = pickle.load(file)

    save_directory = os.path.join(os.getcwd(), "result_single", MLIP_name)
    print(f"Starting {MLIP_name} Benchmarking")
    # Basic Settings==============================================================================
    os.makedirs(f"{save_directory}/structures", exist_ok=True)
    os.makedirs(f"{save_directory}/gases", exist_ok=True)

    final_result = {}

    # Calculation Part==============================================================================

    gas_energies = {}

    print("Starting calculations...")
    for index, key in enumerate(ref_data):
        try:
            print(f"[{index+1}/{len(ref_data)}] {key}")
            final_result[key] = {}
            final_result[key]["reference"] = {}
            final_result[key]["reference"]["ads_eng"] = ref_data[key]["ref_ads_eng"]
            for structure in ref_data[key]["raw"]:
                if "gas" not in str(structure):
                    final_result[key]["reference"][f"{structure}_abs"] = ref_data[key]["raw"][structure]["energy_ref"]
                    
            structure_path = f"{save_directory}/structures/{key}"
            os.makedirs(structure_path, exist_ok=True)
            informs = {}
            informs["ads_eng"] = []

            ads_energy_calc = 0
            for structure in ref_data[key]["raw"]:
                if "gas" not in str(structure):
                    POSCAR_str = ref_data[key]["raw"][structure]["atoms"]
                    write(f"{structure_path}/CONTCAR_{structure}", POSCAR_str)
                    energy_calculated = energy_cal_single(calculator, POSCAR_str)
                    ads_energy_calc += (
                        energy_calculated * ref_data[key]["raw"][structure]["stoi"]
                    )
                    if structure == "star":
                        slab_energy = energy_calculated
                    else:
                        ads_energy = energy_calculated

                else:
                    if structure in gas_energies:
                        ads_energy_calc += (
                            gas_energies[structure]
                            * ref_data[key]["raw"][structure]["stoi"]
                        )
                    else:
                        print(f"{structure} calculating")
                        gas_CONTCAR, gas_energy = energy_cal_gas(
                            calculator,
                            ref_data[key]["raw"][structure]["atoms"],
                            0.05,
                            f"{save_directory}/gases/POSCAR_{structure}",
                            gas_distance,
                            optimizer,
                            f"{save_directory}/gases/{structure}.txt",
                            f"{save_directory}/gases/{structure}",
                        )
                        gas_energies[structure] = gas_energy
                        ads_energy_calc += (
                            gas_energy * ref_data[key]["raw"][structure]["stoi"]
                        )
                        write(f"{save_directory}/gases/CONTCAR_{structure}", gas_CONTCAR)

            final_result[key]["SC_calc"] = {
                "ads_eng": ads_energy_calc,
                "slab_abs": slab_energy,
                "ads_abs": ads_energy,
            }

            with open(f"{save_directory}/{MLIP_name}_result.json", "w") as file:
                json.dump(final_result, file, indent=4)

            with open(f"{save_directory}/{MLIP_name}_gases.json", "w") as file:
                json.dump(gas_energies, file, indent=4)

        except Exception as e:
            print(f"Error occurred while processing {key}: {str(e)}")
            print("Skipping to next reaction...")
            continue

    print(f"{MLIP_name} Benchmarking Finish")


def data_to_excel_single(main_data, MLIPs_data, analysis_adsorbates, **kwargs):
    benchmarking_name = kwargs.get("Benchmarking_name", os.path.basename(os.getcwd()))

    df_main = pd.DataFrame(main_data)

    output_file = f"{benchmarking_name}_Single_Benchmarking_Analysis.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df_main.to_excel(writer, sheet_name="MLIP_Data", index=False)

        for MLIP_name, data_dict in MLIPs_data.items():
            data_tmp = []
            for adsorbate in analysis_adsorbates:
                if f"len_{adsorbate}" in data_dict:
                    data_tmp.append(
                        {
                            "Adsorbate_name": adsorbate,
                            "MAE_total (eV)": data_dict[adsorbate],
                            "Num_total": data_dict[f"len_{adsorbate}"],
                        }
                    )

            data_df = pd.DataFrame(data_tmp)
            data_df.to_excel(writer, sheet_name=MLIP_name, index=False)

        # 워크북 및 포맷 정의
        workbook = writer.book
        header_format = workbook.add_format({
            "align": "center", 
            "valign": "vcenter",
            "bold": True
        })
        center_align = workbook.add_format({"align": "center", "valign": "vcenter"})
        number_format_0f = workbook.add_format(
            {"num_format": "#,##0", "align": "center", "valign": "vcenter"}
        )
        number_format_1f = workbook.add_format(
            {"num_format": "0.0", "align": "center", "valign": "vcenter"}
        )
        number_format_2f = workbook.add_format(
            {"num_format": "0.00", "align": "center", "valign": "vcenter"}
        )
        number_format_3f = workbook.add_format(
            {"num_format": "0.000", "align": "center", "valign": "vcenter"}
        )

        # 열 별 형식 및 너비 지정
        column_formats = {
            "MAE (eV)": (
                15,
                workbook.add_format(
                    {
                        "num_format": "0.000",
                        "align": "center",
                        "bold": True,
                        "valign": "vcenter",
                    }
                ),
            ),
            "MAE_total (eV)": (15, number_format_3f),
            "Num_total": (12, number_format_0f),
        }

        # 모든 시트에 대해 포맷 적용
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            df = (
                df_main if sheet_name == "MLIP_Data" 
                else pd.DataFrame(data_tmp)
            )

            # 헤더 포맷 적용
            for col_num, col_name in enumerate(df.columns):
                worksheet.write(0, col_num, col_name, header_format)

            for col_num, col_name in enumerate(df.columns):
                if col_name in column_formats:
                    width, fmt = column_formats[col_name]
                else:
                    width = (
                        max(df[col_name].astype(str).map(len).max(), len(col_name)) + 10
                    )
                    fmt = center_align

                worksheet.set_column(col_num, col_num, width, fmt)

                # 문자열 열인 경우
                if df[col_name].dtype == "object":
                    worksheet.set_column(col_num, col_num, width, center_align)
                else:
                    worksheet.set_column(col_num, col_num, width, fmt)

            # 행 높이 설정
            row_height = 20
            for row in range(len(df) + 1):
                worksheet.set_row(row, row_height)

    print(f"Excel file '{output_file}' created successfully.")
