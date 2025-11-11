"""Motor de consultas de la base de conocimiento"""
from sbc.ed import Tripleta, Regla, Sustitucion, es_variable
from sbc.unificar import unify

def query(tripleta: Tripleta, kb: dict):
    """
    Consulta la base de conocimiento para todas las formas en las que se pueda satisfacer una tripleta.
    Produce una sustitución por cada match exitoso.
    """

    for hecho in kb['hechos']:
        # item es un hecho
        match unify(tripleta, hecho):
            case []:
                continue
            case [ss]:
                yield ss

    for regla in kb['reglas']:
        # Prueba a unificar con el consecuente
        match unify(tripleta, regla.get_consecuente()):
            case []:
                continue
            case [ss]:
                # Necesitamos satisfacer TODOS los antecedentes
                # Usar query_all para verificar que todos se cumplan
                resultados = list(query_all(regla.get_antecedentes(), kb, ss))
                for resultado_ss in resultados:
                    yield resultado_ss

def query_all(antecedentes: list[Tripleta], kb: dict, ss_inicial: Sustitucion):
    """
    Satisface TODOS los antecedentes de una regla.
    Genera todas las combinaciones de sustituciones que satisfacen todos los antecedentes.
    """
    if not antecedentes:
        yield ss_inicial
        return

    # Tomar el primer antecedente
    primer_antecedente = antecedentes[0]
    resto_antecedentes = antecedentes[1:]

    # Aplicar la sustitución actual al primer antecedente
    primer_antecedente_ss = primer_antecedente.aplicar_sustitucion(ss_inicial)

    # Consultar el primer antecedente
    for ss_primer in query(primer_antecedente_ss, kb):
        # Combinar sustituciones
        merged = Sustitucion(ss_inicial.mappings.copy())
        merged.mappings.update(ss_primer.mappings)

        # Recursivamente satisfacer el resto de antecedentes
        for ss_resto in query_all(resto_antecedentes, kb, merged):
            yield ss_resto
            
def descubrir(kb: dict) -> list[Tripleta]:
    """
    Encadenamiento hacia delante: descubre nuevos hechos aplicando reglas.
    Retorna la lista de nuevos hechos descubiertos y los agrega a la KB.
    """

    nuevos_hechos = []

    for regla in kb['reglas']:
        # Intentar satisfacer todos los antecedentes de la regla
        # usando los hechos actuales
        for ss in query_all(regla.antecedentes, kb, Sustitucion()):
            # Si se satisfacen todos los antecedentes, aplicar sustitución al consecuente
            nuevo_hecho = regla.consecuente.aplicar_sustitucion(ss)

            # Verificar que el nuevo hecho no tenga variables
            tiene_variables = any(es_variable(t) for t in nuevo_hecho.terminos())
            if tiene_variables:
                continue

            # Verificar que el nuevo hecho no exista ya en la KB
            if nuevo_hecho not in kb['hechos'] and nuevo_hecho not in nuevos_hechos:
                nuevos_hechos.append(nuevo_hecho)

    # Agregar los nuevos hechos a la KB
    kb['hechos'].extend(nuevos_hechos)

    return nuevos_hechos