

def drop_missing_values(input_file):
    """
    """

    ## importation
    import pandas as pd
    import numpy as np

    ## load dataset
    df = pd.read_csv(input_file)

    ## replace Missing & NA values by np.nan
    df = df.replace({
            "MISSING":np.nan,
            "NA":np.nan,
            "N/A":np.nan,
            "nan":np.nan,
            "NaN":np.nan,
            "":np.nan,
            " ":np.nan
        })

    ## drop np.nan
    df = df.dropna()

    ## return dataframe
    return df


def rename_variables(input_file):
    """
    """

    ## importation
    import pandas as pd

    ## laod dataset
    df = pd.read_csv(input_file)

    ## extract features
    features = list(df.keys())

    ## rename first and last features
    df = df.rename(columns={features[0]:"ID", features[-1]:"LABEL"})

    ## display something
    print("[+][PREPROCESSING] => "+str(features[0])+" detected as ID")
    print("[+][PREPROCESSING] => "+str(features[-1])+" detected as LABEL")

    ## return dataframe
    return df
