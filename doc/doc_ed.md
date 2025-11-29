# Estructuras de Datos del Sistema

## Descripción general

El archivo ed.py define las estructuras de datos fundamentales para el sistema de experto. Contiene las clases principales para representar tripletas, reglas y sustituciones, que son los componentes básicos del motor de inferencia.

## Clases y Funciones Principales

### Función es_variable(term: str) -> bool

**Proposito**: Determina si un término es una variable en el sistema.

**Algoritmo**: 
- Las variables se identifican por comenzar con una letra mayúscula.
- Los literales (constantes) comienzan con minúscula o números.

**Ejemplo**:

```bash
es_variable("X") # True
es_variable("Persona") # True
es_variable("pizza") # False
es_variable("123") # False
```

### Función es_literal(term: str) -> bool

**Proposito**: Determina si un término es un literal

**Algoritmo**: 
- Niega el resultado de es_variable().
- Cualquier término que no sea variable, es literal.

**Ejemplo**:

```bash
es_variable("pizza") # True
es_variable("123") # True
es_variable("X") # False
es_variable("Persona") # False
```

### Clase Tripleta

#### Descripción

Representa una afirmación en formato sujeto-predicado-objeto. Es la unidad básica de conocimiento en el sistema.

#### Atributos

- **sujeto**: Entidad principal de la tripleta
- **predicado**: Relación o propiedad
- **objeto**: Valor o entidad relacionada
- **confianza**: Nivel de confianza (0.0 a 1.0) para lógica difusa.

#### Métodos Principales

**`terminos() -> list[str]`**

**Proposito**: Devuelve una lista con los tres términos de la tripleta.

**aplicar_sustituciones(ss: Sustitucion) -> Tripleta**

**Proposito**: Crea una nueva tripleta aplicando una sustitución a todos sus términos.

**Algoritmo**:

1. Crea una nueva tripleta
2. Aplica la sustitución al sujeto, predicado y objeto
3. Mantiene la misma confianza

**Ejemplo**:

```bash
tripleta = Tripleta("X", "contiene", "Y")
sustitucion = Sustitucion({"X": "pizza", "Y": "queso"})
nueva_tripleta = tripleta.aplicar_sustitucion(sustitucion)
# Resultado: Tripleta("pizza", "contiene", "queso")
```

**`get_confianza() -> float`**

**Proposito**: Obtiene el valor de confianza de la tripleta.

### Clase Regla

#### Descripción

Representa una regla de inferencia en formato "consecuente <- antecedentes". Permite derivar nuevo conocimiento a partir de conocimiento existente.

#### Atributos

- **consecuente**: Tripleta que se puede inferir si se cumplen los antecedentes.
- **antecedentes**: Lista de tripletas que deben ser verdaderas para aplicar la regla.
- **confianza**: Confianza de la regla (afecta a la confianza del consecuente inferido).

#### Métodos Principales

**`get_consecuentes() -> Tripleta`**

**Proposito**: Devuelve el consecuente de la regla.

**`get_antecedentes() -> list[Tripleta]`**

**Proposito**: Devuelve la lista de antecedentes de la regla.

### Clase Sustitucion

#### Descripción

Representa un mapeo de variables a valores. Esencial para el proceso de unificación y aplicación de reglas.

#### Atributos

- **mappings**: Diccionario que mapea nombres de variables a valores

#### Métodos Principales

**`get_mappings() -> dict[str, str]`**

**Proposito**: Devuelve el diccionario de mapeos completo.

**`get(var: str) -> str | None`**

**Proposito**: Obtiene el valor de una variable específica.

**Ejemplo**:
```bash
ss = Sustitucion({"X": "pizza", "Y": "queso"})
valor = ss.get("X") # pizza
valor = ss.get("Z") # None
```
**add(var: str, value: str) -> None**

**Proposito**: Agrega una nueva sustitución al mapeo.

**`aplicar(termino: str) -> str`**

**Proposito**: Aplica la sustitución a un término de manera recursiva.

**Algoritmo**:

1. Si el término es una variable y tiene sustitución, aplica recursivamente.
2. Si el término es literal, lo devuelve sin cambios.
3. Maneja sustituciones encadenadas.
   - {"X": "Y", "Y": "pizza"}
   - (X → Y → "pizza")

**Ejemplo**:
```bash
ss = Sustitucion({"X": "Y", "Y": "pizza"})

# Sustitución directa
ss.aplicar("Y") # (Y → "pizza")

# Sustitución recursiva
ss.aplicar("X")  # "pizza" (X → Y → "pizza")

# Sustitución recursiva
ss.aplicar("queso")  # "queso" (literal, no cambia)

# Variable sin sustitución
ss.aplicar("Z")  # "Z" (se mantiene igual)
```

**__contains__(var: str) -> bool**

## Ejemplos de Uso Completo

```python
# Crear una sustitución
sustitucion = Sustitucion({"X": "pizza", "Y": "queso"})

# Verificar sustituciones
if "X" in sustitucion:
    valor = sustitucion.get("X")  # "pizza"

# Aplicar a una tripleta
tripleta = Tripleta("X", "contiene", "Y")
nueva_tripleta = tripleta.aplicar_sustitucion(sustitucion)
# Resultado: Tripleta("pizza", "contiene", "queso")
```

## Uso en Sistema Culinario

```python
from ed import Tripleta, Regla, Sustitucion, es_variable

# Definir hechos
hecho1 = Tripleta("pizza_margarita", "contiene", "queso_mozzarella")
hecho2 = Tripleta("queso_mozzarella", "contiene", "lactosa", 0.9)

# Definir regla
regla_lactosa = Regla(
    consecuente=Tripleta("X", "contiene", "lactosa", 0.8),
    antecedentes=[Tripleta("X", "contiene", "Y"), Tripleta("Y", "contiene", "lactosa")],
    confianza=0.8
)

# Crear y aplicar sustitución
sustitucion = Sustitucion({"X": "pizza_margarita", "Y": "queso_mozzarella"})
tripleta_inferida = regla_lactosa.consecuente.aplicar_sustitucion(sustitucion)
# Tripleta inferida: "pizza_margarita contiene lactosa" con confianza 0.72 (0.9 * 0.8)
```