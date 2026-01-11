# CORRECCION

- Reparto de trabajo: Suficiente
- Entrega: OK

## Test básico común

`corregir.sh test/comun.txt SI NO`

Puntos: 8/10

Error en 't_pinguino t_tipo t_pez ?': se esperaba 'SI', dio: NO.
Error en 't_pinguino t_tipo t_pez ?': se esperaba 'NO', dio: SI.
(opcional revocación hechos, sintaxis mal interpretada)

## Test integración

Usado `test/pruebas_integracion.txt`. Muy bien!

`corregir.sh test/pruebas_integracion.txt SI NO`

Puntos: 10/10

## Test especial

```
sudo mount --bind test/kb_especial kb
corregir.sh test/especial.txt SI NO
```

Puntos: 3/10 -2 por errores carga

Notas: vuestro código no carga bases de conocimiento genéricas. Debe cargar los
ficheros txt, independientemente de que tengan hechos o reglas. Además, se
atraganta con las extensiones desconocidas. Por otro lado, muchas consultas
incluida la genérica `X Y Z?` dan errores de recursión infinita.
