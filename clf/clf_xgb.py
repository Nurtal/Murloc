## importation
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import dataset_preprocessing
import os
import shutil
from sklearn.metrics import mean_squared_error
from sklearn.metrics import plot_confusion_matrix
import matplotlib.pyplot as plt

def run_hyperparametrisation(input_file, work_folder):
    """
    """

    ## clean & prepare output folde
    if(not os.path.isdir(work_folder+"/xgb_log")):
        os.mkdir(work_folder+"/xgb_log")
    else:
        shutil.rmtree(work_folder+"/xgb_log")
        os.mkdir(work_folder+"/xgb_log")

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

    # detrmine if its a binary classification case or not
    if(len(set(Y)) == 2):
        objective_function = 'binary:logistic'
        scoring_system = 'roc_auc'
    else:
        objective_function = "multi:softprob"
        scoring_system = 'accuracy'

    ## init xgb model
    xgb_model = xgb.XGBClassifier(objective = objective_function)

    ## define parmas to explore
    params = {
        'eta': np.arange(0.1, 0.26, 0.05),
        'min_child_weight': np.arange(1, 5, 0.5).tolist(),
        'gamma': np.arange(1, 10, 1).tolist(),
        'alpha': np.arange(1, 10, 3).tolist(),
        'learning_rate' : np.arange(0.1, 1, 0.1).tolist(),
        'subsample': np.arange(0.5, 1.0, 0.11).tolist(),
        'colsample_bytree': np.arange(0.5, 1.0, 0.11).tolist(),
        'n_estimators' : [2,3],
        'max_depth' : [2]
    }

    ## init machin chose
    skf = StratifiedKFold(n_splits=2, shuffle = True)

    ## init grid search
    grid = GridSearchCV(xgb_model,
        param_grid = params,
        scoring = scoring_system,
        n_jobs = 2,
        cv = skf.split(X, Y),
        refit = "accuracy_score")

    ## Run GirdSearch
    grid.fit(X, Y)

    ## Save results (best params)
    best_pars = grid.best_params_
    output_data = open(f"{work_folder}/xgb_log/optimal_parameters.csv", "w")
    output_data.write("PARAM,VALUE\n")
    for k in best_pars.keys():
        output_data.write(str(k)+","+str(best_pars[k])+"\n")
    output_data.close()
    output_data.close()


def run_xgb_classifier(input_file, work_folder):
    """
    """

    # parameters
    params = {}
    param_file = f"{work_folder}/xgb_log/optimal_parameters.csv"

    ## clean & prepare output folde
    if(not os.path.isdir(work_folder+"/xgb_log")):
        os.mkdir(work_folder+"/xgb_log")

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

    # detrmine if its a binary classification case or not
    if(len(set(Y)) == 2):
        objective_function = 'binary:logistic'
        scoring_system = 'roc_auc'
    else:
        objective_function = "multi:softprob"
        scoring_system = 'accuracy'

    # look for hyperparmaeters
    if(os.path.isfile(param_file)):
        df = pd.read_csv(param_file)
        for index, row in df.iterrows():
            p = row['PARAM']
            v = row['VALUE']
            params[p] = v
    else:
        params = {
            'eta': 0.26,
            'min_child_weight': 1,
            'gamma': 2,
            'alpha': 3,
            'learning_rate' : 0.3,
            'subsample': 0.5,
            'colsample_bytree': 0.5,
            'n_estimators' : 3,
            'max_depth' : 3
        }

    # initialize model
    xgb_model = xgb.XGBClassifier(objective = objective_function,
                                  colsample_bytree = params['colsample_bytree'],
                                  eta = params['eta'],
                                  max_depth = int(params['max_depth']),
                                  gamma = params['gamma'],
                                  alpha = params['alpha'],
                                  learning_rate = params['learning_rate'],
                                  n_estimators = int(params['n_estimators']))

    ## fit model
    xgb_model.fit(X_train,y_train)

    ## make predictions
    preds = xgb_model.predict(X_test)
    
    ## compute RMSE (kind of precision metrics)
    rmse = np.sqrt(mean_squared_error(y_test, preds))

    ## compute ACC
    round_preds = [round(value) for value in preds]
    accuracy = accuracy_score(y_test, round_preds)
    
    # save performances
    perf_file = open(f"{work_folder}/xgb_log/xgb_evaluation.log", "w")
    perf_file.write(f"RMSE\t{rmse}\n")
    perf_file.write(f"ACC\t{accuracy}\n")
    perf_file.close()


    ## save feature importance
    feature_to_importance = xgb_model.get_booster().get_score(importance_type='gain')
    save_feature_file = open(f"{work_folder}/xgb_log/important_features.csv", "w")
    save_feature_file.write("FEATURE,GAIN\n")
    for key in feature_to_importance.keys():
        save_feature_file.write(str(key)+","+str(feature_to_importance[key])+"\n")
    save_feature_file.close()

    ## save confusion matrix for train dataset
    plot_confusion_matrix(xgb_model, X_train, y_train, normalize='true')
    plt.tight_layout()
    plt.savefig(f"{work_folder}/xgb_log/confusion_matrix_train.png", dpi=150)
    plt.close()

    ## save confusion matrix for test dataset
    plot_confusion_matrix(xgb_model, X_test, y_test, normalize='true')
    plt.tight_layout()
    plt.savefig(f"{work_folder}/xgb_log/confusion_matrix_test.png", dpi=150)
    plt.close()




if __name__ == "__main__":
    """
    Use this for local test
    """

    # parameters
    output_folder = "/home/bran/Workspace/misc/murloc_xgb_test/multi/"
    dataset = "/home/bran/Workspace/misc/murloc_xgb_test/multi/dataset_multi_class.csv"
    
    # -> test classifier
    # run_xgb_classifier(dataset, output_folder)
    
    # -> test hyper parmaetrisation
    # run_hyperparametrisation(dataset, output_folder)
