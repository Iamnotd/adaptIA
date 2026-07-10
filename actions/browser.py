"""
actions/browser.py
Acciones relacionadas con el navegador: abrir URLs y realizar búsquedas web.
"""

import webbrowser
from modules.logger import get_logger

logger = get_logger()


def abrir_url(url):
    """Abre una URL específica en el navegador predeterminado del sistema."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        logger.info(f"URL abierta: {url}")
        return True, f"He abierto {url} en tu navegador."
    except Exception as e:
        logger.error(f"Error abriendo URL '{url}': {e}")
        return False, f"No pude abrir la página {url}."


def buscar_en_web(termino, motor="google"):
    """Realiza una búsqueda web en el motor especificado (por defecto Google)."""
    motores = {
        "google": "https://www.google.com/search?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
        "bing": "https://www.bing.com/search?q=",
    }
    base_url = motores.get(motor.lower(), motores["google"])
    termino_codificado = termino.replace(" ", "+")
    url_busqueda = base_url + termino_codificado

    try:
        webbrowser.open(url_busqueda)
        logger.info(f"Búsqueda realizada en {motor}: {termino}")
        return True, f"Busqué '{termino}' en {motor}."
    except Exception as e:
        logger.error(f"Error realizando búsqueda web: {e}")
        return False, "No pude realizar la búsqueda."
