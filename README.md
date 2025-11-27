# Sistema Experto Culinario - Grupo 03

## Información del Grupo
- **Curso**: Sistemas Basados en Conocimiento 2025/26
- **Grupo**: 03
- **Integrantes**:
    - Álvaro Alonso
    - Jiahao Cheng
    - Francisco Pastor
    - Jiayi Wang

## Descripción del Proyecto
Sistema experto para el dominio culinario capaz de resolver múltiples tareas relacionadas con gastronomía y restricciones dietéticas.

## Dominios y Tareas Implementadas

### 1. Gestión de Alergenos y Restricciones Dietéticas
- Identificación de ingredientes.
- Verificación de compatibilidad de recetas con restricciones.

### 2. Composición de Ingredientes y Recetas
- Análisis nutricional de platos.
- Compatibilidad de ingredientes.

### 3. Maridajes y Combinaciones Gastronómicas
- Armonización de sabores.
- Recomendaciones de maridajes.

## Instalación y Ejecución

### Prerrequisitos

- Python ≥ 3.10, recomendado 3.13
- UV package manager

### Instalación

```bash
git clone https://github.com/usuario/fdi-sbc-25XX.git
cd fdi-sbc-25XX
uv sync
```

### Ejecición

```bash
uv run -m sbc.cli
```

## Estructura del Proyecto

fdi-sbc-25XX/
├── kb/                    # Base de conocimiento
│   ├── ingredientes.txt
│   └── hechos.txt
├── sbc/                   # Motor de inferencia
│   ├── __init__.py
│   ├── cargar_kb.py
│   ├── cli.py
│   ├── ed.py
│   ├── parser.py
│   ├── query.py
│   └── unificar.py
├── test/                  # Tests funcionales
│   ├── test_cargar_kb.py
│   ├── test_cli.py
│   ├── test_descubrir.py
│   ├── test_parser.py
│   ├── test_query.py
│   └── test_unify.py
├── doc/                   # Documentación
│   ├── ...
│   └── ...
├── pyproject.toml
└── README.md

## Uso del Sistema

### Comandos Disponibles

- Consultas: X Y Z ? ("tomate color rojo ?")
- Añadir hechos: X Y Z . ("tomate color rojo .")
- Descubrir conocimiento: describir!
- Razonamiento: razona si X Y Z ? ("razona si pizza contiene glutén ?")

### Ejemplos de consultas
```bash
> tomate color rojo ?
< NO
> tomate color rojo .
> tomate color rojo ?
< SI
> tomate color X ?
< color = rojo
> X color rojo ?
< tomate
```

## Base de conocimiento

### Sintaxis Implementada

minus = "a" | ... | "z" ;
mayus = "A" | ... | "Z" ;
digito = "0" | ... | "9" ;
caracter = minus | mayus | digito | "_" ;
literal = minus { caracter } ;
variable = mayus { caracter } ;
termino = literal | variable ;
tripleta = termino "  " termino " " termino ;
afirmacion = tripleta "." [ extension ] ;
comentario = "#" { .... } "\n" ;
consulta = tripleta "?" | "razona si " tripleta "?" ;
palabra = { caracter } ;
comando = palabra { " " palabra } "!" ;
regla = tripleta "<-" tripleta { ", " tripleta } "." [extension ] ;
extension = "[" opcional { "; " opcional } " ]" ;
opcional = difusa | precedencia | restriccion ;
difusa = "0." { digito } | "1" ;

### Ejemplo de hechos

```bash
# COLORES
tomate color rojo [0.90]

# GRANOS
pan tipo grano
```

### Ejemplo de reglas

```bash
# Combinaciones
Ingrediente1 combina_bien Ingrediente2 <- Ingrediente1 sabor dulce, Ingrediente2 sabor acido [0.85]

# PROPIEDADES NUTRICIONALES - RICO EN FIBRA
Plato rico_en fibra <- Plato ingrediente Ingrediente, Ingrediente tipo verdura
```

## Tests y Validación

### Ejecución de Tests
```bash
python -m pytest
uv format --check
```

### Cobertura de Funcionalidades
- Motor de interferencia estándar.
- Base de conocimiento modular.
- CLI interactiva.
- Encadenamiento hacia adelante/atrás.
- Gestión de errores.

## Documentación Adicional
...

## Desarrollo

### Convenciones del Código
- Formateo automático con uv format
...

### Gestión de Proyecto
- Seguimiento mediante GitHub
- Revisiones de código entre pares y grupales

