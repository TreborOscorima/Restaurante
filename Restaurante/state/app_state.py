"""Estado principal del MVP para tablets de mozos, caja y catalogo."""

from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal, InvalidOperation

import reflex as rx
from pydantic import BaseModel
from sqlmodel import select

from Restaurante.db.models import (
    Categoria,
    DetallePedido,
    EstadoMesa,
    EstadoPedido,
    EstadoProduccion,
    Mesa,
    Pedido,
    Producto,
    RolUsuario,
    TipoPedido,
    Usuario,
)
from Restaurante.db.session import get_session, init_db
from Restaurante.services.printers import SilentPrinterService, TicketLine


CURRENCY_SYMBOL = "S/"
OPEN_ORDER_STATES = (
    EstadoPedido.BORRADOR.value,
    EstadoPedido.ENVIADO.value,
    EstadoPedido.EN_PREPARACION.value,
    EstadoPedido.LISTO.value,
)
KITCHEN_VISIBLE_STATES = (
    EstadoProduccion.PENDIENTE.value,
    EstadoProduccion.EN_PREPARACION.value,
)
MESA_LABELS = {
    EstadoMesa.LIBRE.value: "Libre",
    EstadoMesa.OCUPADA.value: "Ocupada",
    EstadoMesa.ESPERANDO_CUENTA.value: "Esperando cuenta",
}
MESA_BADGE_BACKGROUNDS = {
    EstadoMesa.LIBRE.value: "rgba(34, 197, 94, 0.16)",
    EstadoMesa.OCUPADA.value: "rgba(239, 68, 68, 0.16)",
    EstadoMesa.ESPERANDO_CUENTA.value: "rgba(245, 158, 11, 0.16)",
}
MESA_BADGE_TEXTS = {
    EstadoMesa.LIBRE.value: "#4ADE80",
    EstadoMesa.OCUPADA.value: "#FCA5A5",
    EstadoMesa.ESPERANDO_CUENTA.value: "#FCD34D",
}
MESA_CARD_BACKGROUNDS = {
    EstadoMesa.LIBRE.value: "#0C1C12",
    EstadoMesa.OCUPADA.value: "#1C0C0E",
    EstadoMesa.ESPERANDO_CUENTA.value: "#1C1408",
}
MESA_CARD_BORDERS = {
    EstadoMesa.LIBRE.value: "1px solid rgba(34, 197, 94, 0.28)",
    EstadoMesa.OCUPADA.value: "1px solid rgba(239, 68, 68, 0.28)",
    EstadoMesa.ESPERANDO_CUENTA.value: "1px solid rgba(245, 158, 11, 0.32)",
}
READY_ALERT_BORDER = "3px solid #F59E0B"
READY_ALERT_RING = "0 0 0 4px rgba(245, 158, 11, 0.22), 0 18px 45px rgba(234, 88, 12, 0.22)"
PRODUCTION_LABELS = {
    EstadoProduccion.PENDIENTE.value: "Pendiente",
    EstadoProduccion.EN_PREPARACION.value: "En preparación",
    EstadoProduccion.LISTO_PARA_ENTREGAR.value: "Listo para entregar",
    EstadoProduccion.ENTREGADO_AL_CLIENTE.value: "Entregado al cliente",
}
PRODUCTION_BADGE_BACKGROUNDS = {
    EstadoProduccion.PENDIENTE.value: "rgba(251, 191, 36, 0.16)",
    EstadoProduccion.EN_PREPARACION.value: "rgba(249, 115, 22, 0.18)",
    EstadoProduccion.LISTO_PARA_ENTREGAR.value: "rgba(34, 197, 94, 0.16)",
    EstadoProduccion.ENTREGADO_AL_CLIENTE.value: "rgba(59, 130, 246, 0.16)",
}
PRODUCTION_BADGE_TEXTS = {
    EstadoProduccion.PENDIENTE.value: "#FCD34D",
    EstadoProduccion.EN_PREPARACION.value: "#FDBA74",
    EstadoProduccion.LISTO_PARA_ENTREGAR.value: "#4ADE80",
    EstadoProduccion.ENTREGADO_AL_CLIENTE.value: "#93C5FD",
}
KITCHEN_CARD_BACKGROUNDS = {
    EstadoProduccion.PENDIENTE.value: "#16120A",
    EstadoProduccion.EN_PREPARACION.value: "#160E08",
}
KITCHEN_CARD_BORDERS = {
    EstadoProduccion.PENDIENTE.value: "rgba(251, 191, 36, 0.40)",
    EstadoProduccion.EN_PREPARACION.value: "rgba(249, 115, 22, 0.40)",
}
ROLE_HOME_ROUTES = {
    RolUsuario.MOZO.value: "/mozos",
    RolUsuario.CAJA.value: "/caja",
    RolUsuario.COCINA.value: "/cocina",
    RolUsuario.ADMIN.value: "/catalogo",
}
ROLE_ALLOWED_ROUTES = {
    "mozos": {RolUsuario.MOZO.value, RolUsuario.ADMIN.value},
    "caja": {RolUsuario.CAJA.value, RolUsuario.ADMIN.value},
    "mostrador": {RolUsuario.CAJA.value, RolUsuario.ADMIN.value},
    "cocina": {RolUsuario.COCINA.value, RolUsuario.ADMIN.value},
    "catalogo": {RolUsuario.ADMIN.value},
    "admin_ventas": {RolUsuario.ADMIN.value},
}


def _production_label(status: str) -> str:
    return PRODUCTION_LABELS.get(status, status.replace("_", " ").title())


def _production_badge_bg(status: str) -> str:
    return PRODUCTION_BADGE_BACKGROUNDS.get(status, "#E2E8F0")


def _production_badge_text(status: str) -> str:
    return PRODUCTION_BADGE_TEXTS.get(status, "#334155")


def _to_decimal(value: Decimal | float | int | None) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _money_text(value: Decimal | float | int | None) -> str:
    return f"{CURRENCY_SYMBOL} {_to_decimal(value):.2f}"


def _parse_positive_price(raw: str) -> Decimal | None:
    try:
        value = Decimal(raw.replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        return None
    if value <= 0:
        return None
    return value.quantize(Decimal("0.01"))


def _parse_non_negative_int(raw: str, fallback: int = 0) -> int:
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return fallback
    return value if value >= 0 else fallback


def _normalize_pin(raw: str) -> str:
    return "".join(char for char in str(raw) if char.isdigit())[:6]


def _role_home_route(role: str) -> str:
    return ROLE_HOME_ROUTES.get(role, "/login")


def _actor_name(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def _pedido_customer_name(pedido: Pedido) -> str:
    return _actor_name(pedido.nombre_cliente) or "Sin nombre"


def _pedido_table_label(pedido: Pedido, mesas: dict[int, Mesa]) -> str:
    if pedido.mesa_id is None:
        return "Mesa no asignada"
    mesa = mesas.get(pedido.mesa_id)
    if mesa is None:
        return f"Mesa {pedido.mesa_id}"
    return mesa.nombre or f"Mesa {mesa.numero}"


def _pedido_kitchen_label(pedido: Pedido, mesas: dict[int, Mesa]) -> str:
    if pedido.tipo_pedido == TipoPedido.MOSTRADOR.value:
        return f"Para Llevar - Cliente: {_pedido_customer_name(pedido)}"
    return _pedido_table_label(pedido, mesas)


def _pedido_sales_label(pedido: Pedido, mesas: dict[int, Mesa]) -> str:
    if pedido.tipo_pedido == TipoPedido.MOSTRADOR.value:
        return f"Mostrador ({_pedido_customer_name(pedido)})"
    return _pedido_table_label(pedido, mesas)


def _get_open_order(session, mesa_id: int) -> Pedido | None:
    return session.exec(
        select(Pedido)
        .where(Pedido.mesa_id == mesa_id, Pedido.estado.in_(OPEN_ORDER_STATES))
        .order_by(Pedido.id.desc())
    ).first()


def _get_unsent_details(session, pedido_id: int) -> list[DetallePedido]:
    return session.exec(
        select(DetallePedido)
        .where(
            DetallePedido.pedido_id == pedido_id,
            DetallePedido.impreso_cocina.is_(False),
        )
        .order_by(DetallePedido.id)
    ).all()


def _get_ready_details(session, pedido_id: int) -> list[DetallePedido]:
    return session.exec(
        select(DetallePedido)
        .where(
            DetallePedido.pedido_id == pedido_id,
            DetallePedido.impreso_cocina.is_(True),
            DetallePedido.estado_produccion
            == EstadoProduccion.LISTO_PARA_ENTREGAR.value,
        )
        .order_by(DetallePedido.id)
    ).all()


def _get_not_delivered_details(session, pedido_id: int) -> list[DetallePedido]:
    return session.exec(
        select(DetallePedido)
        .where(
            DetallePedido.pedido_id == pedido_id,
            DetallePedido.impreso_cocina.is_(True),
            DetallePedido.estado_produccion
            != EstadoProduccion.ENTREGADO_AL_CLIENTE.value,
        )
        .order_by(DetallePedido.id)
    ).all()


def _recalculate_order_total(session, pedido: Pedido) -> Decimal:
    detalles = session.exec(
        select(DetallePedido).where(DetallePedido.pedido_id == pedido.id)
    ).all()
    total = sum((_to_decimal(detalle.subtotal) for detalle in detalles), Decimal("0.00"))
    pedido.total = total
    pedido.updated_at = datetime.utcnow()
    session.add(pedido)
    return total


def _sync_order_status(session, pedido: Pedido) -> None:
    sent_details = session.exec(
        select(DetallePedido).where(
            DetallePedido.pedido_id == pedido.id,
            DetallePedido.impreso_cocina.is_(True),
        )
    ).all()

    if not sent_details:
        pedido.estado = EstadoPedido.BORRADOR.value
    elif any(
        detalle.estado_produccion == EstadoProduccion.LISTO_PARA_ENTREGAR.value
        for detalle in sent_details
    ):
        pedido.estado = EstadoPedido.LISTO.value
    elif any(
        detalle.estado_produccion == EstadoProduccion.EN_PREPARACION.value
        for detalle in sent_details
    ):
        pedido.estado = EstadoPedido.EN_PREPARACION.value
    elif any(
        detalle.estado_produccion == EstadoProduccion.PENDIENTE.value
        for detalle in sent_details
    ):
        pedido.estado = EstadoPedido.ENVIADO.value
    elif pedido.pagado and all(
        detalle.estado_produccion == EstadoProduccion.ENTREGADO_AL_CLIENTE.value
        for detalle in sent_details
    ):
        pedido.estado = EstadoPedido.COBRADO.value
    else:
        pedido.estado = EstadoPedido.ENVIADO.value

    pedido.updated_at = datetime.utcnow()
    session.add(pedido)


def _ensure_open_order(
    session,
    mesa: Mesa,
    mozo_id: int | None = None,
) -> Pedido:
    pedido = _get_open_order(session, mesa.id or 0)
    if pedido is not None:
        if mozo_id is not None and pedido.mozo_id is None:
            pedido.mozo_id = mozo_id
            pedido.updated_at = datetime.utcnow()
            session.add(pedido)
        return pedido

    pedido = Pedido(
        mesa_id=mesa.id or 0,
        mozo_id=mozo_id,
        estado=EstadoPedido.BORRADOR.value,
        total=Decimal("0.00"),
    )
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return pedido


class MesaView(BaseModel):
    id: int
    numero: int
    label: str
    nombre: str
    estado: str
    estado_label: str
    badge_bg: str
    badge_text: str
    capacidad: int
    total_abierto: float
    total_abierto_texto: str
    card_bg: str
    card_border: str
    tiene_items_listos: bool
    items_listos_count: int


class UsuarioSesion(BaseModel):
    id: int
    nombre: str
    rol: str


class CategoriaView(BaseModel):
    id: int
    nombre: str
    descripcion: str
    orden: int
    activa: bool


class ProductoView(BaseModel):
    id: int
    categoria_id: int
    categoria_nombre: str
    nombre: str
    descripcion: str
    precio: float
    precio_texto: str
    disponible: bool


class CarritoItem(BaseModel):
    producto_id: int
    nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    subtotal_texto: str
    nota: str = ""


class HistorialItem(BaseModel):
    detalle_id: int
    nombre: str
    cantidad: int
    precio_unitario_texto: str
    subtotal_texto: str
    nota: str
    enviado_en_texto: str
    estado_clave: str
    estado_label: str
    estado_bg: str
    estado_color: str
    preparado_por_nombre: str
    puede_entregar: bool


class CocinaTicketView(BaseModel):
    pedido_id: int
    mesa_label: str
    hora_texto: str
    estado_produccion: str
    estado_label: str
    estado_bg: str
    estado_color: str
    mozo_nombre: str
    action_label: str
    accent_bg: str
    accent_border: str
    detalle_ids_csv: str
    items_lines: list[str]


class VentaHistorialView(BaseModel):
    pedido_id: int
    mesa_label: str
    total: float
    total_texto: str
    mozo_nombre: str
    cajero_nombre: str


class MostradorEntregaView(BaseModel):
    pedido_id: int
    cliente_nombre: str
    hora_texto: str
    items_lines: list[str]
    items_count: int


class MostradorEntregadoView(BaseModel):
    pedido_id: int
    cliente_nombre: str
    hora_texto: str
    items_resumen: str
    total_texto: str


class RestaurantState(rx.State):
    """Estado global de la app para el MVP."""

    # ===========================================================
    # VARS — Datos reactivos (agrupados por dominio)
    # ===========================================================
    mesas: list[MesaView] = []
    categorias: list[CategoriaView] = []
    productos: list[ProductoView] = []
    carrito: list[CarritoItem] = []
    mostrador_carrito: list[CarritoItem] = []
    historial_pedido: list[HistorialItem] = []
    tickets_cocina: list[CocinaTicketView] = []
    historial_ventas: list[VentaHistorialView] = []
    pedidos_mostrador_listos: list[MostradorEntregaView] = []
    pedidos_mostrador_entregados: list[MostradorEntregadoView] = []
    mesa_seleccionada_id: int = 0
    mesa_atendida_por_nombre: str = ""
    categoria_activa_id: int = 0
    mostrador_categoria_activa_id: int = 0
    mostrador_cliente_nombre: str = ""
    ultimo_pedido_id: int = 0
    mensaje: str = ""
    usuario_actual: UsuarioSesion | None = None
    login_pin_input: str = ""
    sidebar_collapsed: bool = False

    categoria_form_id: int = 0
    categoria_form_nombre: str = ""
    categoria_form_descripcion: str = ""
    categoria_form_orden: str = "1"

    producto_form_id: int = 0
    producto_form_categoria_nombre: str = ""
    producto_form_nombre: str = ""
    producto_form_descripcion: str = ""
    producto_form_precio: str = ""
    producto_form_disponible: bool = True

    mozos_polling_enabled: bool = False
    cocina_polling_enabled: bool = False
    caja_polling_enabled: bool = False
    mostrador_polling_enabled: bool = False

    # Tab activa en /mozos para mobile/tablet ("salon" | "comanda")
    mozos_tab_activa: str = "salon"

    # ID del producto del carrito cuyo input de nota está abierto (0 = ninguno)
    nota_producto_activo_id: int = 0
    # Texto del input de nota mientras el mozo escribe
    nota_input_temporal: str = ""

    def cargar_datos_iniciales(self) -> None:
        """Inicializa tablas y carga datos base para la UI."""

        init_db()
        self.cargar_mesas()
        self.cargar_menu()
        self.cargar_cocina()
        self._bootstrap_forms()
        if self.mesa_seleccionada_id:
            self._cargar_carrito_mesa(self.mesa_seleccionada_id)
            self._cargar_historial_mesa(self.mesa_seleccionada_id)

    def _bootstrap_forms(self) -> None:
        """Inicializa selects y defaults de catalogo."""

        if not self.producto_form_categoria_nombre and self.categorias:
            self.producto_form_categoria_nombre = self.categorias[0].nombre
        if self.categoria_form_orden == "1" and self.categorias:
            self.categoria_form_orden = str(len(self.categorias) + 1)

    def refrescar(self) -> None:
        """Refresca todas las vistas de trabajo."""

        self.cargar_datos_iniciales()
        self.cargar_pedidos_mostrador_listos()
        self.cargar_pedidos_mostrador_entregados()
        self.mensaje = "Datos actualizados."

    def refrescar_mostrador(self) -> None:
        """Refresca catálogo y pedidos takeaway listos para la vista de mostrador."""

        self.cargar_menu()
        self.cargar_pedidos_mostrador_listos()
        self.cargar_pedidos_mostrador_entregados()
        self.mensaje = "Mostrador actualizado."

    def _clear_operational_context(self) -> None:
        """Limpia el estado sensible al cerrar sesión o cambiar de usuario."""

        self.mesas = []
        self.categorias = []
        self.productos = []
        self.carrito = []
        self.mostrador_carrito = []
        self.historial_pedido = []
        self.tickets_cocina = []
        self.historial_ventas = []
        self.pedidos_mostrador_listos = []
        self.pedidos_mostrador_entregados = []
        self.mesa_seleccionada_id = 0
        self.mesa_atendida_por_nombre = ""
        self.categoria_activa_id = 0
        self.mostrador_categoria_activa_id = 0
        self.mostrador_cliente_nombre = ""
        self.ultimo_pedido_id = 0
        self.mensaje = ""
        self.login_pin_input = ""
        self.sidebar_collapsed = False
        self.mozos_polling_enabled = False
        self.cocina_polling_enabled = False
        self.caja_polling_enabled = False
        self.mostrador_polling_enabled = False

    # ===========================================================
    # NAVEGACIÓN Y SHELL
    # ===========================================================
    def toggle_sidebar(self) -> None:
        """Alterna el ancho del menu lateral en escritorio."""

        self.sidebar_collapsed = not self.sidebar_collapsed

    def _route_access_result(self, route_key: str):
        """Valida autenticación y rol para una ruta protegida."""

        if self.usuario_actual is None:
            return rx.redirect("/login", replace=True)

        allowed_roles = ROLE_ALLOWED_ROUTES[route_key]
        if self.usuario_actual.rol not in allowed_roles:
            return [
                rx.window_alert("No tienes permisos para entrar a este módulo."),
                rx.redirect(self.usuario_home_route, replace=True),
            ]

        self.cargar_datos_iniciales()
        return None

    def on_load_root(self):
        """Resuelve la ruta inicial según el estado de sesión actual."""

        init_db()
        if self.usuario_actual is None:
            return rx.redirect("/login", replace=True)
        return rx.redirect(self.usuario_home_route, replace=True)

    def on_load_login(self):
        """Mantiene /login como puerta de entrada para usuarios no autenticados."""

        init_db()
        self.login_pin_input = ""
        if self.usuario_actual is not None:
            return rx.redirect(self.usuario_home_route, replace=True)
        return None

    def on_load_mozos(self):
        return self._route_access_result("mozos")

    def on_load_caja(self):
        return self._route_access_result("caja")

    def on_load_mostrador(self):
        route_result = self._route_access_result("mostrador")
        if route_result is not None:
            return route_result
        self.cargar_pedidos_mostrador_listos()
        self.cargar_pedidos_mostrador_entregados()
        return None

    def on_load_cocina(self):
        return self._route_access_result("cocina")

    def on_load_catalogo(self):
        return self._route_access_result("catalogo")

    def on_load_admin_ventas(self):
        route_result = self._route_access_result("admin_ventas")
        if route_result is not None:
            return route_result
        self.cargar_historial_ventas()
        return None

    # ===========================================================
    # AUTENTICACIÓN / LOGIN
    # ===========================================================
    def set_login_pin(self, value: str) -> None:
        self.login_pin_input = _normalize_pin(value)

    def append_login_digit(self, digit: str) -> None:
        if not digit.isdigit() or len(self.login_pin_input) >= 6:
            return
        self.login_pin_input = f"{self.login_pin_input}{digit}"

    def backspace_login_pin(self) -> None:
        self.login_pin_input = self.login_pin_input[:-1]

    def clear_login_pin(self) -> None:
        self.login_pin_input = ""

    def _authenticate_with_pin(self, pin: str):
        """Autentica un usuario por PIN y lo redirige a su módulo."""

        normalized_pin = _normalize_pin(pin)
        if len(normalized_pin) < 4:
            self.login_pin_input = ""
            return rx.window_alert("Ingresa un PIN válido de 4 a 6 dígitos.")

        with get_session() as session:
            usuario = session.exec(
                select(Usuario).where(Usuario.pin == normalized_pin)
            ).first()

        if usuario is None:
            self.login_pin_input = ""
            return rx.window_alert("PIN incorrecto. Intenta nuevamente.")

        self.usuario_actual = UsuarioSesion(
            id=usuario.id or 0,
            nombre=usuario.nombre,
            rol=usuario.rol,
        )
        self.login_pin_input = ""
        self.mensaje = f"Sesión iniciada como {usuario.nombre}."
        return rx.redirect(_role_home_route(usuario.rol), replace=True)

    def login(self, pin: str):
        """Busca el PIN en base de datos y abre el módulo correspondiente."""

        return self._authenticate_with_pin(pin)

    def submit_login_pin(self):
        """Ejecuta login usando el PIN construido desde el teclado numérico."""

        return self._authenticate_with_pin(self.login_pin_input)

    def logout(self):
        """Cierra la sesión local y fuerza el regreso a /login."""

        self.usuario_actual = None
        self._clear_operational_context()
        return rx.redirect("/login", replace=True)

    # ===========================================================
    # POLLING — Loops de sincronización en tiempo real
    # ===========================================================
    def _refresh_mozos_slice(self) -> None:
        """Recarga solo los datos operativos que usa Mozos."""

        if self.usuario_actual is None:
            return
        self.cargar_mesas()
        if self.mesa_seleccionada_id:
            self._cargar_carrito_mesa(self.mesa_seleccionada_id)
            self._cargar_historial_mesa(self.mesa_seleccionada_id)

    def _refresh_cocina_slice(self) -> None:
        """Recarga los tickets de cocina y el estado visible de mesas."""

        if self.usuario_actual is None:
            return
        self.cargar_cocina()
        self.cargar_mesas()
        if self.mesa_seleccionada_id:
            self._cargar_historial_mesa(self.mesa_seleccionada_id)

    def _refresh_caja_slice(self) -> None:
        """Recarga las mesas abiertas y la cuenta seleccionada."""

        if self.usuario_actual is None:
            return
        self.cargar_mesas()
        if self.mesa_seleccionada_id:
            self._cargar_historial_mesa(self.mesa_seleccionada_id)

    def _refresh_mostrador_slice(self) -> None:
        """Recarga el panel de pedidos takeaway listos para entrega."""

        if self.usuario_actual is None:
            return
        self.cargar_pedidos_mostrador_listos()
        self.cargar_pedidos_mostrador_entregados()

    def cargar_historial_ventas(self) -> None:
        """Carga pedidos cerrados con datos de mozo y cajero para administración."""

        with get_session() as session:
            pedidos = session.exec(
                select(Pedido)
                .where(Pedido.pagado.is_(True))
                .order_by(Pedido.cerrado_en.desc(), Pedido.id.desc())
            ).all()
            mesas = {mesa.id: mesa for mesa in session.exec(select(Mesa)).all()}
            usuarios = {
                usuario.id: usuario for usuario in session.exec(select(Usuario)).all()
            }

            self.historial_ventas = [
                VentaHistorialView(
                    pedido_id=pedido.id or 0,
                    mesa_label=_pedido_sales_label(pedido, mesas),
                    total=float(_to_decimal(pedido.total)),
                    total_texto=_money_text(pedido.total),
                    mozo_nombre=_actor_name(
                        usuarios[pedido.mozo_id].nombre
                        if pedido.mozo_id in usuarios
                        else "Sin asignar"
                    ),
                    cajero_nombre=_actor_name(
                        usuarios[pedido.cajero_id].nombre
                        if pedido.cajero_id in usuarios
                        else "Sin asignar"
                    ),
                )
                for pedido in pedidos
            ]

    def cargar_pedidos_mostrador_listos(self) -> None:
        """Carga pedidos takeaway con items listos para entregar."""

        with get_session() as session:
            detalles = session.exec(
                select(DetallePedido)
                .where(
                    DetallePedido.impreso_cocina.is_(True),
                    DetallePedido.estado_produccion
                    == EstadoProduccion.LISTO_PARA_ENTREGAR.value,
                )
                .order_by(DetallePedido.enviado_cocina_at, DetallePedido.id)
            ).all()
            if not detalles:
                self.pedidos_mostrador_listos = []
                return

            pedido_ids = {detalle.pedido_id for detalle in detalles}
            pedidos = {
                pedido.id: pedido
                for pedido in session.exec(select(Pedido).where(Pedido.id.in_(pedido_ids)))
                .all()
                if pedido.tipo_pedido == TipoPedido.MOSTRADOR.value
            }
            productos = {
                producto.id: producto
                for producto in session.exec(select(Producto)).all()
            }

            grupos: dict[int, dict[str, object]] = {}
            for detalle in detalles:
                pedido = pedidos.get(detalle.pedido_id)
                if pedido is None:
                    continue
                marca = detalle.updated_at or detalle.enviado_cocina_at or detalle.created_at
                if pedido.id not in grupos:
                    grupos[pedido.id] = {
                        "pedido_id": pedido.id or 0,
                        "cliente_nombre": _pedido_customer_name(pedido),
                        "hora_texto": marca.strftime("%H:%M"),
                        "items_lines": [],
                        "items_count": 0,
                    }

                producto = productos.get(detalle.producto_id)
                grupos[pedido.id]["items_lines"].append(
                    f"{detalle.cantidad} x "
                    f"{producto.nombre if producto else f'Producto {detalle.producto_id}'}"
                )
                grupos[pedido.id]["items_count"] += detalle.cantidad

            self.pedidos_mostrador_listos = [
                MostradorEntregaView(
                    pedido_id=data["pedido_id"],
                    cliente_nombre=data["cliente_nombre"],
                    hora_texto=data["hora_texto"],
                    items_lines=data["items_lines"],
                    items_count=data["items_count"],
                )
                for data in grupos.values()
            ]

    def cargar_pedidos_mostrador_entregados(self) -> None:
        """Carga los últimos 10 pedidos takeaway completamente entregados."""

        with get_session() as session:
            pedidos = session.exec(
                select(Pedido)
                .where(
                    Pedido.tipo_pedido == TipoPedido.MOSTRADOR.value,
                    Pedido.pagado.is_(True),
                )
                .order_by(Pedido.updated_at.desc(), Pedido.id.desc())
            ).all()
            if not pedidos:
                self.pedidos_mostrador_entregados = []
                return

            productos = {
                producto.id: producto
                for producto in session.exec(select(Producto)).all()
            }
            historial: list[tuple[datetime, MostradorEntregadoView]] = []

            for pedido in pedidos:
                detalles = session.exec(
                    select(DetallePedido)
                    .where(DetallePedido.pedido_id == pedido.id)
                    .order_by(DetallePedido.id)
                ).all()
                if not detalles or any(
                    detalle.estado_produccion
                    != EstadoProduccion.ENTREGADO_AL_CLIENTE.value
                    for detalle in detalles
                ):
                    continue

                entregado_en = max(detalle.updated_at for detalle in detalles)
                resumen = " · ".join(
                    f"{detalle.cantidad}x "
                    f"{productos[detalle.producto_id].nombre if detalle.producto_id in productos else f'Producto {detalle.producto_id}'}"
                    for detalle in detalles
                )
                historial.append(
                    (
                        entregado_en,
                        MostradorEntregadoView(
                            pedido_id=pedido.id or 0,
                            cliente_nombre=_pedido_customer_name(pedido),
                            hora_texto=entregado_en.strftime("%H:%M"),
                            items_resumen=resumen,
                            total_texto=_money_text(pedido.total),
                        ),
                    )
                )

            historial.sort(key=lambda item: item[0], reverse=True)
            self.pedidos_mostrador_entregados = [
                item for _, item in historial[:10]
            ]

    async def _run_polling_loop(
        self,
        flag_name: str,
        interval_seconds: int,
        refresh_callback,
    ) -> None:
        """Ejecuta un loop periódico por cliente mientras la vista esté montada."""

        async with self:
            if getattr(self, flag_name):
                return
            setattr(self, flag_name, True)
            refresh_callback()

        while True:
            await asyncio.sleep(interval_seconds)
            try:
                async with self:
                    if not getattr(self, flag_name):
                        break
                    refresh_callback()
            except Exception:
                # El cliente cerró la pestaña o se desconectó antes de que
                # el loop terminara su ciclo de espera. Salimos limpiamente.
                break

    @rx.event(background=True)
    async def start_mozos_polling(self) -> None:
        await self._run_polling_loop(
            flag_name="mozos_polling_enabled",
            interval_seconds=5,
            refresh_callback=self._refresh_mozos_slice,
        )

    def stop_mozos_polling(self) -> None:
        self.mozos_polling_enabled = False

    @rx.event(background=True)
    async def start_cocina_polling(self) -> None:
        await self._run_polling_loop(
            flag_name="cocina_polling_enabled",
            interval_seconds=5,
            refresh_callback=self._refresh_cocina_slice,
        )

    def stop_cocina_polling(self) -> None:
        self.cocina_polling_enabled = False

    @rx.event(background=True)
    async def start_caja_polling(self) -> None:
        await self._run_polling_loop(
            flag_name="caja_polling_enabled",
            interval_seconds=10,
            refresh_callback=self._refresh_caja_slice,
        )

    def stop_caja_polling(self) -> None:
        self.caja_polling_enabled = False

    @rx.event(background=True)
    async def start_mostrador_polling(self) -> None:
        await self._run_polling_loop(
            flag_name="mostrador_polling_enabled",
            interval_seconds=5,
            refresh_callback=self._refresh_mostrador_slice,
        )

    def stop_mostrador_polling(self) -> None:
        self.mostrador_polling_enabled = False

    # ===========================================================
    # MOZOS — Mesas, carrito, envío a cocina, solicitar cuenta
    # ===========================================================
    def cargar_mesas(self) -> None:
        """Sincroniza la grilla de mesas con la base local."""

        mesas_ui: list[MesaView] = []

        with get_session() as session:
            mesas_db = session.exec(
                select(Mesa).where(Mesa.activa.is_(True)).order_by(Mesa.numero)
            ).all()

            for mesa in mesas_db:
                pedido_abierto = _get_open_order(session, mesa.id or 0)
                total_abierto = _to_decimal(
                    pedido_abierto.total if pedido_abierto else Decimal("0.00")
                )
                ready_details = (
                    _get_ready_details(session, pedido_abierto.id or 0)
                    if pedido_abierto is not None
                    else []
                )
                items_listos_count = sum(
                    detalle.cantidad for detalle in ready_details
                )
                tiene_items_listos = items_listos_count > 0
                mesas_ui.append(
                    MesaView(
                        id=mesa.id or 0,
                        numero=mesa.numero,
                        label=f"Mesa {mesa.numero}",
                        nombre=mesa.nombre or f"Mesa {mesa.numero}",
                        estado=mesa.estado,
                        estado_label=MESA_LABELS.get(mesa.estado, mesa.estado),
                        badge_bg=MESA_BADGE_BACKGROUNDS.get(mesa.estado, "#E5E7EB"),
                        badge_text=MESA_BADGE_TEXTS.get(mesa.estado, "#111827"),
                        capacidad=mesa.capacidad,
                        total_abierto=float(total_abierto),
                        total_abierto_texto=_money_text(total_abierto),
                        card_bg=MESA_CARD_BACKGROUNDS.get(mesa.estado, "#FFFFFF"),
                        card_border=(
                            READY_ALERT_BORDER
                            if tiene_items_listos
                            else MESA_CARD_BORDERS.get(
                                mesa.estado, "1px solid #E5E7EB"
                            )
                        ),
                        tiene_items_listos=tiene_items_listos,
                        items_listos_count=items_listos_count,
                    )
                )

        self.mesas = mesas_ui

        if self.mesa_seleccionada_id and not any(
            mesa.id == self.mesa_seleccionada_id for mesa in self.mesas
        ):
            self.mesa_seleccionada_id = 0
            self.carrito = []
            self.historial_pedido = []

    def cargar_menu(self) -> None:
        """Carga categorias y productos para operacion y catalogo."""

        with get_session() as session:
            categorias_db = session.exec(
                select(Categoria).order_by(Categoria.orden, Categoria.nombre)
            ).all()
            productos_db = session.exec(select(Producto).order_by(Producto.nombre)).all()

            categorias_map = {categoria.id: categoria.nombre for categoria in categorias_db}

            self.categorias = [
                CategoriaView(
                    id=categoria.id or 0,
                    nombre=categoria.nombre,
                    descripcion=categoria.descripcion or "",
                    orden=categoria.orden,
                    activa=categoria.activa,
                )
                for categoria in categorias_db
            ]
            self.productos = [
                ProductoView(
                    id=producto.id or 0,
                    categoria_id=producto.categoria_id,
                    categoria_nombre=categorias_map.get(producto.categoria_id, "General"),
                    nombre=producto.nombre,
                    descripcion=producto.descripcion or "",
                    precio=float(_to_decimal(producto.precio)),
                    precio_texto=_money_text(producto.precio),
                    disponible=producto.disponible,
                )
                for producto in productos_db
            ]

    def _cargar_carrito_mesa(self, mesa_id: int) -> None:
        """Sincroniza el carrito con los items pendientes de la mesa."""

        with get_session() as session:
            pedido = _get_open_order(session, mesa_id)
            if pedido is None:
                self.carrito = []
                return

            detalles = _get_unsent_details(session, pedido.id or 0)
            productos_map = {
                producto.id: producto for producto in session.exec(select(Producto)).all()
            }
            self.carrito = [
                CarritoItem(
                    producto_id=detalle.producto_id,
                    nombre=(
                        productos_map.get(detalle.producto_id).nombre
                        if productos_map.get(detalle.producto_id)
                        else f"Producto {detalle.producto_id}"
                    ),
                    cantidad=detalle.cantidad,
                    precio_unitario=float(_to_decimal(detalle.precio_unitario)),
                    subtotal=float(_to_decimal(detalle.subtotal)),
                    subtotal_texto=_money_text(detalle.subtotal),
                    nota=detalle.notas or "",
                )
                for detalle in detalles
            ]

    def _cargar_historial_mesa(self, mesa_id: int) -> None:
        """Carga los items ya enviados a cocina para la mesa seleccionada."""

        with get_session() as session:
            pedido = _get_open_order(session, mesa_id)
            if pedido is None:
                self.historial_pedido = []
                self.mesa_atendida_por_nombre = ""
                return

            detalles = session.exec(
                select(DetallePedido)
                .where(
                    DetallePedido.pedido_id == pedido.id,
                    DetallePedido.impreso_cocina.is_(True),
                )
                .order_by(DetallePedido.enviado_cocina_at, DetallePedido.id)
            ).all()
            productos_map = {
                producto.id: producto for producto in session.exec(select(Producto)).all()
            }
            usuarios_map = {
                usuario.id: usuario for usuario in session.exec(select(Usuario)).all()
            }
            mozo = usuarios_map.get(pedido.mozo_id)
            self.mesa_atendida_por_nombre = _actor_name(
                mozo.nombre if mozo else ""
            )
            historial: list[HistorialItem] = []
            for detalle in detalles:
                producto = productos_map.get(detalle.producto_id)
                preparado_por = usuarios_map.get(detalle.preparado_por_id)
                enviado_en = detalle.enviado_cocina_at or detalle.updated_at
                estado_produccion = (
                    detalle.estado_produccion or EstadoProduccion.PENDIENTE.value
                )
                historial.append(
                    HistorialItem(
                        detalle_id=detalle.id or 0,
                        nombre=producto.nombre if producto else f"Producto {detalle.producto_id}",
                        cantidad=detalle.cantidad,
                        precio_unitario_texto=_money_text(detalle.precio_unitario),
                        subtotal_texto=_money_text(detalle.subtotal),
                        nota=detalle.notas or "",
                        enviado_en_texto=enviado_en.strftime("%H:%M"),
                        estado_clave=estado_produccion,
                        estado_label=_production_label(estado_produccion),
                        estado_bg=_production_badge_bg(estado_produccion),
                        estado_color=_production_badge_text(estado_produccion),
                        preparado_por_nombre=_actor_name(
                            preparado_por.nombre if preparado_por else ""
                        ),
                        puede_entregar=(
                            estado_produccion
                            == EstadoProduccion.LISTO_PARA_ENTREGAR.value
                        ),
                    )
                )
            self.historial_pedido = historial

    # ===========================================================
    # COCINA / KDS
    # ===========================================================
    def cargar_cocina(self) -> None:
        """Agrupa los tickets pendientes en la pantalla de cocina."""

        with get_session() as session:
            detalles = session.exec(
                select(DetallePedido)
                .where(
                    DetallePedido.impreso_cocina.is_(True),
                    DetallePedido.estado_produccion.in_(KITCHEN_VISIBLE_STATES),
                )
                .order_by(DetallePedido.enviado_cocina_at, DetallePedido.id)
            ).all()

            pedido_ids = {detalle.pedido_id for detalle in detalles}
            pedidos = {
                pedido.id: pedido
                for pedido in session.exec(select(Pedido).where(Pedido.id.in_(pedido_ids)))
                .all()
            }
            mesas = {
                mesa.id: mesa
                for mesa in session.exec(select(Mesa)).all()
            }
            usuarios = {
                usuario.id: usuario
                for usuario in session.exec(select(Usuario)).all()
            }
            productos = {
                producto.id: producto
                for producto in session.exec(select(Producto)).all()
            }

            grupos: dict[tuple[int, str, str], dict[str, object]] = {}
            for detalle in detalles:
                pedido = pedidos.get(detalle.pedido_id)
                if pedido is None:
                    continue
                marca = detalle.enviado_cocina_at or detalle.updated_at
                lote = marca.isoformat()
                mesa_label = _pedido_kitchen_label(pedido, mesas)
                estado_produccion = (
                    detalle.estado_produccion or EstadoProduccion.PENDIENTE.value
                )
                mozo = usuarios.get(pedido.mozo_id)
                key = (pedido.id or 0, lote, estado_produccion)
                if key not in grupos:
                    grupos[key] = {
                        "pedido_id": pedido.id or 0,
                        "mesa_label": mesa_label,
                        "hora_texto": marca.strftime("%H:%M"),
                        "estado_produccion": estado_produccion,
                        "estado_label": _production_label(estado_produccion),
                        "estado_bg": _production_badge_bg(estado_produccion),
                        "estado_color": _production_badge_text(estado_produccion),
                        "mozo_nombre": _actor_name(mozo.nombre if mozo else ""),
                        "action_label": (
                            "Empezar a Preparar"
                            if estado_produccion == EstadoProduccion.PENDIENTE.value
                            else "Marcar como Listo"
                        ),
                        "accent_bg": KITCHEN_CARD_BACKGROUNDS.get(
                            estado_produccion, "#FFF7ED"
                        ),
                        "accent_border": KITCHEN_CARD_BORDERS.get(
                            estado_produccion, "#FCD34D"
                        ),
                        "detalle_ids": [],
                        "items_lines": [],
                    }

                producto = productos.get(detalle.producto_id)
                line = f"{detalle.cantidad} x {producto.nombre if producto else f'Producto {detalle.producto_id}'}"
                if detalle.notas:
                    line = f"{line} · Nota: {detalle.notas}"
                grupos[key]["items_lines"].append(line)
                grupos[key]["detalle_ids"].append(str(detalle.id or 0))

            self.tickets_cocina = [
                CocinaTicketView(
                    pedido_id=data["pedido_id"],
                    mesa_label=data["mesa_label"],
                    hora_texto=data["hora_texto"],
                    estado_produccion=data["estado_produccion"],
                    estado_label=data["estado_label"],
                    estado_bg=data["estado_bg"],
                    estado_color=data["estado_color"],
                    mozo_nombre=data["mozo_nombre"],
                    action_label=data["action_label"],
                    accent_bg=data["accent_bg"],
                    accent_border=data["accent_border"],
                    detalle_ids_csv=",".join(data["detalle_ids"]),
                    items_lines=data["items_lines"],
                )
                for _, data in grupos.items()
            ]

    def _transition_ticket_state(
        self,
        detalle_ids_csv: str,
        source_state: str,
        target_state: str,
        success_message: str,
        actor_user_id: int | None = None,
        actor_field_name: str | None = None,
    ) -> None:
        """Actualiza el estado de producción de un lote de cocina."""

        ids = [int(item) for item in detalle_ids_csv.split(",") if item.strip()]
        if not ids:
            self.mensaje = "No se encontro el ticket de cocina."
            return

        with get_session() as session:
            detalles = session.exec(
                select(DetallePedido).where(DetallePedido.id.in_(ids))
            ).all()
            actualizables = [
                detalle
                for detalle in detalles
                if detalle.impreso_cocina and detalle.estado_produccion == source_state
            ]
            if not actualizables:
                self.mensaje = "El ticket ya cambio de estado."
                return

            pedidos_afectados: set[int] = set()
            now = datetime.utcnow()
            for detalle in actualizables:
                detalle.estado_produccion = target_state
                detalle.updated_at = now
                if actor_field_name and actor_user_id is not None:
                    setattr(detalle, actor_field_name, actor_user_id)
                session.add(detalle)
                pedidos_afectados.add(detalle.pedido_id)

            for pedido_id in pedidos_afectados:
                pedido = session.get(Pedido, pedido_id)
                if pedido is not None:
                    _sync_order_status(session, pedido)
            session.commit()

        self.cargar_cocina()
        self.cargar_mesas()
        if self.mesa_seleccionada_id:
            self._cargar_historial_mesa(self.mesa_seleccionada_id)
        self.mensaje = success_message

    def iniciar_preparacion_ticket(self, detalle_ids_csv: str) -> None:
        """Mueve un ticket desde pendiente a en preparación."""

        self._transition_ticket_state(
            detalle_ids_csv=detalle_ids_csv,
            source_state=EstadoProduccion.PENDIENTE.value,
            target_state=EstadoProduccion.EN_PREPARACION.value,
            success_message="Ticket movido a preparación.",
        )

    def marcar_ticket_listo(self, detalle_ids_csv: str) -> None:
        """Mueve un ticket desde preparación a listo para entregar."""

        self._transition_ticket_state(
            detalle_ids_csv=detalle_ids_csv,
            source_state=EstadoProduccion.EN_PREPARACION.value,
            target_state=EstadoProduccion.LISTO_PARA_ENTREGAR.value,
            success_message="Pedido listo para entregar a salón.",
            actor_user_id=(
                self.usuario_actual.id if self.usuario_actual is not None else None
            ),
            actor_field_name="preparado_por_id",
        )

    def entregar_item_historial(self, detalle_id: int) -> None:
        """Marca un item listo como entregado al cliente."""

        with get_session() as session:
            detalle = session.get(DetallePedido, detalle_id)
            if detalle is None or not detalle.impreso_cocina:
                self.mensaje = "El item indicado ya no existe."
                return
            if (
                detalle.estado_produccion
                != EstadoProduccion.LISTO_PARA_ENTREGAR.value
            ):
                self.mensaje = "Ese item no esta listo para entrega."
                return

            detalle.estado_produccion = EstadoProduccion.ENTREGADO_AL_CLIENTE.value
            detalle.updated_at = datetime.utcnow()
            session.add(detalle)

            pedido = session.get(Pedido, detalle.pedido_id)
            if pedido is not None:
                _sync_order_status(session, pedido)
            session.commit()

        if self.mesa_seleccionada_id:
            self._cargar_historial_mesa(self.mesa_seleccionada_id)
        self.cargar_mesas()
        self.cargar_cocina()
        self.mensaje = "Item entregado a la mesa."

    def entregar_pedido_mostrador(self, pedido_id: int) -> None:
        """Marca como entregados los items listos de un pedido takeaway."""

        with get_session() as session:
            pedido = session.get(Pedido, pedido_id)
            if pedido is None or pedido.tipo_pedido != TipoPedido.MOSTRADOR.value:
                self.mensaje = "El pedido de mostrador ya no existe."
                return

            detalles_listos = session.exec(
                select(DetallePedido).where(
                    DetallePedido.pedido_id == pedido_id,
                    DetallePedido.impreso_cocina.is_(True),
                    DetallePedido.estado_produccion
                    == EstadoProduccion.LISTO_PARA_ENTREGAR.value,
                )
            ).all()
            if not detalles_listos:
                self.mensaje = "Ese pedido ya no tiene items listos para entregar."
                return

            now = datetime.utcnow()
            for detalle in detalles_listos:
                detalle.estado_produccion = EstadoProduccion.ENTREGADO_AL_CLIENTE.value
                detalle.updated_at = now
                session.add(detalle)

            _sync_order_status(session, pedido)
            session.add(pedido)
            session.commit()

        self.cargar_cocina()
        self.cargar_pedidos_mostrador_listos()
        self.cargar_pedidos_mostrador_entregados()
        self.cargar_historial_ventas()
        self.mensaje = "Pedido de mostrador entregado al cliente."

    def _finalize_cart_cleanup(self, session, pedido: Pedido, mesa: Mesa) -> None:
        """Recalcula totales y libera la mesa si ya no quedan detalles."""

        detalles_restantes = session.exec(
            select(DetallePedido).where(DetallePedido.pedido_id == pedido.id)
        ).all()

        if not detalles_restantes:
            session.delete(pedido)
            mesa.estado = EstadoMesa.LIBRE.value
            mesa.updated_at = datetime.utcnow()
            session.add(mesa)
            return

        _recalculate_order_total(session, pedido)
        _sync_order_status(session, pedido)
        mesa.estado = EstadoMesa.OCUPADA.value
        mesa.updated_at = datetime.utcnow()
        session.add(mesa)

    def seleccionar_mesa(self, mesa_id: int) -> None:
        """Asigna la mesa activa y recupera su carrito pendiente."""

        self.mesa_seleccionada_id = mesa_id
        self._cargar_carrito_mesa(mesa_id)
        self._cargar_historial_mesa(mesa_id)
        mesa = next((item for item in self.mesas if item.id == mesa_id), None)
        alerta = (
            f" {mesa.items_listos_count} items listos para entregar."
            if mesa and mesa.tiene_items_listos
            else ""
        )
        self.mensaje = (
            f"{self.mesa_seleccionada_label} seleccionada. "
            f"{self.cantidad_items_carrito} items pendientes.{alerta}"
        )

    def seleccionar_categoria(self, categoria_id: int) -> None:
        """Filtra el catalogo de mozos por categoria."""

        self.categoria_activa_id = categoria_id

    # ===========================================================
    # MOSTRADOR — Pedidos para llevar / delivery
    # ===========================================================
    def set_mostrador_cliente_nombre(self, value: str) -> None:
        self.mostrador_cliente_nombre = str(value)[:120]

    def seleccionar_mostrador_categoria(self, categoria_id: int) -> None:
        self.mostrador_categoria_activa_id = categoria_id

    def agregar_producto_mostrador(self, producto_id: int) -> None:
        """Agrega productos al carrito de mostrador sin depender de una mesa."""

        producto = next(
            (
                item
                for item in self.productos
                if item.id == producto_id and item.disponible
            ),
            None,
        )
        if producto is None:
            self.mensaje = "Producto no disponible para mostrador."
            return

        carrito = list(self.mostrador_carrito)
        for index, item in enumerate(carrito):
            if item.producto_id == producto_id:
                cantidad = item.cantidad + 1
                subtotal = round(producto.precio * cantidad, 2)
                carrito[index] = CarritoItem(
                    producto_id=producto.id,
                    nombre=producto.nombre,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal,
                    subtotal_texto=_money_text(subtotal),
                )
                self.mostrador_carrito = carrito
                self.mensaje = f"{producto.nombre} agregado a mostrador."
                return

        carrito.append(
            CarritoItem(
                producto_id=producto.id,
                nombre=producto.nombre,
                cantidad=1,
                precio_unitario=producto.precio,
                subtotal=producto.precio,
                subtotal_texto=producto.precio_texto,
            )
        )
        self.mostrador_carrito = carrito
        self.mensaje = f"{producto.nombre} agregado a mostrador."

    def restar_producto_mostrador(self, producto_id: int) -> None:
        """Reduce una unidad del carrito de mostrador."""

        carrito_actualizado: list[CarritoItem] = []
        producto_nombre = ""
        encontrado = False

        for item in self.mostrador_carrito:
            if item.producto_id != producto_id:
                carrito_actualizado.append(item)
                continue

            encontrado = True
            producto_nombre = item.nombre
            cantidad = item.cantidad - 1
            if cantidad > 0:
                subtotal = round(item.precio_unitario * cantidad, 2)
                carrito_actualizado.append(
                    CarritoItem(
                        producto_id=item.producto_id,
                        nombre=item.nombre,
                        cantidad=cantidad,
                        precio_unitario=item.precio_unitario,
                        subtotal=subtotal,
                        subtotal_texto=_money_text(subtotal),
                    )
                )

        if not encontrado:
            self.mensaje = "Ese producto no esta en el carrito de mostrador."
            return

        self.mostrador_carrito = carrito_actualizado
        self.mensaje = (
            f"{producto_nombre} actualizado en mostrador."
            if carrito_actualizado
            else "Carrito de mostrador actualizado."
        )

    def limpiar_carrito_mostrador(self) -> None:
        self.mostrador_carrito = []
        self.mensaje = "Carrito de mostrador limpio."

    def cobrar_y_enviar_mostrador(self) -> None:
        """Cobra en caja y despacha a cocina un pedido para llevar."""

        if not self.mostrador_carrito:
            self.mensaje = "Agrega productos antes de cobrar en mostrador."
            return
        if self.usuario_actual is None:
            self.mensaje = "Inicia sesión para registrar la venta de mostrador."
            return

        pedido_id = 0
        total = 0.0
        cliente_nombre = _actor_name(self.mostrador_cliente_nombre) or "Sin nombre"
        ticket_label = f"Para Llevar - Cliente: {cliente_nombre}"
        attended_by = _actor_name(
            self.usuario_actual.nombre if self.usuario_actual is not None else ""
        ) or "Sin asignar"
        ticket_lines: list[TicketLine] = []

        with get_session() as session:
            productos = {
                producto.id: producto
                for producto in session.exec(select(Producto)).all()
            }
            productos_invalidos = [
                item.nombre
                for item in self.mostrador_carrito
                if item.producto_id not in productos
                or not productos[item.producto_id].disponible
            ]
            if productos_invalidos:
                self.mensaje = (
                    "Algunos productos ya no estan disponibles: "
                    + ", ".join(productos_invalidos)
                )
                return

            now = datetime.utcnow()
            pedido = Pedido(
                mesa_id=None,
                cajero_id=self.usuario_actual.id,
                tipo_pedido=TipoPedido.MOSTRADOR.value,
                nombre_cliente=(
                    _actor_name(self.mostrador_cliente_nombre) or None
                ),
                pagado=True,
                estado=EstadoPedido.ENVIADO.value,
                total=Decimal("0.00"),
                abierto_en=now,
                cerrado_en=now,
            )
            session.add(pedido)
            session.commit()
            session.refresh(pedido)

            for item in self.mostrador_carrito:
                producto = productos[item.producto_id]
                precio = _to_decimal(producto.precio)
                subtotal = precio * item.cantidad
                detalle = DetallePedido(
                    pedido_id=pedido.id or 0,
                    producto_id=producto.id or 0,
                    cantidad=item.cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal,
                    estado_produccion=EstadoProduccion.PENDIENTE.value,
                    impreso_cocina=True,
                    impreso_caja=True,
                    enviado_cocina_at=now,
                )
                session.add(detalle)
                ticket_lines.append(
                    TicketLine(
                        name=producto.nombre,
                        quantity=item.cantidad,
                        unit_price=float(precio),
                        subtotal=float(subtotal),
                        note="",
                    )
                )

            total = float(_recalculate_order_total(session, pedido))
            _sync_order_status(session, pedido)
            session.add(pedido)
            session.commit()
            pedido_id = pedido.id or 0

        self.ultimo_pedido_id = pedido_id
        self.mostrador_carrito = []
        self.mostrador_cliente_nombre = ""
        self.cargar_cocina()
        self.cargar_historial_ventas()
        self.cargar_pedidos_mostrador_entregados()

        printer_errors: list[str] = []
        try:
            printer_service = SilentPrinterService.from_env()
            printer_service.print_kitchen_ticket(
                mesa_label=ticket_label,
                pedido_id=pedido_id,
                items=ticket_lines,
            )
        except Exception as error:
            printer_errors.append(f"cocina: {error}")

        try:
            printer_service = SilentPrinterService.from_env()
            printer_service.print_cashier_ticket(
                order_reference=f"Cliente: {cliente_nombre}",
                pedido_id=pedido_id,
                items=ticket_lines,
                total=total,
                attended_by=attended_by,
            )
        except Exception as error:
            printer_errors.append(f"caja: {error}")

        if printer_errors:
            self.mensaje = (
                f"Pedido de mostrador #{pedido_id} cobrado y enviado. "
                f"Fallos de impresión: {' | '.join(printer_errors)}"
            )
            return

        self.mensaje = f"Pedido de mostrador #{pedido_id} cobrado y enviado."

    def limpiar_carrito(self) -> None:
        """Elimina de la base los items pendientes de la mesa seleccionada."""

        if self.mesa_seleccionada_id == 0:
            self.carrito = []
            self.mensaje = "No hay mesa seleccionada."
            return

        with get_session() as session:
            mesa = session.get(Mesa, self.mesa_seleccionada_id)
            if mesa is None:
                self.mensaje = "La mesa seleccionada ya no existe."
                return

            pedido = _get_open_order(session, mesa.id or 0)
            if pedido is None:
                self.carrito = []
                self.mensaje = "No hay pedido abierto para limpiar."
                return

            for detalle in _get_unsent_details(session, pedido.id or 0):
                session.delete(detalle)

            self._finalize_cart_cleanup(session, pedido, mesa)
            session.commit()

        self._cargar_carrito_mesa(self.mesa_seleccionada_id)
        self._cargar_historial_mesa(self.mesa_seleccionada_id)
        self.cargar_mesas()
        self.mensaje = "Items pendientes eliminados."

    def agregar_producto(self, producto_id: int) -> None:
        """Agrega o incrementa un producto dentro del pedido abierto de la mesa."""

        if self.mesa_seleccionada_id == 0:
            self.mensaje = "Selecciona una mesa antes de agregar productos."
            return

        with get_session() as session:
            mesa = session.get(Mesa, self.mesa_seleccionada_id)
            if mesa is None:
                self.mensaje = "La mesa seleccionada ya no existe."
                return

            producto = session.get(Producto, producto_id)
            if producto is None or not producto.disponible:
                self.mensaje = "Producto no disponible."
                return
            producto_nombre = producto.nombre

            pedido = _ensure_open_order(
                session,
                mesa,
                mozo_id=(
                    self.usuario_actual.id if self.usuario_actual is not None else None
                ),
            )
            detalle = session.exec(
                select(DetallePedido)
                .where(
                    DetallePedido.pedido_id == pedido.id,
                    DetallePedido.producto_id == producto.id,
                    DetallePedido.impreso_cocina.is_(False),
                )
                .order_by(DetallePedido.id.desc())
            ).first()

            precio = _to_decimal(producto.precio)
            if detalle is None:
                detalle = DetallePedido(
                    pedido_id=pedido.id or 0,
                    producto_id=producto.id or 0,
                    cantidad=1,
                    precio_unitario=precio,
                    subtotal=precio,
                    estado_produccion=EstadoProduccion.PENDIENTE.value,
                    impreso_cocina=False,
                    impreso_caja=False,
                )
            else:
                detalle.cantidad += 1
                detalle.precio_unitario = precio
                detalle.subtotal = precio * detalle.cantidad

            session.add(detalle)
            _recalculate_order_total(session, pedido)
            mesa.estado = EstadoMesa.OCUPADA.value
            mesa.updated_at = datetime.utcnow()
            session.add(pedido)
            session.add(mesa)
            session.commit()

        self._cargar_carrito_mesa(self.mesa_seleccionada_id)
        self._cargar_historial_mesa(self.mesa_seleccionada_id)
        self.cargar_mesas()
        self.mensaje = f"{producto_nombre} agregado a {self.mesa_seleccionada_label}."

    def restar_producto(self, producto_id: int) -> None:
        """Reduce una unidad del producto pendiente de la mesa seleccionada."""

        if self.mesa_seleccionada_id == 0:
            self.mensaje = "Selecciona una mesa antes de editar el carrito."
            return

        with get_session() as session:
            mesa = session.get(Mesa, self.mesa_seleccionada_id)
            if mesa is None:
                self.mensaje = "La mesa seleccionada ya no existe."
                return

            pedido = _get_open_order(session, mesa.id or 0)
            if pedido is None:
                self.mensaje = "No hay pedido abierto para esta mesa."
                return

            detalle = session.exec(
                select(DetallePedido)
                .where(
                    DetallePedido.pedido_id == pedido.id,
                    DetallePedido.producto_id == producto_id,
                    DetallePedido.impreso_cocina.is_(False),
                )
                .order_by(DetallePedido.id.desc())
            ).first()

            if detalle is None:
                self.mensaje = "Ese producto ya fue enviado o no existe en el carrito."
                return

            detalle.cantidad -= 1
            if detalle.cantidad <= 0:
                session.delete(detalle)
            else:
                detalle.subtotal = _to_decimal(detalle.precio_unitario) * detalle.cantidad
                session.add(detalle)

            self._finalize_cart_cleanup(session, pedido, mesa)
            session.commit()

        self._cargar_carrito_mesa(self.mesa_seleccionada_id)
        self._cargar_historial_mesa(self.mesa_seleccionada_id)
        self.cargar_mesas()
        self.mensaje = "Carrito actualizado."

    # ------------------------------------------------------------------
    # Notas por ítem del carrito
    # ------------------------------------------------------------------

    def set_mozos_tab(self, tab: str) -> None:
        """Cambia la pestaña activa en /mozos (solo aplica en mobile/tablet)."""
        self.mozos_tab_activa = tab

    def abrir_nota_item(self, producto_id: int) -> None:
        """Muestra el input de nota para el producto indicado del carrito."""

        item = next((i for i in self.carrito if i.producto_id == producto_id), None)
        self.nota_producto_activo_id = producto_id
        self.nota_input_temporal = item.nota if item else ""

    def set_nota_input_temporal(self, value: str) -> None:
        """Actualiza el texto del input de nota mientras el mozo escribe."""

        self.nota_input_temporal = str(value)[:120]

    def guardar_nota_carrito_item(self, producto_id: int) -> None:
        """Persiste la nota del input temporal en el DetallePedido sin enviar."""

        if self.mesa_seleccionada_id == 0:
            self.nota_producto_activo_id = 0
            return

        nota = self.nota_input_temporal.strip()

        with get_session() as session:
            pedido = _get_open_order(session, self.mesa_seleccionada_id)
            if pedido is None:
                self.nota_producto_activo_id = 0
                return

            detalle = session.exec(
                select(DetallePedido)
                .where(
                    DetallePedido.pedido_id == pedido.id,
                    DetallePedido.producto_id == producto_id,
                    DetallePedido.impreso_cocina.is_(False),
                )
                .order_by(DetallePedido.id.desc())
            ).first()

            if detalle is None:
                self.mensaje = "El item ya fue enviado a cocina; no se puede editar."
                self.nota_producto_activo_id = 0
                return

            detalle.notas = nota or None
            detalle.updated_at = datetime.utcnow()
            session.add(detalle)
            session.commit()

        self.nota_producto_activo_id = 0
        self.nota_input_temporal = ""
        self._cargar_carrito_mesa(self.mesa_seleccionada_id)
        self.mensaje = "Nota guardada." if nota else "Nota eliminada."

    def cerrar_nota_item(self) -> None:
        """Cierra el input de nota sin guardar."""

        self.nota_producto_activo_id = 0
        self.nota_input_temporal = ""

    def solicitar_cuenta(self) -> None:
        """Marca la mesa activa como lista para caja si no hay items pendientes."""

        if self.mesa_seleccionada_id == 0:
            self.mensaje = "Selecciona una mesa antes de solicitar cuenta."
            return
        if self.cantidad_items_carrito > 0:
            self.mensaje = "Primero envia a cocina los items pendientes del carrito."
            return

        with get_session() as session:
            mesa = session.get(Mesa, self.mesa_seleccionada_id)
            if mesa is None:
                self.mensaje = "La mesa seleccionada ya no existe."
                return

            pedido = _get_open_order(session, mesa.id or 0)
            if pedido is None or _to_decimal(pedido.total) <= 0:
                self.mensaje = "No hay consumo pendiente en esa mesa."
                return
            if _get_not_delivered_details(session, pedido.id or 0):
                self.mensaje = (
                    "Todavia hay items en cocina o listos por entregar para esa mesa."
                )
                return

            mesa.estado = EstadoMesa.ESPERANDO_CUENTA.value
            mesa.updated_at = datetime.utcnow()
            session.add(mesa)
            session.commit()

        self.cargar_mesas()
        self.mensaje = f"{self.mesa_seleccionada_label} marcada para cobrar."

    def enviar_pedido(self) -> None:
        """Envía solo los items pendientes a cocina y mantiene el pedido abierto."""

        if self.mesa_seleccionada_id == 0:
            self.mensaje = "Selecciona una mesa antes de enviar el pedido."
            return

        pedido_id = 0
        mesa_label = ""
        ticket_lines: list[TicketLine] = []

        with get_session() as session:
            mesa = session.get(Mesa, self.mesa_seleccionada_id)
            if mesa is None:
                self.mensaje = "La mesa seleccionada ya no existe."
                return

            pedido = _get_open_order(session, mesa.id or 0)
            if pedido is None:
                self.mensaje = "No hay items pendientes para enviar."
                return
            if self.usuario_actual is not None and pedido.mozo_id is None:
                pedido.mozo_id = self.usuario_actual.id
                pedido.updated_at = datetime.utcnow()
                session.add(pedido)

            detalles_pendientes = _get_unsent_details(session, pedido.id or 0)
            if not detalles_pendientes:
                self.mensaje = "No hay items nuevos pendientes de enviar."
                return

            productos_map = {
                producto.id: producto
                for producto in session.exec(select(Producto)).all()
            }
            now = datetime.utcnow()
            for detalle in detalles_pendientes:
                producto = productos_map.get(detalle.producto_id)
                ticket_lines.append(
                    TicketLine(
                        name=producto.nombre if producto else f"Producto {detalle.producto_id}",
                        quantity=detalle.cantidad,
                        unit_price=float(_to_decimal(detalle.precio_unitario)),
                        subtotal=float(_to_decimal(detalle.subtotal)),
                        note=detalle.notas or "",
                    )
                )
                detalle.impreso_cocina = True
                detalle.enviado_cocina_at = now
                detalle.estado_produccion = EstadoProduccion.PENDIENTE.value
                session.add(detalle)

            _recalculate_order_total(session, pedido)
            _sync_order_status(session, pedido)
            mesa.estado = EstadoMesa.OCUPADA.value
            mesa.updated_at = datetime.utcnow()

            session.add(pedido)
            session.add(mesa)
            session.commit()

            pedido_id = pedido.id or 0
            mesa_label = mesa.nombre or f"Mesa {mesa.numero}"

        self.ultimo_pedido_id = pedido_id
        self._cargar_carrito_mesa(self.mesa_seleccionada_id)
        self._cargar_historial_mesa(self.mesa_seleccionada_id)
        self.cargar_mesas()
        self.cargar_cocina()

        try:
            printer_service = SilentPrinterService.from_env()
            printer_service.print_kitchen_ticket(
                mesa_label=mesa_label,
                pedido_id=pedido_id,
                items=ticket_lines,
            )
        except Exception as error:
            self.mensaje = (
                f"Pedido #{pedido_id} guardado. Fallo la impresion de cocina: {error}"
            )
            return

        self.mensaje = f"Pedido #{pedido_id} enviado correctamente."

    # ===========================================================
    # CAJA — Cobro, cierre de mesa, ticket de venta
    # ===========================================================
    def cobrar_mesa(self, mesa_id: int) -> None:
        """Cierra la mesa, marca el pedido como cobrado e imprime caja."""

        objetivo = mesa_id or self.mesa_seleccionada_id
        if objetivo == 0:
            self.mensaje = "Selecciona una mesa antes de cobrar."
            return

        pedido_id = 0
        mesa_label = ""
        attended_by = ""
        total = 0.0
        ticket_lines: list[TicketLine] = []

        with get_session() as session:
            mesa = session.get(Mesa, objetivo)
            if mesa is None:
                self.mensaje = "La mesa indicada ya no existe."
                return

            pedido = _get_open_order(session, mesa.id or 0)
            if pedido is None:
                self.mensaje = "No hay pedido abierto para esa mesa."
                return

            detalles_pendientes = _get_unsent_details(session, pedido.id or 0)
            if detalles_pendientes:
                self.mensaje = "Todavia hay items pendientes de enviar a cocina."
                return
            if _get_not_delivered_details(session, pedido.id or 0):
                self.mensaje = (
                    "Todavia hay items en cocina o listos por entregar para esa mesa."
                )
                return

            detalles = session.exec(
                select(DetallePedido).where(DetallePedido.pedido_id == pedido.id)
            ).all()
            productos = {
                producto.id: producto
                for producto in session.exec(select(Producto)).all()
            }
            usuarios = {
                usuario.id: usuario
                for usuario in session.exec(select(Usuario)).all()
            }
            ticket_lines = [
                TicketLine(
                    name=(
                        productos.get(detalle.producto_id).nombre
                        if productos.get(detalle.producto_id)
                        else f"Producto {detalle.producto_id}"
                    ),
                    quantity=detalle.cantidad,
                    unit_price=float(_to_decimal(detalle.precio_unitario)),
                    subtotal=float(_to_decimal(detalle.subtotal)),
                    note=detalle.notas or "",
                )
                for detalle in detalles
            ]
            attended_by = _actor_name(
                (
                    usuarios[pedido.mozo_id].nombre
                    if pedido.mozo_id in usuarios
                    else (
                        self.usuario_actual.nombre
                        if self.usuario_actual is not None
                        else ""
                    )
                )
            ) or "Sin asignar"

            total = float(_to_decimal(pedido.total))
            now = datetime.utcnow()
            if self.usuario_actual is not None:
                pedido.cajero_id = self.usuario_actual.id
            pedido.pagado = True
            pedido.estado = EstadoPedido.COBRADO.value
            pedido.cerrado_en = now
            pedido.updated_at = now
            mesa.estado = EstadoMesa.LIBRE.value
            mesa.updated_at = now

            for detalle in detalles:
                detalle.impreso_caja = True
                session.add(detalle)

            session.add(pedido)
            session.add(mesa)
            session.commit()

            pedido_id = pedido.id or 0
            mesa_label = mesa.nombre or f"Mesa {mesa.numero}"

        if self.mesa_seleccionada_id == objetivo:
            self.mesa_seleccionada_id = 0
            self.mesa_atendida_por_nombre = ""
            self.carrito = []
            self.historial_pedido = []

        self.cargar_mesas()
        self.cargar_cocina()
        self.cargar_historial_ventas()

        try:
            printer_service = SilentPrinterService.from_env()
            printer_service.print_cashier_ticket(
                order_reference=f"Mesa: {mesa_label}",
                pedido_id=pedido_id,
                items=ticket_lines,
                total=total,
                attended_by=attended_by,
            )
        except Exception as error:
            self.mensaje = (
                f"Mesa cobrada por {_money_text(total)}. Fallo la impresion de caja: {error}"
            )
            return

        self.mensaje = f"{mesa_label} cobrada por {_money_text(total)}."

    # ===========================================================
    # CATÁLOGO / ADMIN — Gestión de categorías y productos
    # ===========================================================
    def set_categoria_form_nombre(self, value: str) -> None:
        self.categoria_form_nombre = value

    def set_categoria_form_descripcion(self, value: str) -> None:
        self.categoria_form_descripcion = value

    def set_categoria_form_orden(self, value: str) -> None:
        self.categoria_form_orden = value

    def nueva_categoria(self) -> None:
        self.categoria_form_id = 0
        self.categoria_form_nombre = ""
        self.categoria_form_descripcion = ""
        self.categoria_form_orden = str(len(self.categorias) + 1 if self.categorias else 1)
        self.mensaje = "Formulario de categoria listo para crear."

    def editar_categoria(self, categoria_id: int) -> None:
        categoria = next((item for item in self.categorias if item.id == categoria_id), None)
        if categoria is None:
            self.mensaje = "Categoria no encontrada."
            return

        self.categoria_form_id = categoria.id
        self.categoria_form_nombre = categoria.nombre
        self.categoria_form_descripcion = categoria.descripcion
        self.categoria_form_orden = str(categoria.orden)
        self.mensaje = f"Editando categoria {categoria.nombre}."

    def guardar_categoria(self) -> None:
        nombre = self.categoria_form_nombre.strip()
        if not nombre:
            self.mensaje = "El nombre de la categoria es obligatorio."
            return

        orden = _parse_non_negative_int(self.categoria_form_orden, fallback=1)

        with get_session() as session:
            duplicada = session.exec(
                select(Categoria).where(Categoria.nombre == nombre)
            ).first()
            if duplicada and (duplicada.id or 0) != self.categoria_form_id:
                self.mensaje = "Ya existe una categoria con ese nombre."
                return

            if self.categoria_form_id:
                categoria = session.get(Categoria, self.categoria_form_id)
                if categoria is None:
                    self.mensaje = "La categoria ya no existe."
                    return
            else:
                categoria = Categoria(nombre=nombre, activa=True)

            categoria.nombre = nombre
            categoria.descripcion = self.categoria_form_descripcion.strip()
            categoria.orden = orden
            categoria.activa = True

            session.add(categoria)
            session.commit()

        self.cargar_menu()
        self.nueva_categoria()
        self._bootstrap_forms()
        self.mensaje = f"Categoria {nombre} guardada."

    def toggle_categoria_activa(self, categoria_id: int) -> None:
        with get_session() as session:
            categoria = session.get(Categoria, categoria_id)
            if categoria is None:
                self.mensaje = "La categoria ya no existe."
                return

            categoria.activa = not categoria.activa
            session.add(categoria)
            session.commit()
            categoria_nombre = categoria.nombre

        self.cargar_menu()
        self._bootstrap_forms()
        self.mensaje = f"Categoria {categoria_nombre} actualizada."

    def set_producto_form_categoria_nombre(self, value: str) -> None:
        self.producto_form_categoria_nombre = value

    def set_producto_form_nombre(self, value: str) -> None:
        self.producto_form_nombre = value

    def set_producto_form_descripcion(self, value: str) -> None:
        self.producto_form_descripcion = value

    def set_producto_form_precio(self, value: str) -> None:
        self.producto_form_precio = value

    def set_producto_form_disponible(self, value: bool) -> None:
        self.producto_form_disponible = value

    def nuevo_producto(self) -> None:
        self.producto_form_id = 0
        self.producto_form_nombre = ""
        self.producto_form_descripcion = ""
        self.producto_form_precio = ""
        self.producto_form_disponible = True
        self.producto_form_categoria_nombre = (
            self.categorias[0].nombre if self.categorias else ""
        )
        self.mensaje = "Formulario de producto listo para crear."

    def editar_producto(self, producto_id: int) -> None:
        producto = next((item for item in self.productos if item.id == producto_id), None)
        if producto is None:
            self.mensaje = "Producto no encontrado."
            return

        self.producto_form_id = producto.id
        self.producto_form_categoria_nombre = producto.categoria_nombre
        self.producto_form_nombre = producto.nombre
        self.producto_form_descripcion = producto.descripcion
        self.producto_form_precio = f"{producto.precio:.2f}"
        self.producto_form_disponible = producto.disponible
        self.mensaje = f"Editando producto {producto.nombre}."

    def guardar_producto(self) -> None:
        nombre = self.producto_form_nombre.strip()
        if not nombre:
            self.mensaje = "El nombre del producto es obligatorio."
            return

        precio = _parse_positive_price(self.producto_form_precio)
        if precio is None:
            self.mensaje = "Ingresa un precio valido mayor a cero."
            return

        categoria = next(
            (
                item
                for item in self.categorias
                if item.nombre == self.producto_form_categoria_nombre
            ),
            None,
        )
        if categoria is None:
            self.mensaje = "Selecciona una categoria valida."
            return

        with get_session() as session:
            duplicado = session.exec(
                select(Producto).where(Producto.nombre == nombre)
            ).first()
            if duplicado and (duplicado.id or 0) != self.producto_form_id:
                self.mensaje = "Ya existe un producto con ese nombre."
                return

            if self.producto_form_id:
                producto = session.get(Producto, self.producto_form_id)
                if producto is None:
                    self.mensaje = "El producto ya no existe."
                    return
            else:
                producto = Producto(
                    categoria_id=categoria.id,
                    nombre=nombre,
                    disponible=True,
                )

            producto.categoria_id = categoria.id
            producto.nombre = nombre
            producto.descripcion = self.producto_form_descripcion.strip()
            producto.precio = precio
            producto.disponible = self.producto_form_disponible

            session.add(producto)
            session.commit()

        self.cargar_menu()
        self.nuevo_producto()
        self._bootstrap_forms()
        self.mensaje = f"Producto {nombre} guardado."

    def toggle_producto_disponible(self, producto_id: int) -> None:
        with get_session() as session:
            producto = session.get(Producto, producto_id)
            if producto is None:
                self.mensaje = "El producto ya no existe."
                return

            producto.disponible = not producto.disponible
            session.add(producto)
            session.commit()
            producto_nombre = producto.nombre

        self.cargar_menu()
        self._bootstrap_forms()
        self.mensaje = f"Producto {producto_nombre} actualizado."

    # ===========================================================
    # COMPUTED VARS (@rx.var) — Derivados reactivos
    # ===========================================================
    @rx.var
    def autenticado(self) -> bool:
        return self.usuario_actual is not None

    @rx.var
    def usuario_nombre(self) -> str:
        return self.usuario_actual.nombre if self.usuario_actual is not None else ""

    @rx.var
    def usuario_rol(self) -> str:
        return self.usuario_actual.rol if self.usuario_actual is not None else ""

    @rx.var
    def usuario_home_route(self) -> str:
        if self.usuario_actual is None:
            return "/login"
        return _role_home_route(self.usuario_actual.rol)

    @rx.var
    def puede_ver_mozos(self) -> bool:
        return self.usuario_rol in ROLE_ALLOWED_ROUTES["mozos"]

    @rx.var
    def puede_ver_caja(self) -> bool:
        return self.usuario_rol in ROLE_ALLOWED_ROUTES["caja"]

    @rx.var
    def puede_ver_mostrador(self) -> bool:
        return self.usuario_rol in ROLE_ALLOWED_ROUTES["mostrador"]

    @rx.var
    def puede_ver_cocina(self) -> bool:
        return self.usuario_rol in ROLE_ALLOWED_ROUTES["cocina"]

    @rx.var
    def puede_ver_catalogo(self) -> bool:
        return self.usuario_rol in ROLE_ALLOWED_ROUTES["catalogo"]

    @rx.var
    def puede_ver_admin_ventas(self) -> bool:
        return self.usuario_rol in ROLE_ALLOWED_ROUTES["admin_ventas"]

    @rx.var
    def mesa_seleccionada_label(self) -> str:
        for mesa in self.mesas:
            if mesa.id == self.mesa_seleccionada_id:
                return mesa.label
        return "Sin mesa seleccionada"

    @rx.var
    def mesa_seleccionada_total_texto(self) -> str:
        for mesa in self.mesas:
            if mesa.id == self.mesa_seleccionada_id:
                return mesa.total_abierto_texto
        return _money_text(0)

    @rx.var
    def total_carrito(self) -> float:
        return round(sum(item.subtotal for item in self.carrito), 2)

    @rx.var
    def total_carrito_texto(self) -> str:
        return _money_text(self.total_carrito)

    @rx.var
    def cantidad_items_carrito(self) -> int:
        return sum(item.cantidad for item in self.carrito)

    @rx.var
    def hay_historial_pedido(self) -> bool:
        return len(self.historial_pedido) > 0

    @rx.var
    def categorias_activas(self) -> list[CategoriaView]:
        return [categoria for categoria in self.categorias if categoria.activa]

    @rx.var
    def productos_filtrados(self) -> list[ProductoView]:
        productos_disponibles = [
            producto for producto in self.productos if producto.disponible
        ]
        if self.categoria_activa_id == 0:
            return productos_disponibles
        return [
            producto
            for producto in productos_disponibles
            if producto.categoria_id == self.categoria_activa_id
        ]

    @rx.var
    def productos_filtrados_mostrador(self) -> list[ProductoView]:
        productos_disponibles = [
            producto for producto in self.productos if producto.disponible
        ]
        if self.mostrador_categoria_activa_id == 0:
            return productos_disponibles
        return [
            producto
            for producto in productos_disponibles
            if producto.categoria_id == self.mostrador_categoria_activa_id
        ]

    @rx.var
    def mesas_abiertas(self) -> list[MesaView]:
        return [mesa for mesa in self.mesas if mesa.estado != EstadoMesa.LIBRE.value]

    @rx.var
    def cantidad_mesas_abiertas(self) -> int:
        return len(self.mesas_abiertas)

    @rx.var
    def total_pendiente_caja(self) -> float:
        return round(sum(mesa.total_abierto for mesa in self.mesas_abiertas), 2)

    @rx.var
    def total_pendiente_caja_texto(self) -> str:
        return _money_text(self.total_pendiente_caja)

    @rx.var
    def categoria_opciones(self) -> list[str]:
        return [categoria.nombre for categoria in self.categorias]

    @rx.var
    def hay_categorias(self) -> bool:
        return len(self.categorias) > 0

    @rx.var
    def tickets_nuevos(self) -> list[CocinaTicketView]:
        return [
            ticket
            for ticket in self.tickets_cocina
            if ticket.estado_produccion == EstadoProduccion.PENDIENTE.value
        ]

    @rx.var
    def tickets_en_preparacion(self) -> list[CocinaTicketView]:
        return [
            ticket
            for ticket in self.tickets_cocina
            if ticket.estado_produccion == EstadoProduccion.EN_PREPARACION.value
        ]

    @rx.var
    def hay_tickets_cocina(self) -> bool:
        return len(self.tickets_cocina) > 0

    @rx.var
    def cantidad_tickets_cocina(self) -> int:
        return len(self.tickets_cocina)

    @rx.var
    def cantidad_tickets_nuevos(self) -> int:
        return len(self.tickets_nuevos)

    @rx.var
    def cantidad_tickets_en_preparacion(self) -> int:
        return len(self.tickets_en_preparacion)

    @rx.var
    def mesas_con_alerta_entrega(self) -> int:
        return len([mesa for mesa in self.mesas if mesa.tiene_items_listos])

    @rx.var
    def total_recaudado(self) -> float:
        return round(sum(item.total for item in self.historial_ventas), 2)

    @rx.var
    def total_recaudado_texto(self) -> str:
        return _money_text(self.total_recaudado)

    @rx.var
    def total_mesas_atendidas(self) -> int:
        return len(self.historial_ventas)

    @rx.var
    def hay_historial_ventas(self) -> bool:
        return len(self.historial_ventas) > 0

    @rx.var
    def total_mostrador(self) -> float:
        return round(sum(item.subtotal for item in self.mostrador_carrito), 2)

    @rx.var
    def total_mostrador_texto(self) -> str:
        return _money_text(self.total_mostrador)

    @rx.var
    def cantidad_items_mostrador(self) -> int:
        return sum(item.cantidad for item in self.mostrador_carrito)

    @rx.var
    def hay_pedidos_mostrador_listos(self) -> bool:
        return len(self.pedidos_mostrador_listos) > 0

    @rx.var
    def cantidad_pedidos_mostrador_listos(self) -> int:
        return len(self.pedidos_mostrador_listos)

    @rx.var
    def hay_pedidos_mostrador_entregados(self) -> bool:
        return len(self.pedidos_mostrador_entregados) > 0
