# utils.py
import csv
from datetime import datetime
import requests

HISTORIAL_PATH = "historial_outfits.csv"

def guardar_outfit(outfit_str, le_gusto):
    with open(HISTORIAL_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(timespec="seconds"), outfit_str, le_gusto])

def outfit_a_str(outfit, clima, ocasion):
    outfit_str = f"clima: {clima} | ocasion: {ocasion} "
    for clave in ["superior", "inferior", "capa"]:
        if clave in outfit:
            p = outfit[clave]
            outfit_str += f"| {clave}: {p.nombre} ({p.tipo}, {p.color}) "
    return outfit_str

def obtener_temperatura_santiago(api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Santiago,CL&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data["main"]["temp"]
