"""Motor de consultas de la base de conocimiento"""

from sbc.ed import Tripleta, Sustitucion
from sbc.unificar import unify

MAX_DEPTH = 100


def query(tripleta: Tripleta, kb: dict, visitados=None, profundidad=0):
    """
    Consulta la base de conocimiento para todas las formas en las que se pueda satisfacer una tripleta.
    Produce una sustitución y confianza por cada match exitoso.

    PARÁMETROS

    tripleta: Lo que queremos probar (ej: (juan, padre, pedro))
    kb: Base de conocimiento con hechos y reglas
    visitados: Evita ciclos infinitos en la recursión
    profundidad: Controla la profundidad de inferencia
    """
    if visitados is None:
        visitados = set()
    # Limitamos la profundidad para evitar recursiones infinitas.
    if profundidad > MAX_DEPTH:
        return
    
    clave = (tripleta.sujeto, tripleta.predicado, tripleta.objeto)
    # Si ya hemos procesado esta tripleta, paramos para evitar ciclos.
    if clave in visitados:
        return
    # Si no, la marcamos como vista antes de procesar.
    visitados.add(clave)
    
    try:
        # Primero, buscar en hechos directos
        for hecho in kb["hechos"]:
            match unify(tripleta, hecho):
                case [ss]:
                    yield ss, hecho.confianza

        # Segundo, buscar en reglas
        for regla in kb["reglas"]:
            # Prueba a unificar con el consecuente
            match unify(tripleta, regla.get_consecuente()):
                case [ss]:
                    # Satisfacer TODOS los antecedentes
                    for resultado_ss, confianza_ant in query_antecedentes(
                        regla.get_antecedentes(), kb, ss, visitados, profundidad + 1
                    ):  
                        # MIN entre consecuente, regla y antecedentes
                        confianza_total = min(
                            regla.get_consecuente().confianza,
                            regla.confianza,
                            confianza_ant,
                        )
                        yield resultado_ss, confianza_total
    finally:
        # Esto garantiza que la tripleta se desmarque después del procesamiento, 
        # incluso si hay errores. Permite reutilizar la misma tripleta en diferentes 
        # ramas del árbol de búsqueda.
        visitados.discard(clave)


def query_antecedentes(antecedentes: list[Tripleta], kb: dict, ss_inicial: Sustitucion, visitados=None, profundidad=0):
    """
    Satisface TODOS los antecedentes de una regla recursivamente.
    Devuelve sustitución y confianza mínima de todos los antecedentes.
    """

    if visitados is None:
        visitados = set()
    
    # CASO BASE
    # Si no hay más antecedentes, hemos terminado todas las comprobaciones
    if not antecedentes:
        yield ss_inicial, 1.0 # Confianza máxima si no hay antecedentes
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
    for ss_primer, confianza_primer in query(primer_antecedente_ss, kb, visitados, profundidad):
        # Combinar sustituciones
        merged = Sustitucion(ss_inicial.get_mappings().copy())
        merged.get_mappings().update(ss_primer.get_mappings())

        # Recursivamente satisfacer el resto de antecedentes
        for ss_resto, confianza_resto in query_antecedentes(
            resto_antecedentes, kb, merged, visitados, profundidad
        ):
            yield ss_resto, min(confianza_primer, confianza_resto) # MIN de todas las confianzas (AND)


def descubrir(kb: dict) -> list[Tripleta]:
    """
    Encadenamiento hacia delante: descubre nuevos hechos aplicando reglas.
    Retorna la lista de nuevos hechos descubiertos y los agrega a la KB.
    """
    nuevos_hechos = []

    for regla in kb["reglas"]:
        # query_antecedentes(): Verifica si TODOS los antecedentes de la regla se cumplen
        for ss, confianza in query_antecedentes(regla.get_antecedentes(), kb, Sustitucion()):
            # Aplicar sustitución al consecuente
            nuevo_hecho = regla.get_consecuente().aplicar_sustitucion(ss)
            # MIN entre consecuente, regla y antecedentes
            nuevo_hecho.confianza = min(nuevo_hecho.confianza, regla.confianza, confianza)

            # Verificar que no exista ya en la KB
            # Caso A: no está en la kb
            if nuevo_hecho not in kb["hechos"]:
                # MAX (OR): Si ya está en nuevos_hechos, quedarse con el de mayor confianza
                encontrado = False
                for i, hecho_existente in enumerate(nuevos_hechos):
                    if nuevo_hecho == hecho_existente:
                        if nuevo_hecho.confianza > hecho_existente.confianza:
                            nuevos_hechos[i] = nuevo_hecho
                        encontrado = True
                        break
                # Si no está en nuevos_hechos, lo añadimos
                if not encontrado:
                    nuevos_hechos.append(nuevo_hecho)
            # Caso B: ya está en la kb
            else:
                for i, hecho_kb in enumerate(kb["hechos"]):
                    if nuevo_hecho == hecho_kb:
                        if nuevo_hecho.confianza > hecho_kb.confianza:
                            kb["hechos"][i] = nuevo_hecho # Actualizar en KB si la confianza es mayor
                            nuevos_hechos.append(nuevo_hecho) # Reportar como "nuevo"
                        break
    # Agregar los nuevos hechos en kb y retornar.                    
    kb["hechos"].extend(nuevos_hechos)
    return nuevos_hechos


def razonar(tripleta: Tripleta, kb: dict) -> bool:
    """
    Realiza encadenamiento hacia atrás.
    Retorna True si la tripleta puede demostrarse, False en caso contrario.
    """
    # Si hay algún caso que lo satisface, retorna True
    for _, _ in query(tripleta, kb):
        return True

    return False
