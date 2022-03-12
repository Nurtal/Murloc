



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




def parse_configuration_file(config_file):
    """
    Not tested
    read a config file and return the list of extracted instruction

    config file format:

        action-type_algorithm

    """

    ## parameters
    instruction_list = []
    action_to_available_algorithm = {}
    action_to_available_algorithm["fs"] = ["boruta"]
    action_to_available_algorithm["clf"] = ["lda"]

    ## read config file
    config_data = open(config_file, "r")
    for line in config_data:
        line = line.rstrip()
        line_in_array = line.split("_")

        if(len(line_in_array) > 0):
            action_type = line_in_array[0]
            algorithm = line_in_array[1]

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
    return instruction_list




def run_instruction(instruction_list, input_file, output_folder):
    """
    Not tested
    run with a list of instruction
    """

    ## importation
    import fs_boruta
    import clf_lda
    import dataset_preprocessing
    import os

    ## parameters
    folder_separator = "/"

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
                iteration = 300
                depth = 5
                feature_file = output_folder+folder_separator+"boruta_selected_features.csv"

                #-> run boruta
                fs_boruta.run_boruta(input_file, iteration, depth, output_folder)

                #-> craft dataset with selected variables
                input_file = dataset_preprocessing.craft_selected_variable_dataset(input_file, feature_file, output_folder)

        #-> deal with classification
        elif(action == "clf"):
            if(algorithm == "lda"):

                #-> run lda
                clf_lda.run_lda_classifier(input_file, output_folder)









def run(input_file, output_folder, action):
    """
    """

    ## importation
    import os

    ## parameters

    ## check if input file exist
    if(not os.path.isfile(input_file)):
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
    elif(action == "fs"):
        run_feature_selection(input_file)
    elif(os.path.isfile(action)):
        instruction_list = parse_configuration_file(action)
        run_instruction(instruction_list, input_file, output_folder)









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
                -LDA picker
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
    if(input_file == ''):
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
