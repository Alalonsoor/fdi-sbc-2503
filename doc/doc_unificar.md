# Algoritmo de Unificación

## Descripción general

El archivo `unificar.py` implementa el algoritmo de unificación, que es el núcleo del sistema de inferencia. La unificación permite determinar si dos expresiones lógicas pueden hacerse idénticas mediante sustituciones de variables, y en caso afirmativo, encontrar dichas sustituciones.

## Funciones Principales

### `ocurre(var: str, term: str, ss: Sustitucion) -> bool`

**Proposito**: Comprueba si una variable aparece en un término siguiendo las sustituciones actuales. Previene ciclos infinitos en sustituciones recursivas.

**Algoritmo**:

1. Si la variable y el término son iguales, retorna True
2. Mientras el término no sea literal y tenga sustitución, sigue la cadena de sustituciones
3. Si en algún punto encuentra la variable, retorna True
4. Si termina la cadena sin encontrar la variable, retorna False

**Ejemplo**:

```bash
ss = Sustitucion({"X": "Y", "Y": "Z"})

ocurre("X", "Z", ss)  # True (X -> Y -> Z)
ocurre("X", "pizza", ss)  # False
ocurre("Y", "Z", ss)  # True (Y -> Z)
```

### `unify_terms(t1: str, t2: str, ss: Sustitucion) -> Sustitucion | None`

**Proposito**: Unifica dos términos individuales aplicando las reglas de unificación.

**Algoritmo**: Maneja 4 casos posibles mediante pattern matching

1. **Literal con literal**

    ```bash
    unify_terms("tomate", "tomate", ss)    # "tomate" == "tomate" -> ss (éxito)
    unify_terms("tomate", "queso", ss)     # "tomate" != "queso" -> None (fallo)
    ```

2. **Literal con Variable**

    ```bash
    unify_terms("tomate", "X", ss)
    ```

    1. Si X no tiene sustitución: Devuelve `ss` con `{"X" : "tomate"}`
    2. Si X tiene sustitución: `unify_terms("tomate", ss.get("X"), ss)`
3. **Variable con Literal**

    ```bash
    unify_terms("X", "tomate", ss)
    ```

    1. Si X no tiene sustitución: Devuelve `ss` con `{"X" : "tomate"}`
    2. Si X tiene sustitución: `unify_terms(ss.get("X"), "tomate", ss)`
4. **Variable con Variable**

   ```bash
    unify_terms("X", "Y", ss)
    ```

    1. Devuelve `ss` con `{"X" : "Y"}`
    2. Si ambas tienen tiene sustitución: `unify_terms(ss.get("X"), ss.get("Y"), ss)`
    3. Si son la misma varable: `{}`

**Ejemplo**:

```bash
ss = Sustitucion()

# Unificación básica
unify_terms("pizza", "X", ss)          # ss = {"X": "pizza"}

# Variables encadenadas
ss = Sustitucion({"Y": "pizza"})
unify_terms("X", "Y", ss)              # ss = {"X": "Y", "Y": "pizza"}

```

### `unify(x: Tripleta, y: Tripleta, ss: Sustitucion | None = None) -> list[Sustitucion]`

**Proposito**: Unifica dos tripletas completas.

**Algoritmo**:

1. Inicializa la sustitución si es None
2. Unifica sujeto con sujeto
3. Si tiene éxito, unifica predicado con predicado
4. Si tiene éxito, unifica objeto con objeto
5. Retorna lista con una sustitución si todo tiene éxito, lista vacía si falla

**Ejemplo**:

1. **Unificación exitosa**

    ```bash
    tripleta1 = Tripleta("X", "contiene", "lactosa")
    tripleta2 = Tripleta("pizza", "contiene", "Y")
    resultado = unify(tripleta1, tripleta2)
    # [Sustitucion({"X": "pizza", "Y": "lactosa"})]
    ```

2. **Unificación con sustitución parcial**

    ```bash
    tripleta1 = Tripleta("X", "contiene", "queso")
    tripleta2 = Tripleta("pizza", "contiene", "queso")
    resultado = unify(tripleta1, tripleta2)
    # [Sustitucion({"X": "pizza"})]
    ```

3. **Unificación con sustitución parcial**

    ```bash
    tripleta1 = Tripleta("X", "contiene", "lactosa")
    tripleta2 = Tripleta("pizza", "es_tipo", "comida")
    resultado = unify(tripleta1, tripleta2)
    # [] (predicados diferentes)
    ```

## Ejemplos Completos de Flujo de Unificación

1. **Unificación simple**

    ```bash
    from unificar import unify
    from ed import Tripleta, Sustitucion

    # Tripleta con variables
    consulta = Tripleta("X", "contiene", "lactosa")
    # Hecho concreto
    hecho = Tripleta("pizza", "contiene", "lactosa")
    hecho = Tripleta("yogurt", "contiene", "lactosa")
    # ...

    sustituciones = unify(consulta, hecho)
    # sustituciones = [{"X": "pizza"}, {"X": "yogurt"}, ...]
    ```

2. **Unificación con Variables en Ambos Lados**

    ```bash
    consulta = Tripleta("X", "contiene", "Y")
    hecho = Tripleta("pizza", "contiene", "queso")
    hecho = Tripleta("tarta", "contiene", "huevo")
    # ...

    sustituciones = unify(consulta, hecho)
    # sustituciones = [{"X": "pizza", "Y": "queso"}, {"X": "tarta", "Y": "huevo"}, ...]
    ```

3. **Unificación con Sustituciones Previas**

    ```bash
    ss = Sustitucion({"Z": "lactosa"})
    consulta = Tripleta("X", "contiene", "Z")
    hecho = Tripleta("pizza", "contiene", "lactosa")

    sustituciones = unify(consulta, hecho, ss)
    # sustituciones = [{"X": "pizza", "Z": "lactosa"}]
    ```

4. **Unificación Fallida por Parte Diferente**

    ```bash
    consulta = Tripleta("X", "contiene", "lactosa")
    hecho = Tripleta("pizza", "es_tipo", "comida")

    sustituciones = unify(consulta, hecho)
    # sustituciones = [] (fallo)
    ```

5. **Unificación con Sustituciones Encadenadas**

    ```bash
    ss = Sustitucion({"A": "B"})
    tripleta1 = Tripleta("A", "contiene", "X")
    tripleta2 = Tripleta("B", "contiene", "lactosa")

    sustituciones = unify(tripleta1, tripleta2, ss)
    # sustituciones = [{"A": "B", "X": "lactosa"}]
    ```
