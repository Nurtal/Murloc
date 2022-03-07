def run_boruta(dataset, iteration, depth, output_folder):
    """
    """

    ## importation
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from boruta import BorutaPy

    ## load file
    df = pd.read_csv(dataset)

    ## TODO - START
    #-> data preprocessing
    df = df.dropna()

    ## drop control if there are present
    df = df.rename(columns={"Omics":"OMIC", "OMICs":"OMIC", "OMICS":"OMIC", "OMICID":"OMIC"})
    df = df[df['CLUSTER'].isin(["C1", "C2", "C3", "C4"])]
    df = df.replace({"C1":0,"C2":1,"C3":2,"C4":3})

    ## extract features
    features = [f for f in df.columns if f not in ['CLUSTER','OMIC']]

    ## prepare dataset
    X = df[features].values
    Y = df['CLUSTER'].values.ravel()
    ## TODO - END

    ## setup the RandomForrestClassifier as the estimator to use for Boruta
    rf = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=depth)

    ## prepare Boruta
    boruta_feature_selector = BorutaPy(
        rf,
        n_estimators='auto',
        verbose=2,
        random_state=4242,
        max_iter = iteration,
        perc = 90
    )

    ## run boruta
    boruta_feature_selector.fit(X, Y)

    # extract selected features
    X_filtered = boruta_feature_selector.transform(X)

    ## save extracted feature
    final_features = list()
    indexes = np.where(boruta_feature_selector.support_ == True)
    for x in np.nditer(indexes):
        final_features.append(features[x])

    ## craft feature output file
    output_filename = output_folder+"/boruta_selected_features.csv"
    output_dataset = open(output_filename, "w")
    for final_f in final_features:
        output_dataset.write(str(final_f)+"\n")
    output_dataset.close()
