def format_table(data, columns=3, col_width=15):
    """
    Formatea una lista en una tabla con columnas.
    
    :param data: Lista de elementos a imprimir en forma de tabla.
    :param columns: Número de columnas.
    :param col_width: Ancho de cada columna.
    :return: Una cadena con la tabla formateada.
    """
    import math
    
    rows = math.ceil(len(data) / columns)
    formatted_rows = []

    for i in range(rows):
        row_items = []
        for j in range(columns):
            index = i + j * rows
            if index < len(data):
                row_items.append(f"{data[index]:<{col_width}}")
            else:
                row_items.append(" " * col_width)
        formatted_rows.append(" ".join(row_items))
    
    return "\n".join(formatted_rows)
