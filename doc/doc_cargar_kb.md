# Cargar la Base de Conocimiento

## Descripción general

El módulo `cargar_kb.py` se encarga de cargar la base de conocimiento (KB) del sistema a partir de dos ficheros de texto:
uno con los hechos y otro con las reglas. A partir de estos archivos, construye las estructuras internas que el sistema
utiliza para razonar y responder consultas.

El resultado de la carga es un diccionario con dos claves principales:

- `hechos`: lista de objetos `Tripleta`
- `reglas`: lista de objetos `Regla`

---

## Función principal

### `carga_kb(fichero_hechos: Path, fichero_reglas: Path) -> dict`

Carga los hechos y reglas desde los ficheros indicados y construye la base de conocimiento.

### Parámetros

- `fichero_hechos` (`Path`): Ruta al fichero que contiene los hechos.
- `fichero_reglas` (`Path`): Ruta al fichero que contiene las reglas.

### Valor de retorno

Un diccionario con la estructura:

```python
{
    "hechos": List[Tripleta],
    "reglas": List[Regla]
}
```

donde cada hecho es un objeto `Tripleta` y cada regla es un objeto `Regla`.

---

## Funcionamiento

La función sigue los siguientes pasos:

1. Inicializa dos listas vacías: una para hechos y otra para reglas.
2. Comprueba si existe el fichero de hechos:
   - Si existe, lo abre y procesa línea a línea.
   - Si no existe, la lista de hechos queda vacía.
3. Para cada línea del fichero de hechos:
   - Elimina espacios sobrantes.
   - Ignora líneas vacías.
   - Ignora líneas que comienzan por `#` (comentarios).
   - Convierte la línea en una `Tripleta` mediante la función `parsear_tripleta`.
4. Repite el mismo proceso para el fichero de reglas:
   - Ignora líneas vacías y comentadas.
   - Convierte cada línea válida en una `Regla` usando `parsear_regla`.
5. Devuelve un diccionario con ambas listas.

---

## Ejemplo de uso

```python
from pathlib import Path
from sbc.cargar_kb import carga_kb

kb = carga_kb(Path("kb/ingredientes.txt"), Path("kb/reglas.txt"))

print(len(kb["hechos"]))   # número de hechos cargados
print(len(kb["reglas"]))   # número de reglas cargadas
```

---

## Formato esperado de los ficheros

### Fichero de hechos

Cada línea debe definir una tripleta con el formato:

```
sujeto predicado objeto [confianza]
```

Ejemplo:

```
tomate color rojo
leche tipo lacteo [0.9]
```

- La confianza es opcional.
- Si no se indica, se asume confianza 1.0.
- Las líneas que comiencen por `#` se ignoran.

### Fichero de reglas

Cada línea debe definir una regla lógica con la estructura:

```
consecuente <- antecedente1, antecedente2, ...
```

Ejemplo:

```
X proteina alto <- X tipo carne
X alergeno lactosa <- X tipo lacteo [0.8]
```

- Los antecedentes pueden ser uno o varios.
- Cada antecedente es una tripleta.
- Las reglas también pueden incluir confianza.

---

## Gestión de errores

- Si un fichero no existe, la lista correspondiente (hechos o reglas) se deja vacía.
- La función no aborta el programa por ficheros inexistentes.
- Si el contenido de una línea es incorrecto, la excepción se propagará desde
  `parsear_tripleta` o `parsear_regla`.

---

## Relación con otros módulos

`cargar_kb.py` depende directamente de:

- `parser.py`:
  - Funciones `parsear_tripleta` y `parsear_regla`
- `ed.py`:
  - Clases `Tripleta` y `Regla`

Este módulo no realiza razonamiento ni consultas directamente: su única responsabilidad
es **construir la base de conocimiento inicial**.

---

## Resumen

El módulo `cargar_kb.py`:

- Centraliza la lectura de datos desde ficheros externos.
- Limpia entradas inválidas (comentarios y líneas vacías).
- Convierte texto en estructuras lógicas internas.
- Construye una KB lista para ser usada por `query.py` y `cli.py`.

Es el primer paso en el flujo general del sistema, ya que sin esta carga inicial
no es posible realizar consultas ni razonamiento.
