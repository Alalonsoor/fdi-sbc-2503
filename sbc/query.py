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