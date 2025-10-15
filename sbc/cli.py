from pathlib import Path

fichero = Path("fdi-sbc-2503/kb/ingredientes.txt")

lineas = fichero.read_text(encoding="utf8").splitlines()
ingredientes = [linea.lower() for linea in lineas if linea.strip()]


ingrediente_buscar = "tomate"

if ingrediente_buscar.lower() in ingredientes:
    print(f"'{ingrediente_buscar}' está en la lista.")