

def create_report(input_file, output_folder):
    """
    """

    ## importation
    from pylatex import Document, Section, Subsection, Table, Math, TikZ, Axis, Plot, Figure, Package, Tabular
    from pylatex.utils import italic, escape_latex
    import os
    import pandas as pd
    import glob

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
            with doc.create(Figure(position='h!')) as meta_fig:
                meta_fig.add_image(output_folder+"/lda_log/lda_confusion_matrix.png", width='550px')


    ## Annotation
    if(os.path.isdir(output_folder+"/annotation_log")):
        with doc.create(Section('Annotation')):

            ## check if selected pathway file exist
            if(os.path.isfile(output_folder+"/annotation_log/selected_pathways.csv")):

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


            else:
                doc.append("No Pathway detected")





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
