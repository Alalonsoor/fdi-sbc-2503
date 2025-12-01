# Interfaz de linea de comandos

## Descripción general

El módulo `cli.py` implementa la interfaz de línea de comandos (CLI) del sistema. Su función principal es actuar como punto de entrada
para el usuario, permitiendo introducir consultas, hechos y comandos, y mostrando los resultados formateados de manera adecuada.

Este módulo no realiza razonamiento ni consultas directamente, sino que delega esas tareas en los módulos correspondientes
(`query.py`, `parser.py`, `ed.py`) y presenta los resultados de forma legible.

---

## Funciones principales

### `extraer_variables(tripleta: Tripleta) -> list[str]`

Devuelve la lista de variables presentes en una tripleta sin duplicados y respetando el orden de aparición.

#### Funcionamiento
- Recorre los tres términos de la tripleta.
- Usa `es_variable` para identificar qué términos son variables.
- Evita incluir variables repetidas.
- Devuelve una lista con las variables encontradas.

#### Ejemplo

```python
Tripleta("?x", "tipo", "?y")  ->  ["?x", "?y"]
Tripleta("tomate", "tipo", "verdura")  ->  []
```

---

### `formatear_resultados(consulta_str: str, kb: dict)`

Esta función es un generador que procesa una consulta del usuario y devuelve una secuencia de líneas de texto listas para ser mostradas en pantalla.

#### Funcionamiento general

1. Llama a `parsear_consulta` para interpretar la entrada del usuario.
2. Identifica el tipo de consulta:
   - `hecho`
   - `consulta`
   - `razonar`
   - `descubrir`
3. Ejecuta la lógica correspondiente a cada tipo.
4. Devuelve resultados mediante `yield`.

---

## Casos de uso

### Añadir hechos (`tipo == 'hecho'`)

Si el usuario introduce una tripleta con `.` al final:

```
tomate tipo verdura .
```

- Si el hecho no existe:
  ```
  Hecho agregado: tomate tipo verdura
  ```
- Si ya existe:
  ```
  Ya existe el hecho: tomate tipo verdura
  ```

---

### Razonar (`tipo == 'razonar'`)

Ejemplo:

```
razona si tomate tipo verdura ?
```

Salida:
```
SI
```
o
```
NO
```

La función delega el razonamiento al módulo `query.py`.

---

### Consulta (`tipo == 'consulta'`)

Ejemplo sin variables:

```
tomate tipo verdura ?
```

- Si no hay resultados:
  ```
  NO
  ```
- Si hay resultados:
  ```
  SI
  ```
  o, si la confianza es menor que 1:
  ```
  SI (confianza: 90%)
  ```

---

#### Consulta con una variable

Ejemplo:

```
?x tipo fruta ?
```

Salida:
```
manzana
pera [70%]
```

Si la variable está en el objeto:

```
pizza contiene ?x ?
```

Salida:
```
contiene = queso [80%]
```

---

#### Consulta con varias variables

Ejemplo:

```
?x contiene ?y ?
```

Salida:
```
pizza queso
ensalada tomate [90%]
```

---

### Descubrir nuevos hechos (`tipo == 'descubrir'`)

Ejemplo:

```
descubrir!
```

Salida:
```
Se descubrieron 2 nuevos hechos:
  pizza contiene queso
  ensalada contiene tomate [0.8]
```

Si no hay nuevos hechos:
```
No se descubrieron nuevos hechos
```

---

## Relación con otros módulos

El módulo `cli.py` depende directamente de:

- `parser.py`
  - para analizar la entrada del usuario
- `query.py`
  - para consultas, razonamiento y descubrimiento
- `ed.py`
  - para estructuras de datos (`Tripleta`, `Sustitucion`, `Regla`)
- `cargar_kb.py`
  - para inicializar la base de conocimiento

---

## Flujo del programa

Cuando se ejecuta directamente:

1. Se carga la base de conocimiento desde `kb/ingredientes.txt` y `kb/reglas.txt`.
2. Se entra en un bucle interactivo:
   - Se pide una consulta al usuario.
   - Se procesa la entrada.
   - Se muestran los resultados.
3. El programa finaliza cuando el usuario escribe:
   - `exit`, `quit`, `q`, `cerrar` o `e`.


