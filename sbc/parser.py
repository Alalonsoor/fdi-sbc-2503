"""Parsers para tripletas y reglas usando pyparsing"""
from pyparsing import Word, alphanums, Suppress, Literal
from sbc.ed import Tripleta, Regla

# Definir variables
# Variable puede ser ? o ?X o ?Plato
variable = Word('?', alphanums + '_') | Literal('?')

# Literal
literal = Word(alphanums + '_')

# Termino o es literal o variable
termino = literal | variable

# Si se detecta '<-' se ignora
flecha = Suppress('<-')

def crear_tripleta(tokens)->Tripleta:
    """Convertir tokens a tripleta"""
    return Tripleta(str(tokens[0]),str(tokens[1]),str(tokens[2]))

def crear_regla(tokens)->Regla:
    """Convertir tokens a regla"""
    return Regla(tokens[0],tokens[1])

# Parser de tripleta
tripleta_parser = (termino + termino + termino).setParseAction(crear_tripleta)
# Parser de regla
regla_parser = (tripleta_parser + flecha + tripleta_parser).setParseAction(crear_regla)

#
# Funciones
#

def parsear_tripleta(input: str) -> Tripleta:
    """Parsear un string en una Tripleta"""
    return tripleta_parser.parseString(input, parseAll=True)[0]

def parsear_regla(input: str) -> Regla:
    """Parsear un string en una Regla"""
    return regla_parser.parseString(input, parseAll=True)[0]

def parsear_consulta(input: str) -> Tripleta:
    """
    Parsea la entrada de una consulta introducida por un usuario.
    Convierte signos '?' en '?X', '?Y', '?Z' para poder aplicar sustituciones.
    """

    # Separar el input en partes
    partes = input.strip().split()

    if len(partes) != 3:
        raise ValueError(f'La consulta tiene que ser exactamente 3 terminos')
    
    # Evitar consultar por prediado 'Tomate ? Rojo'
    if partes[1] == '?' and partes[0] != '?' and partes[2] != '?':
        raise ValueError(f'No se puede consultar por predicado')

    # Reemplazar ? por ?X, ?Y, ?Z
    idx = 0
    resultado = []
    for parte in partes:
        if parte == '?':
            resultado.append(f'?{chr(88 + idx)}')
            idx += 1
        else:
            resultado.append(parte)
    
    return Tripleta(resultado[0], resultado[1], resultado[2])
