from sbc.ed import Tripleta, Sustitucion, es_literal

def unify_terms(t1: str, t2: str, ss: Sustitucion) -> Sustitucion:
    """
    Unifica dos terminos
    Retorna las sustituciones actualizadas si tiene exito, None en caso contrario
    Existen 4 posibles combinaciones.
    """
    match (es_literal(t1), es_literal(t2)):
        # Caso 1: literal con literal (tomate, tomate)
        case (True, True):
            return ss if t1 == t2 else None
        
        # Caso 2: literal con variable (tomate, X)
        case (True, False):
            if t2 in ss:
                return unify_terms(t1, ss.get(t2), ss)
            ss.add(t2, t1)
            return ss
        
        # Caso 3: variable con literañ (X, tomate)
        case (False, True):
            if t1 in ss:
                return unify_terms(ss.get(t1), t2, ss)
            ss.add(t1, t2)
            return ss
        
        # Caso 4: variable con variable (X, P)
        case (False, False):
            if t1 in ss:
                return unify_terms(ss.get(t1), t2, ss)
            if t2 in ss:
                return unify_terms(t1, ss.get(t2), ss)
            # Si son la misma variable no hace falta hacer nada
            if t1 == t2:
                return ss
            ss.add(t1, t2)
            return ss

def unify(x: Tripleta, y: Tripleta, ss: Sustitucion | None = None) -> list[Sustitucion]:
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