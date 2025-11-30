# Motor de Consultas e Inferencia

## Descripción general

El archivo query.py implementa el motor de consultas y el sistema de inferencia del sistema de base de conocimientos. Contiene los algoritmos principales para realizar consultas, aplicar reglas, razonamiento mediante encadenamiento hacia atrás y descubrir nuevo conocimiento mediante razonamiento hacia adelante.

## Funciones Principales

### `query(tripleta: Tripleta, kb: dict)`

**Proposito**: Realiza una consulta sobre la base de conocimientos y retorna todas las sustituciones posibles que satisfacen la tripleta.

**Algoritmo**:

1. Búsqueda en Hechos: Intenta unificar con cada hecho en la KB.
2. Aplicación de Reglas: Si no hay hechos directos, aplica reglas recursivamente.
3. Cálculo de Confianza: Usa el mínimo de las confianzas (lógica AND).
4. Retorno Generador: Yield de cada sustitución encontrada con su confianza

**Ejemplos**:

1. **Consulta Directa a Hechos**

    ```bash
        # KB tiene: Tripleta("pizza", "contiene", "queso")
        consulta = Tripleta("pizza", "contiene", "queso")
        resultados = list(query(consulta, kb))
        # [ ({}, 1.0) ]
    ```

2. **Consulta con Variables**

    ```bash
        # KB tiene: 
        # - Tripleta("pizza", "contiene", "queso")
        # - Tripleta("ensalada", "contiene", "lechuga")
        consulta = Tripleta("X", "contiene", "Y")
        resultados = list(query(consulta, kb))
        # [
        #   ({"X": "pizza", "Y": "queso"}, 1.0),
        #   ({"X": "ensalada", "Y": "lechuga"}, 1.0)
        # ]
    ```

### `query_antecedentes(antecedentes: list[Tripleta], kb: dict, ss_inicial: Sustitucion)`

**Proposito**: Satisface TODOS los antecedentes de una regla recursivamente.

**Algoritmo**:

1. **Caso Base**: Si no hay antecedentes, retorna la sustitución con confianza 1.0
2. **Caso Recursivo**:
   - Toma el primer antecedente y aplica la sustitución actual.
   - Encuentra todas las formas de satisfacerlo.
   - Para cada una, satisface recursivamente el resto de antecedentes.
   - Combinación de Confianzas: Usa el mínimo (lógica AND).

**Ejemplos**:

```bash
    antecedentes = [
        Tripleta("X", "contiene", "vegetales"),
        Tripleta("X", "no_contiene", "carne")
    ]
    ss_inicial = Sustitucion({"X": "ensalada"})

    resultados = list(query_antecedentes(antecedentes, kb, ss_inicial))
    # Encontraríamos hechos que verificasen todos los antecedentes recursivamente [ ({"X": "ensalada"}, 1.0) ]
```

### `descubrir(kb: dict) -> list[Tripleta]`

**Proposito**: Encadenamiento hacia adelante - descubre nuevos hechos aplicando reglas.

**Algoritmo**:

1. Por cada regla: Intenta satisfacer todos sus antecedentes
2. Generar Consecuente: Para cada combinación exitosa, aplica la sustitución al consecuente
3. Calcular Confianza.
4. Evitar Duplicados:
   - No agregar si ya existe en KB
   - En nuevos hechos, mantener el de máxima confianza

**Ejemplos**:

```bash
    # KB inicial:
    hechos = [Tripleta("pizza", "contiene", "queso")]
    reglas = [
        Regla(
            Tripleta("X", "contiene", "lactosa", 0.8),
            [Tripleta("X", "contiene", "queso")],
            0.8
        )
    ]

    nuevos_hechos = descubrir(kb)
    # [ Tripleta("pizza", "contiene", "lactosa", 0.64) ]
    # Cálculo: min(0.8, 0.8, 1.0) = 0.64
```

### `razonar(tripleta: Tripleta, kb: dict) -> bool`

**Proposito**: Encadenamiento hacia atrás - determina si una tripleta puede ser demostrada.

**Algoritmo**:

1. Consulta Completa: Usa query() para buscar hechos directos o inferidos.
2. Evaluación Booleana: Retorna True si hay al menos un resultado, False en caso contrario.

**Ejemplos**:

1. **Razonamiento con Hecho Directo**

    ```bash
        # KB: Tripleta("pizza", "contiene", "queso")
            consulta = Tripleta("pizza", "contiene", "queso")
            resultado = razonar(consulta, kb)  # True
    ```

2. **Razonamiento con Inferencia**

    ```bash
        # KB: 
        # - Hecho: Tripleta("pizza", "contiene", "queso")
        # - Regla: "X contiene lactosa <- X contiene queso"
        consulta = Tripleta("pizza", "contiene", "lactosa")
        resultado = razonar(consulta, kb)  # True (inferido mediante regla)
    ```

## Ejemplos Complejos de Flujo

### Aplicación de Regla con Variables

```bash
    # Regla: "Si X contiene Y y Y contiene lactosa, entonces X contiene lactosa"
    regla = Regla(
        Tripleta("X", "contiene", "lactosa", 0.8),
        [
            Tripleta("X", "contiene", "Y"),
            Tripleta("Y", "contiene", "lactosa")
        ],
        0.8
    )

    # Hechos:
    # - Tripleta("pizza", "contiene", "queso")
    # - Tripleta("queso", "contiene", "lactosa", 0.9)

    # Consulta: "pizza contiene lactosa"
    consulta = Tripleta("pizza", "contiene", "lactosa")

    # Flujo:
    # 1. Unifica con consecuente: X="pizza"
    # 2. Query antecedentes con ss_inicial = {"X": "pizza"}
    # 3. Primer antecedente: "pizza contiene Y" -> Y = "queso"
    # 4. Segundo antecedente: "queso contiene lactosa" -> éxito con confianza 0.9
    # 5. Confianza total: min(0.8, 0.8, 0.9) = 0.64

    resultados = list(query(consulta, kb))
    # [ ({}, 0.64) ] -> SI
```

### Múltiples Antecedentes

```bash
    # KB con diferentes formas de inferir el mismo hecho
    kb = {
        'hechos': [
            Tripleta("pizza", "contiene", "queso"),
            Tripleta("pizza", "contiene", "mozzarella")
        ],
        'reglas': [
            Regla(
                Tripleta("X", "contiene", "lactosa"),
                [
                    Tripleta("X", "contiene", "queso"),
                    Tripleta("X", "contiene", "mozzarella")
                ],
                0.8
            ),
        ]
    }

    consulta = Tripleta("pizza", "contiene", "lactosa")
    resultados = list(query(consulta, kb))
    # Cumple ambas reglas: SI
```

## Separación de Responsabilidades

- `query()`: Búsqueda general
- `query_antecedentes()`: Satisfacción de conjuntos de condiciones
- `descubrir()`: Inferencia hacia adelante
- `razonar()`: Verificación booleana hacia atrás
