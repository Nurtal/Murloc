## importation
import os
import shutil
import pandas as pd













def run_matching(data_file, work_folder):
    """
    """

    ## importation
    import os
    import pandas as pd
    import numpy as np
    import pandas as pd
    import seaborn as sns
    import scipy.stats as stats
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_auc_score
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import NearestNeighbors
    import shutil

    ## parameters
    id_save_list = work_folder+"/pairing_log/matched_id_list.csv"
    distribution_save_file = work_folder+"/pairing_log/distribution_check.png"

    ## clean & prepare output folde
    if(not os.path.isdir(work_folder+"/pairing_log")):
        os.mkdir(work_folder+"/pairing_log")
    else:
        shutil.rmtree(work_folder+"/pairing_log")
        os.mkdir(work_folder+"/pairing_log")

    ## load dataset
    df = pd.read_csv(data_file)

    ## prepare table
    features = df.columns.tolist()
    features.remove("LABEL")
    features.remove("ID")
    agg_operations = {"LABEL": 'count'}
    agg_operations.update({
        feature: ['mean', 'std'] for feature in features
    })
    table_one = df.groupby("LABEL").agg(agg_operations)

    feature_smds = []
    for feature in features:
        feature_table_one = table_one[feature].values
        neg_mean = feature_table_one[0, 0]
        neg_std = feature_table_one[0, 1]
        pos_mean = feature_table_one[1, 0]
        pos_std = feature_table_one[1, 1]

        smd = (pos_mean - neg_mean) / np.sqrt((pos_std ** 2 + neg_std ** 2) / 2)
        smd = round(abs(smd), 4)
        feature_smds.append(smd)

    table_one_smd = pd.DataFrame({'features': features, 'smd': feature_smds})


    ## compute propensity score
    disease = df["LABEL"]
    omicid = df["ID"]
    df = df.drop(["LABEL", "ID"], axis=1)

    num_cols = ["AGE", "SEX"]
    column_transformer = ColumnTransformer(
        [('numerical', StandardScaler(), num_cols)],
        sparse_threshold=0,
        remainder='passthrough'
    )

    data = column_transformer.fit_transform(df)


    logistic = LogisticRegression(solver='liblinear')
    logistic.fit(data, disease)

    pscore = logistic.predict_proba(data)[:, 1]
    score = roc_auc_score(disease, pscore)

    ## if score close to 0,5, no real need for appariement
    print("[+][MATCHER] AUC score => "+str(score))

    ## cjeck overlap
    mask = disease == 1
    pos_pscore = pscore[mask]
    neg_pscore = pscore[~mask]

    plt.rcParams['figure.figsize'] = 8, 6
    plt.rcParams['font.size'] = 12

    sns.distplot(neg_pscore, label='control')
    sns.distplot(pos_pscore, label='patient')

    plt.xlim(0, 1)
    plt.title('Propensity Score Distribution of Control vs Patient')
    plt.ylabel('Density')
    plt.xlabel('Scores')
    plt.legend()
    plt.tight_layout()
    plt.savefig(distribution_save_file)
    plt.close()

    ## pick the most similar
    topn = 1
    n_jobs = 1
    knn = NearestNeighbors(n_neighbors=topn + 1, metric='euclidean', n_jobs=n_jobs)
    knn.fit(neg_pscore.reshape(-1, 1))

    distances, indices = knn.kneighbors(pos_pscore.reshape(-1, 1))
    sim_distances = distances[:, 1:]
    sim_indices = indices[:, 1:]

    ## craft matched dataset
    df["LABEL"] = disease
    df["ID"] = omicid
    df_pos = df[mask]
    df_neg = df[~mask].iloc[sim_indices[:, 0]]
    df_matched = pd.concat([df_pos, df_neg], axis=0)

    ## save matched ID list
    df_matched = df_matched[["ID"]]
    df_matched.to_csv(id_save_list, index=False)

    ## return list of matched ID
    return list(df_matched["ID"])



def home_made_appariement(data_file, work_folder):
    """
    Because in the end, intuituve is not always stupid
    """

    ## parameters
    id_save_list = work_folder+"/pairing_log/matched_id_list.csv"
    distribution_save_file = work_folder+"/pairing_log/distribution_check.png"
    pair_list = []
    pos_neg_to_dist = {}
    pos_to_neg_to_dist = {}
    age_penality = 1
    sex_penality = 5

    ## clean & prepare output folde
    if(not os.path.isdir(work_folder+"/pairing_log")):
        os.mkdir(work_folder+"/pairing_log")
    else:
        shutil.rmtree(work_folder+"/pairing_log")
        os.mkdir(work_folder+"/pairing_log")

    ## load dataset
    df = pd.read_csv(data_file)

    ## consider only age and gender
    df = df[["ID","SEX","AGE","LABEL"]]

    ## split into pos and neg
    df_pos = df[df["LABEL"] == 1]
    df_neg = df[df["LABEL"] == 0]

    ## loop over pos patient
    for index, row in df_pos.iterrows():

        id = row["ID"]
        a1 = row["AGE"]
        s1 = row["SEX"]

        #-> loop over neg
        for i2, r2 in df_neg.iterrows():

            id2 = r2["ID"]
            a2 = r2["AGE"]
            s2 = r2["SEX"]

            #-> compute distance
            dist = (abs(int(a1)-int(a2)))*age_penality + (abs(int(s1) - int(s2)))*sex_penality

            #-> update matrix distance
            key = str(id)+"_"+str(id2)
            inverse_key = str(id2)+"_"+str(id)
            if(key not in pos_neg_to_dist.keys() and inverse_key not in pos_neg_to_dist.keys()):
                pos_neg_to_dist[key] = dist

            #-> update matrix distance 2
            if(id in pos_to_neg_to_dist.keys()):
                pos_to_neg_to_dist[id][id2] = dist
            else:
                pos_to_neg_to_dist[id] = {}
                pos_to_neg_to_dist[id][id2] = dist


    ## loop over the matrix, first id of the key is supposed to be the pos id (i.e for us the patient with disease, assume that those guys are more rare then control)
    ## sort dictionnary
    """
    pos_neg_to_dist = {k: v for k, v in sorted(pos_neg_to_dist.items(), key=lambda item: item[1])}
    matched_patient = []
    for k in pos_neg_to_dist.keys():
        k_array = k.split("_")
        pos = k_array[0]
        neg = k_array[1]
        pos = pos.replace(".0", "")
        neg = neg.replace(".0", "")
        dist = pos_neg_to_dist[k]
        if(pos not in matched_patient and neg not in matched_patient):
            matched_patient.append(pos)
            matched_patient.append(neg)
    """

    neg_patient_used = []
    for pos in pos_to_neg_to_dist.keys():
        neg_to_dist = pos_to_neg_to_dist[pos]
        neg_to_dist = {k: v for k, v in sorted(neg_to_dist.items(), key=lambda item: item[1])}
        neg_candidates = list(neg_to_dist.keys())
        for neg in neg_candidates:
            if(neg not in neg_patient_used):
                neg_patient_used.append(neg)
                print("-> "+str(pos)+" - "+str(neg))
                break


    ## craft id final list
    final_list = neg_patient_used
    for id in list(pos_to_neg_to_dist.keys()):
        final_list.append(id)

    ## craft final dataframe
    df = pd.read_csv(data_file)
    df = df[df["ID"].isin(final_list)]
    print(df)

    ## write csv
    df.to_csv("data_picvert_processed_apparied.csv", index=False)




#data_file = "/home/bran/Workspace/PRECISINV/fatigue/labels/matching_patients.csv"
data_file = "/home/bran/Workspace/SIDEQUEST/Bene/picvert_in_R/data_picvert_processed_for_appariement.csv"
#run_matching(data_file, "/home/bran/Workspace/SIDEQUEST/Bene/picvert_in_R/appariement")
home_made_appariement(data_file, "/home/bran/Workspace/SIDEQUEST/Bene/picvert_in_R/appariement")
