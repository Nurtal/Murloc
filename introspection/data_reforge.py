# importation
import os
import pandas as pd


def reforge(work_folder, target_list, original_dataset_file, output_data_name):
    """
    """

    # parameters
    log_file_name = output_data_name.replace(".csv", ".log")

    # init sub data folder if not exist
    if(not os.path.isdir(f"{work_folder}/introspection_log/data")):
        os.mkdir(f"{work_folder}/introspection_log/data")

    # try to locate original dataset file
    if(not os.path.isfile(original_dataset_file)):
        print(f"<<!>> [INTROSPECTION] -> can't find the file {original_dataset_file}")
        print(f"<<!>> [INTROSPECTION] -> droping introspection step")
        return 0

    # check that target list is not empty
    if(len(target_list) == 0):
        print(f"<<!>> [INTROSPECTION] -> the provided target list is empty")
        print(f"<<!>> [INTROSPECTION] -> droping introspection step for {output_data_name}")
        return 0
    
    # read original dataset
    df = pd.read_csv(original_dataset_file)
    id_var = list(df.keys())[0]
    label_var = list(df.keys())[-1]
    var_to_keep = [id_var]
    missed_target = []
    for target in target_list:
        if(target in list(df.keys())):
            var_to_keep.append(target)
        else:
            missed_target.append(target)
    var_to_keep.append(label_var)
    
    # select targets
    df = df[var_to_keep]

    # save file
    df.to_csv(output_data_name, index=False)

    # write log file
    log_file = open(log_file_name, "w")
    log_file.write("MISSED-TARGET\n")
    for elt in missed_target:
        log_file.write(f"{elt}\n")
    log_file.close()


    
