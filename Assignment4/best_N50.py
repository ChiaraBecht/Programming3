import pandas as pd
import shutil

df = pd.read_csv('/students/2021-2022/master/Chiara_DSLS/output/kmer_settings.csv', header = None)

kmers = list(df[0].values)
n50 = list(df[1].values)


index = 0 
best_index = 0 
best_n50 = 0
for i in n50:

    if i > best_n50:
        best_index = index
        best_n50 = i
    index += 1
    
best_kmer = kmers[best_index]





original = '/students/2021-2022/master/Chiara_DSLS/output/Chiara_{}/contigs.fa'.format(best_kmer)
target = '/homes/cbecht/programming3/Programming3/Assignment4/output/contig.fa'
csv_path = '/students/2021-2022/master/Chiara_DSLS/output/kmer_settings.csv'
target2 = '/homes/cbecht/programming3/Programming3/Assignment4/output/kmer_settings.csv'

shutil.move(original, target)
shutil.move(csv_path, target2)