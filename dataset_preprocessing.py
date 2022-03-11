

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
