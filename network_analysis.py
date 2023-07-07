import stat_stuff
import os
import annotation_runner


def extract_connexe_island(interactions):
    """
    Use the dataframe interactions to extract list of interacting genes/protein
    return a dictionnary where the key is the id of the intrecating set og genes/protein (called an "island")
    and the values are the genes/protein composing the set
    """

    # parameters
    island_to_prot = {}
    elt_to_island = {}

    # loop over data
    cmpt = 0
    for index, row in interactions.iterrows():
        elt_a = row["preferredName_A"]
        elt_b = row["preferredName_B"]
        if elt_a not in elt_to_island.keys():
            if elt_b not in elt_to_island.keys():
                cmpt += 1
                elt_to_island[elt_a] = f"i{cmpt}"
                elt_to_island[elt_b] = f"i{cmpt}"
            else:
                elt_to_island[elt_a] = elt_to_island[elt_b]
        elif elt_b not in elt_to_island.keys():
            elt_to_island[elt_b] = elt_to_island[elt_a]

    # reverse dictionnary
    for elt in elt_to_island.keys():
        island = elt_to_island[elt]
        if island not in island_to_prot.keys():
            island_to_prot[island] = [elt]
        else:
            island_to_prot[island].append(elt)

    # return island to list of prot
    return island_to_prot


def generate_zscore_figure(input_data_file, output_folder, island_to_prot):
    """
    Generate a zscore figure for each "island" (set of connected genes/proteine)
    found with stringdb

    figures are saved in a subfolder of the display_log subfolder
    """

    # parameters
    subfolder = f"{output_folder}/display_log/stringdb_zscore"

    # init output directory
    if not os.path.isdir(subfolder):
        os.mkdir(subfolder)

    # extract list og genes
    for island in island_to_prot:

        gene_list = island_to_prot[island]
        output_file_name = f"{subfolder}/{island}_zscore.png"

        # give them to the zscore function
        stat_stuff.plot_zscore(input_data_file, gene_list, output_file_name)


def hunt_pathway_for_island(output_folder, island_to_prot):
    """
    assign a list of pathway to each island, using reactome annotation
    save the result file in display_log subfolder
    """

    # parameters
    subfolder = f"{output_folder}/display_log/"

    # init output file
    result_data = open(f"{subfolder}/stringdb_island_annotation.csv", "w")
    result_data.write("ISLAND_ID,PATHWAYS,GENES\n")

    # fill file
    for island in island_to_prot.keys():
        gene_list = island_to_prot[island]
        path_list = annotation_runner.get_reactome_pathway_from_gene_list(gene_list)

        # craft gene entry
        gene_str = ""
        for elt in gene_list:
            gene_str += f"{elt} - "
        gene_str = gene_str[:-2]

        # craft pathway enrty
        path_str = ""
        for elt in path_list:
            elt = elt.replace(",", " ")
            path_str = f"{elt} / "
        path_str = path_str[:-2]

        # update file
        result_data.write(f"{island},{path_str},{gene_str}\n")

    # close file
    result_data.close()


def rescale(l, newmin, newmax):
    """
    ploting graph stuff
    """
    arr = list(l)
    try:
        arr = [
            (x - min(arr)) / (max(arr) - min(arr)) * (newmax - newmin) + newmin
            for x in arr
        ]
    except:
        pass
    return arr


def run_string_analysis(input_data_file, selected_feature_file, output_folder):
    """ """

    ## importation
    import networkx as nx
    import requests
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    import os

    ## check if there is a display log folder
    if not os.path.isdir(output_folder + "/display_log"):
        os.mkdir(output_folder + "/display_log")

    ## load selected features
    df_feature = pd.read_csv(selected_feature_file)
    protein_list = []
    for elt in list(df_feature["FEATURE"]):
        if str(elt) != "nan":
            protein_list.append(elt)

    ## send request to string db
    proteins = "%0d".join(protein_list)
    url = (
        "https://string-db.org/api/tsv/network?identifiers="
        + proteins
        + "&species=9606"
    )
    r = requests.get(url)

    lines = r.text.split(
        "\n"
    )  # pull the text from the response object and split based on new lines
    data = [
        l.split("\t") for l in lines
    ]  # split each line into its components based on tabs

    # convert to dataframe using the first row as the column names; drop empty, final row
    df = pd.DataFrame(data[1:-1], columns=data[0])

    # dataframe with the preferred names of the two proteins and the score of the interaction
    try:
        interactions = df[["preferredName_A", "preferredName_B", "score"]]
    except:
        return -1

    # extract list of interaction in genes
    island_to_prot = extract_connexe_island(interactions)

    # Associate list of pathway to each island, save it in a csv file
    hunt_pathway_for_island(output_folder, island_to_prot)

    # compute zscore & craft graphe
    generate_zscore_figure(input_data_file, output_folder, island_to_prot)

    ## create graphe
    G = nx.Graph(name="Protein Interaction Graph")
    interactions = np.array(interactions)
    for i in range(len(interactions)):
        interaction = interactions[i]
        a = interaction[0]  # protein a node
        b = interaction[1]  # protein b node
        w = float(
            interaction[2]
        )  # score as weighted edge where high scores = low weight
        G.add_weighted_edges_from([(a, b, w)])  # add weighted edge to graph

    ## enhence graphe
    # use the matplotlib plasma colormap
    graph_colormap = cm.get_cmap("plasma", 12)
    # node color varies with Degree
    c = rescale([G.degree(v) for v in G], 0.0, 0.9)
    c = [graph_colormap(i) for i in c]
    # node size varies with betweeness centrality - map to range [10,100]
    bc = nx.betweenness_centrality(G)  # betweeness centrality
    s = rescale([v for v in bc.values()], 1500, 7000)
    # edge width shows 1-weight to convert cost back to strength of interaction
    ew = rescale([float(G[u][v]["weight"]) for u, v in G.edges], 0.1, 4)
    # edge color also shows weight
    ec = rescale([float(G[u][v]["weight"]) for u, v in G.edges], 0.1, 1)
    ec = [graph_colormap(i) for i in ec]

    ## display graphe
    pos = nx.spring_layout(G)  # position the nodes using the spring layout
    plt.figure(figsize=(11, 11), facecolor=[0.7, 0.7, 0.7, 0.4])
    nx.draw_networkx(G)
    plt.axis("off")
    plt.savefig(output_folder + "/display_log/string_graphe_simple.png")
    plt.close()

    pos = nx.spring_layout(G)
    plt.figure(figsize=(19, 9), facecolor=[0.7, 0.7, 0.7, 0.4])
    nx.draw_networkx(
        G,
        pos=pos,
        with_labels=True,
        node_color=c,
        node_size=s,
        edge_color=ec,
        width=ew,
        font_color="white",
        font_weight="bold",
        font_size="9",
    )
    plt.axis("off")
    plt.savefig(output_folder + "/display_log/string_graphe_enhanced.png")
    plt.close()


if __name__ == "__main__":

    # test string network
    input_data_file = "/home/bran/Workspace/SIDEQUEST/Eleonore/paps_sle/murloc_run/rnaseq_for_murloc_selected_features_from_boruta_selected_features_selected_features_from_picker_selected_features.csv"
    selected_feature_file = "/home/bran/Workspace/SIDEQUEST/Eleonore/paps_sle/murloc_run/boruta_log/boruta_selected_features.csv"
    run_string_analysis(
        input_data_file, selected_feature_file, "/tmp/murloc_introspection/"
    )
