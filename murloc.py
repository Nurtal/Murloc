



def run_feature_selection(input_file):
    """
    """

    ## importation
    import fs_boruta

    ## parameters

    ## ask user with algorithm to use

    ## Boruta Case ##-----------------------------------------------------------
    #-> TODO : ask user for config
    #-> init default config
    iteration = 300
    depth = 5

    #-> run boruta with config
    fs_boruta.run_boruta(input_file, iteration, depth, output_folder)



def run_classification(input_file, output_folder):
    """
    """

    ## importation
    import clf_lda

    ## parameters

    ## ask user which algorithm to use

    ## LDA Case ##--------------------------------------------------------------
    #-> run lda
    clf_lda.run_lda_classifier(input_file, output_folder)



def run_annotation(output_folder):
    """
    """

    ## importation
    import pandas as pd
    import os
    import glob
    import annotation_runner
    import stat_stuff

    ## parameters
    input_file = "NA"
    reactome_target_file = ["reactome_manual.csv", "manual_reactome.csv"]

    ## check if folder exist
    if(os.path.isdir(output_folder)):

        ## determine input file
        #-> check for selected data files
        best_candidate = 0
        for candidates_file in glob.glob(output_folder+"/*_selected_features.csv"):
            candidate = candidates_file.split("selected_features")
            candidate = len(candidates_file)
            if(candidate > best_candidate):
                best_candidate = candidate
                input_file = candidates_file
    else:
        print("[!][ANNOTATION] => can't find folder "+str(output_folder))

    if(os.path.isfile(input_file)):

        ## call KEGG annotation
        annotation_runner.run_annotation(input_file, output_folder)

        ## call REACTOME annotation
        annotation_runner.run_reactome_annotation(input_file, output_folder)

        ## craft features used file
        df = pd.read_csv(input_file)
        feature_file = open(output_folder+"/annotation_log/features_used.csv", "w")
        feature_file.write("FEATURE\n")
        for x in df.keys():
            if(x not in ['ID', "LABEL"]):
                feature_file.write(str(x)+"\n")
        feature_file.close()

        ## check if there is a reactome result file
        for tf in reactome_target_file:
            if(os.path.isfile(output_folder+"/annotation_log/"+tf)):
                stat_stuff.generate_z_score_from_reactome_results_file(
                    input_file,
                    output_folder+"/annotation_log/"+tf,
                    output_folder
                )


    else:
        print("[!][ANNOTATION] => can't determined input file")





def parse_configuration_file(config_file):
    """
    Not tested
    read a config file and return the list of extracted instruction

    config file format:

        action-type_algorithm


    -> annotation should be written :
        "annotation_KEGG-2016" in the config file



    boruta-picker : start with boruta, run picker on the features selected by
    boruta.

    """

    ## parameters
    instruction_list = []
    action_to_available_algorithm = {}
    action_to_available_algorithm["fs"] = ["boruta", "picker", "boruta-picker"]
    action_to_available_algorithm["clf"] = ["lda", "rf", "logistic"]
    action_to_available_algorithm["annotation"] = ["KEGG-2016", 'REACTOME']
    action_to_available_algorithm["pca"] = ["all", 'selected']
    action_to_available_algorithm["display"] = ["string", "heatmap"]
    iterative_limit = "NA"

    ## read config file
    config_data = open(config_file, "r")
    for line in config_data:
        line = line.rstrip()
        line_in_array = line.split("_")

        if(len(line_in_array) > 0):
            action_type = line_in_array[0]
            algorithm = line_in_array[1]

            #-> detect iterative mode
            if(action_type == "iterative"):
                try:
                    iterative_limit = float(line_in_array[1])
                except:
                    print("[!] can't parse iteration limit in "+str(line))

            if(action_type in list(action_to_available_algorithm.keys())):
                if(algorithm in action_to_available_algorithm[action_type]):
                    instruction_list.append(line)
                else:
                    print("[!][CONFIG-PARSER] => Can't find algorithm "+str(algorithm))
            else:
                print("[!][CONFIG-PARSER] => Can't find action "+str(action_type))
        else:
            print("[!][CONFIG-PARSER] => Can't parse line "+str(line))

    ## close config file
    config_data.close()

    ## return list of action
    return (instruction_list,iterative_limit)




def run_instruction(instruction_list, input_file, output_folder):
    """
    run with a list of instruction
    """

    ## importation
    import fs_boruta
    import fs_picker
    import clf_lda
    import clf_rf
    import clf_logistic
    import dataset_preprocessing
    import annotation_runner
    import os
    import shutil
    import display_data
    import network_analysis


    ## parameters
    folder_separator = "/"
    boruta_used = False
    picker_used = False

    ## check if we are running on a fucking windows machine
    if(os.name == 'nt'):
        folder_separator = "\\"

    ## loop over instruction
    for instruction in instruction_list:

        #-> parse instruction
        instruction = instruction.split("_")
        action = instruction[0]
        algorithm = instruction[1]

        #-> deal with feature selection
        if(action == "fs"):
            if(algorithm == "boruta"):

                # -> default parameters
                iteration = 700
                depth = 5
                feature_file = output_folder+folder_separator+"boruta_log"+folder_separator+"boruta_selected_features.csv"

                #-> run boruta
                fs_boruta.run_boruta(input_file, iteration, depth, output_folder)

                #-> craft dataset with selected variables
                input_file = dataset_preprocessing.craft_selected_variable_dataset(input_file, feature_file, output_folder)

                #-> update workflow parameters
                boruta_used = True
                boruta_input_file = input_file

            if(algorithm == "picker"):

                #-> default parameters
                min_features = 10
                step = 1
                feature_file = output_folder+folder_separator+"picker_log"+folder_separator+"picker_selected_features.csv"

                #-> run picker
                fs_picker.run_picker(input_file, output_folder, min_features, step)

                #-> generate graphics
                fs_picker.plot_acc(output_folder)

                #-> save best features
                fs_picker.hunt_best_conf(output_folder)

                #-> craft dataset with selected variables
                input_file = dataset_preprocessing.craft_selected_variable_dataset(input_file, feature_file, output_folder)

                #-> update workflow parameters
                picker_used = True
                picker_input_file = input_file

            if(algorithm == "boruta-picker"):

                ## Start with Boruta
                # -> default parameters
                iteration = 300
                depth = 5
                feature_file = output_folder+folder_separator+"boruta_log"+folder_separator+"boruta_selected_features.csv"

                #-> run boruta
                fs_boruta.run_boruta(input_file, iteration, depth, output_folder)

                #-> craft dataset with selected variables
                input_file = dataset_preprocessing.craft_selected_variable_dataset(input_file, feature_file, output_folder)

                ## Follow with picker
                #-> default parameters
                min_features = 10
                step = 1
                feature_file = output_folder+folder_separator+"picker_log"+folder_separator+"picker_selected_features.csv"

                #-> run picker
                fs_picker.run_picker(input_file, output_folder, min_features, step)

                #-> generate graphics
                fs_picker.plot_acc(output_folder)

                #-> save best features
                fs_picker.hunt_best_conf(output_folder)

                #-> craft dataset with selected variables
                input_file = dataset_preprocessing.craft_selected_variable_dataset(input_file, feature_file, output_folder)

                #-> update workflow parameters
                picker_used = True
                picker_input_file = input_file


        #-> deal with classification
        elif(action == "clf"):
            if(algorithm == "lda"):

                #-> run lda
                clf_lda.run_lda_classifier(input_file, output_folder)


            if(algorithm == "rf"):

                #-> run random forest
                clf_rf.run_rf_classifier(input_file, output_folder)

            if(algorithm == "logistic"):

                #-> run logistic
                clf_logistic.run_logistic_regression(input_file, output_folder)

        #-> deal with annotation
        elif(action == "annotation"):

            if(algorithm == "KEGG-2016"):

                if(boruta_used and not picker_used):
                    annotation_runner.run_annotation(boruta_input_file, output_folder)
                elif(not boruta_used and picker_used):
                    annotation_runner.run_annotation(picker_input_file, output_folder)
                elif(boruta_used and picker_used):
                    print("[!][ANNOTATION] => annotation for all fs technique not implemented yet")
                    print("[!][ANNOTATION] => can't run annotation")
                elif(not boruta_used and not picker_used):
                    annotation_runner.run_annotation(input_file, output_folder)

            if(algorithm == "REACTOME"):

                if(boruta_used and not picker_used):
                    annotation_runner.run_reactome_annotation(boruta_input_file, output_folder)
                elif(not boruta_used and picker_used):
                    annotation_runner.run_reactome_annotation(picker_input_file, output_folder)
                elif(boruta_used and picker_used):
                    print("[!][ANNOTATION] => annotation for all fs technique not implemented yet")
                    print("[!][ANNOTATION] => can't run annotation")
                elif(not boruta_used and not picker_used):
                    annotation_runner.run_reactome_annotation(input_file, output_folder)

        #-> deal PCA
        if(action == "pca"):
            if(algorithm == "all"):
                display_data.run_pca(input_file, output_folder)
            if(algorithm == "selected"):
                if(boruta_used and not picker_used):
                    display_data.run_pca(boruta_input_file, output_folder)
                elif(picker_used):
                    display_data.run_pca(picker_input_file, output_folder)

        #-> deal with display
        if(action == "display"):
            if(algorithm == "string"):
                if(boruta_used and not picker_used):
                    feature_file = output_folder+folder_separator+"boruta_log"+folder_separator+"boruta_selected_features.csv"
                    network_analysis.run_string_analysis(feature_file, output_folder)
                elif(picker_used):
                    feature_file = output_folder+folder_separator+"picker_log"+folder_separator+"picker_selected_features.csv"
                    network_analysis.run_string_analysis(feature_file, output_folder)
            if(algorithm == "heatmap"):
                if(boruta_used and not picker_used):
                    display_data.craft_heatmap(boruta_input_file, output_folder)
                elif(picker_used):
                    display_data.craft_heatmap(picker_input_file, output_folder)





def run_instruction_iterative_mode(instruction_list, input_file, output_folder):
    """
    TO TEST
    """

    ## importation
    import os
    import pandas as pd

    ## parameters
    acc_check = True
    acc_limit = instruction_list[1]
    cmpt_iteration = 0
    target_acc_file_list = [
        "rf_log/rf_evaluation.log",
        "lda_log/lda_evaluation.log",
        "logistic_log/logistic_evaluation.log"
    ]

    ## check fs process
    if("fs_boruta-picker" in instruction_list[0] or "fs_picker" in instruction_list[0]):
        feature_file = "picker_log/picker_selected_features.csv"

    ## init loop
    while(acc_check):

        #-> create output sub folder
        sub_folder = output_folder+"/iterative_mining_"+str(cmpt_iteration)
        os.mkdir(sub_folder)

        #-> run with instruction
        run_instruction(instruction_list[0], input_file, sub_folder)

        #-> control acc
        acc_check = False
        for tf in target_acc_file_list:
            if(os.path.isfile(sub_folder+"/"+tf)):
                acc = pd.read_csv(sub_folder+"/"+tf)
                acc = list(acc['ACC'])
                acc = float(acc[0])
                if(acc >= acc_limit):
                    acc_check = True

        if(acc_check):

            #-> update iteration cmpt
            cmpt_iteration +=1

            #-> create new input file
            if(os.path.isfile(sub_folder+"/"+feature_file)):
                input_data = pd.read_csv(input_file)
                feature_drop_list =  pd.read_csv(sub_folder+"/"+feature_file)
                feature_drop_list = list(feature_drop_list["FEATURE"])
                feature_to_keep = []
                for k in list(input_data.keys()):
                    if(k not in feature_drop_list):
                        feature_to_keep.append(k)
                input_data = input_data[feature_to_keep]
                input_file = sub_folder+"/dataset_iteration_"+str(cmpt_iteration)+".csv"
                input_data.to_csv(input_file, index=False)







def run(input_file, output_folder, action):
    """
    """

    ## importation
    import os
    import report_generator

    ## parameters

    ## check if input file exist
    if(not os.path.isfile(input_file) and action != "annotation"):
        print("[!] Can't find "+str(input_file))
        return -1

    ## check if output folder exist, if not create it
    if(not os.path.isdir(output_folder)):
        os.mkdir(output_folder)

    ## hunt action
    if(action == "brute"):
        #-> run feature selection
        pass

        #-> run classification

        #-> create report
    elif(action == "clf"):
        run_classification(input_file, output_folder)
        report_generator.create_report(input_file, output_folder)
    elif(action == "fs"):
        run_feature_selection(input_file)
        report_generator.create_report(input_file, output_folder)
    elif(os.path.isfile(action)):
        instruction_list = parse_configuration_file(action)
        if(instruction_list[1] == "NA"):
            run_instruction(instruction_list[0], input_file, output_folder)
            report_generator.create_report(input_file, output_folder)
        else:
            run_instruction_iterative_mode(instruction_list, input_file, output_folder)
    elif(action == "annotation"):
        run_annotation(output_folder)


    ## create report
    #report_generator.create_report(input_file, output_folder)









def display_help():
    """
    """

    print("""
        Work in Progress [PLACEHOLDER]


        Idea:

            config :
                load a txt config file to pick a fs and a clf
                -> load this file as an alternative argument for the action arg

            report generator :
                craft a pdf document from the image and log files generated


        To implement
            fs:
                -boruta -> ok
                -LDA picker -> ok
            -clf:
                -lda -> ok
                -ann
                -xgboosted tree
                -dpix
                -random forest
                -svm
                -logistic cascade

        possible actions :
            -fs : feature selection
            -clf : classifier
            -brute : let me do the work for you

            TODO : add annotation action
    """)





##------##
## MAIN ########################################################################
##------##
if __name__=='__main__':

    ## importation
    import sys
    import getopt
    from colorama import init
    init(strip=not sys.stdout.isatty())
    from termcolor import cprint
    from pyfiglet import figlet_format

    ## catch arguments
    argv = sys.argv[1:]

    ## parse arguments
    input_file = ''
    output_folder = ''
    action = ''
    try:
       opts, args = getopt.getopt(argv,"hi:o:a:",["ifile=","ofolder=", "action="])
    except getopt.GetoptError:
       display_help()
       sys.exit(2)
    for opt, arg in opts:
       if opt in ('-h', '--help'):
           display_help()
           sys.exit()
       elif opt in ("-i", "--ifle"):
          input_file = arg
       elif opt in ("-o", "--ofolder"):
           output_folder = arg
       elif opt in ("-a", "--action"):
           action = arg


    ## display cool banner
    text="MURLOC - Manage Unnecessary Recurrent & Long & Obscure Computation"
    cprint(figlet_format(text, font="standard"), "blue")

    ## check that all arguments are present
    if(input_file == '' and action != "annotation"):
        print("[!] No input file detected")
        print("[!] Use -h or --help options to get more informations")
        sys.exit()
    if(output_folder == ''):
        print("[!] No output folder detected")
        print("[!] Use -h or --help options to get more informations")
        sys.exit()
    if(action == ''):
        print("[!] No action detected")
        print("[!] Use -h or --help options to get more informations")
        sys.exit()

    ## perform run
    run(input_file, output_folder, action)
