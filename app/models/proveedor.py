from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class ProveedorBase(BaseModel):
    """Modelo base para Proveedor"""
    nombre: str = Field(..., description="Nombre del proveedor")
    nit: str = Field(..., max_length=100, description="NIT del proveedor")
    descripcion: Optional[str] = Field(None, description="Descripción del proveedor")
    num_art_comprados: int = Field(default=0, ge=0, description="Número de artículos comprados")
    num_art_devoluciones: int = Field(default=0, ge=0, description="Número de artículos devueltos")
    num_art_vendidas: int = Field(default=0, ge=0, description="Número de artículos vendidos")
    num_compras: int = Field(default=0, ge=0, description="Número de compras realizadas")
    valor_comprado: Decimal = Field(default=Decimal("0.00"), ge=0, description="Valor total comprado")
    num_devoluciones: int = Field(default=0, ge=0, description="Número de devoluciones realizadas")
    valor_devuelto: Decimal = Field(default=Decimal("0.00"), ge=0, description="Valor total devuelto")
    num_ventas: int = Field(default=0, ge=0, description="Número de ventas realizadas")
    valor_vendido: Decimal = Field(default=Decimal("0.00"), ge=0, description="Valor total vendido")
    rating_art_provedor: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, le=5, description="Rating del proveedor (0-5)")

class ProveedorCreate(ProveedorBase):
    """Modelo para crear un proveedor"""
    pass

class ProveedorUpdate(BaseModel):
    """Modelo para actualizar un proveedor"""
    nombre: Optional[str] = Field(None, description="Nombre del proveedor")
    nit: Optional[str] = Field(None, max_length=100, description="NIT del proveedor")
    descripcion: Optional[str] = Field(None, description="Descripción del proveedor")
    num_art_comprados: Optional[int] = Field(None, description="Número de artículos comprados")
    num_art_devoluciones: Optional[int] = Field(None, description="Número de artículos devueltos")
    num_art_vendidas: Optional[int] = Field(None, description="Número de artículos vendidos")
    num_compras: Optional[int] = Field(None, description="Número de compras realizadas")
    valor_comprado: Optional[Decimal] = Field(None, description="Valor total comprado")
    num_devoluciones: Optional[int] = Field(None, description="Número de devoluciones realizadas")
    valor_devuelto: Optional[Decimal] = Field(None, description="Valor total devuelto")
    num_ventas: Optional[int] = Field(None, description="Número de ventas realizadas")
    valor_vendido: Optional[Decimal] = Field(None, description="Valor total vendido")
    rating_art_provedor: Optional[Decimal] = Field(None, description="Rating del proveedor basado en artículos")

class ProveedorResponse(ProveedorBase):
    """Modelo de respuesta para Proveedor"""
    id_proveedor: int
    
    class Config:
        from_attributes = True