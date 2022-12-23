# importation
import stringdb
import os


def get_string_neighboor(gene_list, work_folder):
    """
    Use the stringdb module to "extend the target list"
    -> for each gene in the gene list use stringdb to find related genes
       (in our case protein in fact, the idea is to highlight intercation network)

    return a dictionnary where each key is a "signame" and related genes as assigned as value
    """

    # parameters
    gene_to_related_genes = {}
    save_log_information = True
    cmpt = 0
    
    # init introspection folder if do not exist
    if(not os.path.isdir(f"{work_folder}/introspection_log/stringdb_log")):
        os.mkdir(f"{work_folder}/introspection_log/stringdb_log")

    # hunt related genes
    for gene in gene_list:
        
        # try to expand the signature
        try:
            
            # init parameters
            cmpt+=1
            signame = f"sig_{cmpt}"
            gene_to_related_genes[signame] = []
            string_ids = stringdb.get_string_ids([gene])
            
            # try to run the request
            df = stringdb.get_enrichment(string_ids.queryItem)

            # save log
            if(save_log_information):
                df.to_csv(f"{work_folder}/introspection_log/stringdb_log/{signame}_stringdb_scan.csv", index=False)

            # craft data structure
            for index, row in df.iterrows():
                candidate_list = row["inputGenes"].split(",")
                for candidate in candidate_list:
                    if(candidate not in gene_to_related_genes[signame]):
                        gene_to_related_genes[signame].append(candidate)

        # catch error if request end badly
        except:
            if(save_log_information):
                print(f"<<INTROSPECTION>> Failed to find related genes to {gene}")

    # drop duplicate
    sig_to_target = {}
    cmpt = 0
    for key in gene_to_related_genes.keys():
        gene_list = gene_to_related_genes[key]
        if(gene_list not in sig_to_target.values()):
            cmpt+=1
            sig_to_target[f"sig_{cmpt}"] = gene_list
    
    # return dictionnary
    return sig_to_target


def expand_target_list(work_folder, target_list):
    """
    """

    # parameters
    target_to_extented_signature_name = {}
    signame_to_genlist = []

    # check that target list is not empty
    if(len(target_list) == 0):
        print(f"<<!>> [INTROSPECTION] -> the provided target list is empty")
        print(f"<<!>> [INTROSPECTION] -> droping introspection step")
        return 0

    # extend the target list
    signame_to_genlist = get_string_neighboor(target_list, work_folder)
    
    # return extracted pathway
    return signame_to_genlist



if __name__ == "__main__":



    gene_list = ["STIM1", "ORAI1"]
    stuff = expand_target_list("/tmp/", gene_list)
    
    print(stuff)
    # get_string_neighboor(gene_list, "/tmp/")
