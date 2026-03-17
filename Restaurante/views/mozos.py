"""Vista de tablets para mozos."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import (
    CarritoItem,
    CategoriaView,
    HistorialItem,
    MesaView,
    ProductoView,
    RestaurantState,
)
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_HOVER,
    ACCENT_SOFT,
    BORDER_COLOR,
    SUCCESS_SOFT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    action_button,
    app_shell,
    section_card,
    status_banner,
    surface_card,
)


READY_HIGHLIGHT = "rgba(251, 191, 36, 0.18)"
FREE_SURFACE = "rgba(34, 197, 94, 0.15)"
OCCUPIED_SURFACE = "rgba(239, 68, 68, 0.16)"

# Tamaño mínimo táctil recomendado para tabletas (44 px según HIG / Material)
TOUCH_BTN = "44px"


# ---------------------------------------------------------------------------
# Mapa de mesas
# ---------------------------------------------------------------------------

def mesa_tile(mesa: MesaView) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        f"Mesa {mesa.numero}",
                        color=TEXT_MUTED,
                        font_size="0.82rem",
                        font_weight="700",
                        text_transform="uppercase",
                        letter_spacing="0.1em",
                    ),
                    rx.heading(
                        mesa.label,
                        size="7",
                        color=TEXT_PRIMARY,
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.box(
                        mesa.estado_label,
                        padding="0.3rem 0.75rem",
                        border_radius="999px",
                        style={"background": mesa.badge_bg},
                        color=mesa.badge_text,
                        font_weight="800",
                        font_size="0.78rem",
                    ),
                    rx.cond(
                        mesa.tiene_items_listos,
                        rx.box(
                            f"{mesa.items_listos_count} listos",
                            padding="0.3rem 0.75rem",
                            border_radius="999px",
                            background="#FDBA74",
                            color="#7C2D12",
                            font_weight="800",
                            font_size="0.78rem",
                        ),
                        rx.fragment(),
                    ),
                    align="end",
                    spacing="2",
                ),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.spacer(),
            rx.hstack(
                rx.box(
                    rx.text("Capacidad", color=TEXT_MUTED, font_size="0.78rem"),
                    rx.text(mesa.capacidad, color=TEXT_PRIMARY, font_weight="800"),
                    width="100%",
                    padding="0.85rem",
                    border_radius="18px",
                    style={"background": "rgba(255,255,255,0.05)"},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                rx.box(
                    rx.text("Cuenta", color=TEXT_MUTED, font_size="0.78rem"),
                    rx.text(
                        mesa.total_abierto_texto,
                        color=TEXT_PRIMARY,
                        font_weight="800",
                    ),
                    width="100%",
                    padding="0.85rem",
                    border_radius="18px",
                    style={"background": "rgba(255,255,255,0.05)"},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                width="100%",
                spacing="3",
            ),
            rx.cond(
                mesa.tiene_items_listos,
                rx.box(
                    rx.hstack(
                        rx.box(
                            width="10px",
                            height="10px",
                            border_radius="999px",
                            style={"background": "#F59E0B"},
                        ),
                        rx.text(
                            "Hay platos listos para entregar",
                            color="#FED7AA",
                            font_weight="700",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    width="100%",
                    padding="0.8rem 0.95rem",
                    border_radius="18px",
                    style={"background": READY_HIGHLIGHT},
                    border="1px solid rgba(251, 191, 36, 0.36)",
                ),
                rx.box(
                    rx.text(
                        rx.cond(
                            RestaurantState.mesa_seleccionada_id == mesa.id,
                            "Mesa activa",
                            "Toca para tomar pedido",
                        ),
                        color=TEXT_SECONDARY,
                        font_weight="700",
                    ),
                    width="100%",
                    padding="0.8rem 0.95rem",
                    border_radius="18px",
                    style={"background": "rgba(255,255,255,0.05)"},
                    border=f"1px solid {BORDER_COLOR}",
                ),
            ),
            width="100%",
            align="start",
            height="100%",
            spacing="4",
        ),
        on_click=[
            RestaurantState.seleccionar_mesa(mesa.id),
            RestaurantState.set_mozos_tab("comanda"),
        ],
        style={"background": mesa.card_bg},
        border=rx.cond(
            mesa.tiene_items_listos,
            "2px solid rgba(251, 191, 36, 0.72)",
            mesa.card_border,
        ),
        border_radius="32px",
        box_shadow=rx.cond(
            mesa.tiene_items_listos,
            "0 0 0 6px rgba(251, 191, 36, 0.08), 0 26px 56px rgba(249, 115, 22, 0.16)",
            "0 18px 40px rgba(2, 6, 23, 0.28)",
        ),
        width="100%",
        min_height="230px",
        padding="1.1rem",
        cursor="pointer",
        transition="all 180ms ease",
        _hover={"transform": "translateY(-4px)"},
    )


# ---------------------------------------------------------------------------
# Carta (menú)
# ---------------------------------------------------------------------------

def categoria_button(categoria: CategoriaView) -> rx.Component:
    is_active = RestaurantState.categoria_activa_id == categoria.id
    return rx.button(
        categoria.nombre,
        on_click=RestaurantState.seleccionar_categoria(categoria.id),
        background=rx.cond(is_active, ACCENT, "rgba(255,255,255,0.05)"),
        color=TEXT_PRIMARY,
        border=rx.cond(
            is_active,
            "1px solid rgba(249, 115, 22, 0.42)",
            f"1px solid {BORDER_COLOR}",
        ),
        border_radius="999px",
        padding_x="1rem",
        height=TOUCH_BTN,
        font_weight="700",
        _hover={"background": "rgba(249, 115, 22, 0.18)"},
    )


def all_categories_button() -> rx.Component:
    is_active = RestaurantState.categoria_activa_id == 0
    return rx.button(
        "Todas",
        on_click=RestaurantState.seleccionar_categoria(0),
        background=rx.cond(is_active, ACCENT, "rgba(255,255,255,0.05)"),
        color=TEXT_PRIMARY,
        border=rx.cond(
            is_active,
            "1px solid rgba(249, 115, 22, 0.42)",
            f"1px solid {BORDER_COLOR}",
        ),
        border_radius="999px",
        padding_x="1rem",
        height=TOUCH_BTN,
        font_weight="700",
        _hover={"background": "rgba(249, 115, 22, 0.18)"},
    )


def producto_card(producto: ProductoView) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(tag="chef_hat", size=22, color="#FDBA74"),
                width="72px",
                height="72px",
                min_width="72px",
                border_radius="22px",
                style={
                    "background": (
                        "linear-gradient(135deg, rgba(249, 115, 22, 0.18) 0%, "
                        "rgba(234, 88, 12, 0.12) 100%)"
                    )
                },
                border="1px solid rgba(249, 115, 22, 0.18)",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(
                        producto.nombre,
                        color=TEXT_PRIMARY,
                        font_weight="800",
                        font_size="0.95rem",
                    ),
                    rx.box(
                        producto.categoria_nombre,
                        padding="0.2rem 0.55rem",
                        border_radius="999px",
                        style={"background": "rgba(255,255,255,0.05)"},
                        color=TEXT_MUTED,
                        font_size="0.72rem",
                        font_weight="700",
                        white_space="nowrap",
                    ),
                    spacing="2",
                    align="center",
                    wrap="wrap",
                ),
                rx.text(
                    producto.precio_texto,
                    color="#FDBA74",
                    font_weight="800",
                    font_size="1.05rem",
                ),
                width="100%",
                align="start",
                spacing="2",
            ),
            # Botón + con área táctil generosa
            rx.button(
                "+",
                on_click=RestaurantState.agregar_producto(producto.id),
                width="56px",
                height="56px",
                min_width="56px",
                border_radius="20px",
                background=ACCENT,
                color=TEXT_PRIMARY,
                font_size="1.6rem",
                font_weight="800",
                flex_shrink="0",
                box_shadow=f"0 12px 24px {ACCENT_SOFT}",
                _hover={"background": ACCENT_HOVER},
            ),
            width="100%",
            spacing="3",
            align="center",
        ),
        width="100%",
        padding="0.9rem 1rem",
        style={"background": "#1A2438"},
        border=f"1px solid {BORDER_COLOR}",
        border_radius="26px",
        box_shadow="0 12px 28px rgba(2, 6, 23, 0.22)",
    )


# ---------------------------------------------------------------------------
# Carrito — fila + nota inline
# ---------------------------------------------------------------------------

def _nota_input_inline(item: CarritoItem) -> rx.Component:
    """Input de nota expandible que aparece al tocar el lápiz del ítem."""

    nota_activa = RestaurantState.nota_producto_activo_id == item.producto_id
    return rx.cond(
        nota_activa,
        rx.hstack(
            rx.input(
                value=RestaurantState.nota_input_temporal,
                on_change=RestaurantState.set_nota_input_temporal,
                placeholder="Ej: sin cebolla, extra papas, bien cocido...",
                max_length=120,
                flex="1",
                height=TOUCH_BTN,
                border_radius="12px",
                style={"background": "rgba(255,255,255,0.07)"},
                border=f"1px solid {ACCENT}",
                color=TEXT_PRIMARY,
                font_size="0.85rem",
                padding_x="0.65rem",
            ),
            rx.button(
                "✓",
                on_click=RestaurantState.guardar_nota_carrito_item(item.producto_id),
                width=TOUCH_BTN,
                height=TOUCH_BTN,
                border_radius="12px",
                background=ACCENT,
                color=TEXT_PRIMARY,
                font_weight="800",
                font_size="1.1rem",
                _hover={"background": ACCENT_HOVER},
            ),
            rx.button(
                "✕",
                on_click=RestaurantState.cerrar_nota_item,
                width=TOUCH_BTN,
                height=TOUCH_BTN,
                border_radius="12px",
                background="rgba(255,255,255,0.06)",
                color=TEXT_MUTED,
                border=f"1px solid {BORDER_COLOR}",
            ),
            width="100%",
            spacing="2",
            align="center",
        ),
        rx.hstack(
            rx.cond(
                item.nota != "",
                rx.text(
                    f"📝 {item.nota}",
                    color=TEXT_MUTED,
                    font_size="0.8rem",
                    font_style="italic",
                    flex="1",
                ),
                rx.fragment(),
            ),
            rx.button(
                rx.cond(item.nota != "", "✏️ Editar nota", "+ Nota"),
                on_click=RestaurantState.abrir_nota_item(item.producto_id),
                height="32px",
                padding_x="0.65rem",
                border_radius="10px",
                background="rgba(255,255,255,0.05)",
                color=TEXT_MUTED,
                border=f"1px solid {BORDER_COLOR}",
                font_size="0.78rem",
                _hover={"background": ACCENT_SOFT, "color": TEXT_PRIMARY},
            ),
            width="100%",
            justify=rx.cond(item.nota != "", "between", "end"),
            align="center",
        ),
    )


def carrito_row(item: CarritoItem) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(item.nombre, color=TEXT_PRIMARY, font_weight="700"),
                rx.text(item.subtotal_texto, color=TEXT_PRIMARY, font_weight="800"),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.hstack(
                rx.button(
                    "−",
                    on_click=RestaurantState.restar_producto(item.producto_id),
                    width=TOUCH_BTN,
                    height=TOUCH_BTN,
                    border_radius="14px",
                    background="rgba(255,255,255,0.06)",
                    color=TEXT_PRIMARY,
                    font_size="1.25rem",
                    font_weight="800",
                    border=f"1px solid {BORDER_COLOR}",
                ),
                rx.box(
                    item.cantidad,
                    min_width="42px",
                    text_align="center",
                    color=TEXT_PRIMARY,
                    font_weight="800",
                    font_size="1.05rem",
                ),
                rx.button(
                    "+",
                    on_click=RestaurantState.agregar_producto(item.producto_id),
                    width=TOUCH_BTN,
                    height=TOUCH_BTN,
                    border_radius="14px",
                    background=ACCENT,
                    color=TEXT_PRIMARY,
                    font_size="1.25rem",
                    font_weight="800",
                    _hover={"background": ACCENT_HOVER},
                ),
                spacing="2",
                align="center",
            ),
            _nota_input_inline(item),
            width="100%",
            align="start",
            spacing="3",
        ),
        width="100%",
        padding="0.95rem",
        border_radius="20px",
        style={"background": "rgba(255,255,255,0.04)"},
        border=f"1px solid {BORDER_COLOR}",
    )


# ---------------------------------------------------------------------------
# Historial (ya pedido)
# ---------------------------------------------------------------------------

def historial_row(item: HistorialItem) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(item.nombre, color=TEXT_PRIMARY, font_weight="700"),
                    rx.text(
                        f"Enviado {item.enviado_en_texto}",
                        color=TEXT_MUTED,
                        font_size="0.82rem",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.box(
                    item.estado_label,
                    padding="0.25rem 0.65rem",
                    border_radius="999px",
                    style={"background": item.estado_bg},
                    color=item.estado_color,
                    font_weight="800",
                    font_size="0.75rem",
                    white_space="nowrap",
                ),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.hstack(
                rx.text(f"{item.cantidad}x", color=TEXT_MUTED, font_weight="700"),
                rx.text(item.subtotal_texto, color=TEXT_SECONDARY, font_weight="800"),
                spacing="2",
                align="center",
            ),
            rx.cond(
                item.nota != "",
                rx.box(
                    f"📝 {item.nota}",
                    width="100%",
                    padding="0.55rem 0.75rem",
                    border_radius="14px",
                    style={"background": "rgba(255,255,255,0.05)"},
                    color=TEXT_MUTED,
                    font_size="0.84rem",
                ),
                rx.fragment(),
            ),
            rx.cond(
                item.preparado_por_nombre != "",
                rx.box(
                    f"✓ Preparado por: {item.preparado_por_nombre}",
                    width="100%",
                    padding="0.55rem 0.75rem",
                    border_radius="14px",
                    style={"background": "rgba(249, 115, 22, 0.12)"},
                    color="#FDBA74",
                    font_size="0.82rem",
                    font_weight="700",
                    border="1px solid rgba(249, 115, 22, 0.18)",
                ),
                rx.fragment(),
            ),
            rx.cond(
                item.puede_entregar,
                rx.button(
                    "Entregar a la Mesa",
                    on_click=RestaurantState.entregar_item_historial(item.detalle_id),
                    width="100%",
                    height=TOUCH_BTN,
                    background=ACCENT,
                    color=TEXT_PRIMARY,
                    border_radius="16px",
                    font_weight="800",
                    font_size="0.95rem",
                    _hover={"background": ACCENT_HOVER},
                ),
                rx.fragment(),
            ),
            width="100%",
            align="start",
            spacing="2",
        ),
        width="100%",
        padding="0.95rem",
        border_radius="20px",
        style={
            "background": rx.cond(
                item.puede_entregar,
                "rgba(249, 115, 22, 0.14)",
                "rgba(255,255,255,0.04)",
            )
        },
        border=rx.cond(
            item.puede_entregar,
            "1px solid rgba(249, 115, 22, 0.24)",
            f"1px solid {BORDER_COLOR}",
        ),
    )


# ---------------------------------------------------------------------------
# Panel de comanda (carrito + historial + acciones)
# Se usa tanto en desktop (sticky lateral) como en tablet (tab "Comanda")
# ---------------------------------------------------------------------------

def _totales_bar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text("Pendiente", color=TEXT_MUTED, font_size="0.82rem"),
                rx.text(
                    RestaurantState.total_carrito_texto,
                    color=TEXT_PRIMARY,
                    font_size="1.18rem",
                    font_weight="800",
                ),
                align="start",
                spacing="1",
            ),
            rx.vstack(
                rx.text("Acumulado", color=TEXT_MUTED, font_size="0.82rem"),
                rx.text(
                    RestaurantState.mesa_seleccionada_total_texto,
                    color=TEXT_PRIMARY,
                    font_size="1.5rem",
                    font_weight="800",
                ),
                align="end",
                spacing="1",
            ),
            width="100%",
            justify="between",
            align="center",
        ),
        width="100%",
        padding="1rem",
        border_radius="22px",
        style={"background": "rgba(255,255,255,0.05)"},
        border=f"1px solid {BORDER_COLOR}",
    )


def _acciones_bar() -> rx.Component:
    return rx.vstack(
        rx.button(
            rx.hstack(
                rx.icon(tag="send", size=17),
                rx.text("Enviar a Cocina", font_weight="800"),
                spacing="2",
                align="center",
            ),
            on_click=RestaurantState.enviar_pedido,
            width="100%",
            height="52px",
            background=ACCENT,
            color=TEXT_PRIMARY,
            border_radius="18px",
            font_size="1rem",
            _hover={"background": ACCENT_HOVER},
        ),
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon(tag="receipt", size=16),
                    rx.text("Solicitar Cuenta", font_weight="700", font_size="0.9rem"),
                    spacing="2",
                    align="center",
                ),
                on_click=RestaurantState.solicitar_cuenta,
                flex="1",
                height=TOUCH_BTN,
                background="rgba(59, 130, 246, 0.18)",
                color="#BFDBFE",
                border="1px solid rgba(59, 130, 246, 0.24)",
                border_radius="16px",
                _hover={"background": "rgba(59, 130, 246, 0.24)"},
            ),
            rx.button(
                rx.icon(tag="trash_2", size=16),
                on_click=RestaurantState.limpiar_carrito,
                width=TOUCH_BTN,
                height=TOUCH_BTN,
                background="rgba(255,255,255,0.04)",
                color=TEXT_MUTED,
                border=f"1px solid {BORDER_COLOR}",
                border_radius="16px",
                _hover={"background": "rgba(239,68,68,0.12)", "color": "#FCA5A5"},
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        spacing="3",
    )


def carrito_panel() -> rx.Component:
    """Panel sticky para desktop (xl+). Muestra carrito + historial + acciones."""

    return surface_card(
        rx.vstack(
            # Cabecera
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Mesa activa",
                        color=TEXT_MUTED,
                        font_size="0.78rem",
                        font_weight="800",
                        letter_spacing="0.12em",
                        text_transform="uppercase",
                    ),
                    rx.heading(
                        RestaurantState.mesa_seleccionada_label,
                        size="5",
                        color=TEXT_PRIMARY,
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.box(
                    rx.text("Total mesa", color=TEXT_MUTED, font_size="0.78rem"),
                    rx.text(
                        RestaurantState.mesa_seleccionada_total_texto,
                        color=TEXT_PRIMARY,
                        font_size="1.4rem",
                        font_weight="800",
                    ),
                    padding="0.9rem 1rem",
                    border_radius="20px",
                    style={"background": "rgba(255,255,255,0.05)"},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.box(height="1px", width="100%", background=BORDER_COLOR),
            # Carrito (items pendientes) — scrolleable si hay muchos
            rx.vstack(
                rx.hstack(
                    rx.heading("Comanda actual", size="4", color=TEXT_PRIMARY),
                    rx.box(
                        "No enviado",
                        padding="0.25rem 0.65rem",
                        border_radius="999px",
                        style={"background": "rgba(59, 130, 246, 0.18)"},
                        color="#BFDBFE",
                        font_size="0.75rem",
                        font_weight="800",
                    ),
                    width="100%",
                    justify="between",
                    align="center",
                ),
                rx.cond(
                    RestaurantState.cantidad_items_carrito > 0,
                    rx.box(
                        rx.vstack(
                            rx.foreach(RestaurantState.carrito, carrito_row),
                            width="100%",
                            spacing="3",
                        ),
                        width="100%",
                        max_height="280px",
                        overflow_y="auto",
                        padding_right="0.25rem",
                    ),
                    rx.box(
                        "No hay items pendientes por enviar.",
                        width="100%",
                        padding="1.15rem",
                        border_radius="20px",
                        style={"background": "rgba(255,255,255,0.03)"},
                        border=f"1px dashed {BORDER_COLOR}",
                        color=TEXT_MUTED,
                        text_align="center",
                    ),
                ),
                width="100%",
                align="start",
                spacing="3",
            ),
            rx.box(height="1px", width="100%", background=BORDER_COLOR),
            # Historial (ya enviado) — scrolleable
            rx.vstack(
                rx.hstack(
                    rx.heading("Ya pedido", size="4", color=TEXT_PRIMARY),
                    rx.box(
                        "Historial",
                        padding="0.25rem 0.65rem",
                        border_radius="999px",
                        style={"background": "rgba(255,255,255,0.05)"},
                        color=TEXT_MUTED,
                        font_size="0.75rem",
                        font_weight="700",
                    ),
                    width="100%",
                    justify="between",
                    align="center",
                ),
                rx.cond(
                    RestaurantState.hay_historial_pedido,
                    rx.box(
                        rx.vstack(
                            rx.foreach(RestaurantState.historial_pedido, historial_row),
                            width="100%",
                            spacing="3",
                        ),
                        width="100%",
                        max_height="320px",
                        overflow_y="auto",
                        padding_right="0.25rem",
                    ),
                    rx.box(
                        "Todavia no hay items enviados para esta mesa.",
                        width="100%",
                        padding="1.15rem",
                        border_radius="20px",
                        style={"background": "rgba(255,255,255,0.03)"},
                        border=f"1px dashed {BORDER_COLOR}",
                        color=TEXT_MUTED,
                        text_align="center",
                    ),
                ),
                width="100%",
                align="start",
                spacing="3",
            ),
            _totales_bar(),
            _acciones_bar(),
            width="100%",
            align="start",
            spacing="4",
        ),
        # sticky en desktop: se ancla al tope mientras el contenido scrollea
        width=rx.breakpoints(initial="100%", xl="400px"),
        min_width=rx.breakpoints(initial="100%", xl="400px"),
        position=rx.breakpoints(initial="static", xl="sticky"),
        top="1.5rem",
        max_height=rx.breakpoints(initial="none", xl="calc(100vh - 3rem)"),
        overflow_y=rx.breakpoints(initial="visible", xl="auto"),
        padding="1.2rem",
        background="linear-gradient(160deg, #131F33 0%, #0F1826 100%)",
    )


# ---------------------------------------------------------------------------
# Secciones contenedor
# ---------------------------------------------------------------------------

def mesas_section() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Salon",
                        color=ACCENT,
                        font_size="0.78rem",
                        font_weight="800",
                        letter_spacing="0.14em",
                        text_transform="uppercase",
                    ),
                    rx.heading("Mapa de mesas", size="6", color=TEXT_PRIMARY),
                    rx.text(
                        "Toca una mesa para tomar pedido o entregar platos listos.",
                        color=TEXT_MUTED,
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.box(
                    rx.text(
                        f"{RestaurantState.cantidad_mesas_abiertas} activas",
                        color=TEXT_SECONDARY,
                        font_weight="700",
                    ),
                    padding="0.85rem 1rem",
                    border_radius="18px",
                    style={"background": "rgba(255,255,255,0.04)"},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                width="100%",
                justify="between",
                align="center",
                wrap="wrap",
                gap="0.8rem",
            ),
            rx.grid(
                rx.foreach(RestaurantState.mesas, mesa_tile),
                template_columns=rx.breakpoints(
                    initial="repeat(2, minmax(0, 1fr))",
                    md="repeat(3, minmax(0, 1fr))",
                    xl="repeat(auto-fit, minmax(220px, 1fr))",
                ),
                gap="1rem",
                width="100%",
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
    )


def menu_section() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Carta",
                    color=ACCENT,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading("Carta digital", size="6", color=TEXT_PRIMARY),
                rx.text(
                    "Agrega platos al carrito con botones táctiles grandes.",
                    color=TEXT_MUTED,
                ),
                align="start",
                spacing="1",
            ),
            rx.flex(
                all_categories_button(),
                rx.foreach(RestaurantState.categorias_activas, categoria_button),
                wrap="wrap",
                gap="0.75rem",
                width="100%",
            ),
            rx.grid(
                rx.foreach(RestaurantState.productos_filtrados, producto_card),
                template_columns=rx.breakpoints(
                    initial="1fr",
                    md="repeat(2, minmax(0, 1fr))",
                    xl="repeat(2, minmax(0, 1fr))",
                ),
                gap="1rem",
                width="100%",
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
    )


# ---------------------------------------------------------------------------
# Tab switcher para mobile / tablet (< xl)
# En desktop no se muestra; el layout de 2 columnas es suficiente.
# ---------------------------------------------------------------------------

def _tab_button(label: str, tab_key: str, icon_tag: str) -> rx.Component:
    is_active = RestaurantState.mozos_tab_activa == tab_key
    return rx.button(
        rx.hstack(
            rx.icon(tag=icon_tag, size=16),
            rx.text(label, font_weight="800"),
            spacing="2",
            align="center",
        ),
        on_click=RestaurantState.set_mozos_tab(tab_key),
        flex="1",
        height="48px",
        border_radius="16px",
        background=rx.cond(is_active, ACCENT, "rgba(255,255,255,0.04)"),
        color=rx.cond(is_active, TEXT_PRIMARY, TEXT_MUTED),
        border=rx.cond(
            is_active,
            "1px solid rgba(249, 115, 22, 0.38)",
            f"1px solid {BORDER_COLOR}",
        ),
        _hover={"background": rx.cond(is_active, ACCENT_HOVER, "rgba(255,255,255,0.08)")},
    )


def _mobile_tab_bar() -> rx.Component:
    """Barra de pestañas visible solo en mobile/tablet (< xl)."""

    return rx.box(
        rx.hstack(
            _tab_button("Salon / Carta", "salon", "layout_grid"),
            _tab_button("Comanda", "comanda", "clipboard_list"),
            width="100%",
            spacing="3",
        ),
        # Solo visible en pantallas < xl
        display=rx.breakpoints(initial="block", xl="none"),
        width="100%",
    )


def _badge_count(count) -> rx.Component:
    """Badge numérico flotante para la tab de Comanda cuando hay items."""

    return rx.cond(
        count > 0,
        rx.box(
            count,
            position="absolute",
            top="-8px",
            right="-8px",
            min_width="22px",
            height="22px",
            border_radius="999px",
            background=ACCENT,
            color=TEXT_PRIMARY,
            font_size="0.72rem",
            font_weight="800",
            display="flex",
            align_items="center",
            justify_content="center",
            padding_x="0.3rem",
        ),
        rx.fragment(),
    )


# ---------------------------------------------------------------------------
# Página principal
# ---------------------------------------------------------------------------

def mozos_page() -> rx.Component:
    """Módulo principal para tablets de mozos."""

    # Contenido de la tab "Salon": mapa de mesas + carta
    salon_content = rx.vstack(
        mesas_section(),
        menu_section(),
        width="100%",
        spacing="5",
        align="start",
    )

    # Contenido de la tab "Comanda" en mobile
    comanda_mobile = rx.vstack(
        carrito_panel(),
        width="100%",
        spacing="4",
        align="start",
    )

    # Layout mobile: tabs (< xl)
    mobile_layout = rx.box(
        rx.vstack(
            _mobile_tab_bar(),
            # Panel salon
            rx.cond(
                RestaurantState.mozos_tab_activa == "salon",
                salon_content,
                comanda_mobile,
            ),
            width="100%",
            spacing="4",
            align="start",
        ),
        display=rx.breakpoints(initial="block", xl="none"),
        width="100%",
    )

    # Layout desktop: 2 columnas (>= xl)
    desktop_layout = rx.box(
        rx.grid(
            salon_content,
            carrito_panel(),
            template_columns="minmax(0, 1.45fr) 400px",
            gap="1.25rem",
            width="100%",
            align_items="start",
        ),
        display=rx.breakpoints(initial="none", xl="block"),
        width="100%",
    )

    content = rx.vstack(
        status_banner(
            rx.cond(
                RestaurantState.mensaje != "",
                RestaurantState.mensaje,
                "Revisa mesas, arma la comanda actual y controla los platos listos para entregar.",
            )
        ),
        mobile_layout,
        desktop_layout,
        width="100%",
        spacing="5",
        align="start",
        padding_bottom="1.5rem",
    )

    return rx.box(
        app_shell(
            active="mozos",
            title="Mozos / Salon",
            subtitle="Mapa de mesas, carta digital y comanda viva pensada para tablets en operacion continua.",
            action=action_button(
                "Actualizar",
                RestaurantState.refrescar,
                icon_tag="layout_grid",
            ),
            content=content,
        ),
        on_mount=RestaurantState.start_mozos_polling,
        on_unmount=RestaurantState.stop_mozos_polling,
    )
