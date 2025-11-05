from pathlib import Path
from sbc.cargar_kb import carga_kb
from sbc.parser import parsear_consulta
from sbc.query import query
from sbc.ed import Tripleta, es_variable

def extraer_variables(tripleta: Tripleta) -> list[str]:
    """Extrae todas las variables únicas de una tripleta."""
    variables = []
    for termino in tripleta.terminos():
        if es_variable(termino) and termino not in variables:
            variables.append(termino)
    return variables

def formatear_resultados(consulta_str: str, kb: list):
    """Consulta la KB y produce strings formateados como resultado"""

    tripleta_consulta, tipo = parsear_consulta(consulta_str)

    # Si es hecho, agregar a la KB, la lista
    if tipo == 'hecho':
        kb.append(tripleta_consulta)
        yield f'Hecho agregado: {tripleta_consulta.sujeto} {tripleta_consulta.predicado} {tripleta_consulta.objeto}'
        return

    # Si es consulta, procesar normalmente
    resultados = list(query(tripleta_consulta, kb))
    variables = extraer_variables(tripleta_consulta)

    # No existen variables -> SI/NO
    if not variables:
        yield 'SI' if resultados else 'NO'
        return

    # Una o mas variables
    if len(variables) == 1:
        var = variables[0]
        for ss in resultados:
            valor = ss.aplicar(var)
            if tripleta_consulta.sujeto == var:
                yield valor
            else:
                yield f'{tripleta_consulta.predicado} = {valor}'
    else:
        for ss in resultados:
            valores = [ss.aplicar(v) for v in variables]
            yield ' '.join(valores)

if __name__ == '__main__':
    # Cargar la base de conocimientos
    kb_dir = Path('kb')
    fichero_hechos = kb_dir / "ingredientes.txt"
    fichero_reglas = kb_dir / "reglas.txt"

    kb = carga_kb(fichero_hechos=fichero_hechos, fichero_reglas=fichero_reglas)

    while True:
        try:
            usr_input = input('Consulta>>> ').strip()

            if usr_input.lower() in ('exit', 'quit', 'q', 'cerrar', 'e'):
                print('Hasta luego!!!')
                break
            if not usr_input:
                continue

            for res in formatear_resultados(usr_input, kb):
                print(res)
            print()
        except Exception as e:
            print(f'Error: {e}')
