import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# 1. Configuración visual de la web
st.set_page_config(page_title="Próximos Dividendos IBEX 35", layout="wide")
st.title("📅 Próximos Pagos de Dividendos - IBEX 35")
st.write("Listado exclusivo de los dividendos futuros confirmados o pendientes de próxima fecha oficial.")

# Lista oficial de las 35 empresas del IBEX
tickers_ibex = [
    'ANA.MC', 'ACS.MC', 'AENA.MC', 'ALM.MC', 'AMS.MC', 'MTS.MC', 'BKT.MC', 'BBVA.MC',
    'CABK.MC', 'CLNX.MC', 'COL.MC', 'ENG.MC', 'ELE.MC', 'FER.MC', 'FLUI.MC', 'GRLS.MC',
    'IAG.MC', 'IBE.MC', 'ITX.MC', 'IDR.MC', 'LOG.MC', 'MAP.MC', 'MEL.MC', 'MRL.MC',
    'NTGY.MC', 'PLT.MC', 'RED.MC', 'REP.MC', 'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SLR.MC',
    'TEF.MC', 'UNI.MC', 'SCYR.MC'
]

@st.cache_data(ttl=14400) # Se actualiza en segundo plano cada 4 horas
def obtener_proximos_pagos():
    proximos_dividendos = []
    fecha_hoy = datetime.now().date()
    
    for t in tickers_ibex:
        try:
            ticker_obj = yf.Ticker(t)
            nombre = ticker_obj.info.get('longName', t).replace(', S.A.', '').replace('S.A.', '').strip()
            
            # Buscamos en el calendario de eventos futuros de Yahoo
            calendar = ticker_obj.calendar
            ultimo_importe = 0.0
            fecha_pago_dt = None
            estado = "Pendiente de confirmación"
            
            if calendar is not None and 'Dividend Date' in calendar:
                fecha_evento = calendar['Dividend Date']
                if fecha_evento:
                    if isinstance(fecha_evento, (list, tuple)):
                        fecha_evento = fecha_evento[0]
                    
                    # Convertimos a formato fecha para poder comparar si es futura
                    if hasattr(fecha_evento, 'date'):
                        fecha_pago_dt = fecha_evento.date()
                    else:
                        fecha_pago_dt = fecha_evento
                    
                    # SI LA FECHA ES MAYOR O IGUAL A HOY: Es el próximo dividendo
                    if fecha_pago_dt >= fecha_hoy:
                        ultimo_importe = ticker_obj.info.get('dividendRate', 0)
                        estado = "Confirmado / Próximamente"
            
            # Guardamos los resultados con formato limpio
            proximos_dividendos.append({
                "Empresa": nombre,
                "Próximo Dividendo (€)": ultimo_importe if ultimo_importe > 0 else "Por anunciar",
                "Fecha de Cobro": fecha_pago_dt.strftime('%d/%m/%Y') if (fecha_pago_dt and fecha_pago_dt >= fecha_hoy) else "Por anunciar",
                "Estado": estado,
                "_fecha_orden": fecha_pago_dt if (fecha_pago_dt and fecha_pago_dt >= fecha_hoy) else datetime.max.date()
            })
            
        except Exception:
            continue
            
    return pd.DataFrame(proximos_dividendos)

# Animación de carga de datos financieros
with st.spinner("Escaneando el calendario oficial del IBEX 35 en tiempo real..."):
    df_futuro = obtener_proximos_pagos()

st.divider()

# 2. Ordenamos automáticamente para que los pagos más urgentes y cercanos aparezcan arriba
df_filtrado = df_futuro.sort_values(by="_fecha_orden", ascending=True).drop(columns=["_fecha_orden"])

# 3. Dibujar la tabla limpia en tu página web
st.dataframe(
    df_filtrado,
    column_config={
        "Empresa": st.column_config.TextColumn("Empresa", width="medium"),
        "Próximo Dividendo (€)": st.column_config.TextColumn("Importe por Acción", help="Dividendo bruto por acción confirmado para el próximo pago"),
        "Fecha de Cobro": st.column_config.TextColumn("Fecha del Próximo Pago", help="Día en el que se ingresa el dinero en cuenta"),
        "Estado": st.column_config.TextColumn("Estado Oficial")
    },
    hide_index=True,
    use_container_width=True
)
