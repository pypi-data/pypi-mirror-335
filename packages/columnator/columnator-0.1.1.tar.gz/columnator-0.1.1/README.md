# Columnator

`Columnator` es una librería simple para formatear listas en tablas con múltiples columnas en Python. Es útil para mostrar datos de forma ordenada en la terminal, similar al comando `column` de Bash.

## Instalación

Después de subir el paquete a PyPI, puedes instalarlo con:

```bash
pip install columnator
```

Si estás probando localmente antes de subirlo, instálalo con:

```bash
pip install .
```

## Uso

```python
from columnator import format_table

data = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt", "file6.txt"]
print(format_table(data, columns=3))
```

### Salida esperada:
```
file1.txt      file3.txt      file5.txt      
file2.txt      file4.txt      file6.txt      
```

## Parámetros de `format_table`

- `data` (list): Lista de elementos a mostrar en la tabla.
- `columns` (int, opcional): Número de columnas. Por defecto es 3.
- `col_width` (int, opcional): Ancho de cada columna. Por defecto es 15.

## Contribuir

Si deseas mejorar esta librería, ¡tus contribuciones son bienvenidas! Puedes clonar el repositorio y hacer un pull request.

```bash
git clone https://github.com/PanecilloPY/Columnator/
cd Columnator
```

## Licencia

Este proyecto está bajo la licencia MIT.

