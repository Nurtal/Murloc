# importation
import random

def generate_test_dataset():
    """
    Generate a simple dataset in the current folder
    """

    # parameters
    nb_var = 100
    nb_patient = 40
    output_file_name = "toy_dataset.csv"

    # init file & write header
    data_file = open(output_file_name, "w")
    header = "ID,"
    for x in range(0,nb_var):
        header+=f"{x},"
    header+="LABEL\n"
    data_file.write(header)

    # populate data file
    id_cmpt = 1
    for x in range(0,nb_patient):
        line = f"{id_cmpt},"
        for x in range(0,nb_var):
            line+=f"{random.randint(0,10)},"
        line+=f"{random.randint(0,2)}\n"
        data_file.write(line)

    # close data file
    data_file.close()
