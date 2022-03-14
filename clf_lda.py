

def run_lda_classifier(input_file, work_folder):
    """
    TODO:
        - generate lda representation
        - save features contributions
    """

    ## importation
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from joblib import dump
    from sklearn.metrics import confusion_matrix
    from sklearn.metrics import accuracy_score
    import dataset_preprocessing
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    import matplotlib.pyplot as plt
    import seaborn as sn
    import os

    ## parameters
    lda_save_name = work_folder+"/lda_log/lda_model.joblib"
    lda_confusion_save_file = work_folder+"/lda_log/lda_confusion_matrix.png"
    log_file_name = work_folder+"/lda_log/lda_evaluation.log"

    ## clean & prepare output folde
    if(not os.path.isdir(work_folder+"/lda_log")):
        os.mkdir(work_folder+"/lda_log")
    else:
        shutil.rmtree(work_folder+"/lda_log")
        os.mkdir(work_folder+"/lda_log")

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

    ## init LDA
    lda = LinearDiscriminantAnalysis(n_components=cmpt_class-1)
    X_r2 = lda.fit(X_train, y_train).transform(X_train)

    ## save model
    dump(lda, lda_save_name)

    ## evaluate model
    y_pred = lda.predict(X_test)
    matrix = confusion_matrix(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    acc = acc*100.0

    ## display results
    print("[+][CLF-LDA] => ACC : "+str(acc)+" %")

    ## create confusion matrix figure
    df_cm = pd.DataFrame(
        matrix,
        index = list(old_label_to_encode.keys()),
        columns = list(old_label_to_encode.keys())
    )
    plt.figure(figsize = (10,7))
    sn.heatmap(df_cm, annot=True, cmap='Blues')
    plt.savefig(lda_confusion_save_file)
    plt.close()

    ## save acc in a log file
    log_file = open(log_file_name, "w")
    log_file.write("ACC\n")
    log_file.write(str(acc)+"\n")
    log_file.close()





#run_lda_classifier("../SSA/dataset/33_gene_sig_MCTD_classification.csv", "../misc/murloc_test")
