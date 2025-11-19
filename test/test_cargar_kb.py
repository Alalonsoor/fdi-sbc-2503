import pytest
from pathlib import Path
from sbc.parser import parsear_consulta, parsear_tripleta, parsear_regla
from sbc.ed import Tripleta, Regla
from sbc.cargar_kb import carga_kb

# ============================
#  Tests de carga de datos
# ============================

def test_cargar_kb_hechos(tmp_path):
    """
    Test carga de hechos desde archivo
    """
    # Crear archivo temporal de hechos en 
    # un directorio temporal creado por pytest
    hechos_file = tmp_path / "hechos.txt"
    hechos_file.write_text(
        """
        tomate color rojo
        platano color amarillo [1.0]
        """
    )
    
    # Crear archivo temporal de reglas (vacío)
    reglas_file = tmp_path / "reglas.txt"
    reglas_file.write_text("")
    
    # Ejecutamos carga_kb
    kb = carga_kb(hechos_file, reglas_file)
    
    assert isinstance(kb, dict)
    assert "hechos" in kb
    assert "reglas" in kb
    assert len(kb["hechos"]) == 2
    assert len(kb["reglas"]) == 0
    
    primer_hecho = kb["hechos"][0]
    assert isinstance(primer_hecho, Tripleta)
    assert primer_hecho.terminos() == ["tomate", "color", "rojo"]
    
    segundo_hecho = kb["hechos"][1]
    assert isinstance(segundo_hecho, Tripleta)
    assert segundo_hecho.confianza == 1.0
    assert segundo_hecho.terminos() == ["platano", "color", "amarillo"]

def test_cargar_kb_reglas(tmp_path):
    """
    Test carga de reglas desde archivo
    """
    # Crear archivo temporal de hechos (vacío) en 
    # un directorio temporal creado por pytest
    hechos_file = tmp_path / "hechos.txt"
    hechos_file.write_text("")
    
    # Crear archivo temporal de reglas
    reglas_file = tmp_path / "reglas.txt"
    reglas_file.write_text(
        """
        Plato marida vino_blanco <- Plato ingrediente pescado
        Plato marida vino_blanco <- Plato ingrediente marisco [0.8]
        """
    )
    
    # Ejecutamos carga_kb
    kb = carga_kb(hechos_file, reglas_file)
    
    assert isinstance(kb, dict)
    assert "hechos" in kb
    assert "reglas" in kb
    assert len(kb["hechos"]) == 0
    assert len(kb["reglas"]) == 2
    
    primera_regla = kb["reglas"][0]  
    assert isinstance(primera_regla, Regla)
    assert isinstance(primera_regla.get_consecuente(), Tripleta)
    assert isinstance(primera_regla.get_antecedentes(), list)
    assert primera_regla.get_consecuente().terminos() == ["Plato", "marida", "vino_blanco"]
    assert len(primera_regla.get_antecedentes()) == 1
    assert primera_regla.get_antecedentes()[0].terminos() == ["Plato", "ingrediente", "pescado"]
    
    segunda_regla = kb["reglas"][1]
    assert segunda_regla.confianza == 1.0
    assert segunda_regla.get_antecedentes()[0].confianza == 0.8 
    
def test_carga_kb_ignora_comentarios(tmp_path):
    """
    Test de que ignora líneas comentadas
    """
    
    hechos_file = tmp_path / "hechos.txt"
    hechos_file.write_text(
        """
        # COMENTARIO 1
        tomate color rojo
        platano color amarillo
        # COMENTARIO 2
        """
    )
    
    # Crear archivo temporal de reglas (vacío)
    reglas_file = tmp_path / "reglas.txt"
    reglas_file.write_text("")
    
    kb = carga_kb(hechos_file, reglas_file)
    
    # Comprobar que cargue los dos hechos ignorando comentarios
    assert len(kb["hechos"]) == 2

def test_carga_kb_ignora_lineas_vacias(tmp_path):
    """
    Test de que ignora líneas vacias
    """
    
    hechos_file = tmp_path / "hechos.txt"
    hechos_file.write_text(
        """
        
        tomate color rojo
        
        platano color amarillo
        
        """
    )
    
    # Crear archivo temporal de reglas (vacío)
    reglas_file = tmp_path / "reglas.txt"
    reglas_file.write_text("")
    
    kb = carga_kb(hechos_file, reglas_file)
    
    # Comprobar que cargue los dos hechos ignorando los blancos
    assert len(kb["hechos"]) == 2
    
# ============================
#  Tests de archivos
# ============================

def test_carga_kb_archivos_inexistentes(tmp_path):
    """
    Test con archivos que no existen
    """
    
    hechos_file = tmp_path / "no_existe_hechos.txt"
    reglas_file = tmp_path / "no_existe_reglas.txt"
    
    kb = carga_kb(hechos_file, reglas_file)
    
    assert kb["hechos"] == []
    assert kb["reglas"] == []

# ============================
#  Tests de estructura completa
# ============================

def test_carga_kb_estructura_completa(tmp_path):
    """
    Test que verifica la estructura completa del resultado
    """
    hechos_file = tmp_path / "hechos.txt"
    hechos_file.write_text("tomate color rojo")
    
    reglas_file = tmp_path / "reglas.txt"
    reglas_file.write_text("X color rojo <- X tipo fruta")
    
    kb = carga_kb(hechos_file, reglas_file)
    
    # Verificar estructura del diccionario
    assert isinstance(kb, dict)
    assert set(kb.keys()) == {"hechos", "reglas"}
    assert all(isinstance(h, Tripleta) for h in kb["hechos"])
    assert all(isinstance(r, Regla) for r in kb["reglas"])

