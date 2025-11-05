"""Motor de consultas de la base de conocimiento"""
from sbc.ed import Tripleta, Regla, Sustitucion, es_variable
from sbc.unificar import unify

def query(tripleta: Tripleta, kb: list[Tripleta | Regla]):
    """
    Consulta la base de conocimiento para todas las formas en las que se pueda satisfacer una tripleta.
    Produce una sustitución por cada match exitoso.
    """

    for item in kb:
        match item:
            case Regla(consecuente, antecedentes):
                # Prueba a unificar con el consecuente
                match unify(tripleta, consecuente):
                    case []:
                        continue
                    case [ss]:
                        # Necesitamos satisfacer TODOS los antecedentes
                        # Usar query_all para verificar que todos se cumplan
                        resultados = list(query_all(antecedentes, kb, ss))
                        for resultado_ss in resultados:
                            yield resultado_ss

            case Tripleta():
                # item es un hecho
                match unify(tripleta, item):
                    case []:
                        continue
                    case [ss]:
                        yield ss

def query_all(antecedentes: list[Tripleta], kb: list[Tripleta | Regla], ss_inicial: Sustitucion):
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
            
def descubrir(kb: list[Tripleta | Regla]) -> list[Tripleta]:
    """
    Encadenamiento hacia delante: descubre nuevos hechos aplicando reglas.
    Retorna la lista de nuevos hechos descubiertos y los agrega a la KB.
    """
    nuevos_hechos = []

    # Obtener solo los hechos (no reglas) de la KB
    hechos_actuales = [item for item in kb if isinstance(item, Tripleta)]

    # Iterar sobre cada regla
    for item in kb:
        if isinstance(item, Regla):
            regla = item

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
                if nuevo_hecho not in hechos_actuales and nuevo_hecho not in nuevos_hechos:
                    nuevos_hechos.append(nuevo_hecho)

    # Agregar los nuevos hechos a la KB
    kb.extend(nuevos_hechos)

    return nuevos_hechos