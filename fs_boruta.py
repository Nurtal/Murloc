def run_boruta(dataset, iteration, depth):
    """
    """

    ## importation
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from boruta import BorutaPy

    ## load file
    df = pd.read_csv(dataset)
    try:
        df = df.replace({"MISSING":np.nan})
    except:
        pass
    df = df.dropna()

    ## drop control if there are present
    df = df.rename(columns={"Omics":"OMIC", "OMICs":"OMIC", "OMICS":"OMIC", "OMICID":"OMIC"})
    df = df[df['CLUSTER'].isin(["C1", "C2", "C3", "C4"])]
    df = df.replace({"C1":0,"C2":1,"C3":2,"C4":3})

    print("[+] dataset loaded")

    ## extract features
    features = [f for f in df.columns if f not in ['CLUSTER','OMIC']]

    print("[+] features extracted")

    ## prepare dataset
    X = df[features].values
    Y = df['CLUSTER'].values.ravel()

    print("[+] matrix ready")

    ## setup the RandomForrestClassifier as the estimator to use for Boruta
    rf = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=depth)

    print("[+] random forest ready")

    ## run Boruta
    boruta_feature_selector = BorutaPy(
        rf,
        n_estimators='auto',
        verbose=2,
        random_state=4242,
        max_iter = iteration,
        perc = 90
    )

    print("[+] Boruta ready")

    boruta_feature_selector.fit(X, Y)

    # extract selected features
    X_filtered = boruta_feature_selector.transform(X)

    ## save extracted feature
    final_features = list()
    indexes = np.where(boruta_feature_selector.support_ == True)

    #print(len(indexes))
    #if(len(indexes) > 1):
    for x in np.nditer(indexes):
        final_features.append(features[x])

    ## craft feature output file
    output_filename = dataset.split("/")
    output_filename = output_filename[-1]
    output_filename = output_filename.replace(".csv", "_boruta_selected_features_i"+str(iteration)+"d"+str(depth)+".csv")
    output_filename = "features/"+str(output_filename)
    output_dataset = open(output_filename, "w")
    for final_f in final_features:
        output_dataset.write(str(final_f)+"\n")
    output_dataset.close()
