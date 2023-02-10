def run_rf_classifier(input_file, work_folder):
    """ """

    ## importation
    import os
    import shutil
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import dataset_preprocessing
    from sklearn.model_selection import train_test_split
    from joblib import dump
    from sklearn.metrics import confusion_matrix
    from sklearn.metrics import accuracy_score
    import matplotlib.pyplot as plt
    import seaborn as sn
    from sklearn.model_selection import RandomizedSearchCV
    import numpy as np

    ## parameters
    rf_save_name = work_folder + "/rf_log/rf_model.joblib"
    rf_confusion_save_file = work_folder + "/rf_log/rf_confusion_matrix.png"
    log_file_name = work_folder + "/rf_log/rf_evaluation.log"

    ## clean & prepare output folde
    if not os.path.isdir(work_folder + "/rf_log"):
        os.mkdir(work_folder + "/rf_log")
    else:
        shutil.rmtree(work_folder + "/rf_log")
        os.mkdir(work_folder + "/rf_log")

    ## load file
    df = pd.read_csv(input_file)

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

    # run only if we have features
    if len(features) > 0:

        ## prepare dataset
        X = df[features].values
        Y = df["LABEL"].values.ravel()

        ## split into train & validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, Y, test_size=0.33, random_state=42
        )

        ## init model
        rf = RandomForestClassifier()

        ## prepare for hyper param
        # -> Number of trees in random forest
        n_estimators = [int(x) for x in np.linspace(start=5, stop=2000, num=5)]
        # -> Number of features to consider at every split
        max_features = ["auto", "sqrt"]

        # -> Maximum number of levels in tree
        max_depth = [int(x) for x in np.linspace(3, 110, num=5)]
        max_depth.append(None)

        # -> Minimum number of samples required to split a node
        min_samples_split = [2, 5, 10]

        # -> Minimum number of samples required at each leaf node
        min_samples_leaf = [1, 2, 4]

        # -> Method of selecting samples for training each tree
        bootstrap = [True, False]

        # -> Create the random grid
        random_grid = {
            "n_estimators": n_estimators,
            "max_features": max_features,
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "bootstrap": bootstrap,
        }

        clf = RandomizedSearchCV(
            estimator=rf,
            param_distributions=random_grid,
            n_iter=100,
            cv=3,
            verbose=2,
            random_state=42,
            n_jobs=-1,
        )

        # Fit the random search model
        clf.fit(X_train, y_train)

        ## pick the best
        clf = clf.best_estimator_

        ## save model
        dump(clf, rf_save_name)

        ## evaluate model
        y_pred = clf.predict(X_test)
        matrix = confusion_matrix(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)
        acc = acc * 100.0

        ## display results
        print("[+][CLF-RF] => ACC : " + str(acc) + " %")

        ## create confusion matrix figure
        df_cm = pd.DataFrame(
            matrix,
            index=list(old_label_to_encode.keys()),
            columns=list(old_label_to_encode.keys()),
        )
        plt.figure(figsize=(10, 7))
        sn.heatmap(df_cm, annot=True, cmap="Blues")
        plt.savefig(rf_confusion_save_file)
        plt.close()

        ## save acc in a log file
        log_file = open(log_file_name, "w")
        log_file.write("ACC\n")
        log_file.write(str(acc) + "\n")
        log_file.close()


# run_rf_classifier("../SSA/dataset/33_gene_sig_MCTD_classification.csv", "../misc/murloc_test")
