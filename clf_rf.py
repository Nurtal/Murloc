

def run_rf_classifier(input_file, work_folder):
    """
    """

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

    ## parameters
    max_depth = 5
    rf_save_name = work_folder+"/rf_log/rf_model.joblib"
    rf_confusion_save_file = work_folder+"/rf_log/rf_confusion_matrix.png"
    log_file_name = work_folder+"/rf_log/rf_evaluation.log"

    ## clean & prepare output folde
    if(not os.path.isdir(work_folder+"/rf_log")):
        os.mkdir(work_folder+"/rf_log")
    else:
        shutil.rmtree(work_folder+"/rf_log")
        os.mkdir(work_folder+"/rf_log")

    ## load file
    df = pd.read_csv(input_file)

    ## preprocess file
    df = dataset_preprocessing.drop_missing_values(df)
    df = dataset_preprocessing.rename_variables(df)

    ## encode class label
    cmpt_class = 0
    old_label_to_encode = {}
    for y in list(df['LABEL']):
        if(y not in old_label_to_encode.keys()):
            old_label_to_encode[y] = cmpt_class
            cmpt_class+=1
    df = df.replace(old_label_to_encode)

    ## extract features
    features = [f for f in df.columns if f not in ['ID','LABEL']]

    ## prepare dataset
    X = df[features].values
    Y = df['LABEL'].values.ravel()

    ## split into train & validation
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=42)

    ## run LDA
    clf = RandomForestClassifier(max_depth=max_depth)
    clf.fit(X_train, y_train)

    ## save model
    dump(clf, rf_save_name)

    ## evaluate model
    y_pred = clf.predict(X_test)
    matrix = confusion_matrix(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    acc = acc*100.0

    ## display results
    print("[+][CLF-RF] => ACC : "+str(acc)+" %")

    ## create confusion matrix figure
    df_cm = pd.DataFrame(
        matrix,
        index = list(old_label_to_encode.keys()),
        columns = list(old_label_to_encode.keys())
    )
    plt.figure(figsize = (10,7))
    sn.heatmap(df_cm, annot=True, cmap='Blues')
    plt.savefig(rf_confusion_save_file)
    plt.close()

    ## save acc in a log file
    log_file = open(log_file_name, "w")
    log_file.write("ACC\n")
    log_file.write(str(acc)+"\n")
    log_file.close()



#run_rf_classifier("../SSA/dataset/33_gene_sig_MCTD_classification.csv", "../misc/murloc_test")
