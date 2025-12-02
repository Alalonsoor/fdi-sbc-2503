import pytest
from sbc.ed import Tripleta, Regla
from sbc.query import descubrir


def test_descubrir_sin_hechos_ni_reglas():
    """Test: descubrir en KB vacía no devuelve nada"""
    kb = {"hechos": [], "reglas": []}
    resultados = list(descubrir(kb))
    assert resultados == []


def test_descubrir_solo_hechos_sin_confianza():
    """Test: descubrir con hechos sin confianza (confianza = 1.0)"""
    hechos = [
        Tripleta("tomate", "tipo", "verdura", confianza=1.0),
        Tripleta("manzana", "tipo", "fruta", confianza=1.0),
    ]
    kb = {"hechos": hechos, "reglas": []}
    resultados = list(descubrir(kb))

    # Sin reglas, no se descubre nada nuevo
    assert resultados == []


def test_descubrir_regla_simple_sin_confianza():
    """Test: descubrir con regla simple (confianza = 1.0)"""
    hechos = [
        Tripleta("tomate", "color", "rojo", confianza=1.0),
    ]
    reglas = [
        Regla(
            consecuente=Tripleta("X", "tipo", "verdura", confianza=1.0),
            antecedentes=[Tripleta("X", "color", "rojo", confianza=1.0)],
            confianza=1.0,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}
    resultados = list(descubrir(kb))

    # Debe inferir: tomate tipo verdura [1.0]
    assert len(resultados) == 1
    assert resultados[0].terminos() == ["tomate", "tipo", "verdura"]
    assert resultados[0].confianza == 1.0


def test_descubrir_regla_con_confianza_consecuente():
    """Test: descubrir con regla que tiene confianza en consecuente"""
    hechos = [
        Tripleta("tomate", "color", "rojo", confianza=1.0),
    ]
    reglas = [
        Regla(
            consecuente=Tripleta("X", "tipo", "verdura", confianza=0.8),
            antecedentes=[Tripleta("X", "color", "rojo", confianza=1.0)],
            confianza=1.0,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}
    resultados = list(descubrir(kb))

    # Inferencia: tomate tipo verdura con MIN(0.8, 1.0) = 0.8
    assert len(resultados) == 1
    assert resultados[0].terminos() == ["tomate", "tipo", "verdura"]
    assert resultados[0].confianza == 0.8


def test_descubrir_regla_con_confianza_antecedente():
    """Test: descubrir con regla donde el antecedente tiene confianza"""
    hechos = [
        Tripleta("tomate", "color", "rojo", confianza=0.7),
    ]
    reglas = [
        Regla(
            consecuente=Tripleta("X", "tipo", "verdura", confianza=1.0),
            antecedentes=[Tripleta("X", "color", "rojo", confianza=1.0)],
            confianza=1.0,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}
    resultados = list(descubrir(kb))

    # Inferencia: MIN(1.0 consecuente, 0.7 hecho) = 0.7
    assert len(resultados) == 1
    assert resultados[0].terminos() == ["tomate", "tipo", "verdura"]
    assert resultados[0].confianza == 0.7


def test_descubrir_regla_multiples_antecedentes_min():
    """Test: descubrir con regla con múltiples antecedentes (operador MIN)"""
    hechos = [
        Tripleta("pizza", "ingrediente", "tomate", confianza=0.9),
        Tripleta("tomate", "contiene", "licopeno", confianza=0.8),
    ]
    reglas = [
        Regla(
            consecuente=Tripleta("X", "saludable", "si", confianza=1.0),
            antecedentes=[
                Tripleta("X", "ingrediente", "tomate", confianza=1.0),
                Tripleta("tomate", "contiene", "licopeno", confianza=1.0),
            ],
            confianza=1.0,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}
    resultados = list(descubrir(kb))

    # Inferencia: MIN(0.9, 0.8) = 0.8
    assert len(resultados) == 1
    assert resultados[0].terminos() == ["pizza", "saludable", "si"]
    assert resultados[0].confianza == 0.8


def test_descubrir_multiples_reglas_mismo_hecho_max():
    """Test: descubrir con múltiples reglas generando el mismo hecho (operador MAX)"""
    hechos = [
        Tripleta("pizza", "ingrediente", "queso", confianza=1.0),
        Tripleta("pizza", "ingrediente", "leche", confianza=1.0),
    ]
    reglas = [
        # Regla 1: X contiene lactosa <- X ingrediente queso [0.7]
        Regla(
            consecuente=Tripleta("X", "contiene", "lactosa", confianza=1.0),
            antecedentes=[Tripleta("X", "ingrediente", "queso", confianza=1.0)],
            confianza=0.7,
        ),
        # Regla 2: X contiene lactosa <- X ingrediente leche [0.9]
        Regla(
            consecuente=Tripleta("X", "contiene", "lactosa", confianza=1.0),
            antecedentes=[Tripleta("X", "ingrediente", "leche", confianza=1.0)],
            confianza=0.9,
        ),
    ]
    kb = {"hechos": hechos, "reglas": reglas}
    resultados = list(descubrir(kb))

    # Debe aplicar MAX(0.7, 0.9) = 0.9 y devolver UNA SOLA versión del hecho
    hechos_lactosa = [
        t for t in resultados if t.terminos() == ["pizza", "contiene", "lactosa"]
    ]
    assert len(hechos_lactosa) == 1
    assert hechos_lactosa[0].confianza == 0.9


def test_descubrir_cadena_inferencias():
    """Test: descubrir con cadena de inferencias (reglas que generan hechos para otras reglas)"""
    hechos = [
        Tripleta("pizza", "ingrediente", "trigo", confianza=0.8),
    ]
    reglas = [
        # Regla 1: X contiene gluten <- X ingrediente trigo
        Regla(
            consecuente=Tripleta("X", "contiene", "gluten", confianza=1.0),
            antecedentes=[Tripleta("X", "ingrediente", "trigo", confianza=1.0)],
            confianza=0.95,
        ),
        # Regla 2: X apto celiaco no <- X contiene gluten
        Regla(
            consecuente=Tripleta("X", "apto_celiaco", "no", confianza=1.0),
            antecedentes=[Tripleta("X", "contiene", "gluten", confianza=1.0)],
            confianza=1.0,
        ),
    ]
    kb = {"hechos": hechos, "reglas": reglas}

    # Una sola pasada genera ambos hechos (encadenamiento hacia adelante)
    resultados = list(descubrir(kb))

    # Inferencia 1: pizza contiene gluten [MIN(1.0, 0.95, 0.8) = 0.8]
    assert any(
        t.terminos() == ["pizza", "contiene", "gluten"] and t.confianza == 0.8
        for t in resultados
    )

    # Inferencia 2: pizza apto_celiaco no [MIN(1.0, 1.0, 0.8) = 0.8]
    assert any(
        t.terminos() == ["pizza", "apto_celiaco", "no"] and t.confianza == 0.8
        for t in resultados
    )


def test_descubrir_no_duplica_hechos_existentes():
    """Test: descubrir no duplica hechos que ya existen en la KB"""
    hechos = [
        Tripleta("tomate", "tipo", "verdura", confianza=1.0),
        Tripleta("tomate", "color", "rojo", confianza=1.0),
    ]
    reglas = [
        # Regla que generaría el mismo hecho que ya existe
        Regla(
            consecuente=Tripleta("tomate", "tipo", "verdura", confianza=1.0),
            antecedentes=[Tripleta("tomate", "color", "rojo", confianza=1.0)],
            confianza=1.0,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}
    resultados = list(descubrir(kb))

    # No debe devolver nada porque el hecho ya existe
    assert len(resultados) == 0


def test_descubrir_actualiza_confianza_si_nueva_es_mayor():
    """Test: descubrir actualiza la confianza si una nueva inferencia tiene mayor confianza (MAX)"""
    hechos = [
        Tripleta("pizza", "ingrediente", "queso", confianza=1.0),
        Tripleta("pizza", "ingrediente", "leche", confianza=1.0),
        # Hecho existente con confianza baja
        Tripleta("pizza", "contiene", "lactosa", confianza=0.5),
    ]
    reglas = [
        # Regla que genera el mismo hecho con mayor confianza
        Regla(
            consecuente=Tripleta("X", "contiene", "lactosa", confianza=1.0),
            antecedentes=[Tripleta("X", "ingrediente", "leche", confianza=1.0)],
            confianza=0.9,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}
    resultados = list(descubrir(kb))

    # Debe devolver el hecho actualizado con MAX(0.5 existente, 0.9 nueva) = 0.9
    hechos_lactosa = [
        t for t in resultados if t.terminos() == ["pizza", "contiene", "lactosa"]
    ]
    assert len(hechos_lactosa) == 1
    assert hechos_lactosa[0].confianza == 0.9
