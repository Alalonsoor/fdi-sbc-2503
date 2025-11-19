import pytest
from sbc.parser import parsear_consulta, parsear_tripleta, parsear_regla
from sbc.ed import Tripleta, Regla


# ============================
#  Tests parsear_tripleta / regla
# ============================

def test_parsear_tripleta_basico():
    t = parsear_tripleta("tomate tipo verdura")
    assert isinstance(t, Tripleta)
    assert t.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_regla_basica():
    r = parsear_regla("tomate tipo verdura <- tomate color rojo")
    assert isinstance(r, Regla)
    # consecuente es una Tripleta
    assert isinstance(r.consecuente, Tripleta)
    assert r.consecuente.terminos() == ["tomate", "tipo", "verdura"]
    # antecedentes es lista de Tripleta
    assert len(r.antecedentes) == 1
    assert r.antecedentes[0].terminos() == ["tomate", "color", "rojo"]


# ============================
#  Tests parsear_consulta OK
# ============================

def test_parsear_consulta_hecho():
    tripleta, tipo = parsear_consulta("tomate tipo verdura .")
    assert tipo == "hecho"
    assert isinstance(tripleta, Tripleta)
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_consulta_pregunta():
    tripleta, tipo = parsear_consulta("tomate tipo verdura ?")
    assert tipo == "consulta"
    assert isinstance(tripleta, Tripleta)
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_consulta_razonar():
    tripleta, tipo = parsear_consulta("razona si tomate tipo verdura ?")
    assert tipo == "razonar"
    assert isinstance(tripleta, Tripleta)
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_consulta_descubrir():
    tripleta, tipo = parsear_consulta("descubrir!")
    assert tipo == "descubrir"
    assert tripleta is None


# ============================
#  Tests parsear_consulta ERRORES
# ============================

def test_parsear_consulta_vacia():
    # aquí esperamos que NO pete con IndexError,
    # sino que lance un ValueError controlado
    with pytest.raises(ValueError):
        parsear_consulta("")


def test_parsear_consulta_formato_invalido_pocos_terminos():
    # Falta objeto y signo final
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("tomate tipo")
    assert "Formato de consulta inválido" in str(excinfo.value)


def test_parsear_consulta_formato_invalido_demasiados_terminos():
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("tomate tipo verdura extra ?")
    assert "Formato de consulta inválido" in str(excinfo.value)


def test_parsear_consulta_ultimo_no_valido():
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("tomate tipo verdura !")
    assert "debe terminar en ? (consulta) o . (hecho)" in str(excinfo.value)


def test_parsear_consulta_razonar_longitud_incorrecta():
    # le falta el objeto
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("razona si tomate tipo ?")
    assert "razona si S P O ?" in str(excinfo.value)


def test_parsear_consulta_razonar_sin_interrogacion():
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("razona si tomate tipo verdura .")
    assert "terminar en ?" in str(excinfo.value)


def test_parsear_consulta_descubrir_con_argumentos():
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("descubrir! algo")
    assert 'descubrir!' in str(excinfo.value)