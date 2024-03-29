# importation
import pandas as pd
import os
import stat_stuff

def run(work_folder, data_file):
    """
    This is a touchy one

    - a note about z-score : the way we intend to compute it (z -score of each individual based on
    multiple variables) is kind of disturbing, as I understand it assume that all variables
    describing the patient share a similar distribution (or at least modality in same range of magnitude)
        -> might be tricky to use outside normalize data such as vst
        Have to double check the process
    """

    # parameters
    introspection_folder = f"{work_folder}/introspection_log"
    statistic_folder = f"{work_folder}/introspection_log/statistic"

    # check that data file exist
    if(not os.path.isfile(data_file)):
        print(f"<<INTROSPECTION||P-HACKING>> no file {data_file}, skipping")
        return 0

    # init work environment
    if(not os.path.isdir(introspection_folder)):
        os.mkdir(introspection_folder)
        os.mkdir(statistic_folder)
    elif(not os.path.isdir(statistic_folder)):
        os.mkdir(statistic_folder)

    # load data
    df = pd.read_csv(data_file)

    # test z score value of all variables between the different classes
    # init gene list
    gene_list = []
    for k in list(df.keys()):
        if(k not in ["ID", "LABEL"]):
            gene_list.append(k)

    # init output_file_name
    output_file_name = data_file.split("/")
    output_file_name = output_file_name[-1]
    output_file_name = output_file_name.replace("_data.csv", "zscore.png")
    output_file_name = f"{statistic_folder}/{output_file_name}"
    
    # generate figure
    stat_stuff.plot_zscore(data_file, gene_list, output_file_name)

    # perform stat test for each single component of each signature
    # nut sure its very interesting to implement at this point
    # let in stand by for now
    
    # target_list = []
    # for target in list(df.keys()):
    #     if(target not in ["ID", "LABEL"]):
    #
    #         # save in traget list
    #         target_list.append(target)
    #
    #         # TODO extract data
    #         # TODO compute stat test between classes
    #         # TODO generate figure
    #         # TODO save figure


if __name__ == "__main__":
    
    # test space
    work_folder = "/tmp/murloc_test"
    data_file = "/home/fox/Workspace/trash/toy_data_murloc.csv"

    run(
        work_folder,
        data_file
    )
    
