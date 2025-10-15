from pathlib import Path

fichero = Path("kb")/"ingredientes.txt"

lineas = fichero.read_text(encoding="utf8").splitlines()
ingredientes = [linea.lower() for linea in lineas if linea.strip()]


ingrediente_buscar = "tomate"

if ingrediente_buscar.lower() in ingredientes:
    print(f"'{ingrediente_buscar}' está en la lista.")
else:
    print(f"'{ingrediente_buscar}' no está en la lista")