"""
Lógica de negocio de la demo de "Alertas tempranas en una sola vista por
cliente" -- separada de la interfaz para que se pueda probar sola, sin
necesidad de tener Streamlit instalado.
"""

from pathlib import Path

import pandas as pd

ORDEN_PERFILES = ["Bajo", "Medio", "Alto", "Rechazado"]

BASES = {
    "Alertas Empresas": "alertas_empresas.csv",
    "Alertas PES": "alertas_pes.csv",
    "Alertas Consumo": "alertas_consumo.csv",
}


def cargar_bases(carpeta: str = ".") -> dict[str, pd.DataFrame]:
    """Carga las 3 bases desde CSV. Cambia esto por tu fuente real
    (Excel, base de datos, etc.) cuando conectes datos reales."""
    carpeta_path = Path(carpeta)
    return {
        nombre: pd.read_csv(carpeta_path / archivo, dtype=str)
        for nombre, archivo in BASES.items()
    }


def buscar_cliente(termino: str, bases: dict[str, pd.DataFrame]) -> list[dict]:
    """Busca por cédula (coincidencia exacta) o nombre (coincidencia parcial)
    en las 3 bases. Como los segmentos son excluyentes, lo normal es
    encontrar como máximo 1 resultado."""
    termino = termino.strip().lower()
    if not termino:
        return []

    resultados = []
    for nombre_base, df in bases.items():
        coincide = df["cedula"].str.lower().eq(termino) | df["nombre"].str.lower().str.contains(
            termino, na=False, regex=False
        )
        for _, fila in df[coincide].iterrows():
            resultados.append({"base": nombre_base, **fila.to_dict()})
    return resultados


def agrupar_por_cedula(resultados: list[dict]) -> dict[str, list[dict]]:
    """Agrupa los resultados de buscar_cliente() por cédula.

    Una búsqueda por nombre puede traer varios CLIENTES distintos (nombres
    parecidos): eso es normal, no un error. Lo que sí sería un error de
    segmentación es que la MISMA cédula aparezca en más de una base --
    eso es lo que hay que revisar."""
    grupos: dict[str, list[dict]] = {}
    for r in resultados:
        grupos.setdefault(r["cedula"], []).append(r)
    return grupos


def estabilidad(perfil: str, perfil_anterior: str) -> str:
    """Compara el perfil actual contra el del corte anterior."""
    if perfil == perfil_anterior:
        return "Estable vs. mes anterior"
    subio = ORDEN_PERFILES.index(perfil) > ORDEN_PERFILES.index(perfil_anterior)
    verbo = "Subió" if subio else "Bajó"
    return f"{verbo} de {perfil_anterior} a {perfil}"


ID_MASTER_LARGO = 14


def id_valido(id_cliente: str) -> bool:
    """El ID de la base master debe ser numérico de 14 dígitos."""
    id_cliente = id_cliente.strip()
    return id_cliente.isdigit() and len(id_cliente) == ID_MASTER_LARGO


def cargar_base_master(carpeta: str = ".") -> pd.DataFrame:
    """Carga la base master (historial de todas las empresas: cartera total
    y días de mora por corte). Cambia esto por tu fuente real cuando
    conectes datos reales."""
    df = pd.read_csv(Path(carpeta) / "base_master.csv", dtype={"id": str})
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def historial_cliente(id_cliente: str, base_master: pd.DataFrame) -> pd.DataFrame:
    """Serie histórica (ordenada por fecha) de un cliente, por su ID de 14
    dígitos."""
    id_cliente = id_cliente.strip()
    return base_master[base_master["id"] == id_cliente].sort_values("fecha")
