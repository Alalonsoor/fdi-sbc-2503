"""Parsers para tripletas y reglas usando pyparsing"""
from pyparsing import Word, alphanums, Suppress, alphas, delimitedList, nums
from sbc.ed import Tripleta, Regla

# Definir variables: cualquier string que empiece con mayuscula
variable = Word(alphas.upper(), alphanums + '_'  + 'áéíóúñÁÉÍÓÚÑ')

# Literal: empieza con minuscula
literal = Word(alphas.lower() + nums, alphanums + '_' + 'áéíóúñÁÉÍÓÚÑ')

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
    - 'descubrir' : 'descubrir nuevos hechos (descubrir!)'
    - 'razonar': consulta con razonamiento (empieza por 'razona si ... ?')
    """
    input_usr = input.strip()
    # Separar el input en partes (lista)
    partes = input_usr.split()

    # Consultas de 'descubrir!'
    if partes[0].lower() == 'descubrir!':
        if len(partes) != 1:
            raise ValueError('El comando "descubrir!" no lleva argumentos')
        return None, 'descubrir'

    # Consultas de 'razona si'
    if input_usr.startswith('razona si'):
        # Quitando ['razona', 'si'] el resto de la lista tiene que ser de tamaño 4. 
        # [Sujeto, Predicado, Objeto, ?] 
        if len(partes) != 6:  # ['razona','si',S,P,O,'?']
            raise ValueError('La consulta de razonamiento debe ser: razona si S P O ?')
        if partes[-1] != '?':
            raise ValueError('La consulta de razonamiento debe terminar en ?')
        tripleta_str = ' '.join(partes[2:5])
        tripleta = parsear_tripleta(tripleta_str)

        return tripleta, 'razonar'

    # Consultas normales: s p o ?
    if len(partes) != 4:
        raise ValueError('Formato de consulta inválido: debe ser S P O ? o S P O .')

    # El ultimo elemento debe ser ? o .
    ultimo = partes[3]
    if ultimo not in ['?', '.']:
        raise ValueError(f'La consulta debe terminar en ? (consulta) o . (hecho)')

    tipo = 'consulta' if ultimo == '?' else 'hecho'

    # Parsear la tripleta (primeros 3 elementos)
    tripleta_str = ' '.join(partes[:3])
    tripleta = parsear_tripleta(tripleta_str)

    return tripleta, tipo
