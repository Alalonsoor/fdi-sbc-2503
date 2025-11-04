from sbc.ed import Tripleta, Sustitucion, es_literal

def unify_terms(t1: str, t2: str, ss: Sustitucion) -> Sustitucion:
    """
    Unifica dos terminos

    """
    match (es_literal(t1), es_literal(t2)):
        ...

def unify(x: Tripleta, y: Tripleta, ss = Sustitucion | None) -> list[Sustitucion]:
    """
    Unifica dos tripletas x, y. 
    Retorna una lista con una Sustitucion si  tiene éxito, lista vacía en caso contrario.
    """

    if ss is None:
        ss = Sustitucion()

    sx, px, ox = x
    sy, py, oy = y

    # Unificar sujetos
    ss = unify_terms(sx, sy, ss)
    if ss is None:
        return []
    # Unificar predicados
    ss = unify_terms(px, py, ss)
    if ss is None:
        return []
    # Unificar objeto
    ss = unify_terms(ox, oy, ss)
    if ss is None:
        return []

    return [ss]    