



def run_logistic_regression(input_file, work_folder):
    """
    """

    ## importation
    import pandas as pd
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix
    from sklearn.metrics import accuracy_score
    import seaborn as sn
    from joblib import dump
    import os
    import dataset_preprocessing
    import shutil


    ## parameters
    rf_save_name = work_folder+"/logistic_log/logistic_model.joblib"
    rf_confusion_save_file = work_folder+"/logistic_log/logistic_confusion_matrix.png"
    log_file_name = work_folder+"/logistic_log/logistic_evaluation.log"

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

    ## control that we have only 2 targets
    if(cmpt_class == 2):

        ## clean & prepare output folde
        if(not os.path.isdir(work_folder+"/logistic_log")):
            os.mkdir(work_folder+"/logistic_log")
        else:
            shutil.rmtree(work_folder+"/logistic_log")
            os.mkdir(work_folder+"/logistic_log")

        ## extract features
        features = [f for f in df.columns if f not in ['ID','LABEL']]

        # split into input (X) and output (Y)
        X = df[features].values
        Y = df['LABEL'].values.ravel()

        ## split into train and validation
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42)

        ## train classifier
        clf = LogisticRegression().fit(X_train, y_train)

        ## save model
        dump(clf, rf_save_name)

        ## evaluate model
        y_pred = clf.predict(X_test)
        matrix = confusion_matrix(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)
        acc = acc*100.0

        ## display results
        print("[+][LOGISTIC-REGRESSION] => ACC : "+str(acc)+" %")

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

    else:
        print("[!][LOGISTIC-REGRESSION] => more than 2 classes to predict, can't run logistic regression")


#run_logistic_regression("../SSA/dataset/33_gene_sig_MCTD_classification.csv", "../misc/murloc_test")
