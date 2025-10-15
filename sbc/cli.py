from pathlib import Path 
 
fichero = Path("kb")/"ingredientes.txt" 
entrada = Path("sbc")/"entrada.in"  

lineas = fichero.read_text(encoding="utf8").splitlines() 
ingredientes = [linea.lower() for linea in lineas if linea.strip()] 

lineas_entrada = entrada.read_text(encoding="utf8").splitlines() 
ingredientes_buscar = [linea.lower() for linea in lineas_entrada if linea.strip()]  

for ingrediente in ingredientes_buscar:     
    if ingrediente.lower() in ingredientes:         
        print(f"'{ingrediente}' SÍ está en la lista.")     
    else:         
        print(f"'{ingrediente}' NO está en la lista.")