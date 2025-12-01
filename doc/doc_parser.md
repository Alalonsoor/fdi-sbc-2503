# Parser

## Descripción general

El módulo `parser.py` se encarga de analizar (parsear) las entradas de texto del usuario y convertirlas en estructuras internas
del sistema: tripletas, reglas y tipos de consulta. Actúa como la capa de traducción entre el lenguaje que escribe el usuario
y los objetos que el motor lógico puede procesar.

Este módulo no razona ni consulta la base de conocimiento: solamente **interpreta texto** y construye objetos bien formados.

---

## Funciones principales

### `parsear_tripleta(cadena: str) -> Tripleta`

Convierte una cadena de texto en una instancia de `Tripleta`.

#### Formato esperado

```
sujeto predicado objeto [confianza]
```

- `confianza` es opcional.
- Si no se especifica, se asume confianza = 1.0.

#### Ejemplo

```python
parsear_tripleta("tomate color rojo")
parsear_tripleta("leche tipo lacteo [0.8]")
```

#### Comportamiento
- Divide la cadena en sus componentes lógicos.
- Valida el número de elementos.
- Parsea la confianza si aparece.
- Devuelve un objeto `Tripleta`.

Si el formato es incorrecto, lanza una excepción.

---

### `parsear_regla(cadena: str) -> Regla`

Convierte una regla escrita como texto en un objeto `Regla`.

#### Formato esperado

```
consecuente <- antecedente1, antecedente2, ...
```

Ejemplo:

```
X alergeno lactosa <- X tipo lacteo [0.9]
```

#### Comportamiento
- Separa consecuente de antecedentes mediante `<-`.
- Convierte el consecuente en una `Tripleta`.
- Convierte cada antecedente en una `Tripleta`.
- Construye un objeto `Regla`.

---

### `parsear_consulta(cadena: str) -> tuple[Tripleta | None, str]`

Interpreta una cadena introducida por el usuario y determina de qué tipo de operación se trata.

#### Tipos de entrada reconocidos

| Entrada | Tipo devuelto |
|----------|---------------|
| `S P O .` | `hecho` |
| `S P O ?` | `consulta` |
| `razona si S P O ?` | `razonar` |
| `descubrir!` | `descubrir` |

#### Ejemplos

```
tomate tipo verdura .            -> ("hecho", Tripleta)
tomate tipo verdura ?            -> ("consulta", Tripleta)
razona si tomate tipo verdura ?  -> ("razonar", Tripleta)
descubrir!                       -> ("descubrir", None)
```

#### Comportamiento
1. Elimina espacios sobrantes.
2. Comprueba si la entrada está vacía.
3. Detecta el comando `descubrir!`.
4. Detecta el prefijo `razona si`.
5. Analiza si termina en `?` o `.`.
6. Llama internamente a `parsear_tripleta`.
7. Devuelve la tripleta y el tipo de consulta.

Si el formato es incorrecto, lanza un `ValueError`.

---

## Formato de los términos

El parser distingue:

- **Literales**: palabras normales (`tomate`, `verdura`, `queso`)
- **Variables**: términos del lenguaje que representan incógnitas

El formato concreto de variables debe ser coherente con la implementación de `es_variable` en `ed.py`.

Además, se aplican las siguientes convenciones:

- **Detección de variables:** Las variables se identifican mediante la función `es_variable` definida en `ed.py`, que generalmente reconoce términos que empiezan con mayúscula o que cumplen un patrón específico. Esto permite distinguirlas de literales comunes.
- **Sensibilidad a mayúsculas y minúsculas:** El parser es sensible a mayúsculas y minúsculas para diferenciar variables de literales. Por ejemplo, `X` se tratará como variable, mientras que `x` como literal.
- **Caracteres permitidos:** Los términos pueden contener letras, números y guiones bajos. No se permiten caracteres especiales o espacios dentro de un término individual.

---

## Detalles de implementación

### Normalización de entrada

Para procesar las cadenas de entrada, el parser primero elimina espacios en blanco sobrantes al inicio y al final mediante `strip()`. Luego, divide la cadena en tokens usando `split()` para separar términos y posibles indicadores de confianza o símbolos finales (`.`, `?`).

### Detección de comandos

El parser reconoce comandos especiales:

- `descubrir!` se identifica directamente como un comando sin parámetros, devolviendo el tipo `"descubrir"` y sin tripleta asociada.
- `razona si` es un prefijo que indica una consulta de razonamiento. El parser verifica que la cadena comience con este prefijo para procesarla adecuadamente.

### Identificación de hechos vs consultas

El parser distingue entre hechos y consultas analizando el carácter final de la entrada:

- Un punto (`.`) indica que la entrada es un hecho.
- Un signo de interrogación (`?`) indica que es una consulta.
- La ausencia o presencia incorrecta de estos caracteres genera error.

### Tratamiento de confianza

Cuando una tripleta contiene un término de confianza, este debe estar entre corchetes al final, por ejemplo `[0.8]`. El parser extrae esta parte, la convierte a un valor numérico de tipo `float` y la asocia con la tripleta. Si no se especifica confianza, se asigna por defecto `1.0`.

### Uso de pyparsing o lógica equivalente

Aunque el módulo puede utilizar la librería `pyparsing` para análisis estructural avanzado, la implementación actual puede basarse en lógica manual para dividir y validar componentes de las reglas y tripletas. Esto incluye dividir la cadena por delimitadores (`<-`, `,`), validar el número de términos y parsear los valores de confianza, sin depender exclusivamente de un parser formal.

---

## Ejemplos completos

### Ejemplo de añadir un hecho

Entrada:

```
tomate color rojo .
```

Resultado:

- Tipo: `"hecho"`
- Tripleta: sujeto=`"tomate"`, predicado=`"color"`, objeto=`"rojo"`, confianza=1.0

### Ejemplo de consulta con una variable

Entrada:

```
X color rojo ?
```

Resultado:

- Tipo: `"consulta"`
- Tripleta: sujeto=`"X"` (variable), predicado=`"color"`, objeto=`"rojo"`, confianza=1.0

### Ejemplo de consulta de razonamiento

Entrada:

```
razona si X tipo lacteo ?
```

Resultado:

- Tipo: `"razonar"`
- Tripleta: sujeto=`"X"` (variable), predicado=`"tipo"`, objeto=`"lacteo"`, confianza=1.0

### Ejemplo de comando descubrir

Entrada:

```
descubrir!
```

Resultado:

- Tipo: `"descubrir"`
- Sin tripleta asociada (None)

---
