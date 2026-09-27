"""
Demo: Alertas tempranas en una sola vista por cliente + serie histórica de
cartera y mora (base master).

Pestaña 1: busca una cédula o nombre en las 3 bases (Empresas, PES,
Consumo) y muestra el perfil de riesgo y su estabilidad frente al corte
anterior.
Pestaña 2: con el ID de 14 dígitos de un cliente, grafica su historial
mensual de cartera total y días de mora.

Ejecutar:
    streamlit run app.py
"""

import matplotlib.pyplot as plt
import streamlit as st

from logica import (
    agrupar_por_cedula,
    buscar_cliente,
    cargar_base_master,
    cargar_bases,
    estabilidad,
    historial_cliente,
    id_valido,
)

st.set_page_config(page_title="Alertas tempranas", page_icon="🔎", layout="centered")

COLOR_PERFIL = {
    "Bajo": ("#DCF5E3", "#1F7A43"),
    "Medio": ("#FDF3D8", "#8A6100"),
    "Alto": ("#FBE3D0", "#B4530A"),
    "Rechazado": ("#FAD9D9", "#B42318"),
}


@st.cache_data
def _cargar_bases_cacheado():
    return cargar_bases(".")


@st.cache_data
def _cargar_master_cacheado():
    return cargar_base_master(".")


def mostrar_resultado(r: dict) -> None:
    bg, color = COLOR_PERFIL.get(r["perfil"], ("#EEEEEE", "#333333"))
    st.markdown(f"#### {r['base']}")
    st.markdown(
        f"<span style='background:{bg}; color:{color}; padding:6px 18px; "
        f"border-radius:999px; font-weight:600; font-size:16px'>{r['perfil']}</span>",
        unsafe_allow_html=True,
    )
    st.caption(estabilidad(r["perfil"], r["perfil_anterior"]))
    st.write(f"**Nombre:** {r['nombre']}")
    st.write(f"**Cédula:** {r['cedula']}  ·  **Corte:** {r['corte']}")
    if "sector" in r:
        st.write(f"**Sector:** {r['sector']}")
    if "saldo_pasivo" in r:
        st.write(f"**Saldo cuenta pasivo:** {r['saldo_pasivo']}")
    st.divider()


def graficar_historial(hist) -> None:
    fig, ax_cartera = plt.subplots(figsize=(8, 4))

    ax_cartera.plot(
        hist["fecha"], hist["cartera_total"], color="#0B1E3D", marker="o", linewidth=2
    )
    ax_cartera.set_ylabel("Cartera total ($)", color="#0B1E3D")
    ax_cartera.tick_params(axis="y", labelcolor="#0B1E3D")
    ax_cartera.set_xlabel("Corte")

    ax_mora = ax_cartera.twinx()
    ax_mora.plot(
        hist["fecha"],
        hist["dias_mora"],
        color="#B4530A",
        marker="o",
        linewidth=2,
        linestyle="--",
    )
    ax_mora.set_ylabel("Días de mora", color="#B4530A")
    ax_mora.tick_params(axis="y", labelcolor="#B4530A")

    fig.autofmt_xdate()
    fig.tight_layout()
    st.pyplot(fig)


tab_alertas, tab_historico = st.tabs(["🔎 Alertas por cliente", "📈 Serie histórica"])

with tab_alertas:
    st.title("Alertas tempranas por cliente")
    st.caption("Demo ilustrativa — datos generados aleatoriamente, no reales.")

    termino = st.text_input("Cédula o nombre del cliente")
    buscar = st.button("Buscar", type="primary")

    if buscar:
        if not termino:
            st.info("Ingresa una cédula o nombre para buscar.")
        else:
            bases = _cargar_bases_cacheado()
            resultados = buscar_cliente(termino, bases)
            grupos = agrupar_por_cedula(resultados)

            if len(grupos) == 0:
                st.warning("No se encontró el cliente en ninguna de las 3 bases.")
            else:
                if len(grupos) > 1:
                    st.info(
                        f"El nombre coincide con {len(grupos)} clientes distintos. "
                        "Usa la cédula para precisar uno solo."
                    )
                for cedula, matches in grupos.items():
                    if len(matches) > 1:
                        st.error(
                            f"⚠️ La cédula {cedula} aparece en {len(matches)} bases distintas "
                            "(Empresas / PES / Consumo son segmentos excluyentes) — "
                            "revisar la segmentación."
                        )
                    for r in matches:
                        mostrar_resultado(r)

with tab_historico:
    st.title("Serie histórica de cartera y mora")
    st.caption(
        "Base master — historial mensual de todas las empresas. "
        "Demo ilustrativa, no datos reales."
    )

    id_cliente = st.text_input("ID del cliente (14 dígitos)", key="id_master")
    ver = st.button("Ver historial", type="primary")

    if ver:
        if not id_valido(id_cliente):
            st.warning("El ID debe ser numérico y tener exactamente 14 dígitos.")
        else:
            master = _cargar_master_cacheado()
            hist = historial_cliente(id_cliente, master)
            if hist.empty:
                st.warning("No se encontró historial para ese ID.")
            else:
                graficar_historial(hist)
                st.dataframe(
                    hist[["fecha", "cartera_total", "dias_mora"]],
                    hide_index=True,
                    use_container_width=True,
                )
