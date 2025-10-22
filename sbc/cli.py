from pathlib import Path
from pyparsing import Word, alphas, alphanums, Regex


def crear_parser_palabra():
    return Word(alphas + "áéíóúÁÉÍÓÚñÑ", alphanums + "áéíóúÁÉÍÓÚñÑ")


def leer_base_conocimiento(ruta_archivo):
    word = crear_parser_palabra()
    parser = word("ingrediente") + word("atributo") + word("valor")
    
    fichero = Path(ruta_archivo)
    lineas = fichero.read_text(encoding="utf8").splitlines()
    
    for linea in lineas:
        parsed = parser.parse_string(linea)
        ingrediente = parsed.ingrediente.lower()
        atributo = parsed.atributo.lower()
        valor = parsed.valor.lower()
        yield (ingrediente, atributo, valor)


def construir_diccionario_conocimiento(ruta_archivo):
    base_conocimiento = {}
    for ingrediente, atributo, valor in leer_base_conocimiento(ruta_archivo):
        base_conocimiento[(ingrediente, atributo)] = valor
    return base_conocimiento


def leer_consultas(ruta_archivo):
    word = crear_parser_palabra()
    token_any = Regex(r"\S+")
    parser_in = word("ingrediente") + word("atributo") + word("valor") + token_any("signo")
    
    entrada = Path(ruta_archivo)
    lineas = entrada.read_text(encoding="utf8").splitlines()
    
    for linea in lineas:
        parsed = parser_in.parse_string(linea)
        ingrediente = parsed.ingrediente.lower()
        atributo = parsed.atributo.lower()
        valor = parsed.valor.lower()
        signo = parsed.signo
        yield (ingrediente, atributo, valor, signo, linea)


def procesar_consulta(ingrediente, atributo, valor, signo, linea_original, base_conocimiento):
    if signo == "?":
        if (ingrediente, atributo) in base_conocimiento:
            yield f"{base_conocimiento[(ingrediente, atributo)]}"
        else:
            yield f"No se encuentra información para {ingrediente} {atributo}."
    else:
        yield f"Entrada no es una consulta: {linea_original}"


def ejecutar_sistema():
    # Construir base de conocimientos
    base_conocimiento = construir_diccionario_conocimiento("kb/ingredientes.txt")
    
    # Procesar consultas
    for ingrediente, atributo, valor, signo, linea in leer_consultas("sbc/entrada.in"):
        for resultado in procesar_consulta(ingrediente, atributo, valor, signo, linea, base_conocimiento):
            yield resultado


if __name__ == "__main__":
    for mensaje in ejecutar_sistema():
        print(mensaje)