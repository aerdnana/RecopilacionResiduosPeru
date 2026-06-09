import pandas as pd
import numpy as np

# LIMPIEZA

df = pd.read_csv("1. DataSet Generación Anual de residuos sólidos domiciliario_Distrital_2014_2024.csv", encoding='latin-1', sep=';')

# Visualizar primeras filas
print(df.head())
print(df.info())
print(df.isnull().sum())