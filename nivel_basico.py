import os
import time 
from dotenv import load_dotenv
from groq import Groq

# 1. Cargamos las variables secretas de nuestro .env
load_dotenv()

# 2. Inicializamos nuestro cliente de Groq
cliente = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# ==========================================
# MENÚ DINÁMICO 
# ==========================================
print("\n=== MENÚ DE SELECCIÓN DE MODELO ===")
print("Consultando a Groq qué modelos están activos HOY...")

try:
    # Le pedimos a Groq su lista de modelos en tiempo real
    lista_modelos = cliente.models.list().data
    
    # Filtramos modelos para asegurar que son gratuitos y de texto
    modelos_chat = []
    marcas_gratuitas = ["llama", "gemma", "mixtral", "qwen"]
    
    for m in lista_modelos:
        nombre = m.id.lower()
        # Comprobamos si el nombre contiene alguna de las marcas gratuitas
        es_modelo_valido = any(marca in nombre for marca in marcas_gratuitas)
        # Excluimos modelos de audio o herramientas internas de seguridad
        es_herramienta = "guard" in nombre or "whisper" in nombre
        
        if es_modelo_valido and not es_herramienta:
            modelos_chat.append(m.id)
            
    # Mostramos exactamente los 3 primeros modelos disponibles
    modelos_chat = modelos_chat[:3]
    
    for i, nombre_modelo in enumerate(modelos_chat):
        print(f"{i + 1}. {nombre_modelo}")
        
    opcion = input("\nElige un número de modelo: ")
    indice = int(opcion) - 1
    modelo_activo = modelos_chat[indice]
    print(f"\n-> ¡Genial! Has elegido: {modelo_activo}\n")

except Exception as e:
    # Si hay algún error eligiendo, ponemos uno de respaldo que sabemos que hoy existe
    print("Hubo un error al elegir. Usando modelo de respaldo.")
    modelo_activo = "llama-3.1-8b-instant"

print("--- Chat Iniciado (escribe 'salir' para terminar) ---")

while True: 
    # 3. Leemos lo que escribe el usuario
    texto_usuario = input("Tú: ")
    
    # 4. Comprobamos la condición de salida
    if texto_usuario.lower() == "salir":
        print("Saliendo del programa. ¡Hasta pronto!")
        break 
        
    # 5. Protegemos la llamada a internet
    try:
        # CRONÓMETRO - INICIO
        inicio = time.time()
        
        # Hacemos la petición a la API
        respuesta = cliente.chat.completions.create(
            # Usamos el modelo que haya salido del menú dinámico
            model=modelo_activo, 
            messages=[
                {
                    "role": "user",
                    "content": texto_usuario 
                }
            ]
        )
        
        # CRONÓMETRO - FIN
        fin = time.time()
        duracion = fin - inicio
        
        # Mostramos la respuesta y el tiempo
        print("IA:", respuesta.choices[0].message.content)
        print(f"\n⏱️ (Tiempo de respuesta: {duracion:.2f} segundos)")
        print("-" * 50) 
        
    except Exception as e:
        print("IA: Ups, parece que he tenido un problema de conexión o el modelo ha fallado.")
        print(f"[Aviso técnico: {e}]")
