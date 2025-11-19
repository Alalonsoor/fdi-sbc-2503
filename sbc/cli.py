from pathlib import Path
from sbc.cargar_kb import carga_kb
from sbc.parser import parsear_consulta
from sbc.query import query, descubrir, razonar
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
        sujeto_usr, predicado_usr, objeto_usr = tripleta_usr.terminos()
        if tripleta_usr not in kb['hechos']:
            kb['hechos'].append(tripleta_usr)
            yield f'Hecho agregado: {sujeto_usr} {predicado_usr} {objeto_usr}'
        else:
            yield f'Ya existe el hecho: {sujeto_usr} {predicado_usr} {objeto_usr}'
    elif tipo == 'razonar':
        resultado = razonar(tripleta_usr, kb)
        yield 'SI' if resultado else 'NO'
    elif tipo == 'consulta':
        # Si es consulta, procesar normalmente
        resultados = list(query(tripleta_usr, kb))
        variables = extraer_variables(tripleta_usr)

        # No existen variables -> SI/NO con confianza
        if not variables:
            if resultados:
                # Tomar la confianza máxima de todos los resultados
                max_confianza = max(confianza for _, confianza in resultados)
                if max_confianza < 1.0:
                    yield f'SI (confianza: {int(max_confianza * 100)}%)'
                else:
                    yield 'SI'
            else:
                yield 'NO'
        else:
            # Una o mas variables
            if len(variables) == 1: 
                var = variables[0]
                for ss, confianza in resultados:
                    valor = ss.aplicar(var)
                    sujeto_usr, predicado_usr, _ = tripleta_usr.terminos()
                    conf_str = f' [{int(confianza * 100)}%]' if confianza < 1.0 else ''
                    if sujeto_usr == var:
                        yield f'{valor}{conf_str}'
                    else:
                        yield f'{predicado_usr} = {valor}{conf_str}'
            else:
                for ss, confianza in resultados:
                    valores = [ss.aplicar(v) for v in variables]
                    conf_str = f' [{int(confianza * 100)}%]' if confianza < 1.0 else ''
                    yield f'{" ".join(valores)}{conf_str}'
                    
    elif tipo == 'descubrir':
        nuevos_hechos = descubrir(kb)
        if nuevos_hechos:
            yield(f'Se descubrieron {len(nuevos_hechos)} nuevos hechos:')
            for hecho in nuevos_hechos:
                hecho_sujeto, hecho_predicado, hecho_objeto = hecho.terminos()
                conf_str = f'[{hecho.confianza}]' if hecho.confianza < 1.0 else ''
                yield(f'  {hecho_sujeto} {hecho_predicado} {hecho_objeto} {conf_str}')
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
