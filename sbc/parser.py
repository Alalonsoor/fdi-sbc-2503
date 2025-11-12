"""Parsers para tripletas y reglas usando pyparsing"""
from pyparsing import Word, alphanums, Suppress, alphas, delimitedList
from sbc.ed import Tripleta, Regla

# Definir variables: cualquier string que empiece con mayuscula
variable = Word(alphas.upper(), alphanums + '_'  + 'áéíóúñÁÉÍÓÚÑ')

# Literal: empieza con minuscula
literal = Word(alphas.lower(), alphanums + '_' + 'áéíóúñÁÉÍÓÚÑ')

# Termino o es literal o variable
termino = variable | literal

# Si se detecta '<-' se ignora
flecha = Suppress('<-')
# Si se detecta ',' se ignora (para separar multiples antecedentes)
coma = Suppress(',')

def crear_tripleta(tokens)->Tripleta:
    """Convertir tokens a tripleta"""
    return Tripleta(str(tokens[0]),str(tokens[1]),str(tokens[2]))

def crear_regla(tokens)->Regla:
    """Convertir tokens a regla con multiples antecedentes"""
    consecuente = tokens[0]
    # tokens[1:] son todos los antecedentes
    antecedentes = list(tokens[1:])
    return Regla(consecuente, antecedentes)

# Parser de tripleta
tripleta_parser = (termino + termino + termino).setParseAction(crear_tripleta)
# Parser de regla: consecuente <- antecedente1, antecedente2, ...
regla_parser = (tripleta_parser + flecha + delimitedList(tripleta_parser, delim=',')).setParseAction(crear_regla)

#
# Funciones
#

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
    """

    # Separar el input en partes
    partes = input.strip().split()
    
    if partes.lower() == 'descubrir!':
        return None, 'descubrir'

    if len(partes) != 4:
        raise ValueError(f'La consulta tiene que ser 3 terminos + (? o .)')

    # El ultimo elemento debe ser ? o .
    ultimo = partes[3]
    if ultimo not in ['?', '.']:
        raise ValueError(f'La consulta debe terminar en ? (consulta) o . (hecho)')

    tipo = 'consulta' if ultimo == '?' else 'hecho'

    # Parsear la tripleta (primeros 3 elementos)
    tripleta_str = ' '.join(partes[:3])
    tripleta = parsear_tripleta(tripleta_str)

    return tripleta, tipo
