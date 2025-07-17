# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from closet import Prenda, Closet
from utils import guardar_outfit, outfit_a_str, obtener_temperatura_santiago

# === CONFIGURACIÓN GENERAL ===
INVENTARIO_PATH = "v2_Inventario_Seminario.xlsx"
HISTORIAL_PATH = "historial_outfits.csv"

# === INICIALIZACIÓN DEL INVENTARIO ===
@st.cache_data
def cargar_inventario(path):
    df = pd.read_excel(path)
    prendas_ar = [
        Prenda(row["nombre_prenda"], row["tipo"], row["color"],
               row["temporada"], row["estado"], row["ocasion"])
        for _, row in df.iterrows()
    ]
    return df, Closet(prendas_ar)

if "df" not in st.session_state:
    df_base, closet_base = cargar_inventario(INVENTARIO_PATH)
    st.session_state.df = df_base.copy()
    st.session_state.closet = closet_base

df = st.session_state.df
closet = st.session_state.closet

# === INTERFAZ ===
st.set_page_config(page_title="Clóset Inteligente", layout="centered")

st.title("👚 Clóset Inteligente")

opcion = st.sidebar.selectbox(
    "¿Qué quieres hacer?",
    ["Sugerir outfit", "Ver favoritos", "Agregar prenda", "Editar estado"]
)

# === SUGERIR OUTFIT ===
if opcion == "Sugerir outfit":
    st.header("👗 Sugerencia de Outfit")

    try:
        api_key = "****1c1fb8b2336136f7f4c9620ffc1229ee"  # Tu API key
        temperatura = obtener_temperatura_santiago(api_key)
        st.success(f"Temperatura en Santiago: {temperatura:.1f} °C")

        if temperatura <= 20.0:
            clima = "invierno"
        elif temperatura <= 23.0:
            clima = "otoño"
        elif temperatura <= 27.0:
            clima = "primavera"
        else:
            clima = "verano"

    except:
        st.warning("No se pudo obtener la temperatura automáticamente.")
        clima = st.selectbox("Selecciona la temporada:", ["otoño", "invierno", "primavera", "verano"])

    ocasion = st.radio("¿Cuál es la ocasión?", ["formal", "informal"])

    if st.button("🎲 Generar outfit"):
        outfit = closet.sugerir_outfit(clima, ocasion)

        if outfit:
            outfit_str = outfit_a_str(outfit, clima, ocasion)
            st.markdown("### Recomendación:")
            for parte in ["superior", "inferior", "capa"]:
                if parte in outfit:
                    prenda = outfit[parte]
                    st.write(f"**{parte.capitalize()}:** {prenda.nombre} ({prenda.color})")

            gusto = st.radio("¿Te gustó la sugerencia?", ["Sí", "No"], horizontal=True)
            if gusto:
                guardar_outfit(outfit_str, gusto.lower() == "sí")
        else:
            st.error("No hay suficientes prendas disponibles para sugerir un outfit.")

# === FAVORITOS ===
elif opcion == "Ver favoritos":
    st.header("💖 Tus outfits favoritos")
    if not mostrar_outfits_favoritos(HISTORIAL_PATH):
        st.info("Aún no tienes outfits favoritos.")

# === AGREGAR PRENDA ===
elif opcion == "Agregar prenda":
    st.header("➕ Agregar nueva prenda")

    with st.form("form_nueva_prenda"):
        nombre = st.text_input("Nombre de la prenda")
        tipo = st.selectbox("Tipo", ["polera", "pantalonlargo", "short", "falda", "vestido", "abrigo"])
        color = st.text_input("Color")
        temporada = st.selectbox("Temporada", ["otoño", "invierno", "primavera", "verano"])
        estado = st.radio("Estado", ["limpio", "sucio"])
        ocasion = st.radio("Ocasión", ["formal", "informal"])
        submitted = st.form_submit_button("Agregar")

    if submitted:
        nueva = Prenda(nombre, tipo, color, temporada, estado, ocasion)
        st.session_state.df.loc[len(df)] = [nombre, tipo, color, temporada, estado, ocasion]
        st.session_state.closet.prendas.append(nueva)
        st.success("Prenda agregada correctamente.")

# === CAMBIAR ESTADO ===
elif opcion == "Editar estado":
    st.header("♻️ Cambiar estado de una prenda")

    nombre_objetivo = st.text_input("Nombre de la prenda a editar").strip()
    if st.button("Buscar"):
        indices = df.index[df["nombre_prenda"].str.lower() == nombre_objetivo.lower()].tolist()
        if not indices:
            st.error("No se encontró una prenda con ese nombre.")
        else:
            for i in indices:
                estado_actual = df.at[i, "estado"]
                nuevo_estado = st.radio(
                    f"La prenda '{df.at[i, 'nombre_prenda']}' está actualmente: {estado_actual}",
                    ["limpio", "sucio"],
                    key=f"estado_{i}"
                )
                df.at[i, "estado"] = nuevo_estado
                for prenda in closet.prendas:
                    if prenda.nombre.lower() == nombre_objetivo.lower():
                        prenda.estado = nuevo_estado
                st.success("Estado actualizado correctamente.")
