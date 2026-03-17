"""Modelos SQLModel del MVP para restaurante."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel


class EstadoMesa(str, Enum):
    """Estados válidos para una mesa."""

    LIBRE = "libre"
    OCUPADA = "ocupada"
    ESPERANDO_CUENTA = "esperando_cuenta"


class EstadoPedido(str, Enum):
    """Estados válidos para un pedido."""

    BORRADOR = "borrador"
    ENVIADO = "enviado"
    EN_PREPARACION = "en_preparacion"
    LISTO = "listo"
    COBRADO = "cobrado"
    CANCELADO = "cancelado"


class EstadoProduccion(str, Enum):
    """Estados operativos de producción por item enviado a cocina."""

    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    LISTO_PARA_ENTREGAR = "listo_para_entregar"
    ENTREGADO_AL_CLIENTE = "entregado_al_cliente"


class TipoPedido(str, Enum):
    """Modalidades de venta soportadas por el sistema."""

    MESA = "Mesa"
    MOSTRADOR = "Mostrador"


class RolUsuario(str, Enum):
    """Roles válidos para los módulos del sistema."""

    MOZO = "Mozo"
    CAJA = "Caja"
    COCINA = "Cocina"
    ADMIN = "Admin"


class TimestampedModel(SQLModel):
    """Campos compartidos de auditoría."""

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Usuario(TimestampedModel, table=True):
    """Usuario operativo autenticado por PIN."""

    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=120, nullable=False)
    pin: str = Field(
        index=True,
        unique=True,
        min_length=4,
        max_length=6,
        nullable=False,
    )
    rol: str = Field(index=True, max_length=32, nullable=False)


class Mesa(TimestampedModel, table=True):
    """Mesa física del salón."""

    __tablename__ = "mesas"

    id: int | None = Field(default=None, primary_key=True)
    numero: int = Field(index=True, unique=True, nullable=False)
    nombre: str = Field(default="", max_length=80, nullable=False)
    capacidad: int = Field(default=4, ge=1, nullable=False)
    estado: str = Field(
        default=EstadoMesa.LIBRE.value,
        index=True,
        max_length=32,
        nullable=False,
    )
    activa: bool = Field(default=True, nullable=False)

    pedidos: list["Pedido"] = Relationship(back_populates="mesa")


class Categoria(TimestampedModel, table=True):
    """Agrupación de productos de la carta."""

    __tablename__ = "categorias"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=120, nullable=False)
    descripcion: str | None = Field(default=None, max_length=240)
    orden: int = Field(default=0, nullable=False)
    activa: bool = Field(default=True, nullable=False)

    productos: list["Producto"] = Relationship(back_populates="categoria")


class Producto(TimestampedModel, table=True):
    """Producto vendible del restaurante."""

    __tablename__ = "productos"

    id: int | None = Field(default=None, primary_key=True)
    categoria_id: int = Field(foreign_key="categorias.id", index=True, nullable=False)
    nombre: str = Field(index=True, max_length=160, nullable=False)
    descripcion: str | None = Field(default=None, max_length=240)
    sku: str | None = Field(default=None, index=True, max_length=60)
    precio: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    disponible: bool = Field(default=True, nullable=False)

    categoria: Categoria | None = Relationship(back_populates="productos")
    detalles: list["DetallePedido"] = Relationship(back_populates="producto")


class Pedido(TimestampedModel, table=True):
    """Pedido asociado a una mesa."""

    __tablename__ = "pedidos"

    id: int | None = Field(default=None, primary_key=True)
    mesa_id: int | None = Field(default=None, foreign_key="mesas.id", index=True)
    mozo_id: int | None = Field(default=None, foreign_key="usuarios.id", index=True)
    cajero_id: int | None = Field(default=None, foreign_key="usuarios.id", index=True)
    tipo_pedido: str = Field(
        default=TipoPedido.MESA.value,
        index=True,
        max_length=24,
        nullable=False,
    )
    nombre_cliente: str | None = Field(default=None, max_length=120)
    pagado: bool = Field(default=False, index=True, nullable=False)
    estado: str = Field(
        default=EstadoPedido.BORRADOR.value,
        index=True,
        max_length=32,
        nullable=False,
    )
    notas: str | None = Field(default=None, max_length=500)
    total: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    abierto_en: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    cerrado_en: datetime | None = Field(default=None)

    mesa: Mesa | None = Relationship(back_populates="pedidos")
    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")


class DetallePedido(TimestampedModel, table=True):
    """Línea individual de producto dentro de un pedido."""

    __tablename__ = "detalle_pedidos"

    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True, nullable=False)
    producto_id: int = Field(foreign_key="productos.id", index=True, nullable=False)
    cantidad: int = Field(default=1, ge=1, nullable=False)
    precio_unitario: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    subtotal: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    notas: str | None = Field(default=None, max_length=240)
    enviado_cocina_at: datetime | None = Field(default=None)
    preparado_por_id: int | None = Field(
        default=None,
        foreign_key="usuarios.id",
        index=True,
    )
    estado_produccion: str = Field(
        default=EstadoProduccion.PENDIENTE.value,
        index=True,
        max_length=40,
        nullable=False,
    )
    impreso_cocina: bool = Field(default=False, nullable=False)
    impreso_caja: bool = Field(default=False, nullable=False)

    pedido: Pedido | None = Relationship(back_populates="detalles")
    producto: Producto | None = Relationship(back_populates="detalles")
