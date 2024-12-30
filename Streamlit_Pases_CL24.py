import json
import pandas as pd
import streamlit as st
from mplsoccer import Pitch
import numpy as np

import os

# Título de la aplicación
st.title("Liga MX Clausura 2024 Pass Map")
st.subheader("Visualización de Pases con Análisis de Presión y Efectividad del CL24 de la Liga MX")

# Cambiar el directorio de trabajo
os.chdir(r"d:/VISUAL/STREAMLIT_WORK/CL24/PASES")

# Ahora carga el archivo
df = pd.read_csv('df_pass.csv')

# Filtrar solo los eventos de pase ("Pass") usando el nombre del evento
df = df[df['event_type_name'] == 'Pass'].reset_index(drop=True)

# Eliminar valores NaN de las columnas necesarias
df = df.dropna(subset=['obv_for_net', 'pass_success_probability', 'under_pressure'])

# Configurar sliders para obv_for_net y pass_success_probability
min_obv = df['obv_for_net'].min()
max_obv = df['obv_for_net'].max()
min_psp = df['pass_success_probability'].min()
max_psp = df['pass_success_probability'].max()

st.sidebar.header("Selecciona los rangos de valores")
value_min_obv = st.sidebar.slider("Valor mínimo de obv_for_net", min_value=float(min_obv), max_value=float(max_obv), value=float(min_obv))
value_max_obv = st.sidebar.slider("Valor máximo de obv_for_net", min_value=float(min_obv), max_value=float(max_obv), value=float(max_obv))
value_min_psp = st.sidebar.slider("Valor mínimo de pass_success_probability", min_value=float(min_psp), max_value=float(max_psp), value=float(min_psp))
value_max_psp = st.sidebar.slider("Valor máximo de pass_success_probability", min_value=float(min_psp), max_value=float(max_psp), value=float(max_psp))

# Filtrar los pases dentro de los rangos seleccionados
df_filtered = df[
    (df['obv_for_net'] >= value_min_obv) & (df['obv_for_net'] <= value_max_obv) &
    (df['pass_success_probability'] >= value_min_psp) & (df['pass_success_probability'] <= value_max_psp)
]

# Filtrado interactivo para equipo, jugador y tipo de pase
team = st.selectbox("Selecciona un equipo", df_filtered['team_name'].sort_values().unique(), index=None)
player = st.selectbox("Selecciona un jugador", df_filtered[df_filtered['team_name'] == team]['player_name'].sort_values().unique(), index=None)
pass_type = st.radio("Selecciona el tipo de pase", ["Ambos", "Pases Completos", "Pases Incompletos"])

# Aplicar filtros adicionales (equipo, jugador, tipo de pase)
filtered_all_df = df_filtered[
    (df_filtered['team_name'] == team) &
    (df_filtered['player_name'] == player)
]

if pass_type == "Pases Completos":
    filtered_df = filtered_all_df[filtered_all_df['outcome_name'] == 'Complete']
elif pass_type == "Pases Incompletos":
    filtered_df = filtered_all_df[filtered_all_df['outcome_name'] != 'Complete']
else:
    filtered_df = filtered_all_df

# Calcular estadísticas de pases
total_passes = len(filtered_df)
completed_passes = len(filtered_df[filtered_df['outcome_name'] == 'Complete'])
incomplete_passes = total_passes - completed_passes
under_pressure_passes = len(filtered_df[filtered_df['under_pressure'] == True])
under_pressure_completed = len(filtered_df[(filtered_df['under_pressure'] == True) & (filtered_df['outcome_name'] == 'Complete')])
under_pressure_incomplete = under_pressure_passes - under_pressure_completed
pass_accuracy = (completed_passes / total_passes * 100) if total_passes > 0 else 0

# Mostrar estadísticas
st.markdown(f"""
### Resumen de Pases
- **Pases totales en los rangos seleccionados:** {total_passes}
- **Pases completados:** {completed_passes}
- **Pases incompletos:** {incomplete_passes}
- **Efectividad (%):** {pass_accuracy:.2f}
- **Pases bajo presión:** {under_pressure_passes}
  - **Pases completados bajo presión:** {under_pressure_completed}
  - **Pases incompletos bajo presión:** {under_pressure_incomplete}
""")

# Dibujar el campo de fútbol horizontal usando mplsoccer
pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f0f0f0', line_color='black', half=False)

# Función para graficar los pases con grosor basado en obv_for_net
def plot_passes(df, ax, pitch):
    for _, row in df.iterrows():
        # Calcular el grosor basado en el valor absoluto de obv_for_net
        arrow_width = max(0.5, abs(row['obv_for_net']) * 10)  # Escalar para que el grosor sea significativo
        color = 'blue' if row['outcome_name'] == 'Complete' else 'red'
        pitch.arrows(
            xstart=row['location_x'],
            ystart=row['location_y'],
            xend=row['end_location_x'],
            yend=row['end_location_y'],
            ax=ax,
            color=color,
            width=arrow_width,
            headwidth=5,
            alpha=0.7,
            zorder=2
        )

# Generar automáticamente el mapa de pases
fig, ax = pitch.draw(figsize=(10, 10))
plot_passes(filtered_df, ax, pitch)
st.pyplot(fig)
