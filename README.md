# adaptIA

Asistente de inteligencia artificial de escritorio para Windows 10/11, controlado por voz,
con micrófono siempre abierto, palabra de activación, y confirmación antes de ejecutar
cualquier acción en el sistema.

---

## Requisitos previos

- Windows 10 (build 1903+) o Windows 11
- Python 3.11 instalado y agregado al PATH ([descargar aquí](https://www.python.org/downloads/))
- Micrófono funcional
- Conexión a internet (para Claude API, Whisper en línea de respaldo, Twilio, etc.)

---

## Instalación

1. Descomprime esta carpeta `adaptIA` en tu computadora (por ejemplo en `C:\adaptIA`)
2. Haz doble clic en **setup.bat** y espera a que termine (instala Python deps automáticamente)
3. Abre el archivo **.env** con el Bloc de Notas o VS Code y pega tus API keys (ver abajo cómo conseguirlas)
4. Haz doble clic en **start.bat** para iniciar adaptIA

---

## Cómo obtener cada API key

### Claude API (obligatorio, es el cerebro de adaptIA)
1. Ve a https://console.anthropic.com y crea una cuenta
2. Ve a **API Keys → Create Key**
3. Copia la key y pégala en `.env` en la línea `CLAUDE_API_KEY=`

### ElevenLabs (opcional, voz de alta calidad — si se deja vacío usa voz del sistema)
1. Ve a https://elevenlabs.io y crea una cuenta
2. Ve a tu perfil → API Keys
3. Elige una voz en la sección "Voices" y copia su Voice ID
4. Pega ambos en `.env`

### Twilio (SMS, WhatsApp y llamadas)
1. Ve a https://www.twilio.com/try-twilio y crea una cuenta gratis
2. Verifica tu número de teléfono real
3. En el panel principal copia **Account SID** y **Auth Token**
4. Ve a **Phone Numbers → Manage → Buy a Number** para conseguir tu número Twilio
5. Para WhatsApp: ve a **Messaging → Try it out → Send a WhatsApp message** y activa el Sandbox
6. Pega todos los datos en `.env`

### Correo (Gmail recomendado)
1. Activa la verificación en dos pasos en tu cuenta de Gmail
2. Ve a https://myaccount.google.com/apppasswords y genera una "contraseña de aplicación"
3. Usa esa contraseña (no la de tu cuenta normal) en `.env` en `EMAIL_PASSWORD`

---

## Cómo usar adaptIA

1. Ejecuta `start.bat`. Verás el mensaje "adaptIA está activo y escuchando en segundo plano."
2. Di **"adaptIA"** en voz alta. Escucharás "Dime."
3. Di tu comando, por ejemplo: *"adaptIA, abre Chrome"* o *"envía un correo a juan@gmail.com diciendo que llego tarde"*
4. adaptIA te dirá qué acción va a realizar y pedirá confirmación: *"Estoy a punto de abrir Chrome, ¿confirmas?"*
5. Responde **"sí"** para ejecutar o **"no"** para cancelar

Para detener adaptIA por completo, presiona `Ctrl + C` en la ventana de la consola.

---

## Comandos de ejemplo

- "adaptIA, abre Word"
- "adaptIA, cierra Spotify"
- "adaptIA, busca en internet recetas de pasta"
- "adaptIA, abre la página de YouTube"
- "adaptIA, envía un correo a [nombre] sobre [tema]"
- "adaptIA, manda un WhatsApp a [número] diciendo [mensaje]"
- "adaptIA, llama a [número]"
- "adaptIA, toma una captura de pantalla"
- "adaptIA, dime el estado del sistema"
- "adaptIA, sube el volumen al 70 por ciento"

---

## Estructura del proyecto

```
adaptIA/
├── main.py                  # Punto de entrada principal
├── config.py                # Configuración global
├── .env                     # Tus API keys (NO compartir)
├── requirements.txt         # Dependencias de Python
├── setup.bat                # Instalador automático
├── start.bat                # Iniciador de adaptIA
├── modules/
│   ├── listener.py          # Captura de audio y palabra clave
│   ├── transcriber.py       # Transcripción con Whisper
│   ├── brain.py             # Procesamiento con Claude API
│   ├── action_manager.py    # Flujo de confirmación
│   ├── executor.py          # Ejecución de acciones
│   ├── speaker.py           # Texto a voz
│   ├── memory.py            # Memoria persistente (SQLite)
│   └── logger.py            # Sistema de logs
└── actions/
    ├── apps.py               # Abrir/cerrar aplicaciones
    ├── browser.py            # Navegador y búsquedas
    ├── communicator.py       # Correos, SMS, WhatsApp, llamadas
    ├── files.py               # Gestión de archivos
    └── system.py             # Control del sistema
```

---

## Solución de problemas

**"No se reconoce pyaudio" al instalar:**
Si `pip install pyaudio` falla en Windows, descarga el archivo `.whl` precompilado desde
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio que coincida con tu versión de Python,
e instálalo con `pip install nombre_del_archivo.whl`

**El micrófono no detecta la palabra clave:**
Verifica que el micrófono correcto esté seleccionado como predeterminado en la configuración
de sonido de Windows. adaptIA usa el micrófono predeterminado del sistema.

**Whisper tarda mucho en cargar:**
La primera vez que ejecutas adaptIA, Whisper descarga el modelo (puede tardar varios minutos
según tu internet). Las siguientes veces será instantáneo porque queda en caché local.

**Error de autenticación en Gmail:**
Gmail bloquea contraseñas normales por seguridad. Debes usar una "contraseña de aplicación"
generada específicamente, no la contraseña de tu cuenta.
