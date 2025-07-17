# app.py
import streamlit as st
import pandas as pd
import os
import uuid
from closet import Prenda, Closet
from utils import guardar_outfit, outfit_a_str, obtener_temperatura_santiago

API_KEY = "1c1fb8b2336136f7f4c9620ffc1229ee"
INVENTARIO_BASE = "v2_Inventario Seminario.xlsx"

# Generar ID único de sesión si no existe
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Crear archivo personalizado para cada usuario
INVENTARIO_USUARIO = f"inventario_{st.session_state.session_id}.xlsx"

@st.cache_data
def cargar_inventario_base():
    """Carga el inventario base original (solo lectura)"""
    return pd.read_excel(INVENTARIO_BASE)

# Inicializar datos de usuario
if 'df' not in st.session_state:
    # Si es primera vez, copiar base a archivo personalizado
    df_base = cargar_inventario_base()
    df_base.to_excel(INVENTARIO_USUARIO, index=False)
    st.session_state.df = df_base
    
    # Crear closet personalizado
    prendas = [
        Prenda(row["nombre_prenda"], row["tipo"], row["color"], row["temporada"],
        row["estado"], row["ocasion"]) 
        for _, row in df_base.iterrows()
    ]
    st.session_state.closet = Closet(prendas)

# Cargar datos de la sesión actual
df = st.session_state.df
closet = st.session_state.closet

st.title("👗 Clóset Inteligente Personalizado")

opcion = st.sidebar.selectbox("¿Qué quieres hacer?", 
                             ["Recomendar outfit", "Agregar prenda", "Cambiar estado", "Ver favoritos"])

if opcion == "Recomendar outfit":
    try:
        temp = obtener_temperatura_santiago(API_KEY)
        if temp <= 20:
            clima = "invierno"
        elif temp <= 23:
            clima = "otoño"
        elif temp <= 27:
            clima = "primavera"
        else:
            clima = "verano"
        st.success(f"Temperatura actual en Santiago: {temp:.1f}°C → Clima: {clima}")
    except:
        clima = st.selectbox("No se pudo obtener el clima. Selecciónalo manualmente:", 
                            ["otoño", "invierno", "primavera", "verano"])

    ocasion = st.selectbox("¿Ocasión del día?", ["informal", "formal"])

    # Variables para controlar el estado del feedback
    if 'outfit_generado' not in st.session_state:
        st.session_state.outfit_generado = None
    if 'feedback_dado' not in st.session_state:
        st.session_state.feedback_dado = False

    if st.button("Sugerir outfit"):
        outfit = closet.sugerir_outfit(clima, ocasion)
        if outfit:
            st.session_state.outfit_generado = outfit
            st.session_state.feedback_dado = False
        else:
            st.warning("No hay prendas suficientes disponibles para sugerir un outfit.")
            st.session_state.outfit_generado = None

    if st.session_state.outfit_generado:
        outfit = st.session_state.outfit_generado
        partes = []
        for parte in outfit:
            prenda = outfit[parte]
            partes.append(f"**{parte}**: {prenda.nombre} ({prenda.color})")
        st.markdown("### Te sugerimos usar:\n" + "\n".join(partes))
        
        if not st.session_state.feedback_dado:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sí, me gusta 👍"):
                    guardar_outfit(outfit_a_str(outfit, clima, ocasion), True)
                    st.session_state.feedback_dado = True
                    st.success("¡Gracias! Outfit guardado como favorito.")
            with col2:
                if st.button("No, no me gusta 👎"):
                    guardar_outfit(outfit_a_str(outfit, clima, ocasion), False)
                    st.session_state.feedback_dado = True
                    st.info("¡Gracias por tu feedback! Buscaremos mejores opciones.")
        else:
            st.info("Ya has dado tu feedback sobre este outfit.")

elif opcion == "Agregar prenda":
    st.subheader("Agregar nueva prenda a TU clóset")
    nombre = st.text_input("Nombre")
    tipo = st.selectbox("Tipo", ["polera", "pantalonlargo", "short", "falda", "vestido", "abrigo"])
    color = st.text_input("Color")
    temporada = st.selectbox("Temporada", ["otoño", "invierno", "primavera", "verano"])
    estado = st.selectbox("Estado", ["limpio", "sucio"])
    ocasion = st.selectbox("Ocasión", ["formal", "informal"])

    if st.button("Agregar prenda"):
        # Crear nueva fila
        nueva_fila = pd.DataFrame([{
            "nombre_prenda": nombre,
            "tipo": tipo,
            "color": color,
            "temporada": temporada,
            "estado": estado,
            "ocasion": ocasion
        }])
        
        # Actualizar DataFrame en memoria
        nuevo_df = pd.concat([df, nueva_fila], ignore_index=True)
        st.session_state.df = nuevo_df
        
        # Guardar en archivo personalizado
        nuevo_df.to_excel(INVENTARIO_USUARIO, index=False)
        
        # Actualizar closet
        prendas = [
            Prenda(row["nombre_prenda"], row["tipo"], row["color"], row["temporada"],
            row["estado"], row["ocasion"]) 
            for _, row in nuevo_df.iterrows()
        ]
        st.session_state.closet = Closet(prendas)
        
        st.success("¡Prenda agregada a TU clóset personal!")

elif opcion == "Cambiar estado":
    st.subheader("Cambiar estado de una prenda en TU clóset")
    prenda = st.selectbox("Selecciona prenda", df["nombre_prenda"].tolist())
    estado_actual = df[df["nombre_prenda"] == prenda]["estado"].values[0]
    st.text(f"Estado actual: {estado_actual}")
    nuevo_estado = st.radio("Nuevo estado", ["limpio", "sucio"])

    if st.button("Actualizar estado"):
        # Actualizar DataFrame en memoria
        nuevo_df = df.copy()
        nuevo_df.loc[nuevo_df["nombre_prenda"] == prenda, "estado"] = nuevo_estado
        st.session_state.df = nuevo_df
        
        # Guardar en archivo personalizado
        nuevo_df.to_excel(INVENTARIO_USUARIO, index=False)
        
        # Actualizar closet
        prendas = [
            Prenda(row["nombre_prenda"], row["tipo"], row["color"], row["temporada"],
            row["estado"], row["ocasion"]) 
            for _, row in nuevo_df.iterrows()
        ]
        st.session_state.closet = Closet(prendas)
        
        st.success("¡Estado actualizado en TU clóset!")

elif opcion == "Ver favoritos":
    import csv
    st.subheader("Tus outfits favoritos")
    try:
        with open("historial_outfits.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for fila in reader:
                if len(fila) == 3 and fila[2].strip().lower() == "true":
                    st.write(f"[{fila[0]}] {fila[1]}")
    except FileNotFoundError:
        st.warning("Aún no tienes outfits favoritos guardados.")
