


def run_pca(data_file, output_folder):
    """
    """

    ## importation
    import pandas as pd
    from sklearn.decomposition import PCA
    import numpy as np
    import matplotlib.pyplot as plt
    import os

    ## init folder of not exist
    if(not os.path.isdir(output_folder+"/display_log")):
        os.mkdir(output_folder+"/display_log")

    ## load dataset
    df = pd.read_csv(data_file)

    ## preprocess data
    categories = list(df["LABEL"])
    df = df.drop(columns=['ID','LABEL'])
    X = df.values

    ## generate OCA
    pca = PCA(n_components=2)
    X = pca.fit_transform(X, y=None)

    ## prepare output vector
    color_grid = ["tab:blue","tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:grey", "tab:olive", "tab:cyan"]
    class_to_x = {}
    class_to_y = {}
    class_to_color = {}
    x = []
    y = []
    cmpt = 0
    color_cmpt = 0
    for vector in X:
        x.append(vector[0])
        y.append(vector[1])
        label = str(categories[cmpt])

        if(label not in class_to_x.keys()):
            class_to_x[label] = [vector[0]]
            class_to_y[label] = [vector[1]]
            class_to_color[label] = color_grid[color_cmpt]
            color_cmpt+=1
        else:
            class_to_x[label].append(vector[0])
            class_to_y[label].append(vector[1])

        cmpt+=1

    ## build plot
    for label in class_to_x.keys():
        x = np.array(class_to_x[label])
        y = np.array(class_to_y[label])
        color = class_to_color[label]
        plt.scatter(x, y, c=color, label=label)
    plt.legend()
    plt.title("PCA")

    ## save plot
    save_name = data_file.split("/")
    save_name = save_name[-1]
    save_name = save_name.replace(".csv", "_PCA.png")
    save_name = output_folder+"/display_log/"+save_name
    plt.savefig(save_name)
    plt.close()



def craft_heatmap(data_file, output_folder):
    """
    """

    ## importation
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os

    ## init folder of not exist
    if(not os.path.isdir(output_folder+"/display_log")):
        os.mkdir(output_folder+"/display_log")

    ## parameters
    output_filename = output_folder+"/display_log/heatmap.png"

    ## load dataset
    df = pd.read_csv(data_file)

    ## preprocess data
    old_to_new = {}
    for index, row in df.iterrows():
        id = row["ID"]
        label = row["LABEL"]
        old_to_new[id] = str(id)+"_"+str(label)
    df["ID"] = df["ID"].replace(old_to_new)
    df = df.set_index(['ID'])
    df_to_plot = df.drop(columns=["LABEL"])

    ## normalisze dataset
    df_to_plot=(df_to_plot-df_to_plot.mean())/df_to_plot.std()

    ## craft heatmap
    plt.figure(figsize=(10,10))
    heat_map = sns.heatmap(df_to_plot, cmap="YlGnBu")
    plt.title("HeatMap")
    plt.savefig(output_filename)
    plt.close()




#run_pca("/home/bran/Workspace/misc/test_murloc45678879/rnaseq_SSc_X60_selected_features_from_boruta_selected_features_selected_features_from_picker_selected_features.csv", "/home/bran/Workspace/misc/test_murloc45678879")
#craft_heatmap("/home/bran/Workspace/misc/test_murloc45678879/rnaseq_SSc_X60_selected_features_from_boruta_selected_features_selected_features_from_picker_selected_features.csv", "/home/bran/Workspace/misc/test_murloc45678879")
