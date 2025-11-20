import pytest
from sbc.cli import extraer_variables, formatear_resultados
from sbc.ed import Tripleta


# ============================
#  Tests extraer_variables
# ============================

def test_extraer_variables_sin_variables(monkeypatch):
    """Extrae variables cuando no hay ninguna variable."""
    # Forzamos es_variable a devolver siempre False
    monkeypatch.setattr("sbc.cli.es_variable", lambda t: False)

    t = Tripleta("tomate", "tipo", "verdura")
    vars_encontradas = extraer_variables(t)

    assert vars_encontradas == []


def test_extraer_variables_con_variables_sin_duplicados(monkeypatch):
    """Extrae variables únicas manteniendo orden."""
    # Consideramos variables las que empiezan por '?'
    monkeypatch.setattr("sbc.cli.es_variable", lambda t: isinstance(t, str) and t.startswith("?"))

    # La Tripleta devuelve terminos() como lista, p.ej ['?x', 'tipo', '?x']
    t = Tripleta("?x", "tipo", "?x")
    vars_encontradas = extraer_variables(t)

    # Debe mantener orden y no repetir
    assert vars_encontradas == ["?x"]


def test_extraer_variables_varias(monkeypatch):
    """Extrae múltiples variables correctamente."""
    monkeypatch.setattr("sbc.cli.es_variable", lambda t: isinstance(t, str) and t.startswith("?"))

    t = Tripleta("?x", "rel", "?y")
    vars_encontradas = extraer_variables(t)

    assert vars_encontradas == ["?x", "?y"]


# ============================
#  Helpers para formatear_resultados
# ============================

class DummySustitucion:
    def __init__(self, mapping):
        self.mapping = mapping

    def aplicar(self, var):
        return self.mapping[var]


class DummyHecho:
    def __init__(self, s, p, o, confianza=1.0):
        self._s = s
        self._p = p
        self._o = o
        self.confianza = confianza

    def terminos(self):
        return [self._s, self._p, self._o]


# ============================
#  Tests formatear_resultados: tipo 'hecho'
# ============================

def test_formatear_resultados_hecho_nuevo(monkeypatch):
    """Agrega hecho nuevo a la KB y lo informa."""
    # Simulamos que parsear_consulta detecta un hecho
    def fake_parsear_consulta(_):
        return Tripleta("pan", "tipo", "cereal"), "hecho"

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)

    kb = {"hechos": [], "reglas": []}

    resultados = list(formatear_resultados("pan tipo cereal .", kb))

    assert resultados == ["Hecho agregado: pan tipo cereal"]
    # Se ha agregado el hecho a la KB
    assert len(kb["hechos"]) == 1
    assert kb["hechos"][0].terminos() == ["pan", "tipo", "cereal"]


# ============================
#  Tests formatear_resultados: tipo 'razonar'
# ============================

def test_formatear_resultados_razonar_true(monkeypatch):
    """Razonamiento devuelve SI cuando es verdadero."""
    def fake_parsear_consulta(_):
        return Tripleta("tomate", "tipo", "verdura"), "razonar"

    def fake_razonar(tripleta, kb):
        assert isinstance(tripleta, Tripleta)
        return True

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.razonar", fake_razonar)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("razona si tomate tipo verdura ?", kb))

    assert resultados == ["SI"]


def test_formatear_resultados_razonar_false(monkeypatch):
    """Razonamiento devuelve NO cuando es falso."""
    def fake_parsear_consulta(_):
        return Tripleta("tomate", "tipo", "carne"), "razonar"

    def fake_razonar(tripleta, kb):
        return False

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.razonar", fake_razonar)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("razona si tomate tipo carne ?", kb))

    assert resultados == ["NO"]


# ============================
#  Tests formatear_resultados: tipo 'consulta' sin variables
# ============================

def test_formatear_resultados_consulta_sin_variables_no_resultados(monkeypatch):
    """Consulta sin variables devuelve NO si no hay resultados."""
    def fake_parsear_consulta(_):
        return Tripleta("tomate", "tipo", "verdura"), "consulta"

    def fake_query(tripleta, kb):
        return []  # sin resultados

    # extraer_variables se comporta normal: no hay variables en la tripleta
    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.query", fake_query)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("tomate tipo verdura ?", kb))

    assert resultados == ["NO"]


def test_formatear_resultados_consulta_sin_variables_si_confianza_1(monkeypatch):
    """Consulta sin variables con confianza 1 devuelve SI."""
    def fake_parsear_consulta(_):
        return Tripleta("tomate", "tipo", "verdura"), "consulta"

    def fake_query(tripleta, kb):
        # lista de (sustitucion, confianza)
        return [(DummySustitucion({}), 1.0)]

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.query", fake_query)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("tomate tipo verdura ?", kb))

    # Confianza 1.0 -> solo 'SI'
    assert resultados == ["SI"]


def test_formatear_resultados_consulta_sin_variables_si_confianza_menor(monkeypatch):
    """Consulta sin variables muestra confianza en porcentaje."""
    def fake_parsear_consulta(_):
        return Tripleta("tomate", "tipo", "verdura"), "consulta"

    def fake_query(tripleta, kb):
        # varias soluciones, se toma la confianza máxima
        return [
            (DummySustitucion({}), 0.5),
            (DummySustitucion({}), 0.9),
        ]

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.query", fake_query)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("tomate tipo verdura ?", kb))

    # 0.9 -> 90%
    assert resultados == ["SI (confianza: 90%)"]


# ============================
#  Tests formatear_resultados: tipo 'consulta' con 1 variable
# ============================

def test_formatear_resultados_consulta_una_variable_sujeto(monkeypatch):
    """Consulta con variable en sujeto muestra valores correctamente."""
    def fake_parsear_consulta(_):
        # ?x en sujeto
        return Tripleta("?x", "tipo", "fruta"), "consulta"

    def fake_extraer_variables(tripleta):
        return ["?x"]

    def fake_query(tripleta, kb):
        # Dos resultados distintos
        return [
            (DummySustitucion({"?x": "manzana"}), 1.0),
            (DummySustitucion({"?x": "pera"}), 0.7),
        ]

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.extraer_variables", fake_extraer_variables)
    monkeypatch.setattr("sbc.cli.query", fake_query)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("?x tipo fruta ?", kb))

    # Confianza 1.0 -> sin sufijo; 0.7 -> [70%]
    assert sorted(resultados) == sorted(["manzana", "pera [70%]"])


def test_formatear_resultados_consulta_una_variable_objeto(monkeypatch):
    """Consulta con variable en objeto muestra predicado = valor."""
    def fake_parsear_consulta(_):
        # ?x en objeto
        return Tripleta("pizza", "contiene", "?x"), "consulta"

    def fake_extraer_variables(tripleta):
        return ["?x"]

    def fake_query(tripleta, kb):
        return [
            (DummySustitucion({"?x": "queso"}), 0.8),
        ]

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.extraer_variables", fake_extraer_variables)
    monkeypatch.setattr("sbc.cli.query", fake_query)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("pizza contiene ?x ?", kb))

    # Para una sola variable en objeto -> 'predicado = valor [conf]'
    assert resultados == ["contiene = queso [80%]"]


# ============================
#  Tests formatear_resultados: tipo 'consulta' con varias variables
# ============================

def test_formatear_resultados_consulta_varias_variables(monkeypatch):
    """Consulta con varias variables muestra valor1 valor2 con confianza."""
    def fake_parsear_consulta(_):
        # dos variables
        return Tripleta("?x", "contiene", "?y"), "consulta"

    def fake_extraer_variables(tripleta):
        return ["?x", "?y"]

    def fake_query(tripleta, kb):
        return [
            (DummySustitucion({"?x": "pizza", "?y": "queso"}), 1.0),
            (DummySustitucion({"?x": "ensalada", "?y": "tomate"}), 0.9),
        ]

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.extraer_variables", fake_extraer_variables)
    monkeypatch.setattr("sbc.cli.query", fake_query)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("?x contiene ?y ?", kb))

    # Formato: "valorX valorY[ conf]"
    assert "pizza queso" in resultados
    assert "ensalada tomate [90%]" in resultados


# ============================
#  Tests formatear_resultados: tipo 'descubrir'
# ============================

def test_formatear_resultados_descubrir_sin_nuevos_hechos(monkeypatch):
    """Descubrir sin nuevos hechos informa correctamente."""
    def fake_parsear_consulta(_):
        return None, "descubrir"

    def fake_descubrir(kb):
        return []

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.descubrir", fake_descubrir)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("descubrir!", kb))

    assert resultados == ["No se descubrieron nuevos hechos"]


def test_formatear_resultados_descubrir_con_nuevos_hechos(monkeypatch):
    """Descubrir muestra lista de hechos nuevos con confianza."""
    def fake_parsear_consulta(_):
        return None, "descubrir"

    def fake_descubrir(kb):
        return [
            DummyHecho("pizza", "contiene", "queso", confianza=1.0),
            DummyHecho("ensalada", "contiene", "tomate", confianza=0.8),
        ]

    monkeypatch.setattr("sbc.cli.parsear_consulta", fake_parsear_consulta)
    monkeypatch.setattr("sbc.cli.descubrir", fake_descubrir)

    kb = {"hechos": [], "reglas": []}
    resultados = list(formatear_resultados("descubrir!", kb))

    # Primera línea: número de hechos descubiertos
    assert resultados[0] == "Se descubrieron 2 nuevos hechos:"
    # Formato de líneas siguientes
    # para confianza 1.0 -> sin [conf]
    assert "  pizza contiene queso" in resultados[1]
    # para confianza 0.8 -> [0.8]
    assert "  ensalada contiene tomate [0.8]" in resultados[2]