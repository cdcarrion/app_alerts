"""
Genera bases de ejemplo (ILUSTRATIVAS, no reales) para probar la demo de
"Alertas tempranas en una sola vista por cliente" y la serie histórica de
cartera y mora por cliente (base master).

Las 3 bases de alertas son mutuamente excluyentes: cada cédula aparece en
una sola base (Empresas, PES o Consumo) -- igual que en el negocio real,
donde son segmentos de clientes distintos. La base master es aparte: trae
el historial mensual de TODAS las empresas, identificadas con un ID de
14 dígitos.

Uso:
    python generar_datos_demo.py

Genera: alertas_empresas.csv, alertas_pes.csv, alertas_consumo.csv,
base_master.csv
"""

import random

import pandas as pd

random.seed(42)

PERFILES = ["Bajo", "Medio", "Alto", "Rechazado"]

NOMBRES = [
    "GONZALEZ PEREZ MARIA JOSE",
    "TORRES LOPEZ JUAN CARLOS",
    "VELASCO RUIZ ANA LUCIA",
    "MORALES CASTRO PEDRO PABLO",
    "JIMENEZ VEGA CARLA SOFIA",
    "ROMERO DIAZ LUIS FERNANDO",
    "CASTILLO ORTIZ PAOLA ANDREA",
    "SALAZAR MENA JORGE ANDRES",
    "VARGAS LEON DIANA CAROLINA",
    "HERRERA NUÑEZ CARLOS ALBERTO",
]


def cedula_ficticia(prefijo_base: int, i: int) -> str:
    """Cédula ficticia; el prefijo de base evita que se repita entre bases."""
    return f"{prefijo_base}{i:08d}"


def generar_base(prefijo_base: int, n: int, columnas_extra: dict | None = None) -> pd.DataFrame:
    filas = []
    for i in range(n):
        perfil_anterior = random.choice(PERFILES)
        # la mayoría se mantiene estable; una minoría sube o baja un nivel
        if random.random() < 0.75:
            perfil = perfil_anterior
        else:
            idx = PERFILES.index(perfil_anterior)
            idx = max(0, min(len(PERFILES) - 1, idx + random.choice([-1, 1])))
            perfil = PERFILES[idx]

        fila = {
            "cedula": cedula_ficticia(prefijo_base, i),
            "nombre": f"{random.choice(NOMBRES)} {i}",
            "perfil": perfil,
            "perfil_anterior": perfil_anterior,
            "corte": "2026-08-31",
        }
        if columnas_extra:
            for columna, valores in columnas_extra.items():
                fila[columna] = random.choice(valores)
        filas.append(fila)
    return pd.DataFrame(filas)


def id_ficticio_14(i: int) -> str:
    """ID ficticio de 14 dígitos para la base master."""
    return f"{40000000000000 + i}"


def generar_base_master(n_clientes: int = 15, n_meses: int = 12) -> pd.DataFrame:
    """Historial mensual de cartera total y días de mora por cliente.
    Cada cliente sigue una de 3 tendencias, para tener ejemplos variados
    de estable / en deterioro / en mejora al graficar."""
    fechas = pd.date_range(end="2026-08-31", periods=n_meses, freq="ME")
    filas = []
    for c in range(n_clientes):
        id_cliente = id_ficticio_14(c)
        cartera = random.uniform(80_000, 3_000_000)
        mora = random.choice([0, 0, 0, 5, 15])
        tendencia = random.choice(["estable", "deterioro", "mejora"])
        for fecha in fechas:
            cartera *= 1 + random.uniform(-0.03, 0.03)
            if tendencia == "deterioro":
                mora = max(0, mora + random.uniform(0, 8))
            elif tendencia == "mejora":
                mora = max(0, mora - random.uniform(0, 4))
            else:
                mora = max(0, mora + random.uniform(-3, 3))
            filas.append(
                {
                    "id": id_cliente,
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "cartera_total": round(cartera, 2),
                    "dias_mora": round(mora, 1),
                }
            )
    return pd.DataFrame(filas)


if __name__ == "__main__":
    empresas = generar_base(1, 40)
    pes = generar_base(
        2, 40, {"sector": ["ARROZ", "FARMACÉUTICO", "SECTOR PUBLICO", "MAIZ Y CEREALES"]}
    )
    consumo = generar_base(3, 40, {"saldo_pasivo": [0, 150, 400, 900, 2200]})
    master = generar_base_master()

    empresas.to_csv("alertas_empresas.csv", index=False)
    pes.to_csv("alertas_pes.csv", index=False)
    consumo.to_csv("alertas_consumo.csv", index=False)
    master.to_csv("base_master.csv", index=False)

    print(
        "Listo: alertas_empresas.csv, alertas_pes.csv, alertas_consumo.csv, "
        "base_master.csv"
    )
    print("IDs de ejemplo para probar la serie histórica:")
    print(", ".join(master["id"].unique()[:3]))
