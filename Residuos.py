import pandas as pd
import numpy as np

# LIMPIEZA

df = pd.read_csv("1. DataSet Generación Anual de residuos sólidos domiciliario_Distrital_2014_2024.csv", encoding='latin-1', sep=';')

# Convertir columnas numéricas
df["POB_TOTAL"] = pd.to_numeric(df["POB_TOTAL"], errors='coerce')
df["POB_URBANA"] = pd.to_numeric(df["POB_URBANA"], errors='coerce')
df["POB_RURAL"] = pd.to_numeric(df["POB_RURAL"], errors='coerce')
df["GPC_DOM"] = pd.to_numeric(df["GPC_DOM"], errors='coerce')
df["QRESIDUOS_DOM"] = pd.to_numeric(df["QRESIDUOS_DOM"], errors='coerce')
df["PERIODO"] = pd.to_numeric(df["PERIODO"], errors='coerce')

print(df.head())
print(df.info())
print(df.isnull().sum())
# ANALISIS EXPLORATORIO


# Estadísticas descriptivas
print(df.describe())

# Revisar años disponibles
print(df["PERIODO"].unique())

# Generación total por año
generacion_anual = df.groupby("PERIODO")["QRESIDUOS_DOM"].sum()
print(generacion_anual)

# Generación total por departamento
generacion_departamento = df.groupby("DEPARTAMENTO")["QRESIDUOS_DOM"].sum().sort_values(ascending=False)
print(generacion_departamento)

# Generación promedio por región natural
residuos_por_region = (
    df.groupby("REG_NAT")["QRESIDUOS_DOM"]
    .mean()
    .sort_values(ascending=False)
)

print(residuos_por_region)



#HENRY
# VARIABLES DERIVADAS

# Ordenar por distrito y año
df = df.sort_values(["UBIGEO", "PERIODO"])

# Porcentaje de población urbana
df["porc_urbana"] = df["POB_URBANA"] / df["POB_TOTAL"]

# Porcentaje de población rural
df["porc_rural"] = df["POB_RURAL"] / df["POB_TOTAL"]


#ANGIE
# VARIABLES DERIVADAS - SEGUNDA PARTE

# Residuos por habitante urbano al año en kg
df["residuos_kg_hab_anual"] = (df["QRESIDUOS_DOM"] * 1000) / df["POB_URBANA"]

# Variación anual de generación de residuos por distrito
df["variacion_anual_residuos"] = df.groupby("UBIGEO")["QRESIDUOS_DOM"].pct_change()

# Promedio histórico de generación por distrito
df["promedio_residuos_distrito"] = df.groupby("UBIGEO")["QRESIDUOS_DOM"].transform("mean")

# Categoría de generación
df["categoria_generacion"] = pd.qcut(
    df["QRESIDUOS_DOM"],
    q=3,
    labels=["Baja", "Media", "Alta"]
)

print(df.head())
