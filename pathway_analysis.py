import pandas as pd


def compute_mean_expression(data_file, gene_list):
    """compute the mean of a collection of gene (our 'pathway') and generate a box plot
    for each type in 'TARGET' columnd from data_file

    Args:

    Return:

    """

    # parameters
    gene_to_target_to_value = {}
    log_file = "log/compute_mean_expression.log"

    # init log file
    log_data = open(log_file, "w")

    # load data
    df = pd.read_csv(data_file)

    # init structure
    for g in gene_list:
        if g in list(df.keys()):
            gene_to_target_to_value[g] = {}
            for t in list(df["TARGET"]):
                gene_to_target_to_value[g][t] = []
        else:
            log_data.write(f"can't find gene {g} in data file {data_file}\n")

    # load data int structure
    for index, row in df.iterrows():

        # extract target
        target = row["TARGET"]

        # extract gene and value
        for g in gene_to_target_to_value.keys():
            gene_to_target_to_value[g][target].append(row[g])

    # TODO craft figure

    # close log file
    log_data.close()


if __name__ == "__main__":

    # test
    compute_mean_expression()
