"""
Utilidades comunes para la aplicación
"""
from typing import Dict, List, Tuple, Any
from pydantic import BaseModel


def build_update_query(
    table_name: str,
    update_data: Dict[str, Any],
    id_field: str,
    id_value: Any
) -> Tuple[str, List[Any]]:
    """
    Construye una query de UPDATE dinámica basada en los campos proporcionados.
    
    Args:
        table_name: Nombre de la tabla a actualizar
        update_data: Diccionario con los campos a actualizar
        id_field: Nombre del campo ID
        id_value: Valor del ID
    
    Returns:
        Tupla con (query_string, lista_de_valores)
    
    Example:
        >>> query, values = build_update_query(
        ...     "users", 
        ...     {"name": "John", "age": 30}, 
        ...     "id", 
        ...     1
        ... )
        >>> print(query)
        'UPDATE users SET name = $1, age = $2 WHERE id = $3 RETURNING *'
        >>> print(values)
        ['John', 30, 1]
    """
    if not update_data:
        raise ValueError("No hay datos para actualizar")
    
    update_fields = []
    values = []
    
    for idx, (field, value) in enumerate(update_data.items(), start=1):
        update_fields.append(f"{field} = ${idx}")
        values.append(value)
    
    query = f"""
        UPDATE {table_name} 
        SET {', '.join(update_fields)}
        WHERE {id_field} = ${len(values) + 1}
        RETURNING *
    """
    values.append(id_value)
    
    return query, values


def build_insert_query(
    table_name: str,
    data: Dict[str, Any]
) -> Tuple[str, List[Any]]:
    """
    Construye una query de INSERT dinámica basada en los campos proporcionados.
    
    Args:
        table_name: Nombre de la tabla
        data: Diccionario con los campos y valores a insertar
    
    Returns:
        Tupla con (query_string, lista_de_valores)
    
    Example:
        >>> query, values = build_insert_query(
        ...     "users", 
        ...     {"name": "John", "age": 30}
        ... )
        >>> print(query)
        'INSERT INTO users (name, age) VALUES ($1, $2) RETURNING *'
        >>> print(values)
        ['John', 30]
    """
    if not data:
        raise ValueError("No hay datos para insertar")
    
    fields = list(data.keys())
    placeholders = [f"${i}" for i in range(1, len(fields) + 1)]
    values = list(data.values())
    
    query = f"""
        INSERT INTO {table_name} ({', '.join(fields)})
        VALUES ({', '.join(placeholders)})
        RETURNING *
    """
    
    return query, values


def model_to_dict(model: BaseModel, exclude_unset: bool = True, exclude_none: bool = False) -> Dict[str, Any]:
    """
    Convierte un modelo de Pydantic a diccionario con opciones de filtrado.
    
    Args:
        model: Modelo de Pydantic
        exclude_unset: Excluir campos no establecidos
        exclude_none: Excluir campos con valor None
    
    Returns:
        Diccionario con los datos del modelo
    """
    data = model.model_dump(exclude_unset=exclude_unset, exclude_none=exclude_none)
    return data
