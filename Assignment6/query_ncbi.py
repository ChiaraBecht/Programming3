from Bio import Entrez
from Bio import SeqIO

def query_ncbi(gi_id):
    """
    Download full genbank records using the NCBI api and store the genbank files.
    :param:
        gi_id: gi identifier of reference genome
    :return:
        download_logging: string indicating whether the download was successful or not
    """
    download_logging = ''
    Entrez.email = "chiara.becht@web.de"
    try:
        handle = Entrez.efetch(db='nucleotide',
                                    id = gi_id, 
                                    rettype = 'gbwithparts', 
                                    retmode = 'text', 
                                    api_key='c4507f85c841d7430a209603112dba418607')
        
        gb_obj = SeqIO.read(handle, 'gb')
        file_name = '/students/2021-2022/master/Chiara_DSLS/Assignment6/genbank_cache/' + gi_id + '.gb'
        SeqIO.write(gb_obj, file_name, 'gb')
        download_logging = 'success'
        return download_logging
    except:
        download_logging = 'failed'
        return download_logging
    

if __name__ == '__main__':
    gi_id = '012345678' #'253771435'
    #out_dir = '/students/2021-2022/master/Chiara_DSLS/Assignment6/genbank_cache/'
    logging = query_ncbi(gi_id = gi_id)
    print(logging)