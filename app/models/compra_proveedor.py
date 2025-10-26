from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone

def _normalize_datetime_field(v):
    """
    Función helper para normalizar fechas.
    Convierte todo a naive datetime en UTC para PostgreSQL.
    """
    if v is None:
        return v
    
    if isinstance(v, str):
        # Parsear string a datetime
        v = datetime.fromisoformat(v.replace('Z', '+00:00'))
    
    if isinstance(v, datetime):
        # Si tiene timezone, convertir a UTC y removerlo
        if v.tzinfo is not None:
            v = v.astimezone(timezone.utc).replace(tzinfo=None)
        # Si no tiene timezone, dejarlo como está (asumimos UTC)
    
    return v

class CompraProveedorBase(BaseModel):
    """Modelo base para CompraProveedor"""
    id_proveedor: int = Field(..., gt=0, description="ID del proveedor")
    valor_compra: Decimal = Field(..., gt=0, description="Valor de la compra")
    factura: str = Field(..., min_length=1, description="Número de factura")
    fecha_compra: Optional[datetime] = Field(default=None, description="Fecha de la compra (UTC)")
    fecha_recibido: Optional[datetime] = Field(default=None, description="Fecha cuando se recibió la compra (UTC)")
    destino: Optional[str] = Field(None, description="Destino de la compra")
    estado: Optional[int] = Field(default=0, ge=0, description="Estado de la compra")
    
    @field_validator('fecha_compra', 'fecha_recibido', mode='before')
    @classmethod
    def normalize_datetime(cls, v):
        """Normaliza las fechas usando la función helper"""
        return _normalize_datetime_field(v)
    
    @field_validator('fecha_recibido')
    @classmethod
    def validate_fecha_recibido(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Valida que fecha_recibido no sea anterior a fecha_compra"""
        if v and 'fecha_compra' in info.data and info.data['fecha_compra']:
            if v < info.data['fecha_compra']:
                raise ValueError('La fecha de recibido no puede ser anterior a la fecha de compra')
        return v

class CompraProveedorCreate(CompraProveedorBase):
    """Modelo para crear una compra de proveedor"""
    pass

class CompraProveedorUpdate(BaseModel):
    """Modelo para actualizar una compra de proveedor"""
    id_proveedor: Optional[int] = Field(None, gt=0, description="ID del proveedor")
    valor_compra: Optional[Decimal] = Field(None, gt=0, description="Valor de la compra")
    factura: Optional[str] = Field(None, min_length=1, description="Número de factura")
    fecha_compra: Optional[datetime] = Field(None, description="Fecha de la compra (UTC)")
    fecha_recibido: Optional[datetime] = Field(None, description="Fecha cuando se recibió la compra (UTC)")
    destino: Optional[str] = Field(None, description="Destino de la compra")
    estado: Optional[int] = Field(None, ge=0, description="Estado de la compra")
    
    @field_validator('fecha_compra', 'fecha_recibido', mode='before')
    @classmethod
    def normalize_datetime(cls, v):
        """Normaliza las fechas usando la función helper"""
        return _normalize_datetime_field(v)

class CompraProveedorResponse(CompraProveedorBase):
    """Modelo de respuesta para CompraProveedor"""
    id_compra: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }