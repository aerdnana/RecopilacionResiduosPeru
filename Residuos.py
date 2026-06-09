import pandas as pd

df = pd.read_csv('Dataset.csv', encoding='latin-1')

df = df.dropna() 
df = df.drop_duplicates()  

print(df.head())
print(df.shape)
print(df.columns)