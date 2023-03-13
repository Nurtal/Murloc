# importation
import os
from pylatex import (
    Document,
    Section,
    Subsection,
    Table,
    Math,
    TikZ,
    Axis,
    Plot,
    Figure,
    Package,
    Tabular,
    Itemize,
)
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
    file_name = zscore_figure_name.split(".")
    if file_name[-1] == "png":
        log_file = zscore_figure_name.replace(".png", "_pvalue.log")
    else:
        file_name = zscore_figure_name.split("/")
        if "stringdb_log" in file_name:
            log_file = zscore_figure_name.replace("stringdb_log", "statistic")
            log_file = log_file.replace("_stringdb_scan.csv", "zscore_pvalue.log")

    # see if corresponding log file exist
    if not os.path.isfile(log_file):
        return 0

    # check pvalue in log file
    log_data = open(log_file, "r")
    for line in log_data:
        line = line.rstrip()
        line_in_array = line.split(" = ")
        if len(line_in_array) > 1:
            pval = 999
            try:
                pval = float(line_in_array[1])
            except:
                pass

            # return 1 if at least one pval is under treshol
            if float(pval) <= 0.05:
                log_data.close()
                return 1

    # close log file
    log_data.close()
    return 0


def extract_possible_sig_name(log_file):
    """for introspection module"""

    # parameters
    sig_to_pval = {}

    # load data
    df = pd.read_csv(log_file)

    # extract information
    for index, row in df.iterrows():

        name = row["description"]
        fdr = row["fdr"]
        sig_to_pval[name] = fdr

    # return extracted information
    return sig_to_pval


def create_report_pdf(input_file, output_folder):
    """ """

    ## parameters
    pdf_file_report = output_folder + "/report"

    ## init document
    doc = Document()
    doc.packages.append(Package("geometry", options=["tmargin=1cm", "lmargin=1cm"]))

    ## display something
    print("[+][REPORT-GENERATOR] => Running Latex compilation ...")

    ## Original dataset
    with doc.create(Section("Original dataset")):

        # -> plot dimension
        df = pd.read_csv(input_file)
        doc.append(str(df.shape[1]) + " features in the original dataset\n")
        doc.append(str(df.shape[0]) + " observations in the original dataset\n")

        # -> extract targets
        target_list = []
        for elt in list(df[list(df.keys())[-1]]):
            if elt not in target_list:
                target_list.append(elt)

        # -> plot targets
        doc.append(str(len(target_list)) + " targets extracted :\n")
        with doc.create(Itemize()) as itemize:
            for target in target_list:
                itemize.add_item(target)

    ## Feature Selection
    with doc.create(Section("Feature Selection")):

        # -> deal with boruta
        if os.path.isdir(output_folder + "/boruta_log"):
            with doc.create(Subsection("Boruta")):

                # -> hunt number of features extracted
                df = pd.read_csv(
                    output_folder + "/boruta_log/boruta_selected_features.csv"
                )
                nb_features_selected = len(list(df["FEATURE"]))
                doc.append(str(nb_features_selected) + " features extracted by Boruta")

        # -> deal with picker
        if os.path.isdir(output_folder + "/picker_log"):
            with doc.create(Subsection("Picker")):

                # -> hunt number of features extracted
                df = pd.read_csv(
                    output_folder + "/picker_log/picker_selected_features.csv"
                )
                nb_features_selected = len(list(df["FEATURE"]))
                doc.append(str(nb_features_selected) + " features extracted by Picker")

                # -> insert acc figure
                if os.path.isfile(output_folder + "/picker_log/picker_exploration.png"):
                    with doc.create(Figure(position="h!")) as meta_fig:
                        meta_fig.add_image(
                            output_folder + "/picker_log/picker_exploration.png",
                            width="350px",
                        )

    ## Clacification
    with doc.create(Section("Classifier")):

        # -> deal with lda
        if os.path.isdir(output_folder + "/lda_log"):
            with doc.create(Subsection("Linear Discriminant analysis")):

                # -> hunt acc
                acc_log = open(output_folder + "/lda_log/lda_evaluation.log", "r")
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if cmpt == 1:
                        acc = line
                    cmpt += 1
                acc_log.close()
                doc.append("ACC  = " + str(acc) + " %")

            # -> insert confusion matrix figure
            if os.path.isfile(output_folder + "/lda_log/lda_confusion_matrix.png"):
                with doc.create(Figure(position="h!")) as meta_fig:
                    meta_fig.add_image(
                        output_folder + "/lda_log/lda_confusion_matrix.png",
                        width="550px",
                    )

        # -> deal with random forest
        if os.path.isdir(output_folder + "/rf_log"):
            with doc.create(Subsection("Random Forest")):

                # -> hunt acc
                acc_log = open(output_folder + "/rf_log/rf_evaluation.log", "r")
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if cmpt == 1:
                        acc = line
                    cmpt += 1
                acc_log.close()
                doc.append("ACC  = " + str(acc) + " %")

            # -> insert confusion matrix figure
            if os.path.isfile(output_folder + "/rf_log/rf_confusion_matrix.png"):
                with doc.create(Figure(position="h!")) as meta_fig:
                    meta_fig.add_image(
                        output_folder + "/rf_log/rf_confusion_matrix.png", width="550px"
                    )

        # -> deal with logistic regression
        if os.path.isdir(output_folder + "/logistic_log"):
            with doc.create(Subsection("Logistic Regression")):

                # -> hunt acc
                acc_log = open(
                    output_folder + "/logistic_log/logistic_evaluation.log", "r"
                )
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if cmpt == 1:
                        acc = line
                    cmpt += 1
                acc_log.close()
                doc.append("ACC  = " + str(acc) + " %")

            # -> insert confusion matrix figure
            if os.path.isfile(
                output_folder + "/logistic_log/logistic_confusion_matrix.png"
            ):
                with doc.create(Figure(position="h!")) as meta_fig:
                    meta_fig.add_image(
                        output_folder + "/logistic_log/logistic_confusion_matrix.png",
                        width="550px",
                    )

        # -> deal with logistic regression
        if os.path.isdir(output_folder + "/xgb_log"):
            with doc.create(Subsection("xgboosted Tree")):

                # -> hunt acc
                acc_log = open(output_folder + "/xgb_log/xgb_evaluation.log", "r")
                cmpt = 0
                acc = "NA"
                for line in acc_log:
                    line = line.rstrip()
                    if cmpt == 1:
                        acc = line
                    cmpt += 1
                acc_log.close()
                doc.append("ACC  = " + str(acc) + " %")

            # -> insert confusion matrix figure
            if os.path.isfile(output_folder + "/xgb_log/confusion_matrix_test.png"):
                with doc.create(Figure(position="h!")) as meta_fig:
                    meta_fig.add_image(
                        output_folder + "/xgb_log/confusion_matrix_test.png",
                        width="550px",
                    )

    ## Annotation
    if os.path.isdir(output_folder + "/annotation_log"):
        with doc.create(Section("Annotation")):

            ## check if selected pathway file exist
            if os.path.isfile(output_folder + "/annotation_log/selected_pathways.csv"):
                with doc.create(Subsection("KEGG")):

                    with doc.create(Tabular("c|c")) as table:
                        table.add_row(("PATHWAY", "ADJUSTED-PVAL"))
                        table.add_hline()

                        # -> extract pathways
                        df_pathway = pd.read_csv(
                            output_folder + "/annotation_log/selected_pathways.csv"
                        )
                        for index, row in df_pathway.iterrows():
                            pathway = row["PATHWAY"]
                            pvalue = row["ADJUSTED-PVAL"]
                            table.add_row((pathway, pvalue))

                    for fig_file in glob.glob(
                        output_folder + "/annotation_log/*_zscore.png"
                    ):
                        with doc.create(Figure(position="h!")) as meta_fig:
                            meta_fig.add_image(fig_file, width="550px")

            ## check if reactome pathway is present
            if os.path.isfile(
                output_folder + "/annotation_log/reactome_selected_pathways.csv"
            ):
                with doc.create(Subsection("REACTOME")):

                    with doc.create(Tabular("c|c")) as table:
                        table.add_row(("PATHWAY", "PVAL"))
                        table.add_hline()

                        # -> extract pathways
                        df_pathway = pd.read_csv(
                            output_folder
                            + "/annotation_log/reactome_selected_pathways.csv"
                        )
                        for index, row in df_pathway.iterrows():
                            pathway = row["PATHWAY"]
                            pvalue = row["PVAL"]
                            table.add_row((pathway, pvalue))

            if not os.path.isfile(
                output_folder + "/annotation_log/reactome_selected_pathways.csv"
            ) and not os.path.isfile(
                output_folder + "/annotation_log/selected_pathways.csv"
            ):
                doc.append("No Pathway detected")

    ## STRING network
    if os.path.isdir(output_folder + "/display_log"):
        with doc.create(Section("Network")):

            ## check if simple network file exist
            simple_network_file = (
                output_folder + "/display_log/string_graphe_simple.png"
            )
            if os.path.isfile(simple_network_file):
                with doc.create(Subsection("Simple STRING Network")):
                    with doc.create(Figure(position="h!")) as meta_fig:
                        meta_fig.add_image(simple_network_file, width="550px")

            ## check if enhanced network file exist
            enhanced_network_file = (
                output_folder + "/display_log/string_graphe_enhanced.png"
            )
            if os.path.isfile(enhanced_network_file):
                with doc.create(Subsection("Enhanced STRING Network")):
                    with doc.create(Figure(position="h!")) as meta_fig:
                        meta_fig.add_image(enhanced_network_file, width="550px")

    ## Introspection section
    if os.path.isdir(f"{output_folder}/introspection_log"):
        with doc.create(Section("Introspection")):

            # loop over zscore fig
            for zscore_fig_file in glob.glob(
                f"{output_folder}/introspection_log/statistic/*.png"
            ):

                # check the corresponding pvalue
                if check_zscore_pval(zscore_fig_file):

                    # add figure to report
                    with doc.create(Figure(position="h!")) as meta_fig:
                        meta_fig.add_image(zscore_fig_file, width="550px")

    ## generate pdf
    doc.generate_pdf(pdf_file_report)

    ## delete compimation file
    compilation_file_list = [
        pdf_file_report + ".aux",
        pdf_file_report + ".fdb_latexmk",
        pdf_file_report + ".log",
        pdf_file_report + ".tex",
        pdf_file_report + ".fls",
    ]
    for tf in compilation_file_list:
        try:
            os.remove(tf)
        except:
            pass

    ## display something
    print("[+][REPORT-GENERATOR] => Report Generated")


def create_report(input_file, output_folder):
    """ """

    # parameters
    report_file_name = f"{output_folder}/report.html"

    # init report file
    report_data = open(report_file_name, "w")

    # wite header
    report_data.write("<html>\n")
    report_data.write("<title>MURLOC REPORT</title>\n")
    report_data.write("<h1>Murloc Report</h1>\n")

    # ==============#
    # data section #
    # ==============#
    report_data.write("<h2>Data Summary</h2>\n")

    # -> extract dimension of the data
    df = pd.read_csv(input_file)
    report_data.write(f"<p> {df.shape[1]} features in the original dataset </p>\n")
    report_data.write(f"<p> {df.shape[0]} observations in the original dataset </p>\n")

    # -> extract targets
    target_list = []
    for elt in list(df[list(df.keys())[-1]]):
        if elt not in target_list:
            target_list.append(elt)

    # -> display extracted targets
    report_data.write("<p> Extracted targets:</p>\n<ul>\n")
    for elt in target_list:
        report_data.write(f"<li>{elt}</li>\n")
    report_data.write("</ul>\n")

    # ===========================#
    # feature selection section #
    # ===========================#
    report_data.write("<h2>Feature selection</h2>\n")

    # -> deal with boruta
    if os.path.isdir(output_folder + "/boruta_log"):

        # -> hunt number of features extracted
        df = pd.read_csv(output_folder + "/boruta_log/boruta_selected_features.csv")
        nb_features_selected = len(list(df["FEATURE"]))

        # -> display number of extracted features
        report_data.write(
            f"<p> {nb_features_selected} features extracted by Boruta </p>\n"
        )

    # -> deal with picker
    if os.path.isdir(output_folder + "/picker_log"):

        # -> hunt number of features extracted
        df = pd.read_csv(output_folder + "/picker_log/picker_selected_features.csv")
        nb_features_selected = len(list(df["FEATURE"]))

        # -> display number of extracted features
        report_data.write(
            f"<p> {nb_features_selected} features extracted by Picker </p>"
        )

        # -> insert acc figure
        if os.path.isfile(output_folder + "/picker_log/picker_exploration.png"):
            report_data.write(
                f'<img src="{output_folder}/picker_log/picker_exploration.png">\n'
            )

    # ==========#
    # overview #
    # ==========#
    if os.path.isdir(f"{output_folder}/display_log"):
        report_data.write("<h2>Overview</h2>\n")

        # -> TODO insert pca if exist

        # -> insert heatmap if exist
        if os.path.isfile(f"{output_folder}/display_log/heatmap.png"):
            report_data.write(
                f'<img src = "{output_folder}/display_log/heatmap.png" />\n'
            )

    # ========================#
    # classification section #
    # ========================#
    report_data.write("<h2>Classification</h2>\n")

    # -> deal with lda
    if os.path.isdir(output_folder + "/lda_log"):

        # -> init section
        report_data.write("<h3>Linear Discriminant analysis</h3>\n")

        # -> hunt acc
        acc_log = open(f"{output_folder}/lda_log/lda_evaluation.log", "r")
        cmpt = 0
        acc = "NA"
        for line in acc_log:
            line = line.rstrip()
            if cmpt == 1:
                acc = line
            cmpt += 1
        acc_log.close()
        report_data.write("<p>ACC  = " + str(acc) + " %</p>\n")

        # -> insert confusion matrix figure
        if os.path.isfile(output_folder + "/lda_log/lda_confusion_matrix.png"):
            report_data.write(
                f'<img src="{output_folder}/lda_log/lda_confusion_matrix.png">\n'
            )

    # -> deal with random forest
    if os.path.isdir(output_folder + "/rf_log"):

        # -> init section
        report_data.write("<h3>Random Forest</h3>\n")

        # -> hunt acc
        acc_log = open(f"{output_folder}/rf_log/rf_evaluation.log", "r")
        cmpt = 0
        acc = "NA"
        for line in acc_log:
            line = line.rstrip()
            if cmpt == 1:
                acc = line
            cmpt += 1
        acc_log.close()
        report_data.write("<p>ACC  = " + str(acc) + " %</p>\n")

        # -> insert confusion matrix figure
        if os.path.isfile(output_folder + "/rf_log/rf_confusion_matrix.png"):
            report_data.write(
                f'<img src="{output_folder}/rf_log/rf_confusion_matrix.png">\n'
            )

    # -> deal with logistic regression
    if os.path.isdir(output_folder + "/logistic_log"):

        # -> init section
        report_data.write("<h3>Logistic Regression</h3>\n")

        # -> hunt acc
        acc_log = open(f"{output_folder}/logistic_log/logistic_evaluation.log", "r")
        cmpt = 0
        acc = "NA"
        for line in acc_log:
            line = line.rstrip()
            if cmpt == 1:
                acc = line
            cmpt += 1
        acc_log.close()
        report_data.write("<p>ACC  = " + str(acc) + " %</p>\n")

        # -> insert confusion matrix figure
        if os.path.isfile(
            output_folder + "/logistic_log/logistic_confusion_matrix.png"
        ):
            report_data.write(
                f'<img src="{output_folder}/logistic_log/logistic_confusion_matrix.png">\n'
            )

    # -> deal with xgboosted tree
    if os.path.isdir(output_folder + "/xgb_log"):

        # -> init section
        report_data.write("<h3>Xgboosted Tree </h3>\n")

        # -> hunt acc
        acc_log = open(f"{output_folder}/xgb_log/xgb_evaluation.log", "r")
        cmpt = 0
        acc = "NA"
        for line in acc_log:
            line = line.rstrip()
            if cmpt == 1:
                acc = line
            cmpt += 1
        acc_log.close()
        report_data.write("<p>ACC  = " + str(acc) + " %</p>\n")

        # -> insert confusion matrix figure
        if os.path.isfile(output_folder + "/xgb_log/xgb_confusion_matrix.png"):
            report_data.write(
                f'<img src="{output_folder}/xgb_log/xgb_confusion_matrix.png">\n'
            )

    # ====================#
    # annotation section #
    # ====================#
    if os.path.isdir(f"{output_folder}/annotation_log"):
        report_data.write("<h2>Annotation</h2>\n")

        ## check if selected pathway file exist
        if os.path.isfile(output_folder + "/annotation_log/selected_pathways.csv"):

            # init table
            report_data.write("<h3>KEGG</h3>\n")
            report_data.write(
                "<table>\n<tr>\n<th>PATHWAY</th>\n<th>ADJUSTED-PVAL</th>\n</tr>\n"
            )

            # -> extract pathways
            df_pathway = pd.read_csv(
                output_folder + "/annotation_log/selected_pathways.csv"
            )
            for index, row in df_pathway.iterrows():
                pathway = row["PATHWAY"]
                pvalue = row["ADJUSTED-PVAL"]
                report_data.write(
                    f"<tr>\n<td>{pathway}</td>\n<td>{pvalue}</td>\n</tr>\n"
                )

            # close table
            report_data.write("</table>\n")

        ## check if reactome pathway is present
        if os.path.isfile(
            output_folder + "/annotation_log/reactome_selected_pathways.csv"
        ):

            # init table
            report_data.write("<h3>REACTOME</h3>\n")
            report_data.write(
                "<table>\n<tr>\n<th>PATHWAY</th>\n<th>ADJUSTED-PVAL</th>\n</tr>\n"
            )

            # -> extract pathways
            df_pathway = pd.read_csv(
                output_folder + "/annotation_log/reactome_selected_pathways.csv"
            )
            for index, row in df_pathway.iterrows():
                pathway = row["PATHWAY"]
                pvalue = row["PVAL"]
                report_data.write(
                    f"<tr>\n<td>{pathway}</td>\n<td>{pvalue}</td>\n</tr>\n"
                )

            # close table
            report_data.write("</table>\n")

        ## display z score figure
        for fig_file in glob.glob(output_folder + "/annotation_log/*_zscore.png"):
            report_data.write('<img src ="{fig_file}" />\n')

        ## display string analysis if figure exists
        if os.path.isfile(f"{output_folder}/display_log/string_graphe_simple.png"):
            report_data.write(
                f'<img src= "{output_folder}/display_log/string_graphe_simple.png"/>\n'
            )
        if os.path.isfile(f"{output_folder}/display_log/string_graphe_enhanced.png"):
            report_data.write(
                f'<img src= "{output_folder}/display_log/string_graphe_enhanced.png"/>\n'
            )

        if not os.path.isfile(
            output_folder + "/annotation_log/reactome_selected_pathways.csv"
        ) and not os.path.isfile(
            output_folder + "/annotation_log/selected_pathways.csv"
        ):
            report_data.write("<p> No Pathway detected </p>\n")

        ## display zscore for each island
        report_data.write(f"<h3>Zscore for identified String subnetwork </h3>\n")
        for zscore_fig in glob.glob(
            f"{output_folder}/display_log/stringdb_zscore/*.png"
        ):
            report_data.write(f'<img src= "{zscore_fig}"/>\n')

        ## display pathway name table
        if os.path.isfile(
            f"{output_folder}/display_log/stringdb_island_annotation.csv"
        ):
            report_data.write("<h3>pathway table of identified sub network</h3>\n")
            report_data.write(
                "<table>\n<tr>\n<th>SUBNET ID</th>\n<th>PATHWAYS</th>\n</tr>\n"
            )
            df_pathway = pd.read_csv(
                f"{output_folder}/display_log/stringdb_island_annotation.csv"
            )
            for index, row in df_pathway.iterrows():
                island_id = row["ISLAND_ID"]
                pathway = row["PATHWAYS"]
                report_data.write(
                    f"<tr>\n<td>{island_id}</td>\n<td>{pathway}</td>\n</tr>\n"
                )
            report_data.write("</table>\n")

    # =======================#
    # intropsection section #
    # =======================#
    if os.path.isdir(f"{output_folder}/introspection_log"):
        report_data.write("<h2>Introspection</h2>\n")

        # loop over zscore fig
        for zscore_fig_file in glob.glob(
            f"{output_folder}/introspection_log/statistic/*.png"
        ):

            # check the corresponding pvalue
            if check_zscore_pval(zscore_fig_file):

                # add figure to report
                report_data.write(f'<img src = "{zscore_fig_file}">\n')

        # generate annotation table from stringdb log
        for log_file in glob.glob(
            f"{output_folder}/introspection_log/stringdb_log/*.csv"
        ):

            # check the corresponding pvalue
            if check_zscore_pval(log_file):

                # init list
                sig_id = log_file.split("/")
                sig_id = sig_id[-1].replace("_stringdb_scan.csv", "")
                report_data.write(f"<p>{sig_id}</p>\n<ul>\n")

                # extract potiential sig name
                potential_sig_name_to_proba = extract_possible_sig_name(log_file)
                for potential_name in potential_sig_name_to_proba.keys():
                    proba = potential_sig_name_to_proba[potential_name]
                    report_data.write(f"<li>{potential_name} ({proba})</li>\n")
                report_data.write("</ul>\n")

    # close report file
    report_data.write("</html>\n")
    report_data.close()


if __name__ == "__main__":

    # parameters
    input_file = (
        "/home/bran/Workspace/SIDEQUEST/Eleonore/paps_sle/rnaseq_data_paps_vs_ctrl.csv"
    )
    output_folder = (
        "/home/bran/Workspace/SIDEQUEST/Eleonore/paps_sle/murloc_run_paps_vs_ctrl"
    )

    # test check zscore
    # for png_file in glob.glob("/tmp/murloc_introspection/introspection_log/statistic/*.png"):
    #     restult = check_zscore_pval(png_file)
    #     print(restult)

    # test html report generation
    create_report(input_file, output_folder)

# create_report("D:\\toy_dataset.csv", "D:\\murloc_output_test4")
# create_report("/home/bran/Workspace/SSA/dataset/33_gene_sig_MCTD_classification.csv", "/home/bran/Workspace/misc/murloc_test")
