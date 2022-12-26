# importation
from . import data_generator

def craft_test_material():
    """
    """

    # parameters
    config_file_name = "config/test_config.conf"

    # generate test data
    data_generator.generate_test_dataset()

    # display information
    print(f"[TEST] >> tests/data/test_dataset.csv crafted")

    # generate test conf file
    config_data = open(config_file_name, "w")
    config_data.write("fs_boruta-picker\n")
    config_data.write("clf_rf\n")
    config_data.write("clf_lda\n")
    config_data.write("clf_logistic\n")
    config_data.write("clf_xgb\n")
    config_data.write("annotation_KEGG-2016\n")
    config_data.write("annotation_REACTOME\n")
    config_data.write("introspection\n")
    config_data.close()

    # display information
    print(f"[TEST] >> {config_file_name} crafted")

