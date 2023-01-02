from Bio import Entrez
from Bio import SeqIO

def query_nbi():
    """
    """
    Entrez.email = "chiara.becht@web.de"
    handle = Entrez.efetch(db='nucleotide',
                                id = '253771435', 
                                rettype = 'gbwithparts', 
                                retmode = 'text', 
                                api_key='c4507f85c841d7430a209603112dba418607')
    gb_obj = SeqIO.read(handle, 'gb')