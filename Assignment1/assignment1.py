import multiprocessing as mp
from pathlib import Path
import argparse as ap
import Bio.Entrez


""" 
requirements: for provided PubMed ID download 10 articles which are cited by the provided article
"""
# define E-Mail address
Bio.Entrez.email = "chiara.becht@web.de"

# set output path
cwd = Path(__file__).parent.absolute()
out_dir_p = cwd / 'output'

def output_directory(out_dir_p):
    """
    Create the output directory in the same directory this script is located
    """
    if not(out_dir_p.exists()):
            out_dir_p.mkdir(parents=True, exist_ok=False)


def download_articles_references(pmid):
    """
    For a given pubmed id download the references from NCBI using Bio.Entrez library
    """
    
    results = Bio.Entrez.read(Bio.Entrez.elink(dbfrom="pubmed",
                                   db="pmc",
                                   LinkName="pubmed_pmc_refs",
                                   id=pmid,
                                   api_key='c4507f85c841d7430a209603112dba418607'))
    references = [f'{link["Id"]}' for link in results[0]["LinkSetDb"][0]["Link"]]
    return references

def download_10_referenced_articles(pmid):
    """
    Download the articles based on given pubmed ID's
    """
    Bio.Entrez.email = "chiara.becht@web.de"
    handle = Bio.Entrez.efetch(db="pmc", id=pmid, rettype="XML", retmode="text",
                           api_key='c4507f85c841d7430a209603112dba418607')
    #with open(f'output/{pmid}.xml', 'wb') as file:
    with open(f'{out_dir_p}/{pmid}.xml', 'wb') as file:
        file.write(handle.read())
    

if __name__ == "__main__":
    # handle commandline input
    argparser = ap.ArgumentParser(description="Script that downloads (default) 10 articles referenced by the given PubMed ID concurrently.")
    argparser.add_argument("-n", action="store",
                           dest="n", required=False, type=int,
                           help="Number of references to download concurrently.")
    argparser.add_argument("pubmed_id", action="store", type=str, nargs=1, help="Pubmed ID of the article to harvest for references to download.")
    args = argparser.parse_args()
    print("Getting: ", args.pubmed_id)
    pmid = str(args.pubmed_id)

    # create output directory
    output_directory(out_dir_p)

    # get reference list
    refs = download_articles_references(pmid)
    print(refs)

    # set up mulitprocessing task to download 10 referenced articles concurrently
    cpus = mp.cpu_count()
    if cpus > 10:
        cpus == 10
    with mp.Pool(cpus) as pool:
        results = pool.map(download_10_referenced_articles, refs[0:10])
    