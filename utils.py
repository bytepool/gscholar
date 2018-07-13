"""
utils.py

Some helper classes and functions like dotdict. 
"""
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__        


def convert_pdf_to_txt(pdf, startpage=None):
    """Convert a pdf file to text and return the text.

    This method requires pdftotext to be installed.

    Parameters
    ----------
    pdf : str
        path to pdf file
    startpage : int, optional
        the first page we try to convert

    Returns
    -------
    str
        the converted text

    """
    if startpage is not None:
        startpageargs = ['-f', str(startpage)]
    else:
        startpageargs = []
    stdout = subprocess.Popen(["pdftotext", "-q"] + startpageargs + [pdf, "-"],
                              stdout=subprocess.PIPE).communicate()[0]
    # python2 and 3
    if not isinstance(stdout, str):
        stdout = stdout.decode()
    return stdout

    
