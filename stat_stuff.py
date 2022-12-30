



def plot_zscore(input_file, gene_list, output_file_name):
    """

    """

    ## imortation
    import pandas as pd
    from scipy.stats import zscore
    import seaborn as sns
    import matplotlib.pyplot as plt
    from scipy.stats import mannwhitneyu, normaltest
    from statannotations.Annotator import Annotator
    import os

    ## parameters
    log_file_name = output_file_name.replace(".png", "_pvalue.log")

    ## define title for the figure
    title = output_file_name.split("/")
    title = title[-1]
    title = title.split(".")
    title = title[0]
    title = title.replace("_", " ")

    ## load dataset
    df = pd.read_csv(input_file)
    df['LABEL'] = df['LABEL'].astype(str)

    ## get label's name
    label_list = []
    old_label_to_new = {}
    cmpt = 1
    for label in list(df['LABEL']):
        if(label not in label_list):
            label_list.append(label)
            old_label_to_new[label] = cmpt
            cmpt+=1

    #-> prepare feature list
    features = []
    for var in gene_list:
        if(var in list(df.keys())):
            features.append(var)

    # cancel operation if no variable aivailable
    if(len(features) == 0):
        print(f"<!> Can't access features {gene_list}")
        return 0

    df_ifn = df[features]
    df_ifn = df_ifn.apply(zscore)
    df_ifn['Score'] = df_ifn.mean(axis=1)
    df_ifn['LABEL'] = df['LABEL']
    df_ifn = df_ifn[['Score', 'LABEL']]
    #df_ifn['LABEL'] = df_ifn['LABEL'].replace(old_label_to_new)

    #-> compute stat
    label_to_stat_list = {}
    for label in label_list:
        C =  df_ifn.loc[(df_ifn.LABEL == label), "Score"].values
        label_to_stat_list[label] = C


    #-> prapare vector for stat test
    stat_results = []
    stat_combination = []
    pairs = []
    for l1 in label_to_stat_list.keys():
        for l2 in label_to_stat_list.keys():
            if(l1 != l2):
                combination = str(l1)+"_"+str(l2)
                combination_inv = str(l2)+"_"+str(l1)
                if(combination not in stat_combination and combination_inv not in stat_combination):
                    stat_results.append(mannwhitneyu(label_to_stat_list[l1], label_to_stat_list[l2], alternative="two-sided"))
                    pairs.append((l1,l2))
                    stat_combination.append(combination)
                    stat_combination.append(combination_inv)

    ## run stat test
    pvalues = [result.pvalue for result in stat_results]
    formatted_pvalues = [f'p={pvalue:.2e}' for pvalue in pvalues]

    ## save pvalue in log
    log_file = open(log_file_name, "w")
    cmpt = 0
    for p in pairs:
        log_file.write(str(p[0])+" vs "+str(p[1])+" = "+str(pvalues[cmpt])+"\n")
        cmpt+=1
    log_file.close()


    #-> plot
    plotting_parameters = {
        'data':df_ifn,
        'x':'LABEL',
        'y':'Score',
        'order': list(label_to_stat_list.keys())
    }

    try:
        ax = sns.violinplot(x="LABEL", y="Score", data=df_ifn, order=list(label_to_stat_list.keys()))
        annotator = Annotator(ax, pairs, **plotting_parameters)
        annotator.set_pvalues(pvalues)
        annotator.annotate()
        plt.title(title)
        plt.savefig(output_file_name)
        plt.close()
    except:
        pass

















def run_univar_test(input_file, feature_file, output_folder):
    """
    """

    ## importation
    import pandas as pd
    import os
    import shutil
    from scipy import stats
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np

    ## parameters
    log_file_name = output_folder+"/stat_analysis/univar_test.log"
    drop_outliers = True

    ## clean & prepare output folder
    if(not os.path.isdir(output_folder+"/stat_analysis")):
        os.mkdir(output_folder+"/stat_analysis")
    else:
        shutil.rmtree(output_folder+"/stat_analysis")
        os.mkdir(output_folder+"/stat_analysis")

    ## load features
    feature_list = pd.read_csv(feature_file)
    feature_list = list(feature_list['FEATURE'])

    ## load dataset
    df = pd.read_csv(input_file)

    ## init log file
    log_file = open(log_file_name, "w")
    log_file.write("FEATURE,P-VAL\n")

    ## loop over feature to test
    for feature in feature_list:

        #-> craft test dataframe
        df_test = df[[feature,'LABEL']]
        df_test[feature] = df_test[feature].astype(float)
        label_to_series = {}
        for index, row in df_test.iterrows():
            label = row['LABEL']
            scalar = row[feature]
            if(label not in label_to_series.keys()):
                label_to_series[label] = [scalar]
            else:
                label_to_series[label].append(scalar)

        #-> run stat test
        ## if only 2 labels are detected -> go for t test
        if(len(list(label_to_series.keys())) == 2):
            group_1 = label_to_series[list(label_to_series.keys())[0]]
            group_2 = label_to_series[list(label_to_series.keys())[1]]
            label1 = list(label_to_series.keys())[0]
            label2 = list(label_to_series.keys())[1]

            #-> drop outliers
            if(drop_outliers):

                print("[+][WARNING][STAT] => removing outliers")

                group_1 = np.array(group_1)
                group_1 = list(group_1[~np.isnan(group_1)])
                group_2 = np.array(group_2)
                group_2 = list(group_2[~np.isnan(group_2)])


                treshold = 3
                group_1 = [e for e in group_1 if (np.mean(group_1) - treshold * np.std(group_1) < e < np.mean(group_1) + treshold * np.std(group_1))]
                group_2 = [e for e in group_2 if (np.mean(group_2) - treshold * np.std(group_2) < e < np.mean(group_2) + treshold * np.std(group_2))]


            results = stats.ttest_ind(group_1, group_2)
            pval = results[1]

            #-> update log file
            log_file.write(str(feature)+","+str(pval)+"\n")

            #-> generate violon plot
            label_list = []
            for x in group_1:
                label_list.append(label1)
            for x in group_2:
                label_list.append(label2)
            data_list = group_1+group_2

            dfplot = pd.DataFrame(list(zip(data_list, label_list)), columns =[feature, 'LABEL'])

            sns.violinplot(data=dfplot, x=feature, y="LABEL", inner="point")
            plt.savefig(output_folder+"/stat_analysis/"+str(feature)+"_distribution.png")
            plt.close()

        else:
            pass


        ## if more than 2 labels are detected -> go for anova
        #--> run t test
        #arguments = list(label_to_series.values())
        #results = stats.ttest_ind(arguments)
        #pval = results[1]

        #-> generate figure

        #-> update log file

    ## close log file
    log_file.close()




def generate_z_score_from_reactome_results_file(data_file, reactome_file, output_folder):
    """
    """

    ## importation
    import pandas as pd

    ## parameters
    pval_treshold = 0.05

    ## load reactome dataset
    df = pd.read_csv(reactome_file)

    ## loop over pathway
    for index, row in df.iterrows():

        #-> extract path name
        path_name = row["Pathway name"]

        #-> extract pval
        pval = row["Entities pValue"]

        #-> extract genes
        gene_list = row["Submitted entities found"]
        gene_list = gene_list.split(";")

        #-> if pval below treshold, generate z plot
        if(pval <= pval_treshold):

            #-> generate output file name
            output_file_name = path_name.replace("_", "")
            output_file_name = output_file_name+".png"
            output_file_name = output_folder+"/annotation_log/"+output_file_name

            #-> generate graphic
            plot_zscore(data_file, gene_list, output_file_name)





#run_univar_test("D:\\murloc_output_test5\\toy_dataset_selected_features_from_picker_selected_features.csv", "D:\\murloc_output_test5\\picker_log\\picker_selected_features.csv", "D:\\murloc_output_test")
#run_univar_test("/home/bran/Workspace/luminex/murloc_lukas_mfi/mfi_dataset_selected_features_from_boruta_selected_features.csv", "/home/bran/Workspace/luminex/murloc_lukas_mfi/picker_log/picker_selected_features.csv", "/home/bran/Workspace/luminex/murloc_lukas_mfi")


#plot_zscore("d:\\murloc_output_test254\\toy_dataset_selected_features_from_picker_selected_features.csv", ['EXOC6','FAM168B','FAM65B','FBXO10','FBXO38','GNB1','GNG11'], "d:\\test_zscore.png")
#plot_zscore("/home/bran/Workspace/PRECISINV/fatigue/dataset/rnaseq_with_ctrl_paired.csv", ["DPAGT1"], "/home/bran/Workspace/PRECISINV/fatigue/murloc_search_deep/z_score_with_ctrl_paired.png")
"""
plot_zscore("/home/bran/Workspace/PRECISINV/ccp/dataset/rnaseq_RA_with_ctrl.csv",
    ["FBXO10"],
    "/home/bran/Workspace/PRECISINV/ccp/murloc_rnaseq/RA/FBXO10_with_ctrl.png"
)
"""
"""
plot_zscore("/home/bran/Workspace/PRECISINV/SjS/RESPIRATORY/rnaseq_dataset_selected_features_from_boruta_selected_features_selected_features_from_picker_selected_features.csv",
    ["FLT3"],
    "/home/bran/Workspace/PRECISINV/SjS/RESPIRATORY/display_log/FLT3.png"
)
"""



#generate_z_score_from_reactome_results_file("/home/bran/Workspace/PRECISINV/ccp/dataset/rnaseq_RA_with_ctrl.csv", "/home/bran/Workspace/PRECISINV/ccp/murloc_rnaseq/RA/reactome_manual.csv", "/home/bran/Workspace/PRECISINV/ccp/murloc_rnaseq/RA/")
"""
generate_z_score_from_reactome_results_file(
    "/home/bran/Workspace/PRECISINV/SjS/RESPIRATORY/rnaseq_dataset_selected_features_from_boruta_selected_features_selected_features_from_picker_selected_features.csv",
    "/home/bran/Workspace/PRECISINV/SjS/RESPIRATORY/reactome_manual.csv",
    "/home/bran/Workspace/PRECISINV/SjS/RESPIRATORY/"
)
"""
