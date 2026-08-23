import os
import time
import json
import re
import requests 
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# ==========================================
# FASE 1: HERRAMIENTA PURA (Sin IA)
# ==========================================
def buscar_datos_pelicula(titulo):
    """
    Se conecta a la base de datos de OMDb y busca información de una película.
    Devuelve un texto (string) con los datos clave.
    """
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        return "Error: Falta la clave OMDB_API_KEY en el archivo .env"
        
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={titulo}"
    
    try:
        # Hacemos la petición a la API
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        # OMDb devuelve 'Response' == 'False' si la película no existe
        if datos.get("Response") == "False":
            return f"No se pudo encontrar información sobre la película '{titulo}'."
            
        # Extraemos los datos que nos interesan
        titulo_real = datos.get("Title", "Desconocido")
        año = datos.get("Year", "Desconocido")
        director = datos.get("Director", "Desconocido")
        actores = datos.get("Actors", "Desconocido")
        puntuacion = datos.get("imdbRating", "Desconocido")
        
        # Lo formateamos de manera limpia para devolvérselo a la IA
        resultado = (
            f"Título: {titulo_real} ({año})\n"
            f"Director: {director}\n"
            f"Reparto: {actores}\n"
            f"Puntuación IMDb: {puntuacion}/10"
        )
        return resultado
        
    except Exception as e:
        return f"Error al conectar con la base de datos de cine: {e}"

# ==========================================
# FASE 2: MANUAL DE INSTRUCCIONES (JSON Schema)
# ==========================================
# Aquí le explicamos a la IA exactamente qué herramientas existen y cómo usarlas
mis_herramientas = [
    {
        "type": "function",
        "function": {
            "name": "buscar_datos_pelicula", # IMPORTANTE: Debe coincidir exactamente con el nombre de tu función en Python
            "description": "Busca datos reales de una película en una base de datos externa. Úsala SIEMPRE que el usuario pregunte por películas, actores, notas o directores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "El título de la película. Ej: 'The Matrix'",
                    }
                },
                "required": ["titulo"]
            }
        }
    }
]

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
        
    # Comando especial para resumir la conversación
    if texto_usuario.lower() == "/resumen":
        print("⏳ Generando resumen de la conversación...")
        
        # 1. Hacemos una copia exacta de la memoria
        historial_temporal = historial.copy()
        
        # 2. Le inyectamos la petición a la IA en la memoria temporal
        historial_temporal.append({
            "role": "user", 
            "content": "Por favor, haz un resumen muy breve y en formato de lista (viñetas) de lo que hemos hablado hasta ahora. Ignora este mensaje si no hemos hablado de nada."
        })
        
        try:
            # 3. Llamamos a Groq usando la copia
            resp = cliente.chat.completions.create(
                model=modelo_activo,
                messages=historial_temporal
            )
            # 4. Imprimimos el resultado de forma bonita
            texto_resumen = resp.choices[0].message.content
            texto_resumen_limpio = re.sub(r'<think>.*?</think>\n*', '', texto_resumen, flags=re.DOTALL).strip()
            print("\n" + "="*40)
            print("📜 RESUMEN DE LA CONVERSACIÓN:")
            print(texto_resumen_limpio)
            print("="*40 + "\n")
        except Exception as e:
            print(f"Error al generar resumen: {e}")
            
        # La palabra clave 'continue' rompe la vuelta actual del bucle y vuelve a pedir input.
        # Gracias a esto, la memoria real NUNCA guarda ni el "/resumen" ni la respuesta de la IA.
        continue

    # Añadimos el mensaje del usuario a la memoria
    historial.append({"role": "user", "content": texto_usuario})
        
    try:
        # ==========================================
        # FASE 3: EL BUCLE DEL AGENTE (Tool Calling)
        # ==========================================
        inicio = time.time()
        
        # 1. Primera llamada a la IA (¡ahora le enviamos las herramientas!)
        respuesta = cliente.chat.completions.create(
            model=modelo_activo,
            messages=historial,
            tools=mis_herramientas, # Le pasamos nuestro JSON Schema
            tool_choice="auto"      # Le dejamos decidir libremente si necesita usarla
        )
        
        mensaje_ia = respuesta.choices[0].message
        
        # 2. Comprobamos si la IA ha decidido usar una herramienta
        if mensaje_ia.tool_calls:
            print("\n🤖 [IA PENSANDO]: Mmmm, no me sé esto de memoria. Necesito consultar la base de datos...")
            
            # Guardamos la petición técnica en el historial. 
            # IMPORTANTE: Construimos el diccionario a mano para extraer solo lo necesario.
            # Si usamos .model_dump() a lo bruto, incluye campos basura que la API de Groq rechaza luego.
            peticion_ia = {
                "role": "assistant",
                "content": mensaje_ia.content,
                "tool_calls": [
                    {
                        "id": t.id,
                        "type": "function",
                        "function": {
                            "name": t.function.name,
                            "arguments": t.function.arguments
                        }
                    } for t in mensaje_ia.tool_calls
                ]
            }
            historial.append(peticion_ia)
            
            # 3. Extraemos qué herramienta quiere usar y con qué parámetros
            for tool_call in mensaje_ia.tool_calls:
                nombre_funcion = tool_call.function.name
                
                if nombre_funcion == "buscar_datos_pelicula":
                    # Convertimos el string JSON que nos manda la IA a un diccionario de Python
                    argumentos = json.loads(tool_call.function.arguments)
                    titulo_pedido = argumentos.get("titulo")
                    
                    print(f"🛠️  [SISTEMA]: Ejecutando herramienta para buscar '{titulo_pedido}'...")
                    
                    # ¡AQUÍ ESTÁ LA MAGIA! Ejecutamos nuestra función pura
                    resultado_herramienta = buscar_datos_pelicula(titulo_pedido)
                    
                    # 4. Le devolvemos el resultado a la IA metiéndolo en el historial
                    historial.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": nombre_funcion,
                        "content": resultado_herramienta
                    })
                    
            # 5. Segunda llamada a la IA: Ahora que tiene los datos, le pedimos que responda al usuario
            print("🤖 [IA PENSANDO]: ¡Datos recibidos! Formulando la respuesta final...\n")
            respuesta_final = cliente.chat.completions.create(
                model=modelo_activo,
                messages=historial
            )
            
            texto_final = respuesta_final.choices[0].message.content
            texto_limpio = re.sub(r'<think>.*?</think>\n*', '', texto_final, flags=re.DOTALL).strip()
            
            historial.append({"role": "assistant", "content": texto_limpio})
            
            duracion = time.time() - inicio
            print("IA:", texto_limpio)
            print(f"\n⏱️ (Tiempo total con uso de herramienta: {duracion:.2f}s)")
            print("-" * 50)
            
        else:
            # 6. Si no necesita herramientas, es una conversación normal
            texto_normal = mensaje_ia.content
            texto_limpio = re.sub(r'<think>.*?</think>\n*', '', texto_normal, flags=re.DOTALL).strip()
            
            historial.append({"role": "assistant", "content": texto_limpio})
            
            duracion = time.time() - inicio
            print("IA:", texto_limpio)
            print(f"\n⏱️ (Tiempo normal: {duracion:.2f}s)")
            print("-" * 50)
            
    except Exception as e:
        print(f"IA: Fallo crítico en el Agente. [Detalle técnico: {e}]")

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
    