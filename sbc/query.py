"""Motor de consultas de la base de conocimiento"""
from sbc.ed import Tripleta, Sustitucion
from sbc.unificar import unify

def query(tripleta: Tripleta, kb: dict):
    """
    Consulta la base de conocimiento para todas las formas en las que se pueda satisfacer una tripleta.
    Produce una sustitución por cada match exitoso.
    """
    # Primero, buscar en hechos directos
    for hecho in kb['hechos']:
        match unify(tripleta, hecho):
            case [ss]:
                yield ss

    # Segundo, buscar en reglas
    for regla in kb['reglas']:
        # Prueba a unificar con el consecuente
        match unify(tripleta, regla.get_consecuente()):
            case [ss]:
                # Satisfacer TODOS los antecedentes
                for resultado_ss in query_antecedentes(regla.get_antecedentes(), kb, ss):
                    yield resultado_ss

def query_antecedentes(antecedentes: list[Tripleta], kb: dict, ss_inicial: Sustitucion):
    """
    Satisface TODOS los antecedentes de una regla recursivamente.
    """
    # CASO BASE
    # Si no hay más antecedentes, hemos terminado todas las comprobaciones
    if not antecedentes:
        yield ss_inicial
        return
    
    # CASO RECURSIVO
    # Tomar el primer antecedente
    primer_antecedente = antecedentes[0]
    # En caso de solo tener un elemento (no existe índice 1) antecedentes[1:] devolverá una lista vacía.
    resto_antecedentes = antecedentes[1:]

    # Aplicar la sustitución actual al primer antecedente
    primer_antecedente_ss = primer_antecedente.aplicar_sustitucion(ss_inicial)

    # Crea todas las combinaciones posibles
    # Consultar el primer antecedente
    for ss_primer in query(primer_antecedente_ss, kb):
        # Combinar sustituciones
        merged = Sustitucion(ss_inicial.get_mappings().copy())
        merged.get_mappings().update(ss_primer.get_mappings())

        # Recursivamente satisfacer el resto de antecedentes
        for ss_resto in query_antecedentes(resto_antecedentes, kb, merged):
            yield ss_resto
            
def descubrir(kb: dict) -> list[Tripleta]:
    """
    Encadenamiento hacia delante: descubre nuevos hechos aplicando reglas.
    Retorna la lista de nuevos hechos descubiertos y los agrega a la KB.
    """
    nuevos_hechos = []

    for regla in kb['reglas']:
        for ss in query_antecedentes(regla.get_antecedentes(), kb, Sustitucion()):
            # Si se satisfacen todos los antecedentes (recursivamente), aplicar sustitución al consecuente
            nuevo_hecho = regla.get_consecuente().aplicar_sustitucion(ss)

            # Verificar que el nuevo hecho no exista ya en la KB
            if nuevo_hecho not in kb['hechos'] and nuevo_hecho not in nuevos_hechos:
                nuevos_hechos.append(nuevo_hecho)

    # Agregar los nuevos hechos a la KB
    kb['hechos'].extend(nuevos_hechos)

    return nuevos_hechos

def razonar(tripleta: Tripleta, kb: dict) -> bool:
    """
    Realiza encadenamiento hacia atrás.
    Retorna True si la tripleta puede demostrarse, False en caso contrario.
    """
    # Si hay algún caso que lo satisface, retorna True
    for _ in query(tripleta, kb):
        return True
    
    return False