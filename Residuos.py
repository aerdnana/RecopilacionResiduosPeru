import pandas as pd
import numpy as np
#-----------------------------------------------------------------------------------------------------
# lib para visualización-----------------------------------------------------------------------
import matplotlib.pyplot as plt
import os


# LIMPIEZA

# Cargar dataset limpio 
df = pd.read_csv("DataSet_LIMPIO.csv", encoding='utf-8', sep=';')


# Información general

print(df.head())
print(df.info())

# Revisar valores nulos
print(df.isnull().sum())
print(df.columns)

# ANALISIS EXPLORATORIO-------------------------------------------------------------------------------------------------


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




# VARIABLES DERIVADAS--------------------------------------------------------------------------------------

# Ordenar por distrito y año
df = df.sort_values(["ubigeo", "periodo"])

# Porcentaje de población urbana
df["porc_urbana"] = np.where(
    df["pob_total"] > 0, #evitar divisiones entre cero
    df["pob_urbana"] / df["pob_total"],
    np.nan
)

# Porcentaje de población rural
df["porc_rural"] = np.where(
    df["pob_total"] > 0, #evitar divisiones entre cero
    df["pob_rural"] / df["pob_total"],
    np.nan
)



# VARIABLES DERIVADAS - SEGUNDA PARTE

# Residuos por habitante urbano al año en kg
df["residuos_kg_hab_anual"] = np.where(
    df["pob_urbana"] > 0,
    (df["qresiduos_dom"] * 1000) / df["pob_urbana"],
    np.nan
)

# Variación anual de generación de residuos por distrito
df["variacion_anual_residuos"] = df.groupby("ubigeo")["qresiduos_dom"].pct_change()
# Reemplazar valores infinitos por NaN cuando la población urbana es cero
df["variacion_anual_residuos"] = df["variacion_anual_residuos"].replace(
    [np.inf, -np.inf],
    np.nan
)

# Promedio histórico de generación por distrito
df["promedio_residuos_distrito"] = df.groupby("ubigeo")["qresiduos_dom"].transform("mean")


# Generación acumulada de residuos por distrito
df["generacion_acumulada"] = df.groupby("ubigeo")["qresiduos_dom"].cumsum()

# Generación acumulada previa
df["generacion_acumulada_previa"] = (df["generacion_acumulada"] - df["qresiduos_dom"])

# Generación total histórica por distrito
df["generacion_total_historica"] = (
    df.groupby("ubigeo")["qresiduos_dom"]
    .transform("sum")
)

# Cambio total de residuos entre el primer y último año disponible por distrito
def calcular_cambio_total(serie):
    serie = serie.dropna()
    serie = serie[serie > 0]

    if len(serie) < 2:
        return np.nan

    return (serie.iloc[-1] - serie.iloc[0]) / serie.iloc[0]

df["cambio_total_residuos"] = (
    df.groupby("ubigeo")["qresiduos_dom"]
    .transform(calcular_cambio_total)
)

# Tendencia de crecimiento según el cambio total
df["tendencia_crecimiento"] = np.select(
    [
        df["cambio_total_residuos"] > 0.05,
        df["cambio_total_residuos"] < -0.05
    ],
    [
        "Creciente",
        "Decreciente"
    ],
    default="Estable"
)

# Cuando no hay datos suficientes
df.loc[
    df["cambio_total_residuos"].isna(),
    "tendencia_crecimiento"
] = "Sin datos suficientes"



# Categoría de generación
df["categoria_generacion"] = pd.qcut(
    df["qresiduos_dom"],
    q=3,
    labels=["Baja", "Media", "Alta"]
)

print(df.head())
print(df["categoria_generacion"].value_counts(dropna=False))


# Verificar las nuevas variables
df[
    [
        "ubigeo",
        "distrito",
        "periodo",
        "qresiduos_dom",
        "variacion_anual_residuos",
        "promedio_residuos_distrito",
        "generacion_acumulada",
        "generacion_acumulada_previa",
        "cambio_total_residuos",
        "tendencia_crecimiento",
        "categoria_generacion"
    ]
].head(20)

# ORDENAR FILAS
df = df.sort_values(["departamento", "provincia", "distrito", "periodo"])

# ORDENAR COLUMNAS
columnas_ordenadas = [
    "fecha_corte",
    "periodo",
    "n_sec",
    "ubigeo",
    "reg_nat",
    "departamento",
    "provincia",
    "distrito",
    "pob_total",
    "pob_urbana",
    "pob_rural",
    "gpc_dom",
    "qresiduos_dom",
    "porc_urbana",
    "porc_rural",
    "residuos_kg_hab_anual",
    "variacion_anual_residuos",
    "promedio_residuos_distrito",
    "generacion_acumulada",
    "generacion_acumulada_previa",
    "generacion_total_historica",
    "cambio_total_residuos",
    "tendencia_crecimiento",
    "categoria_generacion"
]

# Mantener solo columnas existentes
columnas_ordenadas = [col for col in columnas_ordenadas if col in df.columns]

df_ordenado = df[columnas_ordenadas]

df_ordenado = df_ordenado.replace([np.inf, -np.inf], np.nan)

# EXPORTAR A EXCEL
df_ordenado.to_excel(
    "dataset_residuos_limpio_ordenado.xlsx",
    index=False
)

print("Archivo Excel generado correctamente.")


# VISUALIZACIÓN DE DATOS--------------------------------------------------------------------------------------

# Crear carpeta para guardar gráficos
os.makedirs("graficos", exist_ok=True)

# 1. Generación total de residuos por año en millones
generacion_anual = df.groupby("periodo")["qresiduos_dom"].sum()

plt.figure(figsize=(8, 5))
plt.plot(generacion_anual.index, generacion_anual.values, marker="o")
plt.title("Generación total de residuos domiciliarios por año")
plt.xlabel("Año")
plt.ylabel("Residuos domiciliarios generados (millones de toneladas)")
plt.grid(True)
plt.tight_layout()
plt.savefig("graficos/generacion_total_por_anio.png")
plt.close()


# 2. Top 10 departamentos con mayor generación acumulada
top_departamentos = (
    df.groupby("departamento")["qresiduos_dom"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(9, 5))
top_departamentos.sort_values().plot(kind="barh")
plt.title("Top 10 departamentos con mayor generación de residuos")
plt.xlabel("Residuos domiciliarios generados")
plt.ylabel("Departamento")
plt.tight_layout()
plt.savefig("graficos/top_10_departamentos.png")
plt.close()


# 3. Generación promedio por región natural
region_promedio = (
    df.groupby("reg_nat")["qresiduos_dom"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(7, 5))
region_promedio.plot(kind="bar")
plt.title("Generación promedio de residuos por región natural")
plt.xlabel("Región natural")
plt.ylabel("Promedio de residuos domiciliarios")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("graficos/promedio_region_natural.png")
plt.close()


# 4. Distribución de categorías de generación
conteo_categorias = df["categoria_generacion"].value_counts()

plt.figure(figsize=(7, 5))
conteo_categorias.plot(kind="bar")
plt.title("Cantidad de registros por categoría de generación")
plt.xlabel("Categoría")
plt.ylabel("Cantidad de registros distritales-anuales")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("graficos/categorias_generacion.png")
plt.close()


# 5. Relación entre población urbana y residuos generados
plt.figure(figsize=(8, 5))
plt.scatter(df["pob_urbana"], df["qresiduos_dom"], alpha=0.5)
plt.title("Relación entre población urbana y residuos domiciliarios")
plt.xlabel("Población urbana")
plt.ylabel("Residuos domiciliarios generados")
plt.tight_layout()
plt.savefig("graficos/poblacion_urbana_vs_residuos.png")
plt.close()


# 6. Relación entre GPC domiciliaria y residuos generados
df_gpc = df[
    (df["gpc_dom"] > 0) &
    (df["qresiduos_dom"] > 0)
]
plt.figure(figsize=(8, 5))
plt.scatter(df_gpc["gpc_dom"], df_gpc["qresiduos_dom"], alpha=0.4, s=15)
plt.yscale("log") # Escala logarítmica para mejor visualización
plt.title("Relación entre GPC domiciliaria y residuos generados")
plt.xlabel("GPC domiciliaria")
plt.ylabel("Residuos domiciliarios generados (escala log)")
plt.tight_layout()
plt.savefig("graficos/gpc_vs_residuos.png")
plt.close()


# 7. Top 15 distritos con mayor generación histórica
top_distritos = (
    df.groupby(["departamento", "provincia", "distrito"])["qresiduos_dom"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
)

plt.figure(figsize=(10, 6))
top_distritos.sort_values().plot(kind="barh")
plt.title("Top 15 distritos con mayor generación histórica de residuos")
plt.xlabel("Residuos domiciliarios generados")
plt.ylabel("Distrito")
plt.tight_layout()
plt.savefig("graficos/top_15_distritos.png")
plt.close()


# 8. Distribución del cambio total de residuos
# Dataset único por distrito para analizar cambio total
df_cambio = df[
    [
        "ubigeo",
        "departamento",
        "provincia",
        "distrito",
        "cambio_total_residuos",
        "tendencia_crecimiento"
    ]
].drop_duplicates(subset=["ubigeo"])

df_cambio = df_cambio.dropna(subset=["cambio_total_residuos"])

# Revisar resumen estadístico
print(df_cambio["cambio_total_residuos"].describe())

# Filtrar valores extremos usando percentiles
limite_inferior = df_cambio["cambio_total_residuos"].quantile(0.01)
limite_superior = df_cambio["cambio_total_residuos"].quantile(0.99)

df_cambio_filtrado = df_cambio[
    (df_cambio["cambio_total_residuos"] >= limite_inferior) &
    (df_cambio["cambio_total_residuos"] <= limite_superior)
]

# Graficar en porcentaje
plt.figure(figsize=(8, 5))
plt.hist(df_cambio_filtrado["cambio_total_residuos"] * 100, bins=30)
plt.title("Distribución del cambio total de residuos por distrito")
plt.xlabel("Cambio total de residuos (%)")
plt.ylabel("Cantidad de distritos")
plt.tight_layout()
plt.savefig("graficos/distribucion_cambio_total_corregido.png")
plt.close()


#9. Cantidad de distritos según tendencia de crecimiento
conteo_tendencia = df_cambio["tendencia_crecimiento"].value_counts()

plt.figure(figsize=(7, 5))
conteo_tendencia.plot(kind="bar")
plt.title("Cantidad de distritos según tendencia de crecimiento")
plt.xlabel("Tendencia")
plt.ylabel("Cantidad de distritos")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("graficos/tendencia_crecimiento_distritos.png")
plt.close()