"""
main file for the introspection module
"""
# imoprtation
from . import retriever
from . import expand_sig
from . import data_reforge


def run(work_folder, original_dataset):
    """
    main
    """

    # retrieve target genes
    target_list = retriever.retrieve_from_annotation(work_folder)

    # expand signatures
    signature_to_target = expand_sig.expand_target_list(
            work_folder,
            target_list
    )

    # craft dataset
    for signature in signature_to_target.keys():

        # craft output file name
        ouput_name = f"{work_folder}/introspection/{signature}_data.csv"

        # extract target list
        target_list = signature_to_target[signature]

        # run reforge
        data_reforge.reforge(
            work_folder,
            target_list,
            original_dataset_file,
            output_name
        )

        # TODO p-hacking
        p_hacking.run(
            work_folder,
            output_name
        )

