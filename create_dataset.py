import random
import pandas as pd
demanda=[]
for i in range(1,15):
    for t in range(1,14):
        demanda.append([i,t,1000+100*random.randint(1,10)])

df_demanda = pd.DataFrame(demanda, columns=["i", "t", "Demanda"])
df_demanda.to_csv("datasets\Demanda.csv", index=False)