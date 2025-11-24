import pytest
from sbc.parser import parsear_consulta, parsear_tripleta, parsear_regla
from sbc.ed import Tripleta, Regla


# ============================
#  Tests EBNF - Sintaxis Básica
# ============================

def test_literal_minuscula():
    """Test: literal = minus { caracter }"""
    t = parsear_tripleta("tomate tipo verdura")
    assert t.sujeto == "tomate"
    assert t.predicado == "tipo"
    assert t.objeto == "verdura"

def test_variable_mayuscula():
    """Test: variable = mayus { caracter }"""
    t = parsear_tripleta("X tipo verdura")
    assert t.sujeto == "X"
    
def test_literal_con_numeros_y_guionbajo():
    """Test: caracter = minus | mayus | digito | "_" """
    t = parsear_tripleta("tomate_123 tipo_2 verdura_ABC")
    assert t.sujeto == "tomate_123"
    assert t.predicado == "tipo_2"
    assert t.objeto == "verdura_ABC"

# ============================
#  Tests EBNF - Tripleta
# ============================

def test_tripleta_basica():
    """Test: tripleta = termino " " termino " " termino"""
    t = parsear_tripleta("tomate tipo verdura")
    assert isinstance(t, Tripleta)
    assert t.terminos() == ["tomate", "tipo", "verdura"]

# ============================
#  Tests EBNF - Afirmación
# ============================

def test_afirmacion_sin_extension():
    """Test: afirmacion = tripleta "." [ extension ]"""
    # Sin extensión (confianza = 1.0 por defecto)
    t = parsear_tripleta("tomate tipo verdura")
    assert t.confianza == 1.0

def test_afirmacion_con_extension_difusa():
    """Test: afirmacion = tripleta "." [ extension ] con difusa"""
    t = parsear_tripleta("tomate tipo verdura [0.8]")
    assert t.confianza == 0.8

def test_difusa_formato_valido():
    """Test: difusa = "0." { digito } | "1" """
    t1 = parsear_tripleta("a b c [0.5]")
    assert t1.confianza == 0.5
    
    t2 = parsear_tripleta("a b c [0.95]")
    assert t2.confianza == 0.95
    
    t3 = parsear_tripleta("a b c [1]")
    assert t3.confianza == 1.0

# ============================
#  Tests EBNF - Regla
# ============================

def test_regla_simple():
    """Test: regla = tripleta "<-" tripleta { ", " tripleta } "." [ extension ]"""
    r = parsear_regla("A tipo B <- X color rojo")
    assert isinstance(r, Regla)
    assert r.get_consecuente().terminos() == ["A", "tipo", "B"]
    assert len(r.get_antecedentes()) == 1
    assert r.get_antecedentes()[0].terminos() == ["X", "color", "rojo"]

def test_regla_multiples_antecedentes():
    """Test: regla con múltiples antecedentes separados por coma"""
    r = parsear_regla("A tipo B <- X color rojo, Y tamaño grande")
    assert len(r.get_antecedentes()) == 2
    assert r.get_antecedentes()[0].terminos() == ["X", "color", "rojo"]
    assert r.get_antecedentes()[1].terminos() == ["Y", "tamaño", "grande"]

def test_regla_con_extension():
    """Test: regla con extensión de confianza"""
    r = parsear_regla("A tipo B [0.9] <- X color rojo")
    assert r.get_consecuente().confianza == 0.9

def test_regla_antecedente_con_confianza():
    """Test: antecedente con confianza individual"""
    r = parsear_regla("A tipo B <- X color rojo [0.8]")
    assert r.get_antecedentes()[0].confianza == 0.8

# ============================
#  Tests EBNF - Consulta
# ============================

def test_consulta_simple():
    """Test: consulta = tripleta "?" """
    tripleta, tipo = parsear_consulta("tomate tipo verdura ?")
    assert tipo == "consulta"
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]

def test_consulta_razonar():
    """Test: consulta = "razona si " tripleta "?" """
    tripleta, tipo = parsear_consulta("razona si tomate tipo verdura ?")
    assert tipo == "razonar"
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]

# ============================
#  Tests EBNF - Comando
# ============================

def test_comando_descubrir():
    """Test: comando = palabra { " " palabra } "!" """
    tripleta, tipo = parsear_consulta("descubrir!")
    assert tipo == "descubrir"
    assert tripleta is None


# ============================
#  Tests parsear_tripleta / regla (originales)
# ============================

def test_parsear_tripleta_basico():
    """
    Test parsear tripleta sin confianza
    """
    t = parsear_tripleta("tomate tipo verdura")
    assert isinstance(t, Tripleta)
    assert t.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_regla_basica():
    """
    Test parsear regla sin confianza
    """
    r = parsear_regla("tomate tipo verdura <- tomate color rojo")
    assert isinstance(r, Regla)
    # consecuente es una Tripleta
    assert isinstance(r.get_consecuente(), Tripleta)
    assert r.get_consecuente().terminos() == ["tomate", "tipo", "verdura"]
    # antecedentes es lista de Tripleta
    assert len(r.get_antecedentes()) == 1
    assert r.antecedentes[0].terminos() == ["tomate", "color", "rojo"]
    
def test_parsear_tripleta_basico_con_confianza():
    """
    Test parsear tripleta con confianza
    """
    t = parsear_tripleta("tomate tipo verdura [0.8]")
    assert isinstance(t, Tripleta)
    assert t.terminos() == ["tomate", "tipo", "verdura"]
    assert t.confianza == 0.8


def test_parsear_regla_basica_con_confianza():
    """
    Test parsear regla con confianza
    """
    r = parsear_regla("tomate tipo verdura [0.95] <- tomate color rojo [0.8]")
    assert isinstance(r, Regla)
    # consecuente es una Tripleta
    assert isinstance(r.get_consecuente(), Tripleta)
    assert r.get_consecuente().terminos() == ["tomate", "tipo", "verdura"]
    assert r.get_consecuente().confianza == 0.95
    # antecedentes es lista de Tripleta
    assert len(r.get_antecedentes()) == 1
    assert r.antecedentes[0].terminos() == ["tomate", "color", "rojo"]
    assert r.get_antecedentes()[0].confianza == 0.8
    
    assert r.confianza == 1.0


# ============================
#  Tests parsear_consulta OK
# ============================

def test_parsear_consulta_hecho():
    """
    Test parsear consulta tipo "hecho" (tripleta .)
    """
    tripleta, tipo = parsear_consulta("tomate tipo verdura .")
    assert tipo == "hecho"
    assert isinstance(tripleta, Tripleta)
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_consulta_pregunta():
    """
    Test parsear consulta tipo "pregunta" (tripleta ?)
    """
    tripleta, tipo = parsear_consulta("tomate tipo verdura ?")
    assert tipo == "consulta"
    assert isinstance(tripleta, Tripleta)
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_consulta_razonar():
    """
    Test parsear consulta tipo "razonar" (razona si tripleta ?)
    """
    tripleta, tipo = parsear_consulta("razona si tomate tipo verdura ?")
    assert tipo == "razonar"
    assert isinstance(tripleta, Tripleta)
    assert tripleta.terminos() == ["tomate", "tipo", "verdura"]


def test_parsear_consulta_descubrir():
    """
    Test parsear consulta tipo "descubrir" (descubrir!)
    """
    tripleta, tipo = parsear_consulta("descubrir!")
    assert tipo == "descubrir"
    assert tripleta is None


# ============================
#  Tests parsear_consulta ERRORES
# ============================

def test_parsear_consulta_vacia():
    """
    Test de comprobación de manejo de errores para consultas vacías
    """
    # aquí esperamos que NO pete con IndexError,
    # sino que lance un ValueError controlado
    with pytest.raises(ValueError):
        parsear_consulta("")


def test_parsear_consulta_formato_invalido_pocos_terminos():
    """
    Test de comprobación de manejo de errores para consultas incompletas
    """
    # Falta objeto y signo final
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("tomate tipo")
    assert "formato de consulta" in str(excinfo.value).lower() or "debe ser" in str(excinfo.value).lower()


def test_parsear_consulta_formato_invalido_demasiados_terminos():
    """
    Test de comprobación de manejo de errores para consultas con demasiados términos
    """
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("tomate tipo verdura extra ?")
    assert "formato de consulta" in str(excinfo.value).lower() or "debe ser" in str(excinfo.value).lower()


def test_parsear_consulta_ultimo_no_valido():
    """
    Test de comprobación de manejo de errores para consultas con final no valido
    """
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("tomate tipo verdura !")
    assert "debe terminar en ? (consulta) o . (hecho)" in str(excinfo.value)


def test_parsear_consulta_razonar_longitud_incorrecta():
    """
    Test de comprobación de manejo de errores para consultas de 
    tipo "razonar" incompletos
    """
    # le falta el objeto
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("razona si tomate tipo ?")
    assert "razonamiento" in str(excinfo.value).lower() or "razona si" in str(excinfo.value).lower()


def test_parsear_consulta_razonar_sin_interrogacion():
    """
    Test de comprobación de manejo de errores para consultas de 
    tipo "razonar" sin signo de interrogación final.
    """
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("razona si tomate tipo verdura .")
    assert "terminar en ?" in str(excinfo.value)


def test_parsear_consulta_descubrir_con_argumentos():
    """
    Test de comprobación de manejo de errores para consultas de 
    tipo "descubrir" con argumentos.
    """
    with pytest.raises(ValueError) as excinfo:
        parsear_consulta("descubrir! algo")
    assert "descubrir" in str(excinfo.value).lower() or "no lleva argumentos" in str(excinfo.value).lower()