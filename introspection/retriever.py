# importation
import os
import pandas as pd
import glob

def retrieve_from_annotation(work_folder):
    """
    Kind of placeholder (a little bit more efficient)
    have to fix the annotation folder name and might be
    adapt to multiple annottaion target files

    -> actually just use a gene list from the generated data file and return it
    """

    # parameters
    introspection_folder = f"{work_folder}/introspection"
    data_file_list = glob.glob(f"{work_folder}/*.csv")

    # check if target file exist
    if(len(data_file_list) == 0):
        print(f"<<!>> [INTROSPECTION] -> can't find data file to extract genes")
        print(f"<<!>> [INTROSPECTION] -> droping introspection step")
        return 0
    
    # pick the longest name possible, ok its seem stupid but actualy the csv file with the
    # longest name is the csv file that have gone through the more steps, ie the one
    # you should_use
    data_file = data_file_list[0]
    for candidate in data_file_list:
        if(len(candidate) > len(data_file)):
            data_file = candidate

    # load annotation file and retrieve target list
    target_list = []
    df = pd.read_csv(data_file)
    for elt in list(df.keys()):

        # extract target
        if(elt not in ["ID", "LABEL"]):
            target_list.append(elt)

    # return extracted list
    return target_list
