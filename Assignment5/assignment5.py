from audioop import avg
import pyspark
from pyspark.sql import Row
from pyspark.sql.functions import desc, explode, split,col
import argparse as ap
import csv

sc = pyspark.SparkContext('local[16]')

#path  = '/data/dataprocessing/interproscan/all_bacilli.tsv'
argparser = ap.ArgumentParser(description="Collect path to the interpro output file, that shall be analysed")
argparser.add_argument("filepath", type = str, action="store", help = "filepath to interpro output file")
args = argparser.parse_args()
path = args.filepath
print(path)

df = pyspark.SQLContext(sc).read.csv(path, sep=r'\t', header=False, inferSchema= True)

df = df.withColumnRenamed('_c0', 'Protein_accession').withColumnRenamed('_c1', 'MD5').withColumnRenamed('_c2', 'Seq_len').withColumnRenamed('_c3', 'Analysis')\
    .withColumnRenamed('_c4', 'Signature_accession').withColumnRenamed('_c5', 'Signature_description').withColumnRenamed('_c6', 'Start')\
        .withColumnRenamed('_c7', 'Stop').withColumnRenamed('_c8', 'Score').withColumnRenamed('_c9', 'Status').withColumnRenamed('_c10', 'Date')\
            .withColumnRenamed('_c11', 'InterPro_accession').withColumnRenamed('_c12', 'InterPro_discription').withColumnRenamed('_c13', 'GO_annotations')\
                .withColumnRenamed('_c14', 'Pathways')




# How many distinct protein annotations are found in the dataset? I.e. how many distinc InterPRO numbers are there?
q1 = df.filter(df.InterPro_accession != '-').groupBy('InterPro_accession').count().count()
print('QUESTION1:', q1)
q1_ex = str(df.groupby('InterPro_accession').count()._sc._jvm.PythonSQLUtils.explainString(df.groupby('InterPro_accession').count()._jdf.queryExecution(),'simple'))

# How many annotations does a protein have on average?
q2 = df.filter(df.InterPro_accession != '-').groupBy('InterPro_accession').count().agg({'count': 'avg'})
print('QUESTION2:', q2)
q2_ex = str(df.groupby('InterPro_accession').count().agg({'count':'avg'})._sc._jvm.PythonSQLUtils.explainString(df.groupby('InterPro_accession').count().agg({'count': 'avg'})._jdf.queryExecution(),'simple'))


# What is the most common GO Term found?
go_terms = []
for i in df.filter(df.GO_annotations != '-').select('GO_annotations').collect():
    go_terms.extend(i[0].split("|"))

sqlContext = pyspark.SQLContext(sc)
rdd = sc.parallelize(go_terms)
ppl = rdd.map(lambda x: Row(name=x))
DF_go_terms = sqlContext.createDataFrame(ppl)

q3 = []
for i in DF_go_terms.groupby('name').count().sort(desc('count')).select('name').head(1):
    q3.append(i[0])
explain_3 = DF_go_terms.groupby('name').count().sort(desc('count'))
q3_ex = str(explain_3._sc._jvm.PythonSQLUtils.explainString(explain_3._jdf.queryExecution(),'simple'))
print('QUESTION3', q3)

# What is the average size of an InterPRO feature found in the dataset?
df = df.withColumn('Feature_size', df.Stop - df.Start)
q4 = df.agg({'Feature_size': 'avg'})
q4_ex = str(q4._sc._jvm.PythonSQLUtils.explainString(q4._jdf.queryExecution(),'simple'))
print('QUESTION4', q4)

# What is the top 10 most common InterPRO features?
q5 = []
for i in df.filter(df.InterPro_accession != '-').groupby('InterPro_accession').count().sort(desc('count')).select('InterPro_accession').head(10):
    q5.append(i[0])
explain_5 = df.filter(df.InterPro_accession != '-').groupby('InterPro_accession').count().sort(desc('count'))
q5_ex = str(explain_5._sc._jvm.PythonSQLUtils.explainString(explain_5._jdf.queryExecution(),'simple'))
print('QUESTION5', explain_5)

# If you select InterPRO features that are almost the same size (within 90-100%) as the protein itself, what is the top10 then?
q6 = []
for i in df.filter(df.InterPro_accession != '-').filter(df.Feature_size / df.Seq_len > 0.9).sort(desc('Feature_size')).select('InterPro_accession').head(10):
    q6.append(i[0])
explain_6 =df.filter(df.InterPro_accession != '-').filter(df.Feature_size / df.Seq_len > 0.9).sort(desc('Feature_size'))
q6_ex = str(explain_6._sc._jvm.PythonSQLUtils.explainString(explain_6._jdf.queryExecution(),'simple'))
print('QUESTION6', explain_6)

# If you look at those features which also have textual annotation, what is the top 10 most common word found in that annotation?
q7 = []
for i in df.filter(df.InterPro_discription != '-').withColumn('word',explode(split(col('InterPro_discription'), ' '))).groupby('word').count().sort(desc('count')).head(10):
    q7.append(i[0])
explain_7 = df.filter(df.InterPro_discription != '-').withColumn('word',explode(split(col('InterPro_discription'), ' '))).groupby('word').count().sort(desc('count'))
q7_ex = str(explain_7._sc._jvm.PythonSQLUtils.explainString(explain_7._jdf.queryExecution(),'simple'))

# And the top 10 least common?
q8 = []
for i in df.filter(df.InterPro_discription != '-').withColumn('word',explode(split(col('InterPro_discription'), ' '))).groupby('word').count().sort('count', descending ='False').head(10):
    q8.append(i[0])
explain_8 =df.filter(df.InterPro_discription != '-').withColumn('word',explode(split(col('InterPro_discription'), ' '))).groupby('word').count()
q8_ex = str(explain_8._sc._jvm.PythonSQLUtils.explainString(explain_8._jdf.queryExecution(),'simple'))


# Combining your answers for Q6 and Q7, what are the 10 most commons words found for the largest InterPRO features?
top_10_inter = df.filter(df.InterPro_discription != '-').filter(df.Feature_size / df.Seq_len > 0.9).sort(desc('Feature_size'))
q9 = []
for i in top_10_inter.filter(top_10_inter.InterPro_discription != '-').withColumn('word',explode(split(col('InterPro_discription'), ' '))).groupby('word').count().sort(desc('count')).head(10):
     q9.append(i[0])

explain_9 = top_10_inter.filter(top_10_inter.InterPro_discription != '-').withColumn('word',explode(split(col('InterPro_discription'), ' '))).groupby('word').count().sort(desc('count'))
q9_ex = str(explain_9._sc._jvm.PythonSQLUtils.explainString(explain_9._jdf.queryExecution(),'simple'))


# What is the coefficient of correlation ( 𝑅2 ) between the size of the protein and the number of features found?
q10 = df.filter(df.InterPro_accession != '-').groupby(['Protein_accession', 'Seq_len']).count().corr('count', 'Seq_len')
explain_10 =  df.filter(df.InterPro_accession != '-').groupby(['Protein_accession', 'Seq_len']).count()
q10_ex = str(explain_10._sc._jvm.PythonSQLUtils.explainString(explain_10._jdf.queryExecution(),'simple'))


sc.stop()

header = ['Questions', 'Answer', 'explain']
data = [
    [1,q1, q1_ex  ],
    [2,q2,  q2_ex ],
    [3,q3,  q3_ex  ],
    [4,q4,  q4_ex  ],
    [5,q5,  q5_ex  ],
    [6,q6,  q6_ex  ],
    [7,q7,  q7_ex  ],
    [8,q8,  q8_ex  ],
    [9,q9,   q9_ex  ],
    [10,q10,  q10_ex  ]

]

with open('anwsers.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write multiple rows
    writer.writerows(data)