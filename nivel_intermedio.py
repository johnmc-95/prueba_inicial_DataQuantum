import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# 1. Configuración inicial
load_dotenv() # Carga las variables de entorno (.env)
cliente = Groq(api_key=os.environ.get("GROQ_API_KEY")) # Inicializa el cliente de la API

# 2. Selección dinámica de modelo
print("\n=== MENÚ DE SELECCIÓN DE MODELO ===")
print("Consultando modelos activos en Groq...")

try:
    # Obtenemos y filtramos la lista de modelos gratuitos disponibles (Llama, Gemma, Mixtral, Qwen)
    lista_modelos = cliente.models.list().data
    marcas_gratuitas = ["llama", "gemma", "mixtral", "qwen"]
    modelos_chat = []
    
    for m in lista_modelos:
        nombre = m.id.lower()
        es_modelo_valido = any(marca in nombre for marca in marcas_gratuitas)
        es_herramienta = "guard" in nombre or "whisper" in nombre
        
        if es_modelo_valido and not es_herramienta:
            modelos_chat.append(m.id)
            
    # Mostramos los 3 primeros modelos para que el usuario elija
    modelos_chat = modelos_chat[:3]
    for i, nombre_modelo in enumerate(modelos_chat):
        print(f"{i + 1}. {nombre_modelo}")
        
    opcion = int(input("\nElige un número de modelo: ")) - 1
    modelo_activo = modelos_chat[opcion]
    print(f"\n-> Modelo seleccionado: {modelo_activo}\n")

except Exception as e:
    print("Error al cargar modelos. Usando modelo de respaldo.")
    modelo_activo = "llama-3.1-8b-instant"

# 3. Inicialización de la memoria (Historial)
print("--- Chat Iniciado (escribe 'salir' para terminar) ---")

# El historial guarda el contexto. El System Prompt define la personalidad inicial de la IA.
historial = [
    {"role": "system", "content": "Eres un asistente de IA con un rol educativo, lenguaje claro y formal, y respuestas breves."}
]

# 4. Bucle principal de conversación
while True:
    texto_usuario = input("Tú: ")
    
    # Comprobación de salida antes de modificar el historial
    if texto_usuario.lower() == "salir":
        print("Saliendo del programa...")
        break
        
    # Añadimos el mensaje del usuario a la memoria
    historial.append({"role": "user", "content": texto_usuario})
        
    try:
        # Llamada a la API y medición de tiempo de respuesta
        inicio = time.time()
        
        respuesta = cliente.chat.completions.create(
            model=modelo_activo,
            messages=historial # Enviamos toda la memoria acumulada
        )
        
        duracion = time.time() - inicio
        
        # Extracción y guardado de la respuesta de la IA en la memoria
        texto_respuesta = respuesta.choices[0].message.content
        historial.append({"role": "assistant", "content": texto_respuesta})
        
        print("IA:", texto_respuesta)
        print(f"\n⏱️ (Tiempo: {duracion:.2f}s)")
        print("-" * 50)
        
    except Exception as e:
        print(f"IA: Error de conexión. [Detalle técnico: {e}]")

# 5. Guardado del historial en disco
# Si hay más de 1 mensaje (el usuario llegó a interactuar), guardamos la conversación
if len(historial) > 1:
    carpeta_destino = "chats_guardados"
    os.makedirs(carpeta_destino, exist_ok=True) # Crea la carpeta si no existe
    
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ruta_archivo = os.path.join(carpeta_destino, f"conversacion_{fecha}.json")
        
    # Guardamos la lista en el archivo con formato estructurado
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(historial, archivo, indent=4, ensure_ascii=False)
            
    print(f"✅ Conversación guardada en: {ruta_archivo}")
else:
    print("Conversación vacía. No se ha generado ningún archivo.")