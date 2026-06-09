import pandas as pd
import numpy as np

# LIMPIEZA

df = pd.read_csv("1. DataSet Generación Anual de residuos sólidos domiciliario_Distrital_2014_2024.csv", encoding='latin-1', sep=';')


print(df.head())
print(df.info())
print(df.isnull().sum())
# ANALISIS EXPLORATORIO


# Estadísticas descriptivas
print(df.describe())

# Revisar años disponibles
print(df["periodo"].unique())

# Generación total por año
generacion_anual = df.groupby("periodo")["qresiduos_dom"].sum()
print(generacion_anual)

# Generación total por departamento
generacion_departamento = df.groupby("departamento")["qresiduos_dom"].sum().sort_values(ascending=False)
print(generacion_departamento)

# Generación promedio por región natural
residuos_por_region = (
    df.groupby("reg_nat")["qresiduos_dom"]
    .mean()
    .sort_values(ascending=False)
)

print(residuos_por_region)



#HENRY
# VARIABLES DERIVADAS

# Ordenar por distrito y año
df = df.sort_values(["ubigeo", "periodo"])

# Porcentaje de población urbana
df["porc_urbana"] = df["pob_urbana"] / df["pob_total"]

# Porcentaje de población rural
df["porc_rural"] = df["pob_rural"] / df["pob_total"]
