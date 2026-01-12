"""Carga de la base de conocimientos"""

from pathlib import Path
from sbc.ed import Tripleta, Regla
from sbc.parser import parsear_regla, parsear_tripleta


def carga_kb(path: Path) -> dict:
    """
    Carga una base de conocimiento desde un archivo o directorio.
    """
    hechos = [] # Lista para almacenar hechos parseados
    reglas = [] # Lista para almacenar reglas parseadas

    # Caso 1: Si es un directorio, carga TODOS los archivos .txt
    if path.is_dir():
        # sorted() asegura orden consistente entre ejecuciones
        for archivo in sorted(path.glob("*.txt")):
            # Carga hechos y reglas de cada archivo
            h, r = _cargar_archivo(archivo)
            # Agrega a la lista acumulativa
            hechos.extend(h) 
            reglas.extend(r)
    # Caso 2: Si es un archivo .txt individual
    elif path.is_file() and path.suffix == ".txt":
        hechos, reglas = _cargar_archivo(path)

    # Si no es ni directorio ni archivo .txt, retorna listas vacías.
    # Retorna la estructura estándar del sistema.
    return {"hechos": hechos, "reglas": reglas}


def _cargar_archivo(archivo: Path) -> tuple[list[Tripleta], list[Regla]]:
    """
    Función interna que carga un único archivo.
    """
    hechos = []
    reglas = []

    # Intenta leer el archivo con encoding UTF-8
    try:
        contenido = archivo.read_text(encoding="utf-8")
    except Exception:
        # Si falla la lectura (archivo no existe, permisos, etc.)
        # retorna listas vacías; fallo silencioso
        return hechos, reglas
    
    # Procesa cada línea del archivo
    for linea in contenido.splitlines():
        linea = linea.strip() # Elimina espacios al inicio/final

        # Elimina comentarios al final de la línea
        # Busca el primer '#' que no esté entre comillas
        # (versión simple: elimina todo después del primer '#')
        if '#' in linea:
            # Encuentra la posición del primer '#'
            pos_comentario = linea.find('#')
            # Toma solo la parte antes del comentario
            linea = linea[:pos_comentario].strip()
        
        # Líneas vacías después de eliminar comentarios se ignoran
        if not linea:
            continue
        
        try:
            # DETECTOR DE REGLAS: Si la línea contiene "<-"
            if "<-" in linea:
                reglas.append(parsear_regla(linea))
            # DETECTOR DE HECHOS: Todo lo demás se considera un hecho
            else:
                hechos.append(parsear_tripleta(linea))
        except Exception:
            # Si el parser falla (sintaxis incorrecta), ignora la línea
            # y continúa con la siguiente
            continue
    
    return hechos, reglas
