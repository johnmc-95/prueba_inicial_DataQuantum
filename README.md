# 🤖 Proyecto Final: Chatbot a Agente Autónomo

Este repositorio contiene la evolución completa de un proyecto de Inteligencia Artificial desarrollado en Python. Comienza como un chatbot de consola muy básico y va evolucionando, nivel a nivel, hasta convertirse en un Agente Autónomo capaz de tomar decisiones y usar herramientas de internet.

## 🚀 Niveles del Proyecto

El proyecto está dividido en tres archivos diferentes para que puedas probar y estudiar la evolución del código paso a paso:

### 1. Nivel Básico (`nivel_basico.py`)
El punto de partida. Es un script de consola puro que establece la conexión fundacional con la API de Groq.
*   **Características:** Bucle infinito de chat (`while True`), control de errores básico y medición de velocidad de respuesta de la IA.
*   **Limitaciones:** La IA no tiene memoria. Si le dices tu nombre y le vuelves a preguntar en el siguiente mensaje, no lo recordará.

### 2. Nivel Intermedio (`nivel_intermedio.py`)
Le damos "cerebro" al chatbot añadiendo persistencia y contexto.
*   **Memoria a corto plazo:** Implementación de un historial de conversación que se envía en cada petición a la IA, permitiéndole recordar todo el contexto del chat.
*   **Menú Dinámico:** Selección en vivo del modelo de IA (Qwen, Llama, etc.) escaneando los modelos disponibles en la API de Groq en tiempo real.
*   **Persistencia:** Comando `salir` que intercepta el cierre y guarda todo el historial en un archivo JSON en la carpeta `chats_guardados/` de forma ordenada por fecha.
*   **System Prompt:** Inyección de personalidad inicial al agente (estricto vs amigable).
*   **Comandos ocultos:** Comando especial `/resumen` que permite usar un historial clonado (temporal) para resumir la charla sin contaminar la memoria real del agente.

### 3. Nivel Avanzado (`nivel_avanzado.py`)
El salto definitivo de Chatbot a **Agente Autónomo**. La IA deja de estar encerrada en su propio conocimiento y sale a internet a buscar datos.
*   **Tool Calling (Llamada a Herramientas):** Se implementa el protocolo JSON Schema para enseñarle a la IA qué herramientas existen en el entorno.
*   **Conexión Externa:** El agente detecta de forma autónoma cuándo necesita datos sobre cine, pausa su respuesta, solicita la ejecución de nuestra función de Python para consultar la base de datos de OMDb (Internet), y finalmente elabora una respuesta humana basada en esos datos exactos y reales.
*   **Gestión de SDK:** Solución robusta de serialización del historial para que el guardado JSON local y el protocolo estricto de Groq funcionen en perfecta armonía.

---

## ⚙️ Instalación y Dependencias

Para ejecutar cualquier nivel de este proyecto, necesitas preparar tu entorno.

### 1. Dependencias y Librerías
Asegúrate de estar en tu entorno virtual y ejecuta la instalación de las siguientes librerías estándar:

```bash
pip install groq python-dotenv requests
```

*   `groq`: SDK oficial para conectar con los modelos ultra-rápidos de Groq.
*   `python-dotenv`: Para leer las variables de entorno de forma segura.
*   `requests`: Para conectarse a la API de películas OMDb en el Nivel Avanzado.

### 2. Variables de Entorno
Crea un archivo llamado `.env` en la raíz de tu proyecto e incluye tus claves secretas sin comillas ni URLs enteras:

```env
GROQ_API_KEY=tu_clave_de_groq_aqui
OMDB_API_KEY=tu_clave_de_omdb_aqui
```

*(La clave de OMDb solo es estrictamente necesaria para el Nivel Avanzado)*.

## 💻 Instrucciones de Uso

Activa tu entorno virtual y ejecuta el archivo del nivel que quieras probar:

```bash
python nivel_avanzado.py
```

Sigue las instrucciones por consola. Para guardar la conversación y generar el archivo JSON, asegúrate de escribir la palabra `salir` para terminar el programa de forma controlada.
