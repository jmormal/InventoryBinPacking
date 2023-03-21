import pandas as pd

# Read Productos.csv

df_prod = pd.read_csv('datasets/Prov1/Productos.csv')
print(type(df_prod["id_container"][0]))

