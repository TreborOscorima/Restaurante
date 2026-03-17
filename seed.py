"""Carga datos de prueba para el MVP del restaurante."""

from __future__ import annotations

from decimal import Decimal

from sqlmodel import select

from Restaurante.db.models import Categoria, EstadoMesa, Mesa, Producto, RolUsuario, Usuario
from Restaurante.db.session import get_session, init_db


MESAS = [
    {"numero": numero, "nombre": f"Mesa {numero}", "capacidad": 4}
    for numero in range(1, 16)
]

CATEGORIAS = [
    {"nombre": "Promociones", "descripcion": "Combos y ofertas del dia", "orden": 1},
    {"nombre": "Platos a la Carta", "descripcion": "Especialidades de la casa", "orden": 2},
    {"nombre": "Bebidas", "descripcion": "Bebidas frias y acompanamientos", "orden": 3},
]

PRODUCTOS = [
    {
        "categoria": "Promociones",
        "nombre": "Promo 1/4 de Pollo",
        "descripcion": "1/4 de pollo con papas fritas y ensalada fresca",
        "precio": Decimal("24.90"),
    },
    {
        "categoria": "Promociones",
        "nombre": "Promo 1/2 Pollo Familiar",
        "descripcion": "1/2 pollo, papas familiares y cremas",
        "precio": Decimal("46.90"),
    },
    {
        "categoria": "Platos a la Carta",
        "nombre": "1/4 de Pollo a la Brasa",
        "descripcion": "Porcion clasica con papas crocantes",
        "precio": Decimal("22.90"),
    },
    {
        "categoria": "Platos a la Carta",
        "nombre": "Pollo Entero a la Brasa",
        "descripcion": "Pollo entero con papas, ensalada y cremas",
        "precio": Decimal("74.90"),
    },
    {
        "categoria": "Platos a la Carta",
        "nombre": "Parrilla Mixta",
        "descripcion": "Pollo, chorizo, anticucho y guarnicion",
        "precio": Decimal("39.90"),
    },
    {
        "categoria": "Platos a la Carta",
        "nombre": "Chaufa de Pollo",
        "descripcion": "Arroz chaufa salteado con pollo y tortilla",
        "precio": Decimal("28.50"),
    },
    {
        "categoria": "Bebidas",
        "nombre": "Chicha Morada Jarra",
        "descripcion": "Jarra helada de chicha morada casera",
        "precio": Decimal("15.90"),
    },
    {
        "categoria": "Bebidas",
        "nombre": "Gaseosa 1.5L",
        "descripcion": "Inca Kola o Coca-Cola en botella familiar",
        "precio": Decimal("11.90"),
    },
]

USUARIOS = [
    {"nombre": "Admin", "pin": "1111", "rol": RolUsuario.ADMIN.value},
    {"nombre": "Juan Mozo", "pin": "2222", "rol": RolUsuario.MOZO.value},
    {"nombre": "Ana Caja", "pin": "3333", "rol": RolUsuario.CAJA.value},
    {"nombre": "Luis Cocina", "pin": "4444", "rol": RolUsuario.COCINA.value},
]


def seed_mesas() -> int:
    creadas = 0

    with get_session() as session:
        existentes = {
            mesa.numero: mesa
            for mesa in session.exec(select(Mesa).where(Mesa.numero <= 15)).all()
        }

        for payload in MESAS:
            mesa = existentes.get(payload["numero"])
            if mesa is None:
                mesa = Mesa(
                    numero=payload["numero"],
                    nombre=payload["nombre"],
                    capacidad=payload["capacidad"],
                    estado=EstadoMesa.LIBRE.value,
                    activa=True,
                )
                session.add(mesa)
                creadas += 1
                continue

            mesa.nombre = payload["nombre"]
            mesa.capacidad = payload["capacidad"]
            mesa.estado = EstadoMesa.LIBRE.value
            mesa.activa = True
            session.add(mesa)

        session.commit()

    return creadas


def seed_categorias() -> dict[str, int]:
    categoria_ids: dict[str, int] = {}

    with get_session() as session:
        existentes = {
            categoria.nombre: categoria
            for categoria in session.exec(select(Categoria)).all()
        }

        for payload in CATEGORIAS:
            categoria = existentes.get(payload["nombre"])
            if categoria is None:
                categoria = Categoria(
                    nombre=payload["nombre"],
                    descripcion=payload["descripcion"],
                    orden=payload["orden"],
                    activa=True,
                )
            else:
                categoria.descripcion = payload["descripcion"]
                categoria.orden = payload["orden"]
                categoria.activa = True

            session.add(categoria)
            session.commit()
            session.refresh(categoria)
            categoria_ids[categoria.nombre] = categoria.id or 0

    return categoria_ids


def seed_productos(categoria_ids: dict[str, int]) -> int:
    creados = 0

    with get_session() as session:
        existentes = {
            producto.nombre: producto
            for producto in session.exec(select(Producto)).all()
        }

        for payload in PRODUCTOS:
            producto = existentes.get(payload["nombre"])
            if producto is None:
                producto = Producto(
                    categoria_id=categoria_ids[payload["categoria"]],
                    nombre=payload["nombre"],
                    descripcion=payload["descripcion"],
                    precio=payload["precio"],
                    disponible=True,
                )
                creados += 1
            else:
                producto.categoria_id = categoria_ids[payload["categoria"]]
                producto.descripcion = payload["descripcion"]
                producto.precio = payload["precio"]
                producto.disponible = True

            session.add(producto)

        session.commit()

    return creados


def seed_usuarios() -> int:
    creados = 0

    with get_session() as session:
        existentes = {
            usuario.pin: usuario for usuario in session.exec(select(Usuario)).all()
        }

        for payload in USUARIOS:
            usuario = existentes.get(payload["pin"])
            if usuario is None:
                usuario = Usuario(
                    nombre=payload["nombre"],
                    pin=payload["pin"],
                    rol=payload["rol"],
                )
                creados += 1
            else:
                usuario.nombre = payload["nombre"]
                usuario.rol = payload["rol"]

            session.add(usuario)

        session.commit()

    return creados


def main() -> None:
    init_db()

    mesas_creadas = seed_mesas()
    categoria_ids = seed_categorias()
    productos_creados = seed_productos(categoria_ids)
    usuarios_creados = seed_usuarios()

    print("Seed completado.")
    print(f"Mesas creadas: {mesas_creadas}")
    print(f"Categorias sincronizadas: {len(categoria_ids)}")
    print(f"Productos creados: {productos_creados}")
    print(f"Usuarios creados: {usuarios_creados}")


if __name__ == "__main__":
    main()
