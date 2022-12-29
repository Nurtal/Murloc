

def rescale(l,newmin,newmax):
    """
    ploting graph stuff
    """
    arr = list(l)
    try:
        arr = [(x-min(arr))/(max(arr)-min(arr))*(newmax-newmin)+newmin for x in arr]
    except:
        pass
    return arr



def run_string_analysis(selected_feature_file, output_folder):
    """
    """

    ## importation
    import networkx as nx
    import requests
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    import os

    ## check if there is a display log folder
    if(not os.path.isdir(output_folder+"/display_log")):
        os.mkdir(output_folder+"/display_log")

    ## load selected features
    df_feature = pd.read_csv(selected_feature_file)
    protein_list = list(df_feature["FEATURE"])

    ## send request to string db
    proteins = '%0d'.join(protein_list)
    url = 'https://string-db.org/api/tsv/network?identifiers=' + proteins + '&species=9606'
    r = requests.get(url)

    lines = r.text.split('\n') # pull the text from the response object and split based on new lines
    data = [l.split('\t') for l in lines] # split each line into its components based on tabs
    # convert to dataframe using the first row as the column names; drop empty, final row
    df = pd.DataFrame(data[1:-1], columns = data[0])
    # dataframe with the preferred names of the two proteins and the score of the interaction
    interactions = df[['preferredName_A', 'preferredName_B', 'score']]

    
    # TODO extract list of interaction in genes
    

    ## create graphe
    G=nx.Graph(name='Protein Interaction Graph')
    interactions = np.array(interactions)
    for i in range(len(interactions)):
        interaction = interactions[i]
        a = interaction[0] # protein a node
        b = interaction[1] # protein b node
        w = float(interaction[2]) # score as weighted edge where high scores = low weight
        G.add_weighted_edges_from([(a,b,w)]) # add weighted edge to graph


    ## enhence graphe
    # use the matplotlib plasma colormap
    graph_colormap = cm.get_cmap('plasma', 12)
    # node color varies with Degree
    c = rescale([G.degree(v) for v in G],0.0,0.9)
    c = [graph_colormap(i) for i in c]
    # node size varies with betweeness centrality - map to range [10,100]
    bc = nx.betweenness_centrality(G) # betweeness centrality
    s =  rescale([v for v in bc.values()],1500,7000)
    # edge width shows 1-weight to convert cost back to strength of interaction
    ew = rescale([float(G[u][v]['weight']) for u,v in G.edges],0.1,4)
    # edge color also shows weight
    ec = rescale([float(G[u][v]['weight']) for u,v in G.edges],0.1,1)
    ec = [graph_colormap(i) for i in ec]


    ## display graphe
    pos = nx.spring_layout(G) # position the nodes using the spring layout
    plt.figure(figsize=(11,11),facecolor=[0.7,0.7,0.7,0.4])
    nx.draw_networkx(G)
    plt.axis('off')
    plt.savefig(output_folder+"/display_log/string_graphe_simple.png")
    plt.close()

    pos = nx.spring_layout(G)
    plt.figure(figsize=(19,9),facecolor=[0.7,0.7,0.7,0.4])
    nx.draw_networkx(G, pos=pos, with_labels=True, node_color=c, node_size=s,edge_color= ec,width=ew,
                 font_color='white',font_weight='bold',font_size='9')
    plt.axis('off')
    plt.savefig(output_folder+"/display_log/string_graphe_enhanced.png")
    plt.close()


#run_string_analysis("/home/bran/Workspace/PRECISINV/ccp/features/RApos_vs_otherPos_genes_from_cpg_selected.csv", "/home/bran/Workspace/PRECISINV/ccp/images/")
