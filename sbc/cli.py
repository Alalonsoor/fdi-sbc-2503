from pathlib import Path
from pyparsing import Word, alphas, alphanums, Regex

# Definimos el parser: palabra palabra palabra
word = Word(alphas + "áéíóúÁÉÍÓÚñÑ", alphanums + "áéíóúÁÉÍÓÚñÑ")  
parser = word("ingrediente") + word("atributo") + word("valor")

# Archivos
fichero = Path("kb") / "ingredientes.txt"
entrada = Path("sbc") / "entrada.in"

lineas_kb = fichero.read_text(encoding="utf8").splitlines()
base_conocimiento = {}

for linea in lineas_kb:
    
    parsed = parser.parse_string(linea)
    ingrediente = parsed.ingrediente.lower()
    atributo = parsed.atributo.lower()
    valor = parsed.valor.lower()
    base_conocimiento[(ingrediente, atributo)] = valor
    

token_any = Regex(r"\S+")
lineas_in = entrada.read_text(encoding="utf8").splitlines()
parser_in = word("ingrediente") + word("atributo") + word("valor") + token_any("signo")
for linea in lineas_in:
    
    parsed = parser_in.parse_string(linea)
    ingrediente = parsed.ingrediente.lower()
    atributo = parsed.atributo.lower()
    valor = parsed.valor.lower()
    signo = parsed.signo
    if signo == "?":
        if (ingrediente, atributo) in base_conocimiento:
            print(f"{ingrediente} {atributo} -> {base_conocimiento[(ingrediente, atributo)]}")
        else:
            print(f"No se encuentra información para {ingrediente} {atributo}.")
    else:
        print(f"Entrada no es una consulta: {linea}")
