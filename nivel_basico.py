import os
from dotenv import load_dotenv
from groq import Groq

# 1. Cargamos las variables secretas de nuestro .env
load_dotenv()

# 2. Inicializamos nuestro cliente de Groq
cliente = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

print("--- Chat Iniciado (escribe 'salir' para terminar) ---")

while True: 
    # 3. Leemos lo que escribe el usuario por consola
    texto_usuario = input("Tú: ")
    
    # 4. Comprobamos la condición de salida
    if texto_usuario.lower() == "salir":
        print("Saliendo del programa. ¡Hasta pronto!")
        break 
        
    # 5. Protegemos la llamada a internet con try/except
    try:
        # Intentamos contactar con los servidores
        respuesta = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile", # Tu modelo actualizado
            messages=[
                {
                    "role": "user",
                    "content": texto_usuario 
                }
            ]
        )
        
        # Si todo va bien, mostramos la respuesta en pantalla
        print("IA:", respuesta.choices[0].message.content)
        
    except Exception as e:
        # Si algo falla (no hay Wi-Fi, los servidores de Groq caen, etc.),
        # el programa salta a esta línea en lugar de cerrarse de golpe.
        print("IA: Ups, parece que he tenido un problema de conexión.")
        
        # Opcional: Mostramos el error técnico real para nosotros (los desarrolladores)
        print(f"[Aviso técnico: {e}]")

