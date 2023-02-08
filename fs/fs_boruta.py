def run_boruta(dataset, iteration, depth, output_folder):
    """ """

    ## importation
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from boruta import BorutaPy
    import dataset_preprocessing
    import os
    import shutil

    ## clean & prepare output folde
    if not os.path.isdir(output_folder + "/boruta_log"):
        os.mkdir(output_folder + "/boruta_log")
    else:
        shutil.rmtree(output_folder + "/boruta_log")
        os.mkdir(output_folder + "/boruta_log")

    ## load file
    df = pd.read_csv(dataset)

    ## preprocess file
    df = dataset_preprocessing.drop_missing_values(df)
    df = dataset_preprocessing.rename_variables(df)

    ## encode class label
    cmpt_class = 0
    old_label_to_encode = {}
    for y in list(df["LABEL"]):
        if y not in old_label_to_encode.keys():
            old_label_to_encode[y] = cmpt_class
            cmpt_class += 1
    df = df.replace(old_label_to_encode)

    ## extract features
    features = [f for f in df.columns if f not in ["ID", "LABEL"]]

    ## prepare dataset
    X = df[features].values
    Y = df["LABEL"].values.ravel()

    ## remove fucking space in numbers
    """
    X_cleaned = []
    for vector in X:
        vector_clean = []
        for scalar in vector:
            scalar_clean = str(scalar)
            scalar_clean = scalar_clean.replace(" ", "")
            print(scalar)
            scalar_clean = float(scalar_clean)
            vector_clean.append(scalar_clean)
        X_cleaned.append(vector_clean)
    X = X_cleaned
    """

    ## setup the RandomForrestClassifier as the estimator to use for Boruta
    rf = RandomForestClassifier(n_jobs=-1, class_weight="balanced", max_depth=depth)

    ## prepare Boruta
    boruta_feature_selector = BorutaPy(
        rf,
        n_estimators="auto",
        verbose=2,
        random_state=4242,
        max_iter=iteration,
        perc=90,
    )

    ## run boruta
    boruta_feature_selector.fit(X, Y)

    # extract selected features
    X_filtered = boruta_feature_selector.transform(X)

    ## save extracted feature
    final_features = list()
    indexes = np.where(boruta_feature_selector.support_ == True)
    try:
        for x in np.nditer(indexes):
            final_features.append(features[x])
    except:
        pass

    ## craft feature output file
    output_filename = output_folder + "/boruta_log/boruta_selected_features.csv"
    output_dataset = open(output_filename, "w")
    output_dataset.write("FEATURE\n")
    for final_f in final_features:
        output_dataset.write(str(final_f) + "\n")
    output_dataset.close()
