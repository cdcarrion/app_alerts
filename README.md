# Demo: Alertas tempranas por cliente + serie histórica

**Pestaña 1 — Alertas por cliente**
Busca una cédula o nombre y muestra el perfil de riesgo (Bajo / Medio / Alto /
Rechazado) en las 3 bases -- Empresas, PES, Consumo -- junto con su
estabilidad frente al corte anterior.

**Pestaña 2 — Serie histórica**
Con el ID de 14 dígitos de un cliente, grafica su historial mensual de
cartera total y días de mora (base master, todas las empresas).

## Cómo correrla

```
pip install -r requirements.txt
python generar_datos_demo.py   # genera los CSV de ejemplo (datos ficticios)
streamlit run app.py           # abre la app en el navegador
```

Al generar los datos, la consola imprime 3 IDs de ejemplo (14 dígitos) que
puedes pegar en la pestaña "Serie histórica" para probarla.

## Archivos

- `generar_datos_demo.py` — crea las bases de ejemplo: 3 de alertas y la
  base master. Cámbialo o bórralo cuando conectes tus bases reales.
- `logica.py` — la búsqueda, el historial y las reglas de negocio, sin
  depender de Streamlit (se puede probar sola).
- `app.py` — la interfaz web (Streamlit), con las 2 pestañas.

## Para usar tus datos reales

**Alertas** (`alertas_empresas.csv`, `alertas_pes.csv`, `alertas_consumo.csv`):
columnas `cedula`, `nombre`, `perfil`, `perfil_anterior`, `corte` (agrega
`sector` en PES o `saldo_pasivo` en Consumo si quieres que se muestren).

**Base master** (`base_master.csv`): columnas `id` (14 dígitos, texto),
`fecha`, `cartera_total`, `dias_mora` -- una fila por cliente y corte.
