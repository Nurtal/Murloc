## importation
import pandas as pd
from gprofiler import GProfiler
import os

def convert_snp_to_gene(feature_file, output_file):
    """
    """

    ## parameters
    extracted_genes = []

    ## load features
    df = pd.read_csv(feature_file)
    features = list(df['FEATURE'])

    ## transformation
    gp = GProfiler(return_dataframe=True)
    df = gp.snpense(query=features)

    ## extract genes
    for gene_list in list(df["gene_names"]):
        for gene in gene_list:
            if(gene not in extracted_genes):
                extracted_genes.append(gene)

    ## write output file
    output_data = open(output_file, "w")
    output_data.write("FEATURE\n")
    for gene in extracted_genes:
        output_data.write(str(gene)+"\n")
    output_data.close()



def convert_cpg_to_gene(feature_file, methylation_ref_file, output_file):
    """
    """

    ## parameters
    gene_list = []

    ## check if methylation file exist
    if(os.path.isfile(methylation_ref_file)):

        ## load stupid methylation ref (usually tab separated)
        df_ref = pd.read_csv(methylation_ref_file, sep="\t")

        ## load stupid cpg list
        cpg_target = pd.read_csv(feature_file)
        cpg_target = list(cpg_target["FEATURE"])
        for index, row in df_ref.iterrows():
            gene = row["geneSymbol"]
            cpg = row["probeID"]
            if(cpg in cpg_target and gene not in gene_list):
                gene_list.append(gene)

        ## save targets
        output_data = open(output_file, "w")
        output_data.write("FEATURE\n")
        for c in gene_list:
            output_data.write(str(c)+"\n")
        output_data.close()


#convert_snp_to_gene("/home/bran/Workspace/PRECISINV/ccp/RApos_vs_otherPos_SNP/picker_log/picker_selected_features.csv", "/home/bran/Workspace/PRECISINV/ccp/RApos_vs_otherPos_SNP/picker_log/picker_selected_features_converted_to_genes.csv")
convert_cpg_to_gene("/home/bran/Workspace/PRECISINV/ccp/RApos_vs_otherPos_methylation_selected/picker_log/picker_selected_features.csv", "/home/bran/Workspace/PRECISINV/ccp/dataset/MethylationEPIC_CpGtools.tsv", "test.csv")
