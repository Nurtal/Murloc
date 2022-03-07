



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
    fs_boruta(input_file, iteration, depth, output_folder)



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
        pass
    elif(action == "fs"):
        run_feature_selection(input_file)









def display_help():
    """
    """

    print("""
        Work in Progress [PLACEHOLDER]

        To implement
            fs:
                -boruta
                -LDA picker
            -clf:
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
