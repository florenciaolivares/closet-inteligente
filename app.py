# app.py
import streamlit as st
import pandas as pd
from closet import Prenda, Closet
from utils import guardar_outfit, outfit_a_str, obtener_temperatura_santiago

API_KEY = "1c1fb8b2336136f7f4c9620ffc1229ee"
INVENTARIO_PATH = "inventario vacio.xlsx"

@st.cache_data
def cargar_inventario(path):
    df = pd.read_excel(path)
    prendas = [Prenda(row["nombre_prenda"], row["tipo"], row["color"], row["temporada"],
                      row["estado"], row["ocasion"]) for _, row in df.iterrows()]
    return df, Closet(prendas)

df, closet = cargar_inventario(INVENTARIO_PATH)

st.title("👗 Clóset Inteligente")

opcion = st.sidebar.selectbox("¿Qué quieres hacer?", ["Recomendar outfit", "Agregar prenda", "Cambiar estado", "Ver favoritos"])

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
        clima = st.selectbox("No se pudo obtener el clima. Selecciónalo manualmente:", ["otoño", "invierno", "primavera", "verano"])

    ocasion = st.selectbox("¿Ocasión del día?", ["informal", "formal"])

    if st.button("Sugerir outfit"):
        outfit = closet.sugerir_outfit(clima, ocasion)
        if outfit:
            partes = []
            for parte in outfit:
                prenda = outfit[parte]
                partes.append(f"**{parte}**: {prenda.nombre} ({prenda.color})")
            st.markdown("### Te sugerimos usar:\n" + "\n".join(partes))
            gusto = st.radio("¿Te gustó esta sugerencia?", ["Sí", "No"]) == "Sí"
            guardar_outfit(outfit_a_str(outfit, clima, ocasion), gusto)
        else:
            st.warning("No hay prendas suficientes disponibles para sugerir un outfit.")

elif opcion == "Agregar prenda":
    st.subheader("Agregar nueva prenda")
    nombre = st.text_input("Nombre")
    tipo = st.selectbox("Tipo", ["polera", "pantalonlargo", "short", "falda", "vestido", "abrigo"])
    color = st.text_input("Color")
    temporada = st.selectbox("Temporada", ["otoño", "invierno", "primavera", "verano"])
    estado = st.selectbox("Estado", ["limpio", "sucio"])
    ocasion = st.selectbox("Ocasión", ["formal", "informal"])

    if st.button("Agregar prenda"):
        nueva_fila = pd.DataFrame([{
            "nombre_prenda": nombre,
            "tipo": tipo,
            "color": color,
            "temporada": temporada,
            "estado": estado,
            "ocasion": ocasion
        }])
        df = pd.concat([df, nueva_fila], ignore_index=True)
        df.to_excel(INVENTARIO_PATH, index=False)
        st.success("Prenda agregada correctamente.")

elif opcion == "Cambiar estado":
    st.subheader("Cambiar estado de una prenda")
    prenda = st.selectbox("Selecciona prenda", df["nombre_prenda"].tolist())
    estado_actual = df[df["nombre_prenda"] == prenda]["estado"].values[0]
    st.text(f"Estado actual: {estado_actual}")
    nuevo_estado = st.radio("Nuevo estado", ["limpio", "sucio"])

    if st.button("Actualizar estado"):
        df.loc[df["nombre_prenda"] == prenda, "estado"] = nuevo_estado
        df.to_excel(INVENTARIO_PATH, index=False)
        st.success("Estado actualizado correctamente.")

elif opcion == "Ver favoritos":
    import csv
    st.subheader("Outfits favoritos")
    try:
        with open("historial_outfits.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for fila in reader:
                if len(fila) == 3 and fila[2].strip().lower() == "true":
                    st.write(f"[{fila[0]}] {fila[1]}")
    except FileNotFoundError:
        st.warning("Aún no hay historial registrado.")
