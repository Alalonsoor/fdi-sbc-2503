"""Parsers para tripletas y reglas usando pyparsing"""

from pyparsing import (
    Word,
    alphanums,
    Suppress,
    alphas,
    delimitedList,
    Optional,
    Regex,
    nums,
)
from sbc.ed import Tripleta, Regla

# Definir variables: cualquier string que empiece con mayuscula
variable = Word(alphas.upper(), alphanums + "_" + "áéíóúñÁÉÍÓÚÑ")

# Literal: empieza con minuscula
literal = Word(alphas.lower() + nums, alphanums + "_" + "áéíóúñÁÉÍÓÚÑ")

# Termino o es literal o variable
termino = variable | literal

# Si se detecta '<-' se ignora
flecha = Suppress("<-")
# Si se detecta ',' se ignora (para separar multiples antecedentes)
coma = Suppress(",")
punto = Suppress(".")

# Parser para extensión de confianza: [0.8] o [1]
difusa = Regex(r"0\.\d+|1\.0|1")
extension = Suppress("[") + difusa + Suppress("]")


def crear_tripleta(tokens) -> Tripleta:
    """Convertir tokens a tripleta con confianza opcional"""
    confianza = float(tokens[3]) if len(tokens) > 3 else 1.0
    return Tripleta(str(tokens[0]), str(tokens[1]), str(tokens[2]), confianza)


def crear_regla(tokens) -> Regla:
    """Convertir tokens a regla con multiples antecedentes y confianza opcional"""
    consecuente = tokens[0]
    # Separar antecedentes (Tripletas) de la confianza (float)
    antecedentes = [t for t in tokens[1:] if isinstance(t, Tripleta)]
    # La confianza es el último token si es un string (el número parseado)
    confianza = (
        float(tokens[-1])
        if len(tokens) > len(antecedentes) + 1 and isinstance(tokens[-1], str)
        else 1.0
    )
    return Regla(consecuente, antecedentes, confianza)


# Parser de tripleta con extensión opcional
tripleta_parser = (
    termino + termino + termino + Optional(punto) + Optional(extension)
).setParseAction(crear_tripleta)

# Tripleta
# tripleta_parser = (termino + termino + termino + Optional(extension)).setParseAction(crear_tripleta)
# Parser de regla: consecuente <- antecedente1, antecedente2, ... [confianza]
regla_parser = (
    tripleta_parser
    + flecha
    + delimitedList(tripleta_parser, delim=",")
    + Optional(punto)
    + Optional(extension)
).setParseAction(crear_regla)

#
# Funciones
#
# def parsear_tripleta_archivo(input: str) -> Tripleta:
#     """Parsear un string en una Tripleta"""
#     return tripleta_parser_archivo.parseString(input, parseAll=True)[0]


def parsear_tripleta(input: str) -> Tripleta:
    """Parsear un string en una Tripleta"""
    return tripleta_parser.parseString(input, parseAll=True)[0]


def parsear_regla(input: str) -> Regla:
    """Parsear un string en una Regla"""
    return regla_parser.parseString(input, parseAll=True)[0]


def parsear_consulta(input: str) -> tuple[Tripleta, str]:
    """
    Parsea la entrada de una consulta/comando introducida por un usuario.
    Retorna (Tripleta, tipo) donde tipo es:
    - 'consulta': consulta (termina en ?)
    - 'hecho': agregar hecho (termina en .)
    - 'revocar': revocar hecho (empieza por 'no' y termina en .)
    - 'descubrir' : 'descubrir nuevos hechos (descubrir!)'
    - 'razonar': consulta con razonamiento (empieza por 'razona si ... ?')
    """
    input_usr = input.strip()
    # Separar el input en partes (lista)
    partes = input_usr.split()
    if not partes:
        raise ValueError("La consulta no puede estar vacía")

    # Consultas de 'descubrir!'
    if partes[0].lower() == "descubrir!":
        if len(partes) != 1:
            raise ValueError('El comando "descubrir!" no lleva argumentos')
        return None, "descubrir"

    # Consultas de 'razona si'
    if input_usr.startswith("razona si"):
        # Quitando ['razona', 'si'] el resto de la lista tiene que ser de tamaño 4.
        # [Sujeto, Predicado, Objeto, ?]
        if len(partes) != 6:  # ['razona','si',S,P,O,'?']
            raise ValueError("La consulta de razonamiento debe ser: razona si S P O ?")
        if partes[-1] != "?":
            raise ValueError("La consulta de razonamiento debe terminar en ?")
        tripleta_str = " ".join(partes[2:5])
        tripleta = parsear_tripleta(tripleta_str)

        return tripleta, "razonar"

    # Consultas de revocación 'no S P O .'
    if partes[0].lower() == "no":
        # Debe tener: ['no', S, P, O, '.']
        if len(partes) != 5:
            raise ValueError("La revocación debe ser: no S P O .")
        if partes[-1] != ".":
            raise ValueError("La revocación debe terminar en .")
        tripleta_str = " ".join(partes[1:4])
        tripleta = parsear_tripleta(tripleta_str)
        return tripleta, "revocar"

    # Consultas normales: s p o ?
    # Agregar hechos s p o . 
    # Agregar hechos con confianza s p o . [confianza]
    if len(partes) < 4 or len(partes) > 5:
        raise ValueError("Formato de consulta inválido: debe ser S P O ? // S P O . // S P O . [confianza]")

    # El cuarto elemento debe ser ? o .
    if partes[3] not in ["?", "."]:
        raise ValueError("La consulta debe terminar en ? (consulta) o . (agregar hecho)")

    tipo = "consulta" if partes[3] == "?" else "hecho"

    # Parsear la tripleta
    if tipo == "hecho":
        # Si lleva factor de confianza.
        if len(partes) == 5:
            tripleta_str = " ".join(partes[:3]) + " . " + partes[4]
        else:
            # Si no lleva factor de confianza
            tripleta_str = " ".join(partes[:3]) + " . "
    else:
        # Si es una consulta normal S P O ?
        tripleta_str = " ".join(partes[:3])
    
    tripleta = parsear_tripleta(tripleta_str)

    return tripleta, tipo
