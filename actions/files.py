"""
actions/files.py
Gestión de archivos y carpetas: crear, mover, copiar, eliminar y buscar.
"""

import os
import shutil
import glob
from modules.logger import get_logger

logger = get_logger()


def crear_carpeta(ruta):
    """Crea una nueva carpeta en la ruta especificada."""
    try:
        os.makedirs(ruta, exist_ok=True)
        logger.info(f"Carpeta creada: {ruta}")
        return True, f"Carpeta creada en {ruta}."
    except Exception as e:
        logger.error(f"Error creando carpeta '{ruta}': {e}")
        return False, f"No pude crear la carpeta {ruta}."


def eliminar_archivo(ruta):
    """Elimina un archivo o carpeta de forma segura."""
    try:
        if os.path.isdir(ruta):
            shutil.rmtree(ruta)
        elif os.path.isfile(ruta):
            os.remove(ruta)
        else:
            return False, f"No encontré {ruta}."
        logger.info(f"Eliminado: {ruta}")
        return True, f"He eliminado {ruta}."
    except Exception as e:
        logger.error(f"Error eliminando '{ruta}': {e}")
        return False, f"No pude eliminar {ruta}."


def mover_archivo(origen, destino):
    """Mueve un archivo o carpeta de una ubicación a otra."""
    try:
        shutil.move(origen, destino)
        logger.info(f"Movido de {origen} a {destino}")
        return True, f"He movido el archivo a {destino}."
    except Exception as e:
        logger.error(f"Error moviendo archivo: {e}")
        return False, "No pude mover el archivo."


def copiar_archivo(origen, destino):
    """Copia un archivo de una ubicación a otra."""
    try:
        if os.path.isdir(origen):
            shutil.copytree(origen, destino)
        else:
            shutil.copy2(origen, destino)
        logger.info(f"Copiado de {origen} a {destino}")
        return True, f"He copiado el archivo a {destino}."
    except Exception as e:
        logger.error(f"Error copiando archivo: {e}")
        return False, "No pude copiar el archivo."


def buscar_archivo(nombre, carpeta_inicio=None):
    """
    Busca archivos por nombre (coincidencia parcial) a partir de una carpeta inicial.
    Si no se especifica carpeta, busca desde la carpeta del usuario actual.
    """
    if carpeta_inicio is None:
        carpeta_inicio = os.path.expanduser("~")

    try:
        patron = os.path.join(carpeta_inicio, "**", f"*{nombre}*")
        resultados = glob.glob(patron, recursive=True)
        resultados = resultados[:10]  # limitar resultados para no saturar
        logger.info(f"Búsqueda de '{nombre}' encontró {len(resultados)} resultados.")
        return True, resultados
    except Exception as e:
        logger.error(f"Error buscando archivo '{nombre}': {e}")
        return False, []


def abrir_archivo(ruta):
    """Abre un archivo con su aplicación predeterminada en Windows."""
    try:
        os.startfile(ruta)
        logger.info(f"Archivo abierto: {ruta}")
        return True, f"He abierto el archivo {ruta}."
    except Exception as e:
        logger.error(f"Error abriendo archivo '{ruta}': {e}")
        return False, f"No pude abrir el archivo {ruta}."
