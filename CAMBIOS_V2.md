# CAMBIOS IMPLEMENTADOS RESPECTO DE V1

## 1. Carga de base de conocimineto

Antes `cargar_kb.py` requeria de archivos `.txt` específicos para reglas y hechos. Ahora, es más flexible. Acepta un único parámetro `Path` que puede ser un archivo o un directorio con archivos `*.txt` y carga el contenido a la `kb`.

## 2. Solución test `comun.txt`

El test `comun.txt` no pasaba las últimas dos consultas de t_pinguino por las siguientes razones:

### 2.1 Falta de revocación

Ahora tenemos la función de revocar hechos. Al escribir `no <hecho> .` se elimina ese hecho de la `kb`.

### 2.1 Correción parser de agregar hecho

En `parser.py` no identificaba factores de confianza a la hora de agregar nuevos hechos `<hecho> .`. Se ha solucionado y ahora el test `comun.txt` pasa perfectamente.

## 3. Motor de inferencia (`query.py`)

### 3.1 Nuevo parámetro `razonamiento`

```python
def query(tripleta: Tripleta, kb: dict, razonamiento=False, visitados=None):

def _query_antecedentes(antecedentes: list[Tripleta], kb: dict, ss_inicial: Sustitucion, razonamiento=False, visitados=None):
```

Ahora la función `query` distingue entre consultas simples y razonamiento, evitando aplicar reglas innecesariamente.

- Si es una consulta simple `razonamineto = False` solo se consultará en hechos.
- Si es un razonamiento `razonamiento = True` se comprobará primero en hechos la consulta y después en reglas aplicando encadenamiento hacia detrás.

### 3.2 Prevención en recursión infinita

`Nota:` Antes habia problemas de recursión infinita hasta en consultas normales `X Y Z ?` porque como se ha mencionado antes, `query.py` no distinguia entre consultas simples y razonamiento.

Para prevenir la recursión infinita se ha agregado un nuevo parámetro `visitados`.

- Es un conjunto de tripletas que rastrea las tripletas que ya estamos intentando probar.
- Antes de procesar uan regla, verifica si la tripleta ya está en `visitados`
- Si está, detiene la recursión para evitar ciclos infinitos.
- Cada llamada recursiva pasa un **NUEVO** conjunto actualizado para que cada rama tenga su propio conjunto.

```python
if razonamiento:
        clave = (tripleta.sujeto, tripleta.predicado, tripleta.objeto)
        # Si ya hemos procesado esta tripleta, paramos para evitar ciclos.
        if clave in visitados:
            return

        # Agregar a visitados
        # crea un nuevo conjunto que contiene todos los elementos de visitados más clave
        # equivalente a : 
        # nuevos_visitados = visitados.copy()
        # nuevos_visitados.add(clave)
        nuevos_visitados = visitados | {clave}
        for regla in kb["reglas"]:
```

### 3.3 `_query_antecedentes`

- Ahora es privada `query_antecedentes` -> `_query_antecedentes`.
- Acepta `razonamiento` y `visitados` para propagar la recurisón.

### 3.3 Mejoras en `descubrir()`

- Solo usa hechos encadenamiento hacia delante con `razonamiento = False`

```python
for ss, confianza in _query_antecedentes(regla.get_antecedentes(), kb, Sustitucion(), razonamiento=False):
```

- Verifica que el hecho esté completamente resuelto, una vez resuelto entonces se agrega a la `kb`.

```python
 # Verificar que el hecho esté completamente resuelto (sin variables)
            tiene_variables = any(es_variable(t) for t in nuevo_hecho.terminos())
            if tiene_variables:
                # Seguir hasta resolver el hecho.
                continue
```

### 3.4 `Razonar()`

Ahora `razonar` de vuelve una lista de tuplas de sustitucione y confianza.

```python
return list(query(tripleta, kb, razonamiento=True))
```

## 4 Estructuras de datos

Se ha implemetado `__eq__` y `__hash__`

- `__eq__` Comparar dos tripletas ignorando el factor de confianza.
- `__hash__` Necesario apra uso de `Tripleta` en conjuntos.

## 5 Interfaz `CLI`

### 5.1 Elegir KB

Ahora acepta el flag `--kb` para especificar el directorio de la `kb`.

```bash
uv run -m sbc.cli --kb dir_kb/
```

por defecto usa `kb/`

```bash
uv run -m sbc.cli
```

### 5.2 Lógica mejorada para agregar hechos

```python
    # Si es hecho, agregar a la KB
    if tipo == "hecho":
        sujeto_usr, predicado_usr, objeto_usr = tripleta_usr.terminos()
        
        # Buscar si ya existe (ahora __eq__ ignora confianza)
        encontrado = False
        for i, hecho in enumerate(kb["hechos"]):
            if hecho == tripleta_usr:
                # Ya existe: actualizar confianza con MAX (lógica OR)
                if tripleta_usr.confianza > hecho.confianza:
                    kb["hechos"][i] = tripleta_usr
                    yield f"Hecho actualizado con mayor confianza: {sujeto_usr} {predicado_usr} {objeto_usr}"
                else:
                    yield f"Ya existe el hecho: {sujeto_usr} {predicado_usr} {objeto_usr}"
                encontrado = True
                break
        
        if not encontrado:
            kb["hechos"].append(tripleta_usr)
            yield f"Hecho agregado: {sujeto_usr} {predicado_usr} {objeto_usr}"
```

- Ahora busca si el hecho ya existe.
- Si existe con menor confianza, lo actualiza con MAX (lógica OR).
- Si no existe, se agrega.

### 5.3 Unificación de consultas y razonamiento

```python
    elif tipo == "consulta" or tipo == "razonar":
        if tipo == "consulta":
            # Si es consulta, procesar normalmente
            resultados = list(query(tripleta_usr, kb))
        else:
            resultados = razonar(tripleta_usr, kb)
        
        ...
```

- Ambos tipos ahora se procesan con la misma lógica de formateo
- La diferencia está en si se usa `query()` con `razonamiento = False` o `razonar()` que llama a `query()` con `razonamiento = True`

### 5.4 Sistema de ayuda

Por ultimo un sistema de ayuda al usario para mostrar todas las acciones que puede realizar.

Se activa con `help, h o ayuda`

Nuevo archivo `help.py` que proporciona la función `mostrar_ayuda()`.
