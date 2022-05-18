


def run():
    """
    """

    ## importation
    import os
    import pandas as pd

    ## parameters
    acc_treshold = 75
    iteration_cmpt = 0
    murlock_path = "/home/bran/Workspace/Murloc/murloc.py"
    input_file = "/home/bran/Workspace/REDSIG/dataset/tractiss_rnaseq_star_RTX_only_W48.csv"
    output_root = "/home/bran/Workspace/REDSIG/RTX_only/iterative_mining_W48"
    output_folder = "/home/bran/Workspace/REDSIG/RTX_only/iterative_mining_W48/murloc_iteration_0"
    action_file = "/home/bran/Workspace/Murloc/tractiss_config.txt"

    ## init log file
    log_file = open(output_root+"/acc_log.csv", "w")
    log_file.write("ITERATION,LDA,RF,LOGISTIC\n")

    ## big loop
    acc_checked = True
    while(acc_checked):

        ## run murlock
        os.system("python3 "+str(murlock_path)+" -i "+str(input_file)+" -o "+str(output_folder)+" -a "+str(action_file))

        ## check results
        #-> define evaluation file
        acc_checked = False
        lda_perf_file = output_folder+"/lda_log/lda_evaluation.log"
        rf_perf_file = output_folder+"/rf_log/rf_evaluation.log"
        logistic_perf_file = output_folder+"/logistic_log/logistic_evaluation.log"

        #-> check lda acc
        eval_data = pd.read_csv(lda_perf_file)
        lda_acc = list(eval_data['ACC'])
        lda_acc = float(lda_acc[0])
        if(lda_acc >= acc_treshold):
            acc_checked = True

        #-> check rf acc
        eval_data = pd.read_csv(rf_perf_file)
        rf_acc = list(eval_data['ACC'])
        rf_acc = float(rf_acc[0])
        if(rf_acc >= acc_treshold):
            acc_checked = True

        #-> check lda acc
        eval_data = pd.read_csv(logistic_perf_file)
        logistic_acc = list(eval_data['ACC'])
        logistic_acc = float(logistic_acc[0])
        if(logistic_acc >= acc_treshold):
            acc_checked = True

        #-> save acc in log file
        log_file.write(str(iteration_cmpt)+","+str(lda_acc)+","+str(rf_acc)+","+str(logistic_acc)+"\n")

        ## craft new dataset
        if(acc_checked):

            #-> update cmpt
            iteration_cmpt +=1

            #-> create new input file
            ##-> get variable to drop
            picker_file = output_folder+"/picker_log/picker_selected_features.csv"
            df_picker = pd.read_csv(picker_file)
            feature_drop_list = list(df_picker['FEATURE'])

            ##-> save new input
            new_input_name = output_root+"/dataset_iteration_"+str(iteration_cmpt)+".csv"
            df_data = pd.read_csv(input_file)
            df_data = df_data.drop(columns=feature_drop_list)
            df_data.to_csv(new_input_name, index=False)

            ##-> update input name
            input_file = new_input_name

            ## update output folder
            output_folder = output_root+"/murloc_iteration_"+str(iteration_cmpt)


    ## close log file
    log_file.close()


run()
