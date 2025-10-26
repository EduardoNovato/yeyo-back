# API de Servicios Tienda Online

API REST desarrollada con FastAPI para gestionar los servicios de una tienda online.

## 🚀 Características

- ✅ Gestión de proveedores (CRUD completo)
- ✅ Gestión de compras de proveedor (CRUD completo)
- ✅ Validación de datos con Pydantic
- ✅ Manejo robusto de errores
- ✅ Conexión asíncrona a PostgreSQL
- ✅ Pool de conexiones optimizado
- ✅ Logging estructurado
- ✅ CORS configurado
- ✅ Documentación automática con Swagger/ReDoc
- ✅ Health check endpoint

## 📋 Requisitos

- Python 3.8+
- PostgreSQL
- Variables de entorno configuradas

## 🔧 Instalación

1. Clonar el repositorio
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno (.env):

```env
HOST_DB=localhost
PORT_DB=5432
NAME_DB=nombre_bd
USER_DB=usuario
PASSWORD_DB=contraseña
```

4. Ejecutar la aplicación:

```bash
python main.py
```

O con uvicorn:

```bash
uvicorn main:app --reload
```

## 📚 Endpoints

### Raíz

- `GET /` - Información de la API
- `GET /health` - Estado de salud de la API y base de datos

### Proveedores

- `POST /proveedores/` - Crear proveedor
- `GET /proveedores/` - Listar todos los proveedores
- `GET /proveedores/{id}` - Obtener proveedor por ID
- `PUT /proveedores/{id}` - Actualizar proveedor
- `DELETE /proveedores/{id}` - Eliminar proveedor
- `GET /proveedores/buscar/nombre?nombre={nombre}` - Buscar por nombre

### Compras de Proveedor

- `POST /compras-proveedor/` - Crear compra
- `GET /compras-proveedor/` - Listar todas las compras
- `GET /compras-proveedor/{id}` - Obtener compra por ID
- `GET /compras-proveedor/proveedor/{id_proveedor}` - Compras de un proveedor
- `PUT /compras-proveedor/{id}` - Actualizar compra
- `DELETE /compras-proveedor/{id}` - Eliminar compra

## 📖 Documentación

Una vez iniciada la aplicación, acceder a:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🏗️ Estructura del Proyecto

```
back-tienda/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_service.py      # Clase base para servicios
│   │   ├── config.py             # Configuración de la BD
│   │   ├── constants.py          # Constantes centralizadas
│   │   ├── database.py           # Conexión a la BD
│   │   └── utils.py              # Utilidades comunes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── proveedor.py          # Modelos de proveedor
│   │   └── compra_proveedor.py   # Modelos de compra
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── proveedor_router.py   # Endpoints de proveedor
│   │   └── compra_proveedor_router.py
│   └── service/
│       ├── __init__.py
│       ├── proveedor_service.py  # Lógica de negocio
│       └── compra_proveedor_service.py
├── main.py                        # Punto de entrada
├── requirements.txt
└── README.md
```

## 🔒 Validaciones

### Proveedor

- Nombre y NIT obligatorios
- NIT único
- Valores numéricos no negativos
- Rating entre 0 y 5

### Compra Proveedor

- ID de proveedor debe existir
- Valor de compra mayor a 0
- Factura obligatoria
- Fecha de recibido no puede ser anterior a fecha de compra

## 🎯 Mejores Prácticas Implementadas

1. **Actualización dinámica de campos**: Usa `model_dump(exclude_unset=True)` para actualizaciones eficientes
2. **Manejo de excepciones personalizado**: Errores específicos por tipo de problema
3. **Transacciones de base de datos**: Garantiza integridad de datos
4. **Logging estructurado**: Facilita debugging y monitoreo
5. **Constantes centralizadas**: Fácil mantenimiento
6. **Validaciones con Pydantic**: Datos seguros desde el origen
7. **CORS configurado**: Listo para frontend
8. **Health checks**: Monitoreo del estado del servicio

## 🚀 Refactorizaciones Realizadas

### ✅ Optimización de Updates

**Antes**: 80+ líneas de código repetitivo

```python
if proveedor_data.nombre is not None:
    update_fields.append(f"nombre = ${param_counter}")
    values.append(proveedor_data.nombre)
    param_counter += 1
# ... repetido para cada campo
```

**Después**: 6 líneas limpias

```python
update_data = proveedor_data.model_dump(exclude_unset=True)
for idx, (field, value) in enumerate(update_data.items(), start=1):
    update_fields.append(f"{field} = ${idx}")
    values.append(value)
```

### ✅ Esquema de BD Centralizado

**Antes**: `"psa_problems"` hardcodeado en múltiples lugares
**Después**: `DB_SCHEMA` constante centralizada

### ✅ Manejo de Errores Mejorado

- Excepciones específicas por tipo de error
- Validación de existencia antes de delete/update
- Mensajes de error descriptivos
- Logging detallado

### ✅ Validaciones en Modelos

- Constraints de Pydantic (gt, ge, le)
- Validadores personalizados para fechas
- Valores por defecto seguros

### ✅ Infraestructura Común

- `base_service.py`: Lógica CRUD reutilizable
- `utils.py`: Funciones helper comunes
- `constants.py`: Configuración centralizada

## 📊 Performance

- Pool de conexiones asíncronas
- Queries optimizadas
- Transacciones controladas
- Logging no bloqueante

## 🔐 Seguridad

- Variables de entorno para credenciales
- Validación de entrada con Pydantic
- SQL parametrizado (previene SQL injection)
- CORS configurable por ambiente

## 📝 Notas de Desarrollo

- El patrón Singleton garantiza una única instancia de conexión a BD
- Las transacciones se revierten automáticamente en caso de error
- Los modelos Update tienen todos los campos opcionales
- Status code 204 en DELETE (sin contenido en respuesta)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama de feature
3. Commit los cambios
4. Push a la rama
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
