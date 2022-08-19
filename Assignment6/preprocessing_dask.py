from dask import dataframe as dd

df = dd.read_table('/students/2021-2022/master/Chiara_DSLS/output/mapping_result.csv', names=['read_id', 'reference'], na_values= '*')
#print(df.compute())
print(df.head())
print(df.tail())

df[['GenInfo_ID', 'gi_number', 'ref', 'NCBI_ID', 'empty']] = df['reference'].str.split(pat = '|', n = 4, expand = True)
df = df.drop(columns = ['reference', 'empty'])
print(df.head())

# calculate some summary statistics
# 1.) number of reads
num_reads = len(df.read_id)
print('total number of reads', len(df.read_id))

# 2.) number of mapped reads
mapped_reads = df.NCBI_ID.notnull().sum().compute()
print('total mapped reads', df.NCBI_ID.notnull().sum().compute())

# 3.) mapping rate
mapping_rate = round(mapped_reads/num_reads, 3)
print('mapping rate', mapping_rate)

# 4.) unique NCBI accession identifier (NC_	Genomic	Complete genomic molecule, usually reference assembly) 
# https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
unique_refs = df.NCBI_ID.nunique().compute()
print('unique reference identifiers', unique_refs)

# write those into a dataframe which will be wrote to csv, to keep track of the attempts per parameter setting


# create a list with NCBI accession numbers to query the KEGG pathway database
NCBI_IDs = df.NCBI_ID.dropna()
print(NCBI_IDs.compute(), len(NCBI_IDs))


# convert NCBI accession numbers into KEGG identifiers
#from Bio.KEGG import REST

#REST.kegg_conv('pathway', NCBI_IDs) #'org'
#h = REST.kegg_conv("eco", "ncbi-geneid")
#print(h.head())
#h = REST.kegg_conv("pathway", "ncbi-geneid:947465")
#print(h)
from urllib import request
#h = request.urlopen('https://rest.kegg.jp/conv/genes/ncbi-geneid:947465')
#print(h)
html = request.urlopen('https://rest.kegg.jp/conv/genes/ncbi-geneid:387825439').read() #947465
print(html)

#htmll = request.urlopen('https://rest.kegg.jp/link/pathway/eco:b0074').read()
#print(htmll)