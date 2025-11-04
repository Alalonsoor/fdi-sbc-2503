"""Carga de la base de conocimientos"""
from pathlib import Path
from sbc.ed import Tripleta, Regla
from sbc.parser import parsear_tripleta, parsear_regla

def carga_kb(fichero_hechos: Path, fichero_reglas: Path) -> list[Tripleta | Regla]:
    kb = []

    # Cargar hechos
    if fichero_hechos.exists():
        for linea in fichero_hechos.read_text(encoding='utf-8').splitlines():
            linea = linea.strip()
            # Ignorar lineas que empiezan con '#'
            if linea and not linea.startswith('#'):
                kb.append(parsear_tripleta(linea))

    # Cargar reglas
    if fichero_reglas.exists():
        for linea in fichero_reglas.read_text(encoding='utf-8').splitlines():
            linea = linea.strip()
            # Ignorar lineas que empiezan con '#'
            if linea and not linea.startswith('#'):
                kb.append(parsear_regla(linea))
    
    return kb