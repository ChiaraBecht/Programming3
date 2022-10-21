import Bio.Entrez
import json

# create a json file (genbank.json)
genbank_json = 'genbank.json'

def extract_gi_number(mapping_file): ## if time is left over make it a user choice whether gi number or NCBI accession number shall be used
    """
    """
    lines = []
    gi_numbers = []
    with open(mapping_file) as f: # is this correct to do? For process splitting, would it open the file then for all processes?
        for line in f:
            lines.append(line.split('\t')[2]) 

    for line in lines:
        if line.startswith('gi'):
            gi_numbers.append(line.split('|')[1]) # .split('|')[1] filtering for gi number, NCBI accession number would be column 3

# define E-Mail address
Bio.Entrez.email = "chiara.becht@web.de"
#help(Bio.Entrez.efetch)
def download_genbank(gi_number):

    with open(genbank_json) as json_file:
        json_decoded = json.load(genbank_json)
    
    if gi_number in json_decoded.keys():
        print('already queried')
    else:
        handle = Bio.Entrez.efetch(db='nucleotide',id = gi_number, rettype = 'gbwithparts', retmode = 'text', api_key='c4507f85c841d7430a209603112dba418607')
        json_decoded[gi_number] = handle

    with open(json_file, 'w') as json_file:
        json.dump(json_decoded, json_file)
    

def main():
    extract_gi_number(mapping_file='/students/2021-2022/master/Chiara_DSLS/Assignment6/output/alignment.sam')