import os
from dotenv import load_dotenv
import requests

# Cargamos el .env para poder leer la API Key
load_dotenv()

def probar_herramienta():
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        print("[ERROR] No encuentro OMDB_API_KEY en tu archivo .env")
        return
        
    print("[OK] API Key encontrada. Conectando con OMDb...\n")
    
    titulo = "Interstellar"
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={titulo}"
    
    respuesta = requests.get(url)
    datos = respuesta.json()
    
    if datos.get("Response") == "False":
        print(f"[ERROR] Pelicula no encontrada. Mensaje de la API: {datos.get('Error')}")
    else:
        print("[EXITO] CONEXION EXITOSA. Datos recibidos:")
        print("="*40)
        print(f"Título: {datos.get('Title')} ({datos.get('Year')})")
        print(f"Director: {datos.get('Director')}")
        print(f"Actores: {datos.get('Actors')}")
        print(f"Puntuación: {datos.get('imdbRating')}")
        print("="*40)

if __name__ == "__main__":
    probar_herramienta()
