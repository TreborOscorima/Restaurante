"""Configuración de engine y sesiones SQLModel."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import event, text
from sqlmodel import Session, SQLModel, create_engine


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(DATA_DIR / 'restaurante.db').resolve().as_posix()}",
)

CONNECT_ARGS = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=CONNECT_ARGS,
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
        """Activa WAL mode para lecturas concurrentes sin bloquear escrituras.

        Con 6 tablets haciendo polling cada 5 s, el modo journal por defecto
        (DELETE) produce 'database is locked'. WAL permite N lectores + 1
        escritor simultáneos. busy_timeout=5000 ms evita que un error de
        concurrencia aborte la operación: SQLite reintenta hasta 5 segundos.
        synchronous=NORMAL es seguro para LAN (sin riesgo de corrupción en
        caída de corriente a diferencia de synchronous=OFF).
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA cache_size=-8000")   # 8 MB de caché por conexión
        cursor.close()


def init_db() -> None:
    """Crea las tablas del MVP si no existen."""

    from Restaurante.db import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _run_lightweight_migrations()


def _run_lightweight_migrations() -> None:
    """Agrega columnas nuevas sin requerir un sistema formal de migraciones."""

    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.connect() as connection:
        detalle_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info('detalle_pedidos')"))
        }
        pedido_columns_info = list(
            connection.execute(text("PRAGMA table_info('pedidos')"))
        )
        pedido_columns = {row[1] for row in pedido_columns_info}
        mesa_id_not_null = any(
            row[1] == "mesa_id" and int(row[3]) == 1 for row in pedido_columns_info
        )
        pedido_requires_rebuild = mesa_id_not_null or not {
            "mozo_id",
            "cajero_id",
            "tipo_pedido",
            "nombre_cliente",
            "pagado",
        }.issubset(pedido_columns)

        if "enviado_cocina_at" not in detalle_columns:
            connection.execute(
                text("ALTER TABLE detalle_pedidos ADD COLUMN enviado_cocina_at DATETIME")
            )
        if "despachado_cocina" not in detalle_columns:
            connection.execute(
                text(
                    "ALTER TABLE detalle_pedidos "
                    "ADD COLUMN despachado_cocina BOOLEAN NOT NULL DEFAULT 0"
                )
            )
        if "estado_produccion" not in detalle_columns:
            connection.execute(
                text(
                    "ALTER TABLE detalle_pedidos "
                    "ADD COLUMN estado_produccion VARCHAR(40) NOT NULL DEFAULT 'pendiente'"
                )
            )
        if "preparado_por_id" not in detalle_columns:
            connection.execute(
                text("ALTER TABLE detalle_pedidos ADD COLUMN preparado_por_id INTEGER")
            )
        if pedido_requires_rebuild:
            mozo_expr = "mozo_id" if "mozo_id" in pedido_columns else "NULL"
            cajero_expr = "cajero_id" if "cajero_id" in pedido_columns else "NULL"
            tipo_expr = (
                "COALESCE(tipo_pedido, 'Mesa')"
                if "tipo_pedido" in pedido_columns
                else "'Mesa'"
            )
            cliente_expr = (
                "nombre_cliente" if "nombre_cliente" in pedido_columns else "NULL"
            )
            pagado_expr = (
                "COALESCE(pagado, CASE WHEN estado = 'cobrado' THEN 1 ELSE 0 END)"
                if "pagado" in pedido_columns
                else "CASE WHEN estado = 'cobrado' THEN 1 ELSE 0 END"
            )

            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            connection.execute(
                text(
                    """
                    CREATE TABLE pedidos_new (
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        id INTEGER PRIMARY KEY,
                        mesa_id INTEGER,
                        mozo_id INTEGER,
                        cajero_id INTEGER,
                        tipo_pedido VARCHAR(24) NOT NULL DEFAULT 'Mesa',
                        nombre_cliente VARCHAR(120),
                        pagado BOOLEAN NOT NULL DEFAULT 0,
                        estado VARCHAR(32) NOT NULL DEFAULT 'borrador',
                        notas VARCHAR(500),
                        total NUMERIC(10, 2) NOT NULL DEFAULT 0,
                        abierto_en DATETIME NOT NULL,
                        cerrado_en DATETIME,
                        FOREIGN KEY (mesa_id) REFERENCES mesas (id),
                        FOREIGN KEY (mozo_id) REFERENCES usuarios (id),
                        FOREIGN KEY (cajero_id) REFERENCES usuarios (id)
                    )
                    """
                )
            )
            connection.execute(
                text(
                    f"""
                    INSERT INTO pedidos_new (
                        created_at,
                        updated_at,
                        id,
                        mesa_id,
                        mozo_id,
                        cajero_id,
                        tipo_pedido,
                        nombre_cliente,
                        pagado,
                        estado,
                        notas,
                        total,
                        abierto_en,
                        cerrado_en
                    )
                    SELECT
                        created_at,
                        updated_at,
                        id,
                        mesa_id,
                        {mozo_expr},
                        {cajero_expr},
                        {tipo_expr},
                        {cliente_expr},
                        {pagado_expr},
                        estado,
                        notas,
                        total,
                        abierto_en,
                        cerrado_en
                    FROM pedidos
                    """
                )
            )
            connection.execute(text("DROP TABLE pedidos"))
            connection.execute(text("ALTER TABLE pedidos_new RENAME TO pedidos"))
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_pedidos_mesa_id ON pedidos (mesa_id)")
            )
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_pedidos_mozo_id ON pedidos (mozo_id)")
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_pedidos_cajero_id ON pedidos (cajero_id)"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_pedidos_tipo_pedido ON pedidos (tipo_pedido)"
                )
            )
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_pedidos_pagado ON pedidos (pagado)")
            )
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_pedidos_estado ON pedidos (estado)")
            )
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")

        connection.execute(
            text(
                "UPDATE detalle_pedidos "
                "SET estado_produccion = 'pendiente' "
                "WHERE estado_produccion IS NULL OR estado_produccion = ''"
            )
        )

        if "despachado_cocina" in detalle_columns:
            connection.execute(
                text(
                    "UPDATE detalle_pedidos "
                    "SET estado_produccion = CASE "
                    "WHEN impreso_cocina = 0 THEN 'pendiente' "
                    "WHEN despachado_cocina = 1 THEN 'entregado_al_cliente' "
                    "ELSE 'pendiente' "
                    "END "
                    "WHERE estado_produccion = 'pendiente'"
                )
            )

        connection.execute(
            text(
                "UPDATE pedidos "
                "SET tipo_pedido = 'Mesa' "
                "WHERE tipo_pedido IS NULL OR tipo_pedido = ''"
            )
        )
        connection.execute(
            text(
                "UPDATE pedidos "
                "SET pagado = CASE WHEN estado = 'cobrado' THEN 1 ELSE pagado END"
            )
        )
        connection.commit()


def get_session() -> Session:
    """Devuelve una sesión de base de datos."""

    return Session(engine)
