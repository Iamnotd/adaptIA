# adaptIA

adaptIA es un asistente de escritorio por voz para Windows. Escucha una palabra de activacion interna (`orion`), graba el comando del usuario, lo transcribe con Whisper local, clasifica la intencion con Groq y ejecuta acciones del sistema solo despues de pedir confirmacion.

El proyecto esta pensado para uso local en Windows 10/11 y combina voz, una interfaz visual sencilla y acciones automatizadas sobre aplicaciones, navegador, archivos, sistema y canales de comunicacion.

## Que hace

- Escucha el microfono en segundo plano esperando la palabra `orion`.
- Transcribe comandos hablados en espanol con Whisper.
- Usa Groq para convertir el texto del usuario en una intencion estructurada.
- Pide confirmacion por voz antes de ejecutar acciones.
- Ejecuta acciones en Windows: abrir apps, navegar, buscar, enviar mensajes, manipular archivos y consultar/controlar el sistema.
- Habla las respuestas con ElevenLabs si esta configurado, o con `pyttsx3` como fallback offline.
- Guarda interacciones recientes en SQLite para dar contexto al modelo.
- Muestra una ventana Tkinter con estado visual y log basico de actividad.

## Flujo general

1. `main.py` inicia el ciclo de voz y la interfaz Tkinter.
2. `modules/listener.py` escucha el microfono y detecta la palabra `orion`.
3. El comando se guarda como audio temporal en `C:\adaptIA_temp`.
4. `modules/transcriber.py` usa Whisper local para transcribir el audio.
5. `modules/memory.py` entrega contexto reciente desde SQLite.
6. `modules/brain.py` envia el comando y contexto a Groq.
7. Groq responde con un JSON de intencion y parametros.
8. `modules/action_manager.py` anuncia la accion y espera confirmacion verbal.
9. `modules/executor.py` despacha la accion hacia `actions/`.
10. El resultado se habla al usuario y se guarda en memoria.

## Tecnologias usadas

- Python 3.11+
- Tkinter para la interfaz visual local.
- SpeechRecognition y PyAudio para captura de audio.
- Whisper local (`openai-whisper`) para transcripcion.
- Groq API para clasificacion de intenciones.
- SQLite + SQLAlchemy para memoria persistente.
- ElevenLabs para voz de alta calidad cuando hay API key.
- pyttsx3 como voz offline de respaldo.
- Twilio para SMS, WhatsApp y llamadas.
- SMTP/IMAP para correo.
- psutil, pyautogui, pycaw y comtypes para acciones del sistema Windows.

## Estructura de carpetas

```text
adaptIA/
|-- main.py                  # Punto de entrada principal
|-- config.py                # Configuracion global y variables de entorno
|-- menu.py                  # Interfaz visual Tkinter
|-- requirements.txt         # Dependencias Python
|-- setup.bat                # Instalador para Windows
|-- start.bat                # Arranque rapido del asistente
|-- .env                     # Credenciales locales, no versionar
|-- modules/
|   |-- listener.py          # Microfono, palabra de activacion y grabacion
|   |-- transcriber.py       # Transcripcion con Whisper
|   |-- brain.py             # Clasificacion de intenciones con Groq
|   |-- action_manager.py    # Confirmacion antes de ejecutar acciones
|   |-- executor.py          # Enrutador hacia acciones concretas
|   |-- speaker.py           # Voz con ElevenLabs o pyttsx3
|   |-- memory.py            # Memoria persistente SQLite
|   `-- logger.py            # Logs con loguru
`-- actions/
    |-- apps.py              # Abrir y cerrar aplicaciones
    |-- browser.py           # Abrir URLs y busquedas web
    |-- communicator.py      # Correo, SMS, WhatsApp y llamadas
    |-- files.py             # Gestion de archivos y carpetas
    `-- system.py            # Capturas, volumen, info y energia del sistema
```

## Variables de entorno

Crea un archivo `.env` en la raiz del proyecto. Las variables disponibles son:

```env
GROQ_API_KEY=

ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
TWILIO_WHATSAPP_NUMBER=

EMAIL_ADDRESS=
EMAIL_PASSWORD=
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

Variables obligatorias para el flujo base:

- `GROQ_API_KEY`: necesaria para clasificar comandos con Groq.

Variables opcionales:

- `ELEVENLABS_API_KEY` y `ELEVENLABS_VOICE_ID`: activan voz de ElevenLabs. Si faltan, se usa `pyttsx3`.
- Variables de Twilio: necesarias solo para SMS, WhatsApp y llamadas.
- Variables de correo: necesarias solo para enviar o leer correos.

## Instalacion

Requisitos:

- Windows 10/11.
- Python 3.11+ agregado al `PATH`.
- Microfono funcional.
- Conexion a internet para Groq, deteccion con Google SpeechRecognition, instalacion inicial de Whisper y servicios externos.

Instalacion recomendada:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Tambien puedes ejecutar:

```bat
setup.bat
```

## Ejecucion

Con entorno virtual activo:

```bat
python main.py
```

O con el script incluido:

```bat
start.bat
```

Uso basico:

1. Inicia el proyecto.
2. Di `orion`.
3. Espera la respuesta "Dime".
4. Di el comando.
5. Confirma con "si" o cancela con "no".

Ejemplos:

- "orion, abre Chrome"
- "orion, busca recetas de pasta"
- "orion, abre youtube.com"
- "orion, envia un correo a alguien@example.com diciendo que llego tarde"
- "orion, manda un WhatsApp a +502..."
- "orion, toma una captura de pantalla"
- "orion, dime el estado del sistema"
- "orion, sube el volumen al 70 por ciento"

## Acciones disponibles

Aplicaciones:

- Abrir aplicaciones conocidas como Chrome, Edge, Word, Excel, PowerPoint, Notepad, Spotify, WhatsApp, VS Code, Discord y Outlook.
- Cerrar aplicaciones buscando procesos activos.

Navegador:

- Abrir URLs.
- Buscar en Google, YouTube o Bing.

Comunicacion:

- Enviar correos por SMTP.
- Leer correos no leidos por IMAP.
- Enviar SMS con Twilio.
- Enviar WhatsApp con Twilio.
- Realizar llamadas con Twilio.

Archivos:

- Crear carpetas.
- Buscar archivos.
- Abrir archivos.
- Mover o copiar archivos.
- Eliminar archivos o carpetas.

Sistema:

- Tomar capturas de pantalla.
- Consultar CPU, RAM y bateria.
- Ajustar volumen.
- Apagar, reiniciar o suspender el equipo.

## Notas de seguridad

- Todas las acciones que ejecutan cambios pasan por confirmacion verbal.
- Apagar y reiniciar requieren doble confirmacion.
- Las acciones de archivos pueden eliminar carpetas completas; usalas con cuidado.
- Las acciones de comunicacion pueden enviar mensajes, correos o llamadas reales si las credenciales estan configuradas.
- El modelo de Groq propone intenciones y parametros; antes de ampliar acciones conviene validar rutas, correos, telefonos, URLs y nombres de aplicaciones.
- No compartas `.env`. Contiene claves y credenciales privadas.

## Estado actual del proyecto

Estado: prototipo funcional local para Windows.

Funciona como arquitectura modular, pero hay puntos pendientes para fases futuras:

- Endurecer validaciones antes de acciones destructivas.
- Mejorar manejo de errores en microfono, Groq y Whisper.
- Revisar dependencias no usadas historicamente.
- Unificar textos visibles entre `adaptIA` y `Orion`.
- Corregir textos con caracteres rotos en archivos Python si aparecen en consola o UI.

## Solucion de problemas

PyAudio falla al instalar:

- En Windows puede requerir wheel precompilado o herramientas de compilacion. Prueba primero con `pip install -r requirements.txt`.

Whisper tarda en iniciar:

- La primera ejecucion puede descargar el modelo local. Despues queda en cache.

No detecta `orion`:

- Verifica el microfono predeterminado de Windows.
- Recuerda que la deteccion actual usa `SpeechRecognition` con el servicio de Google, por lo que requiere internet.

No habla con ElevenLabs:

- Revisa `ELEVENLABS_API_KEY` y `ELEVENLABS_VOICE_ID`. Si faltan, el sistema deberia usar `pyttsx3`.
