# importation
import os
from pylatex import Document, Section, Subsection, Table, Math, TikZ, Axis, Plot, Figure, Package, Tabular, Itemize
from pylatex.utils import italic, escape_latex
import pandas as pd
import glob

def check_zscore_pval(zscore_figure_name):
    """
    Design to check if a zscore figure (usually from introspection module)
    display significant differences, return 0 if its not the case or information
    can't be access, return 1 if at least on pvalue is significant in the
    associated log file

    [TO TEST]
    """

    # guess log file name
    log_file = zscore_figure_name.replace(".png", ".log")

    # see if corresponding log file exist
    if(not os.path.isfile(log_file)):
        return 0

    # check pvalue in log file
    log_data = open(log_file, "r")
    for line in log_data:
        line = line.rstrip()
        line_in_array = line.split(" = ")
        if(len(line_in_array) > 1):
            pval = 999
            try:
                pval = float(line_in_array[1])
            except:
                pass

            # return 1 if at least one pval is under treshol
            if(float(pval) <= 0.05):
                log_data.close()
                return 1
    
    # close log file
    log_data.close()
    return 0




def create_report(input_file, output_folder):
    """
    """

    ## parameters
    pdf_file_report = output_folder+"/report"

    ## init document
    doc = Document()
    doc.packages.append(
        Package(
            'geometry',
            options=['tmargin=1cm','lmargin=1cm']
        )
    )


    ## display something
    print("[+][REPORT-GENERATOR] => Running Latex compilation ...")

    ## Original dataset
    with doc.create(Section('Original dataset')):

        #-> plot dimension
        df = pd.read_csv(input_file)
        doc.append(str(df.shape[1])+" features in the original dataset\n")
        doc.append(str(df.shape[0])+" observations in the original dataset\n")

        #-> extract targets
        target_list = []
        for elt in list(df[list(df.keys())[-1]]):
            if(elt not in target_list):
                target_list.append(elt)

        #-> plot targets
        doc.append(str(len(target_list))+" targets extracted :\n")
        with doc.create(Itemize()) as itemize:
            for target in target_list:
                itemize.add_item(target)


    ## Feature Selection
    with doc.create(Section('Feature Selection')):

        #-> deal with boruta
        if(os.path.isdir(output_folder+"/boruta_log")):
            with doc.create(Subsection('Boruta')):

                #-> hunt number of features extracted
                df = pd.read_csv(output_folder+"/boruta_log/boruta_selected_features.csv")
                nb_features_selected = len(list(df['FEATURE']))
                doc.append(str(nb_features_selected)+" features extracted by Boruta")

        #-> deal with picker
        if(os.path.isdir(output_folder+"/picker_log")):
            with doc.create(Subsection('Picker')):

                #-> hunt number of features extracted
                df = pd.read_csv(output_folder+"/picker_log/picker_selected_features.csv")
                nb_features_selected = len(list(df['FEATURE']))
                doc.append(str(nb_features_selected)+" features extracted by Picker")

                #-> insert acc figure
                if(os.path.isfile(output_folder+"/picker_log/picker_exploration.png")):
                    with doc.create(Figure(position='h!')) as meta_fig:
                        meta_fig.add_image(output_folder+"/picker_log/picker_exploration.png", width='350px')

    ## Clacification
    with doc.create(Section('Classifier')):

        #-> deal with lda
        if(os.path.isdir(output_folder+"/lda_log")):
            with doc.create(Subsection('Linear Discriminant analysis')):

                #-> hunt acc
                acc_log = open(output_folder+"/lda_log/lda_evaluation.log", "r")
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if(cmpt == 1):
                        acc = line
                    cmpt+=1
                acc_log.close()
                doc.append("ACC  = "+str(acc)+" %")

            #-> insert confusion matrix figure
            if(os.path.isfile(output_folder+"/lda_log/lda_confusion_matrix.png")):
                with doc.create(Figure(position='h!')) as meta_fig:
                    meta_fig.add_image(output_folder+"/lda_log/lda_confusion_matrix.png", width='550px')

        #-> deal with random forest
        if(os.path.isdir(output_folder+"/rf_log")):
            with doc.create(Subsection('Random Forest')):

                #-> hunt acc
                acc_log = open(output_folder+"/rf_log/rf_evaluation.log", "r")
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if(cmpt == 1):
                        acc = line
                    cmpt+=1
                acc_log.close()
                doc.append("ACC  = "+str(acc)+" %")

            #-> insert confusion matrix figure
            if(os.path.isfile(output_folder+"/rf_log/rf_confusion_matrix.png")):
                with doc.create(Figure(position='h!')) as meta_fig:
                    meta_fig.add_image(output_folder+"/rf_log/rf_confusion_matrix.png", width='550px')


        #-> deal with logistic regression
        if(os.path.isdir(output_folder+"/logistic_log")):
            with doc.create(Subsection('Logistic Regression')):

                #-> hunt acc
                acc_log = open(output_folder+"/logistic_log/logistic_evaluation.log", "r")
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if(cmpt == 1):
                        acc = line
                    cmpt+=1
                acc_log.close()
                doc.append("ACC  = "+str(acc)+" %")

            #-> insert confusion matrix figure
            if(os.path.isfile(output_folder+"/logistic_log/logistic_confusion_matrix.png")):
                with doc.create(Figure(position='h!')) as meta_fig:
                    meta_fig.add_image(output_folder+"/logistic_log/logistic_confusion_matrix.png", width='550px')


        #-> deal with logistic regression
        if(os.path.isdir(output_folder+"/xgb_log")):
            with doc.create(Subsection('xgboosted Tree')):

                #-> hunt acc
                acc_log = open(output_folder+"/xgb_log/xgb_evaluation.log", "r")
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if(cmpt == 1):
                        acc = line
                    cmpt+=1
                acc_log.close()
                doc.append("ACC  = "+str(acc)+" %")

            #-> insert confusion matrix figure
            if(os.path.isfile(output_folder+"/xgb_log/confusion_matrix_test.png")):
                with doc.create(Figure(position='h!')) as meta_fig:
                    meta_fig.add_image(output_folder+"/xgb_log/confusion_matrix_test.png", width='550px')


    ## Annotation
    if(os.path.isdir(output_folder+"/annotation_log")):
        with doc.create(Section('Annotation')):

            ## check if selected pathway file exist
            if(os.path.isfile(output_folder+"/annotation_log/selected_pathways.csv")):
                with doc.create(Subsection('KEGG')):

                    with doc.create(Tabular('c|c')) as table:
                        table.add_row(("PATHWAY","ADJUSTED-PVAL"))
                        table.add_hline()

                        #-> extract pathways
                        df_pathway = pd.read_csv(output_folder+"/annotation_log/selected_pathways.csv")
                        for index, row in df_pathway.iterrows():
                            pathway = row['PATHWAY']
                            pvalue = row["ADJUSTED-PVAL"]
                            table.add_row((pathway,pvalue))

                    for fig_file in glob.glob(output_folder+"/annotation_log/*_zscore.png"):
                        with doc.create(Figure(position='h!')) as meta_fig:
                            meta_fig.add_image(fig_file, width='550px')

            ## check if reactome pathway is present
            if(os.path.isfile(output_folder+"/annotation_log/reactome_selected_pathways.csv")):
                with doc.create(Subsection('REACTOME')):

                    with doc.create(Tabular('c|c')) as table:
                        table.add_row(("PATHWAY","PVAL"))
                        table.add_hline()

                        #-> extract pathways
                        df_pathway = pd.read_csv(output_folder+"/annotation_log/reactome_selected_pathways.csv")
                        for index, row in df_pathway.iterrows():
                            pathway = row['PATHWAY']
                            pvalue = row["PVAL"]
                            table.add_row((pathway,pvalue))



            if(not os.path.isfile(output_folder+"/annotation_log/reactome_selected_pathways.csv") and not os.path.isfile(output_folder+"/annotation_log/selected_pathways.csv")):
                doc.append("No Pathway detected")

    ## STRING network
    if(os.path.isdir(output_folder+"/display_log")):
        with doc.create(Section('Network')):

            ## check if simple network file exist
            simple_network_file = output_folder+"/display_log/string_graphe_simple.png"
            if(os.path.isfile(simple_network_file)):
                with doc.create(Subsection('Simple STRING Network')):
                    with doc.create(Figure(position='h!')) as meta_fig:
                        meta_fig.add_image(simple_network_file, width='550px')

            ## check if enhanced network file exist
            enhanced_network_file = output_folder+"/display_log/string_graphe_enhanced.png"
            if(os.path.isfile(enhanced_network_file)):
                with doc.create(Subsection('Enhanced STRING Network')):
                    with doc.create(Figure(position='h!')) as meta_fig:
                        meta_fig.add_image(enhanced_network_file, width='550px')





    ## generate pdf
    doc.generate_pdf(pdf_file_report)

    ## delete compimation file
    compilation_file_list = [
        pdf_file_report+".aux",
        pdf_file_report+".fdb_latexmk",
        pdf_file_report+".log",
        pdf_file_report+".tex",
        pdf_file_report+".fls"
    ]
    for tf in compilation_file_list:
        try:
            os.remove(tf)
        except:
            pass

    ## display something
    print("[+][REPORT-GENERATOR] => Report Generated")








#create_report("D:\\toy_dataset.csv", "D:\\murloc_output_test4")
#create_report("/home/bran/Workspace/SSA/dataset/33_gene_sig_MCTD_classification.csv", "/home/bran/Workspace/misc/murloc_test")
