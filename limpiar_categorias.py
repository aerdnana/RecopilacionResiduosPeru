from pathlib import Path
import re
import unicodedata

import numpy as np
import pandas as pd


ARCHIVO_ENTRADA = next(Path(".").glob("1. DataSet*.csv"))
ARCHIVO_SALIDA = Path("DataSet_LIMPIO.csv")

DEPARTAMENTOS_ESPERADOS = 24
PROVINCIAS_ESPERADAS = 196
DISTRITOS_UBIGEO_ESPERADOS = 1891

CORRECCIONES_DEPARTAMENTO = {
    "ANCASH": "ANCASH",
    "NNCASH": "ANCASH",
    "APURIMAC": "APURIMAC",
    "APURNMAC": "APURIMAC",
    "HUANUCO": "HUANUCO",
    "HUNNUCO": "HUANUCO",
    "JUNIN": "JUNIN",
    "JUNNN": "JUNIN",
    "SAN MARTIN": "SAN MARTIN",
    "SAN MARTNN": "SAN MARTIN",
    "CALLAO": "LIMA",
}

CORRECCIONES_PROVINCIA = {
    "ASUNCION": "ASUNCION",
    "ASUNCINN": "ASUNCION",
    "CANETE": "CANETE",
    "CARLOS F FITZCARRALD": "CARLOS FERMIN FITZCARRALD",
    "CONCEPCION": "CONCEPCION",
    "CONCEPCINN": "CONCEPCION",
    "DANIEL ALCIDES CARRION": "DANIEL ALCIDES CARRION",
    "DANIEL ALCIDES CARRINN": "DANIEL ALCIDES CARRION",
    "DATEM DEL MARANON": "DATEM DEL MARANON",
    "FERRENAFE": "FERRENAFE",
    "HUANUCO": "HUANUCO",
    "HUNNUCO": "HUANUCO",
    "JUNIN": "JUNIN",
    "JUNNN": "JUNIN",
    "LA CONVENCION": "LA CONVENCION",
    "LA CONVENCINN": "LA CONVENCION",
    "LA UNION": "LA UNION",
    "LA UNINN": "LA UNION",
    "MARANON": "MARANON",
    "MARANNN": "MARANON",
    "NASCA": "NAZCA",
    "PURUS": "PURUS",
    "PURNS": "PURUS",
}


def normalizar_columna(nombre):
    nombre = str(nombre).strip().lower()
    nombre = re.sub(r"\s+", "_", nombre)
    return nombre.replace(".", "")


def quitar_tildes(texto):
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def limpiar_texto(valor):
    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip()
    texto = texto.replace("\ufeff", "")
    texto = texto.replace("Ã‘", "Ñ").replace("Ã±", "Ñ")
    texto = texto.replace("ï¿½", "Ñ").replace("Ï¿½", "Ñ").replace("�", "Ñ")
    texto = texto.upper()
    texto = unicodedata.normalize("NFC", texto)
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"\s+\d+/$", "", texto)
    return texto.strip()


def clave(valor):
    if pd.isna(valor):
        return valor

    texto = quitar_tildes(limpiar_texto(valor))
    texto = texto.replace("Ñ", "N")
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)
    return " ".join(texto.split())


def normalizar_ubigeo(valor):
    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]

    texto = re.sub(r"\D", "", texto)
    return texto.zfill(6) if texto else np.nan


def aplicar_correcciones(serie, correcciones):
    limpio = serie.apply(limpiar_texto)
    claves = limpio.apply(clave)
    return limpio.mask(claves.isin(correcciones), claves.map(correcciones))


def validar_conteo(nombre, obtenido, esperado):
    estado = "OK" if obtenido == esperado else "REVISAR"
    print(f"{estado}: {nombre}: {obtenido} de {esperado}")


def main():
    df = pd.read_csv(ARCHIVO_ENTRADA, encoding="cp1252", sep=";")
    df.columns = [normalizar_columna(col) for col in df.columns]

    columnas_texto = ["reg_nat", "departamento", "provincia", "distrito"]
    for columna in columnas_texto:
        df[columna] = df[columna].apply(limpiar_texto)

    df["ubigeo"] = df["ubigeo"].apply(normalizar_ubigeo)
    df["departamento"] = aplicar_correcciones(df["departamento"], CORRECCIONES_DEPARTAMENTO)
    df["provincia"] = aplicar_correcciones(df["provincia"], CORRECCIONES_PROVINCIA)

    df = df.dropna(subset=["ubigeo", "departamento", "provincia", "distrito"])
    df = df[~df["departamento"].isin(["DEPARTAMENTO", "COLUMNA", "NAN"])]
    df = df[~df["provincia"].isin(["PROVINCIA", "COLUMNA", "NAN"])]
    df = df[~df["distrito"].isin(["DISTRITO", "COLUMNA", "NAN"])]

    columnas_ordenadas = [
        "fecha_corte",
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
        "periodo",
    ]
    columnas_ordenadas = [col for col in columnas_ordenadas if col in df.columns]
    df = df[columnas_ordenadas].sort_values(
        ["departamento", "provincia", "distrito", "periodo"]
    )

    print("RESUMEN DE LIMPIEZA")
    print(f"Archivo origen: {ARCHIVO_ENTRADA}")
    print(f"Registros limpios: {len(df)}")
    validar_conteo("departamentos", df["departamento"].nunique(), DEPARTAMENTOS_ESPERADOS)
    validar_conteo("provincias", df["provincia"].nunique(), PROVINCIAS_ESPERADAS)
    validar_conteo(
        "distritos por ubigeo",
        df["ubigeo"].nunique(),
        DISTRITOS_UBIGEO_ESPERADOS,
    )

    try:
        df.to_csv(ARCHIVO_SALIDA, encoding="utf-8-sig", sep=";", index=False)
        print(f"Archivo guardado: {ARCHIVO_SALIDA}")
    except PermissionError:
        archivo_alterno = ARCHIVO_SALIDA.with_name("DataSet_LIMPIO_actualizado.csv")
        df.to_csv(archivo_alterno, encoding="utf-8-sig", sep=";", index=False)
        print(f"Archivo bloqueado: {ARCHIVO_SALIDA}")
        print(f"Archivo guardado: {archivo_alterno}")


if __name__ == "__main__":
    main()
