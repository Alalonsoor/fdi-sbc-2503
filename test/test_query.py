import pytest
from sbc.ed import Tripleta, Regla, Sustitucion
from sbc.query import query, query_antecedentes, razonar


# ============================
#  Tests query() - Hechos
# ============================


def test_query_hechos():
    """Test: query busca en hechos con diferentes casos"""
    hechos = [
        Tripleta("tomate", "tipo", "verdura", confianza=0.8),
        Tripleta("lechuga", "tipo", "verdura", confianza=0.9),
    ]
    kb = {"hechos": hechos, "reglas": []}

    # Caso 1: coincidencia exacta
    r = list(query(Tripleta("tomate", "tipo", "verdura"), kb))
    assert len(r) == 1 and r[0][1] == 0.8

    # Caso 2: con variable
    r = list(query(Tripleta("X", "tipo", "verdura"), kb))
    assert len(r) == 2
    assert {ss.get("X") for ss, _ in r} == {"tomate", "lechuga"}

    # Caso 3: sin coincidencias
    r = list(query(Tripleta("manzana", "tipo", "fruta"), kb))
    assert len(r) == 0


# ============================
#  Tests query() - Reglas
# ============================


def test_query_reglas_confianza():
    """Test: query con reglas y propagación de confianza (MIN)"""
    hechos = [Tripleta("tomate", "color", "rojo", confianza=0.6)]
    reglas = [
        # Regla con confianza en consecuente
        Regla(
            consecuente=Tripleta("X", "tipo", "verdura", confianza=0.8),
            antecedentes=[Tripleta("X", "color", "rojo", confianza=1.0)],
            confianza=1.0,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}

    r = list(query(Tripleta("tomate", "tipo", "verdura"), kb))
    assert len(r) == 1
    # MIN(consecuente=0.8, regla=1.0, hecho=0.6) = 0.6
    assert r[0][1] == 0.6


def test_query_reglas_multiples_antecedentes():
    """Test: query con múltiples antecedentes (MIN)"""
    hechos = [
        Tripleta("pizza", "ingrediente", "tomate", confianza=0.9),
        Tripleta("tomate", "contiene", "licopeno", confianza=0.7),
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

    r = list(query(Tripleta("pizza", "saludable", "si"), kb))
    assert len(r) == 1
    # MIN(1.0, 1.0, 0.9, 0.7) = 0.7
    assert r[0][1] == 0.7


def test_query_regla_falla():
    """Test: query con regla cuyo antecedente no se satisface"""
    hechos = [Tripleta("tomate", "color", "verde", confianza=1.0)]
    reglas = [
        Regla(
            consecuente=Tripleta("X", "tipo", "verdura", confianza=1.0),
            antecedentes=[Tripleta("X", "color", "rojo", confianza=1.0)],
            confianza=1.0,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}

    r = list(query(Tripleta("tomate", "tipo", "verdura"), kb))
    assert len(r) == 0


def test_query_hecho_y_regla():
    """Test: query satisfecha por hecho Y regla"""
    hechos = [
        Tripleta("tomate", "tipo", "verdura", confianza=0.9),
        Tripleta("tomate", "color", "rojo", confianza=1.0),
    ]
    reglas = [
        Regla(
            consecuente=Tripleta("X", "tipo", "verdura", confianza=1.0),
            antecedentes=[Tripleta("X", "color", "rojo", confianza=1.0)],
            confianza=0.95,
        )
    ]
    kb = {"hechos": hechos, "reglas": reglas}

    r = list(query(Tripleta("tomate", "tipo", "verdura"), kb))
    assert len(r) == 2
    confs = {conf for _, conf in r}
    assert confs == {0.9, 0.95}


# ============================
#  Tests query_antecedentes()
# ============================


def test_query_antecedentes():
    """Test: query_antecedentes con diferentes casos"""
    hechos = [
        Tripleta("pizza", "ingrediente", "tomate", confianza=0.9),
        Tripleta("tomate", "color", "rojo", confianza=0.7),
    ]
    kb = {"hechos": hechos, "reglas": []}

    # Caso 1: sin antecedentes (caso base)
    r = list(query_antecedentes([], kb, Sustitucion()))
    assert len(r) == 1 and r[0][1] == 1.0

    # Caso 2: un antecedente
    r = list(query_antecedentes([Tripleta("X", "color", "rojo")], kb, Sustitucion()))
    assert len(r) == 1 and r[0][0].get("X") == "tomate" and r[0][1] == 0.7

    # Caso 3: dos antecedentes (MIN)
    r = list(
        query_antecedentes(
            [
                Tripleta("X", "ingrediente", "tomate"),
                Tripleta("tomate", "color", "rojo"),
            ],
            kb,
            Sustitucion(),
        )
    )
    assert len(r) == 1 and r[0][1] == 0.7  # MIN(0.9, 0.7)

    # Caso 4: falla primer antecedente
    r = list(
        query_antecedentes(
            [
                Tripleta("pizza", "ingrediente", "queso"),
                Tripleta("tomate", "color", "rojo"),
            ],
            kb,
            Sustitucion(),
        )
    )
    assert len(r) == 0


# ============================
#  Tests razonar()
# ============================


def test_razonar():
    """Test: razonar devuelve True/False según satisfacción"""
    hechos = [Tripleta("tomate", "tipo", "verdura", confianza=1.0)]
    kb = {"hechos": hechos, "reglas": []}

    assert razonar(Tripleta("tomate", "tipo", "verdura"), kb) is True
    assert razonar(Tripleta("manzana", "tipo", "fruta"), kb) is False
