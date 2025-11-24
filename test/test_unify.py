import pytest
from sbc.ed import Tripleta, Sustitucion
from sbc.unificar import unify, unify_terms, ocurre


# ============================
#  Tests unify()
# ============================

def test_unify_literales():
    """Test: unify con literales iguales y diferentes"""
    # Iguales
    r = unify(
        Tripleta("tomate", "tipo", "verdura"),
        Tripleta("tomate", "tipo", "verdura")
    )
    assert len(r) == 1
    
    # Diferentes
    r = unify(
        Tripleta("tomate", "tipo", "verdura"),
        Tripleta("lechuga", "tipo", "verdura")
    )
    assert len(r) == 0


def test_unify_con_variables():
    """Test: unify con variables en diferentes posiciones"""
    # Variable en sujeto
    r = unify(
        Tripleta("X", "tipo", "verdura"),
        Tripleta("tomate", "tipo", "verdura")
    )
    assert len(r) == 1
    assert r[0].get("X") == "tomate"
    
    # Variables en ambos lados
    r = unify(
        Tripleta("X", "tipo", "Y"),
        Tripleta("tomate", "tipo", "verdura")
    )
    assert len(r) == 1
    assert r[0].get("X") == "tomate"
    assert r[0].get("Y") == "verdura"
    
    # Dos variables que unifican entre sí
    r = unify(
        Tripleta("X", "tipo", "verdura"),
        Tripleta("Y", "tipo", "verdura")
    )
    assert len(r) == 1
    assert r[0].get("X") == "Y" or r[0].get("Y") == "X"


def test_unify_con_sustitucion_previa():
    """Test: unify respeta sustituciones previas"""
    ss = Sustitucion()
    ss.add("X", "tomate")
    
    r = unify(
        Tripleta("X", "tipo", "verdura"),
        Tripleta("tomate", "tipo", "verdura"),
        ss
    )
    assert len(r) == 1
    
    # Falla si la sustitucion previa es inconsistente
    ss = Sustitucion()
    ss.add("X", "lechuga")
    
    r = unify(
        Tripleta("X", "tipo", "verdura"),
        Tripleta("tomate", "tipo", "verdura"),
        ss
    )
    assert len(r) == 0


# ============================
#  Tests unify_terms()
# ============================

def test_unify_terms():
    """Test: unify_terms con diferentes combinaciones"""
    ss = Sustitucion()
    
    # Literal con literal iguales
    result = unify_terms("tomate", "tomate", ss)
    assert result is not None
    
    # Literal con literal diferentes
    result = unify_terms("tomate", "lechuga", Sustitucion())
    assert result is None
    
    # Variable con literal
    ss = Sustitucion()
    result = unify_terms("X", "tomate", ss)
    assert result is not None
    assert result.get("X") == "tomate"
    
    # Variable con variable
    ss = Sustitucion()
    result = unify_terms("X", "Y", ss)
    assert result is not None
    assert result.get("X") == "Y" or result.get("Y") == "X"


# ============================
#  Tests ocurre()
# ============================

def test_ocurre():
    """Test: ocurre detecta ciclos y apariciones"""
    ss = Sustitucion()
    
    # Variable no aparece en literal
    assert ocurre("X", "tomate", ss) is False
    
    # Variable aparece en sí misma
    assert ocurre("X", "X", ss) is True
    
    # Variable aparece si term apunta a ella
    ss.add("Y", "X")
    assert ocurre("X", "Y", ss) is True
