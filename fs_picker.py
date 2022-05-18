
def run_picker(data_file, output_folder, min_features, step):
    """
    Can be very long for some dataset (independant of nb of features & observations)
    """

    # importation
    from sklearn.datasets import make_classification
    from sklearn.model_selection import GridSearchCV
    from sklearn.model_selection import RepeatedStratifiedKFold
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    import pandas as pd
    from joblib import dump
    from sklearn.feature_selection import RFE
    from sklearn.svm import SVR
    import dataset_preprocessing
    import os
    import shutil

    ## clean & prepare output folde
    if(not os.path.isdir(output_folder+"/picker_log")):
        os.mkdir(output_folder+"/picker_log")
    else:
        shutil.rmtree(output_folder+"/picker_log")
        os.mkdir(output_folder+"/picker_log")


    ## load file
    X_data = pd.read_csv(data_file)

    ## preprocess file
    X_data = dataset_preprocessing.drop_missing_values(X_data)
    X_data = dataset_preprocessing.rename_variables(X_data)

    ## hunt the different cluster name in the label feature
    cluster_name = []
    for label in list(X_data['LABEL']):
        if(label not in cluster_name):
            cluster_name.append(label)

    ## parse dataset
    X = X_data[X_data['LABEL'].isin(cluster_name)]
    Y = X['LABEL']
    X = X.drop(columns=['LABEL', 'ID'])
    feature_list = list(X.keys())

    ## process label
    cmpt = 0
    label_to_encode = {}
    for label in cluster_name:
        label_to_encode[label] = cmpt
        cmpt +=1
    Y = Y.replace(label_to_encode)
    y = Y.values
    X = X.values

    ## define number_feature_to_select
    number_feature_to_select = len(feature_list)-step

    ## init log file
    log_file = open(output_folder+"/picker_log/picker_search.log", "w")
    log_file.write("NB_FEATURES,SOLVER,ACC\n")

    ## RFE LOOP
    while(number_feature_to_select > min_features):

        ## run RFE+

        print("[+][FS-PICKER]{Running RFE} => target "+str(number_feature_to_select)+" variables")
        estimator = SVR(kernel="linear")
        selector = RFE(estimator, n_features_to_select=number_feature_to_select, step=1)
        selector = selector.fit(X, y)

        i = 0
        selected_features = []
        for keep in selector.support_:
            if(keep):
                selected_features.append(feature_list[i])
            i+=1
        selected_features.append('LABEL')

        #-> recraft dataset
        X = X_data[X_data['LABEL'].isin(cluster_name)]
        X = X[selected_features]
        Y = X['LABEL']
        X = X.drop(columns=['LABEL'])
        feature_list = list(X.keys())
        Y = Y.replace(label_to_encode)
        y = Y.values
        X = X.values

        #-> update nb of features
        number_feature_to_select = len(selected_features)-step-1

        ## LDA Training
        # define model
        model = LinearDiscriminantAnalysis()

        # define model evaluation method
        ## TODO : automatically assigned best params for cv
        cv = RepeatedStratifiedKFold(n_splits=3, n_repeats=5, random_state=1)

        # define grid
        grid = dict()
        grid['solver'] = ['svd', 'lsqr', 'eigen']

        # define search
        search = GridSearchCV(model, grid, scoring='accuracy', cv=cv, n_jobs=-1)

        # perform the search
        results = search.fit(X, y)

        # summarize
        best_solver = results.best_params_['solver']
        best_score = results.best_score_

        ## save results
        log_file.write(str(len(selected_features)-1)+","+str(results.best_params_['solver'])+","+str(results.best_score_)+"\n")

        ## save features
        feature_file = open(output_folder+"/picker_log/rfe_determined_features_i"+str(len(selected_features)-1)+".csv", "w")
        feature_file.write("FEATURE\n")
        for f in feature_list:
            feature_file.write(str(f)+"\n")
        feature_file.close()

    ## close result file
    log_file.close()






def plot_acc(output_folder):
    """
    Plot results of the LDA Exploration using content of log file
    """

    ## importation
    import pandas as pd
    import matplotlib.pyplot as plt

    ## parameters
    log_file = output_folder+"/picker_log/picker_search.log"

    ## load log file
    df = pd.read_csv(log_file)

    ## get the different solver
    x = df['NB_FEATURES']
    y = df['ACC']

    ## create plot
    plt.plot(x,y, '--bo')
    plt.title("Picker Exploration")
    plt.ylabel("ACC")
    plt.xlabel("Nb Features")
    plt.savefig(output_folder+"/picker_log/picker_exploration.png")
    plt.close()


def hunt_best_conf(output_folder):
    """
    """

    ## importation
    import pandas as pd
    import shutil
    import os

    ## parameters
    max_acc = 0
    best_config = "NA"
    best_var_nb = "NA"
    best_name_file = "NA"
    folder_separator = "/"
    drop_list = []

    ## check if we are running on a fucking windows machine
    if(os.name == 'nt'):
        folder_separator = "\\"

    ## load dataset
    log_file = output_folder+folder_separator+"picker_log"+folder_separator+"picker_search.log"
    df = pd.read_csv(log_file)

    ## parse data
    for index, row in df.iterrows():

        #-> extract data
        acc = row['ACC']
        solver = row['SOLVER']
        nb_features = row['NB_FEATURES']


        #-> get file name
        rfe_file = output_folder+folder_separator+"picker_log"+folder_separator+"rfe_determined_features_i"+str(nb_features)+".csv"
        drop_list.append(rfe_file)

        #-> test if acc is the best
        if(float(acc) > max_acc):
            max_acc = float(acc)
            best_config = solver
            best_var_nb = nb_features
            best_name_file = rfe_file

    ## craft output data
    hunt_results = {
        "acc":max_acc,
        "solver":best_config,
        "features_number":best_var_nb
    }

    ## save best file
    if(best_name_file != "NA"):
        shutil.copy(best_name_file, output_folder+folder_separator+"picker_log"+folder_separator+"picker_selected_features.csv")

    ## remove tmp log file
    for rfe_log in drop_list:
        try:
            os.remove(rfe_log)
        except:
            pass

    ## return data
    return hunt_results






"""
run_picker("D:\\toy_dataset.csv", "D:\\murloc_output_test", 240, 2)
plot_acc("D:\\murloc_output_test")
hunt_best_conf("D:\\murloc_output_test")
"""
#run_picker("../SSA/dataset/33_gene_sig_MCTD_classification.csv", "../misc/murloc_test6", 15, 1)
#hunt_best_conf("/home/bran/Workspace/REDSIG/RTX_only/essdai_picker/")
