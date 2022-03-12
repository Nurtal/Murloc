

def create_report(output_folder):
    """
    """

    ## importation
    from fpdf import FPDF
    import os

    ## parameters
    folder_separator = "/"

    ## check if we are running on a fucking windows machine
    if(os.name == 'nt'):
        folder_separator = "\\"

    ## define pdf output file name
    report_file_name = output_folder+folder_separator+"report.pdf"

    ## init pdf
    class PDF(FPDF):
        pass

    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.output(report_file_name,'F')

    ## hunt feature selection data
    #-> get number of original features
    #-> get number of feature selected by boruta (if file exist)

    ## hunt classification data
    #-> deal with LDA (test if lda results are presents)
    #-> extract acc
    #-> extract confusion matrix

    ## sign
    pdf.set_author('Murloc')





create_report("test")
