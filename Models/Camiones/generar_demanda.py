import pandas as pd
import random
import os
# Import Products from csv
print("esdf",os.getcwd())
df_prod = pd.read_csv(r"C:\Users\jmormal\PycharmProjects\pythonProject1\Models\Camiones\datasets\Productos.csv")

products = df_prod["i"].unique()
print("products", products)
print(df_prod.Stock)

demanda = []
for i in products:
    for t in range(1,21):
        demanda.append([i,t,int(df_prod.loc[(df_prod["i"]==i),"Stock"].values[0]/3*(0.95+random.random()/10))])

df_demanda = pd.DataFrame(demanda, columns=["i", "t", "Demanda"])
df_demanda.to_csv("datasets\Demanda.csv", index=False)
