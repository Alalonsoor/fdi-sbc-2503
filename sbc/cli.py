from pathlib import Path
from sbc.cargar_kb import carga_kb
from sbc.parser import parsear_consulta
from sbc.query import query, descubrir
from sbc.ed import Tripleta, es_variable

def extraer_variables(tripleta: Tripleta) -> list[str]:
    """Extrae todas las variables únicas de una tripleta."""
    variables = []
    for termino in tripleta.terminos():
        if es_variable(termino) and termino not in variables:
            variables.append(termino)
    return variables

def formatear_resultados(consulta_str: str, kb: dict):
    """Consulta la KB y produce strings formateados como resultado"""

    tripleta_usr, tipo = parsear_consulta(consulta_str)

    # Si es hecho, agregar a la KB
    if tipo == 'hecho':
        if tripleta_usr not in kb['hechos']:
            kb['hechos'].append(tripleta_usr)
            yield f'Hecho agregado: {tripleta_usr.sujeto} {tripleta_usr.predicado} {tripleta_usr.objeto}'
        
        yield f'Ya existe el hecho: {tripleta_usr.sujeto} {tripleta_usr.predicado} {tripleta_usr.objeto}'

    elif tipo == 'consulta':
        # Si es consulta, procesar normalmente
        resultados = list(query(tripleta_usr, kb))
        variables = extraer_variables(tripleta_usr)

        # No existen variables -> SI/NO
        if not variables:
            yield 'SI' if resultados else 'NO'
        else:
            # Una o mas variables
            if len(variables) == 1: 
                var = variables[0]
                for ss in resultados:
                    valor = ss.aplicar(var)
                    if tripleta_usr.sujeto == var:
                        yield valor
                    else:
                        yield f'{tripleta_usr.predicado} = {valor}'
            else:
                for ss in resultados:
                    valores = [ss.aplicar(v) for v in variables]
                    yield ' '.join(valores)
    elif tipo == 'descubrir':
        nuevos_hechos = descubrir(kb)
        if nuevos_hechos:
            yield(f'Se descubrieron {len(nuevos_hechos)} nuevos hechos:')
            for hecho in nuevos_hechos:
                yield(f'  {hecho.sujeto} {hecho.predicado} {hecho.objeto}')
        else:
            yield('No se descubrieron nuevos hechos')
                


if __name__ == '__main__':
    # Cargar la base de conocimientos
    kb_dir = Path('kb')
    fichero_hechos = kb_dir / "ingredientes.txt"
    fichero_reglas = kb_dir / "reglas.txt"

    kb = carga_kb(fichero_hechos=fichero_hechos, fichero_reglas=fichero_reglas)
    continuando = True
    while continuando:
        try:
            usr_input = input('Consulta>>> ').strip()

            if usr_input.lower() in ('exit', 'quit', 'q', 'cerrar', 'e'):
                print('Hasta luego!!!')
                continuando = False
            else:
                for res in formatear_resultados(usr_input, kb):
                    print(res)
                print()
        except Exception as e:
            print(f'Error: {e}')
            print()
