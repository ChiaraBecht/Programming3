from Bio import Entrez
from Bio import SeqIO

def query_nbi(gi_id, out_dir):
    """
    """
    Entrez.email = "chiara.becht@web.de"
    handle = Entrez.efetch(db='nucleotide',
                                id = gi_id, 
                                rettype = 'gbwithparts', 
                                retmode = 'text', 
                                api_key='c4507f85c841d7430a209603112dba418607')
    
    gb_obj = SeqIO.read(handle, 'gb')
    file_name = out_dir + '/' + gi_id + '.gb'
    SeqIO.write(gb_obj, file_name, 'gb')
    

if __name__ == '__main__':
    gi_id = '253771435'
    out_dir = '/students/2021-2022/master/Chiara_DSLS/Assignment6/genbank_cache/'
    query_nbi(gi_id = gi_id, out_dir = out_dir)