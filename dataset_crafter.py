


def get_id_to_label(label_file):
    """
    parse label file and return a dictionnary
    """

    ## importation
    import pandas as pd

    ## parameters
    id_to_label = {}

    ## load manifest
    df = pd.read_csv(label_file)

    ## craft id to label
    for index, row in df_manifest.iterrows():
        id_to_label[int(row["ID"])] = row["LABEL"]

    ## return dictionnary
    return id_to_label


def parse_data_file_conf(data_file_conf):
    """
    Read data file conf file,
    each type of data is associated with a data file, ex:

    TYPE,PATH
    rnaseq,/home/databot/PRECISESADS/rnaseq/rnaseq_vst.csv

    IN PROGRESS
    """

    ## importation
    import pandas as pd

    ## parameters
    type_to_path = {}

    ## load dataset
    df = pd.read_csv(data_file_conf)

    ## loop over data
    for index, row in df.iterrows:
        type_to_path[row["TYPE"]] = row["PATH"]

    ## return dictionnary
    return type_to_path



def craft_dataset(label_file, data_type_list, output_filename):
    """

    TO TEST
    
    IN PROGRESS
    """

    ## importation
    import pandas as pd

    ## parameters
    data_file_conf = "configuration/data_path.csv"
    data_frame_list = []

    ## load id to label
    id_to_label = get_id_to_label(label_file)

    ## parse config file
    type_to_path = parse_data_file_conf(data_file_conf)

    ## loop over data type
    for type in data_type_list:

        #-> check if type is referenced in config file
        if(type in type_to_path.keys()):

            #-> load dataframe
            df = pd.read_csv(type_to_path[type])

            #-> select only ids in label file
            df = df[df["ID"].isin(id_to_label.keys())]

            #-> append dataframe to dataframe list
            data_frame_list.append(df)

    ## concat datafame
    df = pd.concat(data_frame_list, axis=1) # to check

    ## clean ID and LABEL duplicates
    col_to_drop = []
    for var in list(df.keys()):
        if(re.search('ID\.[1-9]{1,}', var)):
            col_to_drop.append(var)
        if(re.search('LABEL\.[1-9]{1,}', var)):
            col_to_drop.append(var)
    df = df.drop(columns=col_to_drop)

    ## add new label
    df["LABEL"] = df["ID"].replace(id_to_label)

    ## save dataframe
    df.to_csv(output_filename, index=False)
