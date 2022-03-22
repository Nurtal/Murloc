




def run_annotation(input_file, output_folder):
    """
    """

    ## importation
    import pandas as pd
    import gseapy as gp
    import matplotlib.pyplot as plt
    from gseapy.plot import barplot, dotplot
    import re
    import os
    import stat_stuff


    ## parameters
    gene_sets=['KEGG_2016']
    selected_pathway = []
    pathway_to_pval = {}
    output_file_selected = output_folder+"/annotation_log/selected_pathways.csv"
    output_file_all = output_folder+"/annotation_log/all_pathways.csv"

    ## prepare output subdirectory
    if(not os.path.isdir(output_folder+"/annotation_log")):
        os.mkdir(output_folder+"/annotation_log")

    ## load genes names
    df_genes = pd.read_csv(input_file)
    gene_list = []
    for elt in list(df_genes.keys()):
        if(elt not in ['ID', 'LABEL']):
            gene_list.append(elt)

    ## run annotation
    try:
        enr = gp.enrichr(gene_list=gene_list,
                     gene_sets=gene_sets,
                     organism='Human',
                     description='test_name',
                     outdir=output_folder+"/annotation_log",
                     cutoff=0.5 # test dataset, use lower value from range(0,1)
                    )

        ## scan results
        df_results = enr.results
        for index, row in df_results.iterrows():

            #-> extract adjusted p value
            adjusted_pval = row['Adjusted P-value']
            term = row['Term']

            #-> check adjusted pvalue
            if(adjusted_pval <= 0.05):
                pathway_to_pval[term] = adjusted_pval
                selected_pathway.append(term)
    except:
        print("[!][ANNOTATION] => Can't run enrichr alignement")

    ## save results
    if(len(selected_pathway) > 0):
        print("[*][ANNOTATION] >> TARGET HITS <<")
        output_data = open(output_file_selected, "w")
        output_data.write("PATHWAY,ADJUSTED-PVAL\n")
        for pathway in pathway_to_pval.keys():
            output_data.write(str(pathway)+","+str(pathway_to_pval[pathway])+"\n")
        output_data.close()

        #-> generate zscore for pathway
        for index, row in df_results.iterrows():

            term = row['Term']
            genes = row['Genes']

            if(term in pathway_to_pval.keys()):

                #-> craft parameters
                term_name = term.replace(" ", "_")
                term_name = term_name.replace("/", "-")
                output_zscore_fig_name = output_folder+"/annotation_log/"+term_name+"_zscore.png"
                gene_list = genes.split(";")

                #-> run figure creation
                stat_stuff.plot_zscore(input_file, gene_list, output_zscore_fig_name)


    else:
        print("[+][ANNOTATION] => Nothing Found")

    ## save all annotation results
    df_results.to_csv(output_file_all, index=False)



#run_annotation("D:\\murloc_output_test4\\toy_dataset_selected_features_from_boruta_selected_features.csv","D:\\murloc_output_test4\\boruta_log\\boruta_selected_features.csv", "D:\\murloc_output_test4")
