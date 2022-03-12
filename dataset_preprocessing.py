

def drop_missing_values(df):
    """
    """

    ## importation
    import pandas as pd
    import numpy as np

    ## replace Missing & NA values by np.nan
    ## problem when all scalar are float
    try:
        df = df.replace({
                "MISSING":np.nan,
                "NA":np.nan,
                "N/A":np.nan,
                "nan":np.nan,
                "NaN":np.nan,
                "":np.nan,
                " ":np.nan
            })
    except:
        pass

    ## drop np.nan
    df = df.dropna()

    ## return dataframe
    return df


def rename_variables(df):
    """
    """

    ## importation
    import pandas as pd

    ## extract features
    features = list(df.keys())

    ## rename first and last features
    df = df.rename(columns={features[0]:"ID", features[-1]:"LABEL"})

    ## display something
    print("[+][PREPROCESSING] => "+str(features[0])+" detected as ID")
    print("[+][PREPROCESSING] => "+str(features[-1])+" detected as LABEL")

    ## return dataframe
    return df


def craft_selected_variable_dataset(input_file, feature_file, work_folder):
    """

    TODO : handle windows env (with stupid \\ root system instead of /)

    """

    ## importation
    import pandas as pd

    ## load original dataset
    df = pd.read_csv(input_file)
    df = rename_variables(df)

    ## load features
    df_features = pd.read_csv(feature_file)
    feature_list = ['ID']
    for feature in list(df_features['FEATURE']):
        feature_list.append(feature)
    feature_list.append('LABEL')

    ## select only loaded features
    df = df[feature_list]

    ## craft new dataset file name
    output_file_name = input_file.split("/")
    output_file_name = output_file_name[-1]
    feature_file_name = feature_file.split("/")
    feature_file_name = feature_file_name[-1]
    output_file_name = output_file_name.replace(".csv", "_selected_features_from_")
    output_file_name = output_file_name+feature_file_name
    output_file_name = work_folder+"/"+output_file_name

    ## save new dataset
    df.to_csv(output_file_name, index=False)

    ## return save file name
    return output_file_name
