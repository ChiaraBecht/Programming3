import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('output/timings.txt', header = None, sep = '\t', names = ['cores', 'time'])

plt.plot(df.cores, df.time)
plt.show()
plt.savefig('output/timings.png')
